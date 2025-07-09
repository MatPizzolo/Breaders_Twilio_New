"""
Test suite for TwilioAIHandler

This module provides comprehensive tests for the TwilioAIHandler class,
testing its ability to process various types of messages and interact with the Twilio Assistant API.
"""
import unittest
from unittest.mock import patch, MagicMock
from django.test import TestCase
from whatsapp_bot.services.handlers.twilio_ai_handler import TwilioAIHandler
from whatsapp_bot.services.constants import MENSAJE_NO_ENTIENDO

class TwilioAIHandlerTest(TestCase):
    """
    Tests for the TwilioAIHandler class.
    """
    
    def setUp(self):
        """Set up test environment."""
        # Create a patched version of TwilioAIHandler that doesn't actually call Twilio API
        self.patcher = patch('whatsapp_bot.services.handlers.twilio_ai_handler.Client')
        self.mock_client = self.patcher.start()
        
        # Configure Django settings mock
        self.settings_patcher = patch('whatsapp_bot.services.handlers.twilio_ai_handler.settings')
        self.mock_settings = self.settings_patcher.start()
        self.mock_settings.TWILIO_ACCOUNT_SID = 'test_account_sid'
        self.mock_settings.TWILIO_AUTH_TOKEN = 'test_auth_token'
        self.mock_settings.TWILIO_ASSISTANT_ID = 'test_assistant_id'
        
        # Create handler instance
        self.handler = TwilioAIHandler()
        self.from_number = 'whatsapp:+5491112345678'
        
    def tearDown(self):
        """Clean up after tests."""
        self.patcher.stop()
        self.settings_patcher.stop()
    
    def test_initialization(self):
        """Test that the handler initializes correctly."""
        self.assertEqual(self.handler.account_sid, 'test_account_sid')
        self.assertEqual(self.handler.auth_token, 'test_auth_token')
        self.assertEqual(self.handler.assistant_id, 'test_assistant_id')
        self.assertIsNotNone(self.handler.client)
        self.assertEqual(len(self.handler.user_sessions), 0)
    
    def test_get_user_session(self):
        """Test session creation and retrieval."""
        # First call should create a new session
        session_id = self.handler._get_user_session(self.from_number)
        self.assertIsNotNone(session_id)
        self.assertIn('whatsapp:+5491112345678'.replace('whatsapp:', ''), session_id)
        
        # Second call should return the same session
        second_session_id = self.handler._get_user_session(self.from_number)
        self.assertEqual(session_id, second_session_id)
        
        # Different number should get different session
        other_session_id = self.handler._get_user_session('whatsapp:+5491187654321')
        self.assertNotEqual(session_id, other_session_id)
    
    @patch('whatsapp_bot.services.handlers.twilio_ai_handler.TwilioAIHandler._call_twilio_assistant_api')
    def test_process_message_success(self, mock_call_api):
        """Test successful message processing."""
        # Configure mock to return a successful response
        mock_call_api.return_value = {"success": True, "response": "This is a test response from Twilio AI"}
        
        # Process a message
        response = self.handler.process_message(self.from_number, "Test message")
        
        # Verify the response
        self.assertEqual(response, "This is a test response from Twilio AI")
        mock_call_api.assert_called_once()
    
    @patch('whatsapp_bot.services.handlers.twilio_ai_handler.TwilioAIHandler._call_twilio_assistant_api')
    def test_process_message_failure(self, mock_call_api):
        """Test message processing when API call fails."""
        # Configure mock to return a failure response
        mock_call_api.return_value = {"success": False, "error": "API error"}
        
        # Process a message
        response = self.handler.process_message(self.from_number, "Test message")
        
        # Verify the response is the default error message
        self.assertEqual(response, MENSAJE_NO_ENTIENDO)
        mock_call_api.assert_called_once()
    
    @patch('whatsapp_bot.services.handlers.twilio_ai_handler.TwilioAIHandler._call_twilio_assistant_api')
    def test_process_message_exception(self, mock_call_api):
        """Test message processing when an exception occurs."""
        # Configure mock to raise an exception
        mock_call_api.side_effect = Exception("Test exception")
        
        # Process a message
        response = self.handler.process_message(self.from_number, "Test message")
        
        # Verify the response is the default error message
        self.assertEqual(response, MENSAJE_NO_ENTIENDO)
        mock_call_api.assert_called_once()
    
    def test_missing_credentials(self):
        """Test behavior when credentials are missing."""
        # Reconfigure settings with missing credentials
        self.mock_settings.TWILIO_ACCOUNT_SID = None
        self.mock_settings.TWILIO_AUTH_TOKEN = None
        
        # Create a new handler with missing credentials
        handler = TwilioAIHandler()
        
        # Process a message
        response = handler.process_message(self.from_number, "Test message")
        
        # Verify the response is the default error message
        self.assertEqual(response, MENSAJE_NO_ENTIENDO)
    
    def test_missing_assistant_id(self):
        """Test behavior when assistant ID is missing."""
        # Reconfigure settings with missing assistant ID
        self.mock_settings.TWILIO_ASSISTANT_ID = None
        
        # Create a new handler with missing assistant ID
        handler = TwilioAIHandler()
        
        # Process a message
        response = handler.process_message(self.from_number, "Test message")
        
        # Verify the response is the default error message
        self.assertEqual(response, MENSAJE_NO_ENTIENDO)

