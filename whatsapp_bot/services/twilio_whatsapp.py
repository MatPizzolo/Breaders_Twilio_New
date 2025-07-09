"""
Twilio WhatsApp service for interacting with Twilio API
"""
import logging
import json
import requests
from typing import Dict, Any, Optional, Tuple

from twilio.rest import Client
from django.conf import settings
from ..models import Customer, Conversation, Message, MessageTemplate

logger = logging.getLogger(__name__)

class TwilioWhatsAppService:
    """Service for interacting with Twilio WhatsApp API"""
    
    def __init__(self):
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.whatsapp_number = settings.TWILIO_WHATSAPP_NUMBER
        self.client = Client(self.account_sid, self.auth_token)
        self.ai_assistant_url = getattr(settings, 'AI_ASSISTANT_URL', None)
        self.ai_assistant_api_key = getattr(settings, 'AI_ASSISTANT_API_KEY', '')
    
    def send_message(self, to_number: str, message_content: str, media_url: Optional[str] = None) -> Any:
        """
        Send WhatsApp message using Twilio API
        
        Args:
            to_number: Recipient's WhatsApp number (with whatsapp: prefix)
            message_content: Text content to send
            media_url: Optional URL to media to include
        
        Returns:
            Twilio message object if successful, None if failed
        """
        try:
            # Ensure the number has whatsapp: prefix
            if not to_number.startswith('whatsapp:'):
                to_number = f'whatsapp:{to_number}'
            
            message_params = {
                'from_': self.whatsapp_number,
                'body': message_content,
                'to': to_number
            }
            
            if media_url:
                message_params['media_url'] = [media_url]
            
            # Send the message via Twilio
            twilio_message = self.client.messages.create(**message_params)
            
            logger.info(f"WhatsApp message sent to {to_number}: {twilio_message.sid}")
            return twilio_message
        
        except Exception as e:
            logger.error(f"Failed to send WhatsApp message: {str(e)}")
            return None
    
    def process_incoming_message(self, from_number: str, message_body: str, 
                                media_url: Optional[str] = None, 
                                whatsapp_message_id: Optional[str] = None) -> Tuple[Optional[Conversation], Optional[Message]]:
        """
        Process incoming WhatsApp message
        
        Args:
            from_number: Sender's WhatsApp number
            message_body: Text content received
            media_url: Optional URL to media received
            whatsapp_message_id: Twilio message ID
            
        Returns:
            tuple: (conversation, message) objects created/updated
        """
        try:
            # Clean the phone number (remove whatsapp: prefix if present)
            clean_number = from_number.replace('whatsapp:', '') if from_number.startswith('whatsapp:') else from_number
            
            # Find or create customer
            customer, created = Customer.objects.get_or_create(
                phone_number=clean_number,
                defaults={'name': f"Customer {clean_number[-4:]}"}  # Default name using last 4 digits
            )
            
            # Find active conversation or create new one
            conversation = Conversation.objects.filter(
                customer=customer,
                active=True
            ).first()
            
            # Check if this is a new conversation (first interaction)
            is_first_interaction = False
            if not conversation:
                is_first_interaction = True
                conversation = Conversation.objects.create(
                    customer=customer,
                    current_state='greeting'
                )
            
            # Record the message
            message = Message.objects.create(
                conversation=conversation,
                content=message_body,
                media_url=media_url,
                direction='inbound',
                whatsapp_message_id=whatsapp_message_id
            )
            
            # Update conversation's last interaction time (happens via auto_now)
            conversation.save(update_fields=['last_interaction'])
            
            return conversation, message
            
        except Exception as e:
            logger.error(f"Error processing incoming message: {str(e)}")
            return None, None
    
    def send_template_message(self, to_number: str, template_name: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Send a message using a predefined template
        
        Args:
            to_number: Recipient's WhatsApp number
            template_name: Name of template to use
            context: Dictionary of context variables for template
            
        Returns:
            Twilio message object if successful, None if failed
        """
        try:
            template = MessageTemplate.objects.get(name=template_name)
            message_content = template.render(context or {})
            return self.send_message(to_number, message_content)
        except MessageTemplate.DoesNotExist:
            logger.error(f"Template {template_name} not found")
            return None
        except Exception as e:
            logger.error(f"Error sending template message: {str(e)}")
            return None
    
    def send_to_ai_assistant(self, message_text: str, from_number: str, 
                           context: Optional[Dict[str, Any]] = None,
                           is_first_interaction: bool = False) -> Dict[str, Any]:
        """
        Send a message to the Twilio AI Assistant
        
        Args:
            message_text: The message text to process
            from_number: The sender's phone number
            context: Optional context information for the AI
            is_first_interaction: Whether this is the first interaction with the user
            
        Returns:
            Dictionary with AI response data
        """
        try:
            # If this is the first interaction, check if it's a simple greeting
            if is_first_interaction:
                from ..services.constants import MENSAJE_BIENVENIDA, PALABRAS_SALUDO
                
                # Normalize message text (lowercase and strip)
                normalized_message = message_text.lower().strip()
                
                # Check if the message is a simple greeting
                is_greeting = any(greeting in normalized_message for greeting in PALABRAS_SALUDO)
                
                if is_greeting or len(normalized_message) < 10:  # Short messages are likely greetings
                    logger.info(f"First interaction with {from_number} is a greeting, sending welcome message")
                    return {'message': MENSAJE_BIENVENIDA}
                
                logger.info(f"First interaction with {from_number}, but not a simple greeting")
                # Continue to AI Assistant for non-greeting first messages
                
            # Get the Twilio Assistant ID from settings
            assistant_id = getattr(settings, 'TWILIO_ASSISTANT_ID', None)
            if not assistant_id:
                logger.error("TWILIO_ASSISTANT_ID not configured in settings")
                return {'message': 'Lo siento, el servicio de asistente AI no está disponible en este momento.'}
            
            # Format the session ID using the phone number to maintain conversation context
            # Remove any non-alphanumeric characters from the phone number
            clean_phone = ''.join(c for c in from_number if c.isalnum())
            session_id = f"session_{clean_phone}"
            
            # Prepare the context as a JSON string if provided
            identity = f"phone:{clean_phone}"
            if context:
                # Add context to the identity to pass additional information
                identity = f"phone:{clean_phone}|context:{json.dumps(context)}"
            
            # Prepare the API request
            headers = {
                'Content-Type': 'application/json',
            }
            
            # Determine if we should use synchronous or asynchronous mode
            # For now, use synchronous mode (no webhook)
            payload = {
                'identity': identity,
                'session_id': session_id,
                'body': message_text
            }
            
            # Add webhook URL if configured
            webhook_url = getattr(settings, 'TWILIO_ASSISTANT_WEBHOOK_URL', None)
            if webhook_url:
                payload['webhook'] = webhook_url
            
            logger.info(f"Sending message to Twilio Assistant: {message_text[:50]}...")
            
            # Construct the Twilio Assistant API URL
            assistant_url = f"https://assistants.twilio.com/v1/Assistants/{assistant_id}/Messages"
            
            # Make the API request with Basic Auth using the Twilio credentials
            response = requests.post(
                assistant_url,
                headers=headers,
                data=json.dumps(payload),
                auth=(self.account_sid, self.auth_token),
                timeout=10  # 10 second timeout
            )
            
            if response.status_code == 200 or response.status_code == 201:
                result = response.json()
                # Debug log the full response structure
                logger.debug(f"Twilio Assistant API response: {result}")
                
                # Extract the message from the Twilio response - handle different response formats
                # Try different possible response structures
                message = None
                
                # Option 1: Direct text in 'response' field
                if isinstance(result.get('response'), str):
                    message = result.get('response')
                # Option 2: Nested 'text' field in 'response' object
                elif isinstance(result.get('response'), dict):
                    message = result.get('response', {}).get('text')
                # Option 3: Message in 'body' field
                elif result.get('body'):
                    message = result.get('body')
                # Option 4: Message in 'content' field
                elif result.get('content'):
                    message = result.get('content')
                # Option 5: Message in 'message' field
                elif result.get('message'):
                    message = result.get('message')
                # Fallback
                else:
                    message = str(result)
                logger.info(f"Twilio Assistant response received: {message[:50]}...")
                return {'message': message}
            else:
                logger.error(f"Twilio Assistant error: {response.status_code} - {response.text}")
                return {'message': 'Lo siento, no pude procesar tu mensaje en este momento.'}
                
        except requests.RequestException as e:
            logger.error(f"Error connecting to AI Assistant: {str(e)}")
            return {'message': 'Lo siento, hay un problema de conexión con nuestro asistente.'}
        except Exception as e:
            logger.error(f"Unexpected error with AI Assistant: {str(e)}")
            return {'message': 'Lo siento, ocurrió un error inesperado.'}
    
    def send_order_confirmation(self, order) -> Any:
        """
        Send order confirmation message to customer
        
        Args:
            order: Order object with customer details
            
        Returns:
            Twilio message object
        """
        context = {
            'order_number': order.order_number,
            'total_amount': order.total_amount,
            'status': order.get_status_display()
        }
        
        return self.send_template_message(
            order.customer.phone_number,
            'order_confirmation',
            context
        )
        
    def send_delivery_update(self, order) -> Any:
        """
        Send delivery status update
        
        Args:
            order: Order object with updated status
            
        Returns:
            Twilio message object
        """
        context = {
            'order_number': order.order_number,
            'status': order.get_status_display(),
            'estimated_delivery': order.estimated_delivery_time.strftime('%H:%M %p') if order.estimated_delivery_time else 'Soon'
        }
        
        return self.send_template_message(
            order.customer.phone_number,
            'delivery_update',
            context
        )
