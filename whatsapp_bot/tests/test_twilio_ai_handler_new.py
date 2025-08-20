"""
Test suite for TwilioAIHandler

This module provides comprehensive tests for the TwilioAIHandler class,
testing its ability to process various types of messages and interact with the Twilio Assistant API.
"""
import unittest
import os
from unittest.mock import patch, MagicMock
from whatsapp_bot.services.handlers.twilio_ai_handler import TwilioAIHandler
from whatsapp_bot.services.constants import MENSAJE_NO_ENTIENDO
from whatsapp_bot.tests.test_base import BreadersBotBaseTestCase

class TwilioAIHandlerTest(BreadersBotBaseTestCase):
    """
    Tests for the TwilioAIHandler class.
    """
    
    def setUp(self):
        """Set up test environment."""
        super().setUp()
        self.log_step("Setting up TwilioAIHandler test environment")
        
        # Mock the TwilioWhatsAppService
        self.log_step("Mocking TwilioWhatsAppService")
        self.service_patcher = patch('whatsapp_bot.services.handlers.twilio_ai_handler.TwilioWhatsAppService')
        self.mock_service_class = self.service_patcher.start()
        self.mock_service = MagicMock()
        self.mock_service_class.return_value = self.mock_service
        
        # Configure Django settings mock with real environment variables
        self.log_step("Configuring Django settings with environment variables")
        self.settings_patcher = patch('whatsapp_bot.services.handlers.twilio_ai_handler.settings')
        self.mock_settings = self.settings_patcher.start()
        
        # Use real environment variables or fallback to empty strings if not available
        self.mock_settings.TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '')
        self.mock_settings.TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '')
        self.mock_settings.TWILIO_ASSISTANT_ID = os.environ.get('TWILIO_ASSISTANT_ID', '')
        
        # Create handler instance
        self.log_step("Creating TwilioAIHandler instance")
        self.handler = TwilioAIHandler()
        self.from_number = 'whatsapp:+5491112345678'
        
    def tearDown(self):
        """Clean up after tests."""
        self.log_step("Cleaning up test environment")
        self.service_patcher.stop()
        self.settings_patcher.stop()
        super().tearDown()
    
    def test_initialization(self):
        """Test that the handler initializes correctly."""
        self.log_step("Testing handler initialization")
        
        self.assert_with_log(
            self.handler.twilio_service is not None,
            "Checking twilio_service is initialized"
        )
        
        self.assert_equal_with_log(
            self.handler.assistant_id,
            os.environ.get('TWILIO_ASSISTANT_ID', ''),
            "Checking assistant_id is set correctly"
        )
    
    def test_get_user_session(self):
        """Test session creation and retrieval."""
        self.log_step("Testing session creation and retrieval")
        
        # Add test for TwilioAIHandler._get_user_session
        # First, check if the method exists
        self.assert_with_log(
            hasattr(self.handler, '_get_user_session') and callable(getattr(self.handler, '_get_user_session', None)),
            "Checking if _get_user_session method exists"
        )
        
        # If the method doesn't exist, it might have been renamed or removed
        # In that case, skip the detailed tests
        if not hasattr(self.handler, '_get_user_session'):
            self.log_step("Skipping detailed session tests as method doesn't exist")
            return
            
        # Test session ID creation
        session_id = self.handler._get_user_session(self.from_number)
        
        self.assert_with_log(
            session_id is not None,
            "Checking if session_id is not None"
        )
        
        # Test with different number format
        clean_number = '+5491112345678'
        clean_session = self.handler._get_user_session(clean_number)
        
        self.assert_with_log(
            clean_session is not None,
            "Checking if clean_session is not None"
        )
        
        # Different number should get different session
        other_number = 'whatsapp:+5491187654321'
        other_session = self.handler._get_user_session(other_number)
        
        self.assert_with_log(
            session_id != other_session,
            "Checking if different numbers get different sessions")
    
    def test_process_message_success(self):
        """Test successful message processing with rigorous verification."""
        self.log_step("Testing successful message processing")
        
        # Define test parameters
        test_message = 'Hello, this is a test message'
        test_intent = 'greeting'
        test_confidence = 0.9
        test_response = 'This is a test response from the AI'
        
        # We need to mock the _call_twilio_assistant_api method since that's what's actually called
        # by the process_message method, not directly send_to_ai_assistant
        with patch.object(self.handler, '_call_twilio_assistant_api') as mock_call_api:
            # Setup mock to return success response
            mock_call_api.return_value = {
                'success': True,
                'response': test_response
            }
            
            # Process a message
            self.log_step("Processing test message")
            response = self.handler.process_message(
                self.from_number, 
                test_message,
                intent=test_intent,
                confidence=test_confidence
            )
            
            # Verify response content
            self.assert_equal_with_log(
                response,
                test_response,
                "Verifying response matches expected output"
            )
            
            # Verify API method was called
            self.log_check("Checking if _call_twilio_assistant_api was called")
            mock_call_api.assert_called_once()
            
            # Extract call arguments
            call_args = mock_call_api.call_args
            args, kwargs = call_args
            
            # Verify parameters - from_number and message should be positional args
            self.assert_equal_with_log(
                args[0],
                self.from_number,
                "Checking first argument is from_number"
            )
            
            self.assert_equal_with_log(
                args[1],
                test_message,
                "Checking second argument is message text"
            )
            
            # Context should be in kwargs or args[2]
            context = kwargs.get('context', None) or (args[2] if len(args) > 2 else None)
            self.assert_with_log(
                context is not None,
                "Checking context is not None"
            )
            
            if context is not None:
                # Check context contains expected values
                self.assert_equal_with_log(
                    context.get('intent'),
                    test_intent,
                    "Checking context contains correct intent"
                )
                
                self.assert_equal_with_log(
                    context.get('confidence'),
                    test_confidence,
                    "Checking context contains correct confidence"
                )
        
        # Message verification already done above with args[0]
    
    def test_process_message_failure(self):
        """Test message processing when API call fails."""
        self.log_step("Testing message processing when API call fails")
        
        # Use patch to mock the assistant API call to fail
        with patch.object(self.handler, '_call_twilio_assistant_api') as mock_call_api:
            # Setup mock to return failure response
            mock_call_api.return_value = {
                'success': False,
                'error': 'Test error message'
            }
            
            # Process a message
            self.log_step("Processing test message with failing API")
            response = self.handler.process_message(
                self.from_number, 
                'Hello, this is a test message'
            )
            
            # Verify None is returned when API fails
            self.assert_with_log(
                response is None,
                "Checking that None is returned when API fails"
            )
            
            # Verify API was called
            self.log_check("Checking if _call_twilio_assistant_api was called")
            mock_call_api.assert_called_once()
    
    def test_process_message_exception(self):
        """Test message processing when an exception occurs."""
        self.log_step("Testing message processing when an exception occurs")
        
        # Use patch to mock the assistant API call to raise an exception
        with patch.object(self.handler, '_call_twilio_assistant_api') as mock_call_api:
            # Setup mock to raise exception
            mock_call_api.side_effect = Exception('Test exception')
            
            # Process a message
            self.log_step("Processing test message with exception throwing API")
            response = self.handler.process_message(
                self.from_number, 
                'Hello, this is a test message'
            )
            
            # Verify None is returned when an exception occurs
            self.assert_with_log(
                response is None,
                "Checking that None is returned when exception occurs"
            )
            
            # Verify API was called despite exception
            self.log_check("Checking if _call_twilio_assistant_api was called")
            mock_call_api.assert_called_once()
    
    def test_missing_credentials(self):
        """Test behavior when credentials are missing."""
        self.log_step("Testing behavior when credentials are missing")
        
        # Create a new settings patcher that completely replaces the existing one
        missing_cred_settings_patcher = patch('whatsapp_bot.services.handlers.twilio_ai_handler.settings')
        mock_settings_missing = missing_cred_settings_patcher.start()
        
        # Configure mock settings with missing credentials
        mock_settings_missing.TWILIO_ACCOUNT_SID = None
        mock_settings_missing.TWILIO_AUTH_TOKEN = None
        mock_settings_missing.TWILIO_ASSISTANT_ID = self.mock_settings.TWILIO_ASSISTANT_ID
        
        try:
            # Create a new handler instance with missing credentials
            self.log_step("Creating handler with missing credentials")
            with patch('whatsapp_bot.services.twilio_whatsapp.settings', mock_settings_missing):
                handler = TwilioAIHandler()
                
                # Process a message
                self.log_step("Processing message with handler missing credentials")
                response = handler.process_message(
                    self.from_number, 
                    'Hello, this is a test message'
                )
                
                # Verify None is returned when credentials are missing
                self.assert_with_log(
                    response is None,
                    "Checking that None is returned when credentials are missing"
                )
        finally:
            # Clean up the temporary settings patcher
            missing_cred_settings_patcher.stop()
    
    def test_missing_assistant_id(self):
        """Test behavior when assistant ID is missing."""
        self.log_step("Testing behavior when assistant ID is missing")
        
        # Create a new settings patcher that completely replaces the existing one
        missing_id_settings_patcher = patch('whatsapp_bot.services.handlers.twilio_ai_handler.settings')
        mock_settings_missing_id = missing_id_settings_patcher.start()
        
        # Configure mock settings with credentials but missing assistant ID
        mock_settings_missing_id.TWILIO_ACCOUNT_SID = self.mock_settings.TWILIO_ACCOUNT_SID
        mock_settings_missing_id.TWILIO_AUTH_TOKEN = self.mock_settings.TWILIO_AUTH_TOKEN
        mock_settings_missing_id.TWILIO_ASSISTANT_ID = None
        
        try:
            # Create a new handler instance with missing assistant ID
            self.log_step("Creating handler with missing assistant ID")
            with patch('whatsapp_bot.services.twilio_whatsapp.settings', mock_settings_missing_id):
                handler = TwilioAIHandler()
                
                # Process a message
                self.log_step("Processing message with handler missing assistant ID")
                response = handler.process_message(self.from_number, "Test message")
                
                # Verify None is returned when assistant ID is missing
                self.assert_with_log(
                    response is None,
                    "Checking that None is returned when assistant ID is missing"
                )
        finally:
            # Clean up the temporary settings patcher
            missing_id_settings_patcher.stop()


