"""
Twilio AI Assistant Handler

This module provides the TwilioAIHandler class that integrates with
Twilio's AI Assistant API for handling complex user queries.
"""
import logging
from typing import Optional, Dict, Any
from django.conf import settings
from ..twilio_whatsapp import TwilioWhatsAppService
from ..constants import MENSAJE_ERROR, MENSAJE_NO_ENTIENDO
from .base_handler import BaseConversationHandler

logger = logging.getLogger(__name__)

class TwilioAIHandler(BaseConversationHandler):
    """
    Handler that integrates with Twilio's AI Assistant API for complex query processing.
    """
    
    def __init__(self):
        """Initialize the Twilio AI handler with required credentials"""
        # Create an instance of TwilioWhatsAppService to handle AI Assistant integration
        self.twilio_service = TwilioWhatsAppService()
    
    def _get_user_session(self, from_number: str) -> str:
        """
        Get a session ID for a user.
        
        Args:
            from_number: The user's phone number
            
        Returns:
            Session ID for the user
        """
        # Clean the phone number (remove 'whatsapp:' prefix if present)
        clean_number = from_number.replace('whatsapp:', '') if from_number.startswith('whatsapp:') else from_number
        
        # Create a unique session ID based on the phone number
        # This is a simplified version that doesn't require storing sessions
        return f"session_{clean_number}"
    
    def _call_twilio_assistant_api(self, from_number: str, message: str, context: Optional[Dict[str, Any]] = None, is_first_interaction: bool = False) -> Dict[str, Any]:
        """
        Call the Twilio Assistant API to process a user message using the TwilioWhatsAppService.
        
        Args:
            from_number: User's phone number
            message: User's message content
            context: Optional context information for the AI
            is_first_interaction: Whether this is the first interaction with the user
            
        Returns:
            Dictionary with response from the AI Assistant
        """
        try:
            # Use the TwilioWhatsAppService to send the message to the AI Assistant
            result = self.twilio_service.send_to_ai_assistant(message, from_number, context, is_first_interaction)
            
            if 'message' in result:
                return {"success": True, "response": result['message']}
            else:
                return {"success": False, "error": "No response from AI Assistant"}
                
        except Exception as e:
            logger.error(f"Error calling Twilio AI Assistant: {str(e)}")
            return {"success": False, "error": f"AI Assistant error: {str(e)}"}
    
    def process_message(self, from_number: str, message: str, 
                        intent: Optional[str] = None, 
                        confidence: Optional[float] = None,
                        force_api: bool = True,
                        is_first_interaction: bool = False) -> Optional[str]:
        """
        Process a message using the Twilio AI Assistant API.
        
        Args:
            from_number: The sender's phone number
            message: The message content
            intent: Detected intent of the message (optional)
            confidence: Confidence score of intent detection (optional)
            force_api: Whether to force API usage regardless of DEBUG setting (default: True)
            is_first_interaction: Whether this is the first interaction with the user
            
        Returns:
            Response text from Twilio AI Assistant, or None if there's an error
        """
        try:
            # Log the incoming message
            logger.info(f"Processing message with Twilio AI Assistant: {message[:50]}...")
            
            # Create context with any detected intent information
            context = None
            if intent and confidence:
                context = {
                    'intent': intent,
                    'confidence': confidence
                }
            
            # Call the Twilio Assistant API using the TwilioWhatsAppService
            result = self._call_twilio_assistant_api(from_number, message, context, is_first_interaction)
            
            if result["success"]:
                return result["response"]
            else:
                logger.error(f"AI Assistant error: {result.get('error', 'Unknown')}")
                return MENSAJE_NO_ENTIENDO
            
        except Exception as e:
            logger.error(f"Error processing message with Twilio AI: {str(e)}")
            return MENSAJE_NO_ENTIENDO
