"""
Manejador de Conversación

Este módulo proporciona la clase ConversationHandler que gestiona el flujo de conversación
para el bot de WhatsApp, incluyendo la detección de intenciones y el enrutamiento de mensajes.
"""
import logging
import re
import traceback
from typing import Dict, Any, List, Optional, Tuple
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

class ConversationHandler(BaseConversationHandler):
    """
    Manejador principal de conversación que gestiona el flujo de mensajes.
    Detecta intenciones y enruta mensajes a los manejadores apropiados.
    """
    
    def __init__(self):
        """Inicializa el manejador de conversación con sub-manejadores"""
        # Inicializar la clase base primero
        super().__init__()
        
        # Inicializar los sub-manejadores
        self.chatbot_handler = ChatbotHandler()
        self.twilio_ai_handler = TwilioAIHandler()
        
        # Umbral de confianza para determinar cuándo usar el asistente AI
        self.ai_confidence_threshold = 0.5
        
        logger.info("ConversationHandler inicializado con sistema de estados mejorado")
    
    def detect_intent(self, message: str) -> Tuple[str, float]:
        """
        Detecta la intención del mensaje utilizando coincidencia de patrones simple.
        
        Args:
            message: El mensaje del usuario
            
        Returns:
            Tupla de (intención, confianza)
        """
        # Limpiar el mensaje
        message = message.strip().lower()
        
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
        matched_intents = []
        for intent, pattern in patterns.items():
            # Comprobar si hay coincidencia
            match = re.search(pattern, message)
            if match:
                # Puntuación de confianza simple basada en el recuento de coincidencias de palabras
                matches = re.findall(pattern, message)
                confidence = min(0.9, len(matches) * 0.3)  # Limitar a 0.9
                
                # Para saludos, ajustar la confianza basada en la longitud del mensaje
                # Si el mensaje es más largo, probablemente no es un simple saludo
                if intent == 'saludo':
                    # Reducir la confianza para mensajes largos que contienen saludos
                    words = message.split()
                    if len(words) > 5:  # Si el mensaje tiene más de 5 palabras
                        confidence = min(confidence, 0.5)  # Reducir confianza
                    elif len(words) <= 2:  # Si es un saludo corto (1-2 palabras)
                        confidence = max(confidence, 0.7)  # Mantener confianza alta
                    else:  # Para mensajes de longitud media
                        confidence = min(confidence, 0.6)  # Confianza moderada
                
                matched_intents.append((intent, confidence))
        
        # Si encontramos múltiples intenciones, elegir la de mayor confianza
        if matched_intents:
            matched_intents.sort(key=lambda x: x[1], reverse=True)
            return matched_intents[0]
        
        # Por defecto, baja confianza si no hay coincidencias
        return "desconocido", 0.1
    
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
    
    def process_message(self, from_number: str, message: str, 
                        intent: Optional[str] = None, 
                        confidence: Optional[float] = None) -> Optional[str]:
        """
        Procesa un mensaje entrante y devuelve una respuesta apropiada.
        
        Args:
            from_number: El número de teléfono del remitente
            message: El contenido del mensaje
            intent: Intención detectada (opcional)
            confidence: Nivel de confianza de la intención (opcional)
            
        Returns:
            Texto de respuesta para enviar al usuario, o None si no se puede procesar
        """
        try:
            # Limpiar el mensaje y registrar entrada
            message_clean = message.strip().lower()
            logger.info(f"ConversationHandler.process_message llamado con mensaje: '{message_clean}' de {from_number}")
            
            # Inicializar el estado del usuario si es necesario (asegurar que tenga un estado)
            if not hasattr(self.chatbot_handler, '_user_states'):
                logger.warning("ChatbotHandler no tiene _user_states inicializado, inicializando ahora")
                self.chatbot_handler._user_states = {}
            
            # Obtener el estado actual del usuario para contexto
            current_state = self.chatbot_handler._get_user_state(from_number)
            logger.info(f"Estado actual del usuario {from_number}: {current_state}")
            
            # Detectar la intención del mensaje si no se proporcionó
            if intent is None or confidence is None:
                intent, confidence = self.detect_intent(message)
                logger.info(f"Intención detectada: {intent}, confianza: {confidence}")
            
            # Estrategia mejorada de procesamiento:
            
            # 1. Manejar comandos de navegación explícitos primero
            if message_clean == "volver":
                logger.info(f"Procesando comando de navegación 'volver' en estado '{current_state}'")
                chatbot_response = self.chatbot_handler.process_message(from_number, message_clean)
                logger.info(f"Respuesta del chatbot para 'volver': {chatbot_response}")
                if chatbot_response:
                    return chatbot_response
            
            # 2. Manejar opciones numéricas de menú - Prioridad alta para pruebas
            if message_clean.isdigit():
                logger.info(f"Procesando opción de menú: '{message_clean}' en estado '{current_state}'")
                chatbot_response = self.chatbot_handler.process_message(from_number, message_clean)
                logger.info(f"Respuesta del chatbot para opción numérica '{message_clean}': {chatbot_response}")
                if chatbot_response:
                    return chatbot_response
            
            # 3. Manejar casos especiales basados en el estado actual
            if current_state == "menu_consulta_zona" and not message_clean.isdigit():
                # Interpretar como nombre de barrio/zona
                zona_response = self._handle_zona_response(from_number, message_clean)
                logger.info(f"Respuesta para zona '{message_clean}': {zona_response}")
                return zona_response
            
            # 4. Detectar si el mensaje parece ser una pregunta para el AI
            # Esto permite que el AI conteste preguntas aunque estemos en un estado específico
            question_indicators = ['?', 'cómo', 'como', 'qué', 'que', 'cuál', 'cual', 'cuándo', 'cuando',
                                   'dónde', 'donde', 'por qué', 'por que', 'quién', 'quien', 'cuánto', 'cuanto',
                                   'explica', 'puedes', 'podrías', 'podrias', 'dime']
            
            # Verificar si el mensaje parece ser una pregunta
            is_likely_question = any(indicator in message_clean for indicator in question_indicators) or message_clean.endswith('?')
            
            # Si parece ser una pregunta, priorizar el AI sobre el chatbot para cualquier estado
            if is_likely_question and getattr(settings, 'TWILIO_ASSISTANT_ID', None):
                logger.info(f"El mensaje parece ser una pregunta. Delegando directamente al Twilio AI Assistant")
                
                try:
                    twilio_response = self.twilio_ai_handler.process_message(
                        from_number, 
                        message, 
                        intent, 
                        confidence
                    )
                    
                    if twilio_response:
                        logger.info(f"Twilio AI Assistant generó respuesta para pregunta: {twilio_response[:50]}...")
                        return twilio_response
                except Exception as ai_error:
                    logger.error(f"Error en Twilio AI Assistant para pregunta: {str(ai_error)}")
                    # Continuar con el flujo normal si falla el AI
            
            # 5. Procesar intenciones explícitas con confianza adecuada - IMPORTANTE para pruebas
            # Reducir el umbral de confianza para las pruebas para mejorar coincidencias
            if intent != "desconocido" and confidence >= 0.4:  # Umbral reducido para pruebas
                logger.info(f"Procesando como intención explícita: {intent} con confianza {confidence}")
                chatbot_response = self.chatbot_handler.process_message(
                    from_number, message, intent, confidence
                )
                logger.info(f"Respuesta del chatbot para intención {intent}: {chatbot_response}")
                if chatbot_response:
                    return chatbot_response
            
            # 6. Intentar directamente con el chatbot_handler sin intención explícita (para pruebas)
            logger.info(f"Intentando con chatbot_handler sin intención explícita")
            chatbot_response = self.chatbot_handler.process_message(from_number, message)
            if chatbot_response:
                logger.info(f"Respuesta genérica del chatbot: {chatbot_response}")
                return chatbot_response
            
            # 7. Intentar con el Twilio AI Assistant si está configurado (para mensajes que no son preguntas explícitas)
            if getattr(settings, 'TWILIO_ASSISTANT_ID', None):
                logger.info(f"Delegando mensaje al Twilio AI Assistant como última opción")
                
                try:
                    twilio_response = self.twilio_ai_handler.process_message(
                        from_number, 
                        message, 
                        intent, 
                        confidence
                    )
                    
                    if twilio_response:
                        logger.info(f"Twilio AI Assistant generó respuesta: {twilio_response[:50]}...")
                        return twilio_response
                except Exception as ai_error:
                    logger.error(f"Error en Twilio AI Assistant: {str(ai_error)}")
                    # No fallar completamente, continuar con otros métodos de respuesta
            else:
                logger.warning("TWILIO_ASSISTANT_ID no está configurado. No se puede usar AI fallback.")
            
            # 7. Si todo lo anterior falla, enviar al usuario al menú principal
            if current_state != "menu_principal":
                logger.info(f"Redirigiendo al usuario al menú principal desde estado: {current_state}")
                self.chatbot_handler._set_user_state(from_number, "menu_principal")
                return MENSAJE_MENU_PRINCIPAL
            
            # 8. Último recurso: mensaje por defecto
            logger.info("Enviando mensaje por defecto: no entiendo")
            return MENSAJE_NO_ENTIENDO
            
        except Exception as e:
            logger.error(f"Error en el manejador de conversación: {str(e)}")
            logger.error(traceback.format_exc())
            return MENSAJE_ERROR
    
    def _handle_zona_response(self, from_number: str, zona: str) -> str:
        """
        Maneja la respuesta a la consulta de zona de entrega.
        
        Args:
            from_number: Número de teléfono del usuario
            zona: Nombre de la zona/barrio ingresado por el usuario
            
        Returns:
            Respuesta sobre disponibilidad de entrega
        """
        # Simplemente un ejemplo de manejo contextual
        # En una implementación real, se consultaría una base de datos de zonas de entrega
        zona_lower = zona.lower()
        
        # Lista de zonas de ejemplo donde se entrega
        zonas_disponibles = [
            'palermo', 'recoleta', 'belgrano', 'nuñez', 'caballito', 'flores',
            'villa urquiza', 'villa crespo', 'almagro', 'boedo', 'san telmo',
            'puerto madero', 'retiro', 'colegiales', 'villa devoto'
        ]
        
        # Verificar si la zona está en la lista de zonas disponibles
        for zona_disponible in zonas_disponibles:
            if zona_disponible in zona_lower:
                # Volver al menú de delivery
                self.chatbot_handler._set_user_state(from_number, 'menu_delivery')
                return f"😀 ¡Buenas noticias! Entregamos en {zona}. Nuestros días de entrega son Martes y Jueves entre las 10:00 y 18:00 hs.\n\n📲 Escribí \"Volver\" para regresar al menú anterior."
        
        # Si la zona no está disponible
        self.chatbot_handler._set_user_state(from_number, 'menu_delivery')
        return f"😔 Lo sentimos, actualmente no realizamos entregas en {zona}. Estamos trabajando para expandir nuestras zonas de entrega.\n\n📲 Escribí \"Volver\" para regresar al menú anterior."