class ComprehensiveTwilioAIHandlerTest(TestCase):
    """
    Comprehensive tests for the TwilioAIHandler with various message types.
    """
    
    def setUp(self):
        """Set up test environment."""
        # Create a patched version of TwilioAIHandler that doesn't actually call Twilio API
        self.patcher = patch('whatsapp_bot.services.handlers.twilio_ai_handler.Client')
        self.mock_client = self.patcher.start()
        
        # Configure Django settings mock
        self.settings_patcher = patch('whatsapp_bot.services.handlers.twilio_ai_handler.settings')
        self.mock_settings = self.settings_patcher.start()
        self.mock_settings.TWILIO_ACCOUNT_SID = 'test_account_sid'
        self.mock_settings.TWILIO_AUTH_TOKEN = 'test_auth_token'
        self.mock_settings.TWILIO_ASSISTANT_ID = 'test_assistant_id'
        
        # Create handler instance
        self.handler = TwilioAIHandler()
        self.from_number = 'whatsapp:+5491112345678'
        
    def tearDown(self):
        """Clean up after tests."""
        self.patcher.stop()
        self.settings_patcher.stop()
    
    @patch('whatsapp_bot.services.handlers.twilio_ai_handler.TwilioAIHandler._call_twilio_assistant_api')
    def test_comprehensive_message_types(self, mock_call_api):
        """Test processing of various message types with simulated responses."""
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
            },
            {
                'category': 'Payment Methods',
                'message': '¿Qué formas de pago aceptan?',
                'response': 'Aceptamos múltiples formas de pago: efectivo, tarjetas de débito/crédito, transferencia bancaria y MercadoPago.'
            },
            {
                'category': 'Family Size Order',
                'message': '¿Cuánto debo pedir para una familia de 5 personas?',
                'response': 'Para una familia de 5 personas, recomendamos aproximadamente 1.5kg de milanesas, lo que equivale a unos 300g por persona.'
            },
            {
                'category': 'Dietary Restrictions',
                'message': '¿Tienen opciones para celíacos?',
                'response': 'Sí, contamos con milanesas sin TACC elaboradas en ambiente libre de contaminación cruzada, especiales para celíacos.'
            },
            {
                'category': 'Recommendations',
                'message': '¿Cuál es su especialidad?',
                'response': 'Nuestra especialidad son las milanesas de carne premium, preparadas con carne de primera calidad y un rebozado especial con hierbas.'
            },
            {
                'category': 'Preparation',
                'message': '¿Cómo se cocinan las milanesas?',
                'response': 'Nuestras milanesas vienen listas para cocinar. Puede freírlas en aceite bien caliente durante 2-3 minutos por lado, u hornearlas a 200°C durante 15-20 minutos.'
            },
            {
                'category': 'Availability',
                'message': '¿Tienen stock disponible para hoy?',
                'response': 'Sí, actualmente tenemos stock de todos nuestros productos. Para pedidos estándar, la entrega puede realizarse el mismo día si ordena antes de las 15:00 hs.'
            },
            {
                'category': 'Complex Query',
                'message': '¿Cuál es la diferencia entre las milanesas de carne y las de pollo en términos de sabor y precio?',
                'response': 'Las milanesas de carne tienen un sabor más intenso y jugoso, mientras que las de pollo son más suaves y ligeras. En cuanto al precio, las de carne cuestan $1200 por kg y las de pollo $1000 por kg. Ambas son muy populares entre nuestros clientes.'
            }
        ]
        
        # Process each test case
        print("\n=== COMPREHENSIVE TWILIO AI HANDLER TEST ===")
        print("Testing various message types with simulated responses\n")
        
        for case in test_cases:
            # Configure mock to return the expected response
            mock_call_api.return_value = {"success": True, "response": case['response']}
            
            # Process the message
            response = self.handler.process_message(self.from_number, case['message'])
            
            # Verify and print the results
            self.assertEqual(response, case['response'])
            print(f"Category: {case['category']}")
            print(f"User Message: \"{case['message']}\"")
            print(f"AI Response: \"{response}\"\n")
            
            # Reset the mock for the next test case
            mock_call_api.reset_mock()
        
        print("=== ALL TESTS PASSED SUCCESSFULLY ===")


if __name__ == '__main__':
    unittest.main()
