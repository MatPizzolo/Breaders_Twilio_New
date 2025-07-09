"""
Manejador de Chatbot

Este módulo proporciona la clase ChatbotHandler que maneja las respuestas básicas
del chatbot para intenciones conocidas.
"""
import logging
from typing import Optional, Dict, Any
from django.conf import settings
from ..constants import (
    MENSAJE_BIENVENIDA, MENSAJE_MENU_PRINCIPAL, MENSAJE_VER_PRODUCTOS,
    MENSAJE_HACER_PEDIDO, MENSAJE_CONSULTAR_ESTADO, MENSAJE_OFERTAS_ESPECIALES,
    MENSAJE_ATENCION_CLIENTE, MENSAJE_NO_ENTIENDO,
    ESTADO_SALUDO, ESTADO_MENU_PRINCIPAL, ESTADO_NAVEGANDO_PRODUCTOS,
    ESTADO_AGREGANDO_AL_CARRITO, ESTADO_ESTADO_PEDIDO, ESTADO_OFERTAS_ESPECIALES,
    ESTADO_ATENCION_CLIENTE, MAPEO_INTENCION_ESTADO
)
from .base_handler import BaseConversationHandler

logger = logging.getLogger(__name__)

class ChatbotHandler(BaseConversationHandler):
    """
    Manejador de chatbot que proporciona respuestas para intenciones conocidas.
    """
    
    def __init__(self):
        """Inicializa el manejador de chatbot"""
        # Mapeo de intenciones a funciones de manejo
        self.intent_handlers = {
            'saludo': self._handle_greeting,
            'ver_productos': self._handle_view_products,
            'hacer_pedido': self._handle_make_order,
            'consultar_estado': self._handle_order_status,
            'ofertas_especiales': self._handle_special_offers,
            'atencion_cliente': self._handle_customer_support,
        }
    
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
        try:
            if not intent or intent == "desconocido":
                return None
            
            # Buscar el manejador de intención apropiado
            handler = self.intent_handlers.get(intent)
            if handler:
                return handler(from_number, message)
            
            # Si no hay un manejador específico, devolver None para delegar a otro manejador
            return None
            
        except Exception as e:
            logger.error(f"Error en el manejador de chatbot: {str(e)}")
            return None
    
    def _handle_greeting(self, from_number: str, message: str) -> str:
        """Maneja los saludos"""
        return MENSAJE_BIENVENIDA
    
    def _handle_view_products(self, from_number: str, message: str) -> str:
        """Maneja las solicitudes para ver productos"""
        return MENSAJE_VER_PRODUCTOS
    
    def _handle_make_order(self, from_number: str, message: str) -> str:
        """Maneja las solicitudes para hacer un pedido"""
        return MENSAJE_HACER_PEDIDO
    
    def _handle_order_status(self, from_number: str, message: str) -> str:
        """Maneja las consultas de estado de pedido"""
        return MENSAJE_CONSULTAR_ESTADO
    
    def _handle_special_offers(self, from_number: str, message: str) -> str:
        """Maneja las solicitudes de ofertas especiales"""
        return MENSAJE_OFERTAS_ESPECIALES
    
    def _handle_customer_support(self, from_number: str, message: str) -> str:
        """Maneja las solicitudes de atención al cliente"""
        return MENSAJE_ATENCION_CLIENTE
