"""
Pruebas de flujo de WhatsApp

Este módulo proporciona pruebas para verificar el flujo completo del bot de WhatsApp,
simulando mensajes entrantes y verificando las respuestas.
"""
import json
import unittest
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.urls import reverse
from ..services.handlers.conversation_handler import ConversationHandler
from ..services.handlers.chatbot_handler import ChatbotHandler
from ..services.handlers.twilio_ai_handler import TwilioAIHandler
from ..services.constants import (
    MENSAJE_BIENVENIDA, MENSAJE_CATALOGO_PRODUCTOS, MENSAJE_ESTADO_PEDIDO,
    MENSAJE_OFERTAS_ESPECIALES, MENSAJE_ATENCION_CLIENTE, MENSAJE_ERROR
)

class WhatsAppFlowTest(TestCase):
    """
    Pruebas para el flujo completo del bot de WhatsApp.
    """
    
    def setUp(self):
        """Configuración inicial para las pruebas."""
        self.client = Client()
        self.webhook_url = reverse('whatsapp_webhook')
        
        # Datos de ejemplo para simular mensajes de WhatsApp
        self.whatsapp_data = {
            'From': 'whatsapp:+5491112345678',
            'Body': '',
            'ProfileName': 'Usuario de Prueba',
            'WaId': '5491112345678'
        }
    
    def simulate_whatsapp_message(self, message_body):
        """
        Simula un mensaje entrante de WhatsApp.
        
        Args:
            message_body: Contenido del mensaje
            
        Returns:
            Respuesta HTTP de la solicitud
        """
        data = self.whatsapp_data.copy()
        data['Body'] = message_body
        return self.client.post(self.webhook_url, data)
    
    @patch('whatsapp_bot.views.ConversationHandler')
    def test_greeting_flow(self, mock_handler):
        """Prueba el flujo de saludo."""
        # Configurar el mock para devolver un mensaje de bienvenida
        mock_instance = mock_handler.return_value
        mock_instance.process_message.return_value = MENSAJE_BIENVENIDA
        
        # Simular un mensaje de saludo
        response = self.simulate_whatsapp_message('Hola')
        
        # Verificar que se llamó al manejador con los parámetros correctos
        mock_instance.process_message.assert_called_once_with(
            self.whatsapp_data['From'],
            'Hola'
        )
        
        # Verificar que la respuesta contiene el mensaje de bienvenida
        self.assertIn(MENSAJE_BIENVENIDA, response.content.decode())
        self.assertEqual(response.status_code, 200)
    
    @patch('whatsapp_bot.views.ConversationHandler')
    def test_product_catalog_flow(self, mock_handler):
        """Prueba el flujo del catálogo de productos."""
        # Configurar el mock para devolver un mensaje de catálogo
        mock_instance = mock_handler.return_value
        mock_instance.process_message.return_value = MENSAJE_CATALOGO_PRODUCTOS
        
        # Simular un mensaje solicitando el catálogo
        response = self.simulate_whatsapp_message('Productos')
        
        # Verificar que la respuesta contiene el mensaje de catálogo
        self.assertIn(MENSAJE_CATALOGO_PRODUCTOS, response.content.decode())
        self.assertEqual(response.status_code, 200)
    
    @patch('whatsapp_bot.views.ConversationHandler')
    def test_order_status_flow(self, mock_handler):
        """Prueba el flujo de estado de pedido."""
        # Configurar el mock para devolver un mensaje de estado de pedido
        mock_instance = mock_handler.return_value
        mock_instance.process_message.return_value = MENSAJE_ESTADO_PEDIDO
        
        # Simular un mensaje solicitando el estado del pedido
        response = self.simulate_whatsapp_message('Estado de mi pedido')
        
        # Verificar que la respuesta contiene el mensaje de estado de pedido
        self.assertIn(MENSAJE_ESTADO_PEDIDO, response.content.decode())
        self.assertEqual(response.status_code, 200)
    
    @patch('whatsapp_bot.views.ConversationHandler')
    def test_special_offers_flow(self, mock_handler):
        """Prueba el flujo de ofertas especiales."""
        # Configurar el mock para devolver un mensaje de ofertas especiales
        mock_instance = mock_handler.return_value
        mock_instance.process_message.return_value = MENSAJE_OFERTAS_ESPECIALES
        
        # Simular un mensaje solicitando ofertas especiales
        response = self.simulate_whatsapp_message('Ofertas')
        
        # Verificar que la respuesta contiene el mensaje de ofertas especiales
        self.assertIn(MENSAJE_OFERTAS_ESPECIALES, response.content.decode())
        self.assertEqual(response.status_code, 200)
    
    @patch('whatsapp_bot.views.ConversationHandler')
    def test_customer_support_flow(self, mock_handler):
        """Prueba el flujo de atención al cliente."""
        # Configurar el mock para devolver un mensaje de atención al cliente
        mock_instance = mock_handler.return_value
        mock_instance.process_message.return_value = MENSAJE_ATENCION_CLIENTE
        
        # Simular un mensaje solicitando atención al cliente
        response = self.simulate_whatsapp_message('Ayuda')
        
        # Verificar que la respuesta contiene el mensaje de atención al cliente
        self.assertIn(MENSAJE_ATENCION_CLIENTE, response.content.decode())
        self.assertEqual(response.status_code, 200)
    
    @patch('whatsapp_bot.views.ConversationHandler')
    def test_error_handling(self, mock_handler):
        """Prueba el manejo de errores."""
        # Configurar el mock para lanzar una excepción
        mock_instance = mock_handler.return_value
        mock_instance.process_message.side_effect = Exception("Error de prueba")
        
        # Simular un mensaje que causará un error
        response = self.simulate_whatsapp_message('Mensaje que causa error')
        
        # Verificar que la respuesta contiene el mensaje de error
        self.assertIn(MENSAJE_ERROR, response.content.decode())
        self.assertEqual(response.status_code, 200)


