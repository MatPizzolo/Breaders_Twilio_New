import logging
import re
from typing import Optional
from django.conf import settings
from .base_handler import BaseConversationHandler
from ..services.handlers.chatbot_handler import ChatbotHandler
from ..services.handlers.twilio_ai_handler import TwilioAIHandler

logger = logging.getLogger(__name__)

class ConversationHandler(BaseConversationHandler):
    """
    Maneja la conversación principal, detectando intenciones y delegando a los manejadores específicos.
    """
    
    def __init__(self):
        """Inicializa el manejador de conversación con sus sub-manejadores."""
        self.chatbot_handler = ChatbotHandler()
        self.ai_handler = TwilioAIHandler()
        
        # Umbral de confianza para determinar si usar el asistente AI
        # Reducimos el umbral para capturar más intenciones
        self.ai_confidence_threshold = 0.5
    
    def detect_intent(self, message: str) -> tuple[Optional[str], float]:
        """
        Detecta la intención del mensaje.
        
        Args:
            message: El mensaje del usuario
            
        Returns:
            Tupla con (intención detectada, nivel de confianza)
        """
        # Implementación básica de detección de intención
        # En un sistema real, esto podría usar NLP más avanzado
        
        logger.debug(f"Detectando intención para mensaje: '{message}'")
        
        # Patrones de intención mejorados con más variaciones y expresiones comunes
        intent_patterns = {
            'saludo': r'\b(hola|buenas|saludos|buen[ao]s\s*(d[ií]as|tardes|noches)|qu[eé]\s*tal|c[oó]mo\s*est[aá]n)\b',
            'productos': r'\b(productos?|cat[aá]logos?|ver\s*productos|milanesas?|ofertas?|qu[eé]\s*(tienen|ofrecen|venden)|tipos\s*de\s*milanesas|disponibles?|veganas?|vegetarianas?)\b',
            'pedido': r'\b(pedidos?|[oó]rdenes?|estados?|seguimientos?|hice\s*un\s*pedido|cu[aá]ndo\s*llegar[aá]|pedido\s*[#]?\d+)\b',
            'ayuda': r'\b(ayuda|soporte|problemas?|necesito\s*ayuda|consultas?|dudas?|preguntas?)\b',
            'horarios': r'\b(horarios?|abiertos?|cerrados?|atenci[oó]n|hasta\s*qu[eé]\s*hora|qu[eé]\s*d[ií]as?|domingos?)\b',
            'pago': r'\b(pagos?|formas?\s*de\s*pago|efectivo|tarjetas?|transferencias?|mercadopago|descuentos?|american\s*express|cr[eé]dito|d[eé]bito)\b',
            'menu': r'\b(men[uú]s?|opciones|comandos|^[1-9]$)\b'  # Incluye números del 1-9 como opciones de menú
        }
        
        # Buscar coincidencias con mejor cálculo de confianza
        best_intent = None
        best_confidence = 0.0
        
        for intent, pattern in intent_patterns.items():
            matches = list(re.finditer(pattern, message.lower()))
            if matches:
                # Calcular confianza basada en la cantidad de coincidencias y su longitud total
                total_match_length = sum(match.end() - match.start() for match in matches)
                # Ajustamos la fórmula para dar más peso a múltiples coincidencias
                match_count_factor = min(len(matches) * 0.1, 0.3)  # Máximo 0.3 por múltiples coincidencias
                length_factor = min((total_match_length / len(message)) * 0.6, 0.6)  # Máximo 0.6 por longitud
                confidence = 0.3 + match_count_factor + length_factor  # Base 0.3 + factores
                
                # Limitar la confianza máxima a 0.95
                confidence = min(confidence, 0.95)
                
                logger.debug(f"Intent '{intent}' detectado con confianza {confidence:.2f} (matches: {len(matches)}, longitud: {total_match_length})")
                
                # Guardar la mejor intención encontrada
                if confidence > best_confidence:
                    best_intent = intent
                    best_confidence = confidence
        
        if best_intent:
            return best_intent, best_confidence
        
        return None, 0.3
    
    def process_message(self, from_number: str, message: str) -> Optional[str]:
        """
        Procesa un mensaje entrante y determina la respuesta apropiada.
        
        Args:
            from_number: Número de teléfono del remitente
            message: Contenido del mensaje
            
        Returns:
            Respuesta al mensaje o None si no hay respuesta
        """
        try:
            logger.info(f"Procesando mensaje de {from_number}: {message[:50]}...")
            
            # Detectar intención
            intent, confidence = self.detect_intent(message)
            logger.info(f"Intención detectada: {intent}, confianza: {confidence}")
            
            # Mapeo de intenciones detectadas a intenciones del chatbot
            intent_mapping = {
                'saludo': 'saludo',
                'productos': 'ver_productos',
                'pedido': 'consultar_estado',  # Asumimos que 'pedido' se refiere a consultar estado
                'ayuda': 'atencion_cliente',
                'horarios': 'horarios',
                'pago': 'pago',
                'menu': 'menu'
            }
            
            # Mapear la intención detectada a la intención del chatbot
            chatbot_intent = intent_mapping.get(intent) if intent else None
            logger.info(f"Intención mapeada para chatbot: {chatbot_intent}")
            
            # Si la confianza es alta, usar el chatbot
            if confidence >= self.ai_confidence_threshold and chatbot_intent:
                logger.info(f"Usando chatbot para intención: {chatbot_intent} con confianza: {confidence}")
                response = self.chatbot_handler.process_message(from_number, message, chatbot_intent, confidence)
                if response:
                    logger.info(f"Chatbot respondió: {response[:50]}...")
                    return response
                else:
                    logger.info("Chatbot no pudo manejar el mensaje, delegando a AI")
            else:
                logger.info(f"Confianza baja ({confidence}) o intención no reconocida, delegando a AI")
            
            # Si el chatbot no pudo manejar el mensaje o la confianza es baja, usar el asistente AI
            logger.info(f"Delegando mensaje a asistente AI: {message[:50]}...")
            # Forzar el uso de la API de Twilio en producción
            return self.ai_handler.process_message(from_number, message, intent, confidence, force_api=True)
            
        except Exception as e:
            logger.error(f"Error en ConversationHandler.process_message: {str(e)}")
            return "Lo siento, estamos experimentando problemas técnicos. Por favor, intenta nuevamente más tarde."
