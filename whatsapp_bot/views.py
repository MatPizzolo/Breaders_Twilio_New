import json
import logging
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from twilio.twiml.messaging_response import MessagingResponse
from .services.handlers.conversation_handler import ConversationHandler

logger = logging.getLogger(__name__)

@csrf_exempt
@require_POST
def whatsapp_webhook(request):
    """
    Webhook endpoint for WhatsApp messages via Twilio.
    Processes incoming messages and returns appropriate responses.
    """
    try:
        # Extract message data from the request
        from_number = request.POST.get('From', '')
        to_number = request.POST.get('To', '')
        message_body = request.POST.get('Body', '').strip()
        message_sid = request.POST.get('MessageSid', '')
        # Get additional parameters to identify message type
        message_status = request.POST.get('MessageStatus', '')
        event_type = request.POST.get('EventType', '')
        
        # Initialize response
        twiml_response = MessagingResponse()
        
        # Check if this is a status update or other non-message webhook
        if message_status or event_type:
            logger.debug(f"Received status update: Status={message_status}, Event={event_type}")
            # Just acknowledge receipt for status updates
            return HttpResponse(status=204)  # No content response
        
        # Log actual messages with content
        if message_body:
            logger.info(f"Received message from {from_number}: {message_body[:50]}...")
        else:
            logger.debug(f"Received webhook with empty body from {from_number}")
            # For empty messages from actual users (not status updates), send a response
            return HttpResponse(str(twiml_response))
        
        # Process the message using the conversation handler
        conversation_handler = ConversationHandler()
        response_text = conversation_handler.process_message(from_number, message_body)
        
        # Add response to TwiML
        if response_text:
            twiml_response.message(response_text)
        
        return HttpResponse(str(twiml_response))
        
    except Exception as e:
        logger.error(f"Error processing WhatsApp webhook: {str(e)}")
        # Return a generic error response
        twiml_response = MessagingResponse()
        twiml_response.message("Sorry, we're experiencing technical difficulties. Please try again later.")
        return HttpResponse(str(twiml_response))