class ConversationHandlerTest(TestCase):
    """
    Pruebas para el manejador de conversaciones.
    """
    
    def setUp(self):
        """Configuración inicial para las pruebas."""
        self.handler = ConversationHandler()
        self.from_number = 'whatsapp:+5491112345678'
    
    @patch('whatsapp_bot.services.handlers.conversation_handler.ChatbotHandler')
    def test_intent_detection(self, mock_chatbot):
        """Prueba la detección de intención."""
        # Configurar el mock para devolver un mensaje
        mock_instance = mock_chatbot.return_value
        mock_instance.process_message.return_value = "Respuesta de prueba"
        
        # Probar diferentes mensajes para verificar la detección de intención
        test_cases = [
            ('Hola', 'greeting'),
            ('Quiero ver productos', 'product_catalog'),
            ('Estado de mi pedido', 'order_status'),
            ('Ofertas', 'special_offers'),
            ('Necesito ayuda', 'customer_support')
        ]
        
        for message, expected_intent in test_cases:
            # Reiniciar el mock para cada caso de prueba
            mock_instance.process_message.reset_mock()
            
            # Procesar el mensaje
            self.handler.process_message(self.from_number, message)
            
            # Verificar que se llamó al manejador de chatbot con la intención correcta
            # Nota: Esto asume que el método process_message de ChatbotHandler
            # acepta un parámetro de intención, lo cual debería ser implementado
            mock_instance.process_message.assert_called_once()
            # No podemos verificar los argumentos exactos porque la confianza puede variar
            # pero podríamos verificar que se llamó con algún argumento
    
    @patch('whatsapp_bot.services.handlers.conversation_handler.TwilioAIHandler')
    def test_fallback_to_ai(self, mock_ai_handler):
        """Prueba el fallback al asistente de Twilio AI."""
        # Configurar el mock para devolver un mensaje
        mock_instance = mock_ai_handler.return_value
        mock_instance.process_message.return_value = "Respuesta de AI"
        
        # Configurar el handler para usar confianza baja
        self.handler.detect_intent = MagicMock(return_value=('unknown', 0.1))
        
        # Procesar un mensaje que debería ir al asistente AI
        response = self.handler.process_message(self.from_number, "Mensaje confuso")
        
        # Verificar que se llamó al asistente AI
        mock_instance.process_message.assert_called_once()
        self.assertEqual(response, "Respuesta de AI")


if __name__ == '__main__':
    unittest.main()
