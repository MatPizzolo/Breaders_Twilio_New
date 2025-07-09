"""
Manejador Base

Este módulo proporciona la clase BaseConversationHandler que sirve como base
para todos los manejadores de conversación en el bot de WhatsApp.
"""
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class BaseConversationHandler:
    """
    Clase base para todos los manejadores de conversación.
    Proporciona funcionalidad común e interfaz para manejar mensajes.
    """
    
    def process_message(self, from_number: str, message: str, 
                        intent: Optional[str] = None, 
                        confidence: Optional[float] = None) -> Optional[str]:
        """
        Procesa un mensaje entrante y devuelve una respuesta apropiada.
        
        Args:
            from_number: El número de teléfono del remitente
            message: El contenido del mensaje
            intent: Intención detectada del mensaje (opcional)
            confidence: Puntuación de confianza de la detección de intención (opcional)
            
        Returns:
            Texto de respuesta para enviar al usuario, o None si el manejador
            no puede procesar este mensaje
        """
        # Este es un método base que debe ser sobrescrito por subclases
        logger.warning("BaseConversationHandler.process_message llamado directamente")
        return None
