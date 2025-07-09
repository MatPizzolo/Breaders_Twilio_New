"""
Manejador de Conversación

Este módulo proporciona la clase ConversationHandler que gestiona el flujo de conversación
para el bot de WhatsApp, incluyendo la detección de intenciones y el enrutamiento de mensajes.
"""
import logging
import re
from typing import Dict, Any, List, Optional
from django.conf import settings
from ..constants import (
    PALABRAS_SALUDO, PALABRAS_VER_PRODUCTOS, PALABRAS_HACER_PEDIDO,
    PALABRAS_ESTADO_PEDIDO, PALABRAS_OFERTAS_ESPECIALES, PALABRAS_ATENCION_CLIENTE,
    MENSAJE_BIENVENIDA, MENSAJE_NO_ENTIENDO, MENSAJE_ERROR,
    INTENT_ALTA_CONFIANZA, INTENT_MEDIA_CONFIANZA, INTENT_BAJA_CONFIANZA,
    INTENCIONES_PREDETERMINADAS
)
from .base_handler import BaseConversationHandler
from .chatbot_handler import ChatbotHandler
from .twilio_ai_handler import TwilioAIHandler

logger = logging.getLogger(__name__)

class ConversationHandler:
    """
    Manejador principal de conversación que gestiona el flujo de mensajes.
    Detecta intenciones y enruta mensajes a los manejadores apropiados.
    """
    
    def __init__(self):
        """Inicializa el manejador de conversación con sub-manejadores"""
        self.chatbot_handler = ChatbotHandler()
        self.twilio_ai_handler = TwilioAIHandler()
    
    def detect_intent(self, message: str) -> Dict[str, Any]:
        """
        Detecta la intención de un mensaje de usuario utilizando coincidencia de patrones simple.
        
        Args:
            message: El mensaje del usuario a clasificar
            
        Returns:
            Diccionario con claves 'intent' y 'confidence'
        """
        message = message.lower()
        
        # Coincidencia de patrones simple para intenciones
        patterns = {
            'saludo': self._create_pattern(PALABRAS_SALUDO),
            'ver_productos': self._create_pattern(PALABRAS_VER_PRODUCTOS),
            'hacer_pedido': self._create_pattern(PALABRAS_HACER_PEDIDO),
            'consultar_estado': self._create_pattern(PALABRAS_ESTADO_PEDIDO),
            'ofertas_especiales': self._create_pattern(PALABRAS_OFERTAS_ESPECIALES),
            'atencion_cliente': self._create_pattern(PALABRAS_ATENCION_CLIENTE),
        }
        
        # Verificar cada patrón
        for intent, pattern in patterns.items():
            if re.search(pattern, message):
                # Puntuación de confianza simple basada en el recuento de coincidencias de palabras
                matches = re.findall(pattern, message)
                confidence = min(0.9, len(matches) * 0.3)  # Limitar a 0.9
                return {"intent": intent, "confidence": confidence}
        
        # Por defecto, baja confianza si no hay coincidencias
        return {"intent": "desconocido", "confidence": 0.1}
    
    def _create_pattern(self, keywords: List[str]) -> str:
        """
        Crea un patrón regex a partir de una lista de palabras clave.
        
        Args:
            keywords: Lista de palabras clave
            
        Returns:
            Patrón regex como string
        """
        escaped_keywords = [re.escape(kw) for kw in keywords]
        return r'\b(' + '|'.join(escaped_keywords) + r')\b'
    
    def process_message(self, from_number: str, message: str) -> str:
        """
        Procesa un mensaje entrante y devuelve una respuesta apropiada.
        
        Args:
            from_number: El número de teléfono del remitente
            message: El contenido del mensaje
            
        Returns:
            Texto de respuesta para enviar al usuario
        """
        try:
            logger.info(f"Procesando mensaje: {message[:50]}...")
            
            # Detectar intención
            intent_result = self.detect_intent(message)
            intent = intent_result["intent"]
            confidence = intent_result["confidence"]
            
            logger.info(f"Intención detectada: {intent} con confianza {confidence:.2f}")
            
            # Alta confianza en una intención conocida - usar manejador de chatbot
            if intent != "desconocido" and confidence >= INTENT_MEDIA_CONFIANZA:
                response = self.chatbot_handler.process_message(
                    from_number, 
                    message, 
                    intent=intent, 
                    confidence=confidence
                )
                if response:
                    return response
            
            # Baja confianza o el manejador de chatbot devolvió None - usar Asistente AI de Twilio
            logger.info("Usando Asistente AI de Twilio para respuesta")
            twilio_response = self.twilio_ai_handler.process_message(from_number, message)
            if twilio_response:
                return twilio_response
            
            # Si todo falla, devolver mensaje predeterminado
            return MENSAJE_NO_ENTIENDO
            
        except Exception as e:
            logger.error(f"Error en el manejador de conversación: {str(e)}")
            return MENSAJE_ERROR
