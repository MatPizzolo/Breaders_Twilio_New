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
        
        logger.info(f"Received message from {from_number}: {message_body[:50]}...")
        
        # Initialize response
        twiml_response = MessagingResponse()
        
        if not message_body:
            logger.warning("Received empty message body")
            twiml_response.message("I couldn't understand your message. Please try again.")
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