class ComprehensiveTwilioAIHandlerTest(BreadersBotBaseTestCase):
    """
    Comprehensive tests for the TwilioAIHandler with various message types.
    """
    
    def setUp(self):
        """Set up test environment."""
        super().setUp()
        self.log_step("Setting up TwilioAIHandler test environment")
        
        # Mock the TwilioWhatsAppService
        self.log_step("Mocking TwilioWhatsAppService")
        self.service_patcher = patch('whatsapp_bot.services.handlers.twilio_ai_handler.TwilioWhatsAppService')
        self.mock_service_class = self.service_patcher.start()
        self.mock_service = MagicMock()
        self.mock_service_class.return_value = self.mock_service
        
        # Configure Django settings mock with real environment variables
        self.log_step("Configuring Django settings with environment variables")
        self.settings_patcher = patch('whatsapp_bot.services.handlers.twilio_ai_handler.settings')
        self.mock_settings = self.settings_patcher.start()
        
        # Use real environment variables or fallback to empty strings if not available
        self.mock_settings.TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '')
        self.mock_settings.TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '')
        self.mock_settings.TWILIO_ASSISTANT_ID = os.environ.get('TWILIO_ASSISTANT_ID', '')
        
        # Create handler instance
        self.log_step("Creating TwilioAIHandler instance")
        self.handler = TwilioAIHandler()
        self.from_number = 'whatsapp:+5491112345678'
        
    def tearDown(self):
        """Clean up after tests."""
        self.log_step("Cleaning up test environment")
        self.service_patcher.stop()
        self.settings_patcher.stop()
        super().tearDown()
    
    def test_comprehensive_message_types(self):
        """Test processing of various message types with simulated responses."""
        self.log_step("Testing various message types with simulated responses")
        
        # Define test cases with messages and expected responses
        test_cases = [
            {
                'category': 'Greeting',
                'message': 'Hola, ¿cómo están?',
                'response': 'Hola! Bienvenido a Breaders. ¿En qué podemos ayudarte hoy?'
            },
            {
                'category': 'Product Inquiry',
                'message': '¿Qué productos tienen disponibles?',
                'response': 'Tenemos una variedad de milanesas: de carne, pollo, cerdo y vegetarianas. También ofrecemos acompañamientos como ensalada rusa y papas fritas.'
            },
            {
                'category': 'Price Inquiry',
                'message': '¿Cuánto cuestan las milanesas de pollo?',
                'response': 'Las milanesas de pollo cuestan $1000 por kg. Para pedidos mayores a 3kg, ofrecemos un 10% de descuento.'
            },
            {
                'category': 'Hours',
                'message': '¿Cuál es su horario de atención?',
                'response': 'Nuestro horario de atención es de lunes a viernes de 9:00 a 20:00 hs y sábados de 9:00 a 14:00 hs. Los domingos permanecemos cerrados.'
            },
            {
                'category': 'Delivery',
                'message': '¿Hacen envíos a domicilio?',
                'response': 'Sí, realizamos envíos a domicilio en toda la ciudad. El costo del envío es de $500, pero es gratis para compras superiores a $5000.'
            }
        ]
        
        # Process each test case
        for i, case in enumerate(test_cases):
            self.log_step(f"Testing message category: {case['category']} ({i+1}/{len(test_cases)})")
            
            # Configure mock to return the expected response
            mock_call_api.return_value = {"success": True, "response": case['response']}
            
            # Process the message
            self.log_check(f"Processing message: '{case['message']}'")
            response = self.handler.process_message(self.from_number, case['message'])
            
            # Verify the results
            self.assert_equal_with_log(
                response, 
                case['response'],
                f"Checking response for {case['category']} message",
                f"Response for {case['category']} message is correct"
            )
            
            # Reset the mock for the next test case
            mock_call_api.reset_mock()


if __name__ == '__main__':
    unittest.main()
