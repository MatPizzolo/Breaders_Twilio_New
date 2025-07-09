"""
Servicio de Atención al Cliente

Este módulo proporciona funciones para manejar consultas de atención al cliente
y proporcionar respuestas apropiadas para el bot de WhatsApp.
"""
import logging
import re
from typing import Dict, Any, Optional, List, Tuple
from django.conf import settings
from .constants import (
    PALABRAS_ATENCION_CLIENTE, PALABRAS_VOLVER,
    ESTADO_ATENCION_CLIENTE, ESTADO_MENU_PRINCIPAL,
    MENSAJE_ATENCION_CLIENTE
)

logger = logging.getLogger(__name__)

class CustomerSupportService:
    """
    Servicio para gestionar consultas de atención al cliente y proporcionar
    respuestas apropiadas para el bot de WhatsApp.
    """
    
    # Categorías de soporte comunes y sus palabras clave
    SUPPORT_CATEGORIES = {
        'pedido': [
            'pedido', 'orden', 'compra', 'tracking', 'seguimiento', 
            'estado', 'cancelar', 'modificar', 'cambiar'
        ],
        'producto': [
            'producto', 'calidad', 'ingredientes', 'alérgenos', 'alergenos',
            'conservación', 'conservacion', 'caducidad', 'vencimiento'
        ],
        'pago': [
            'pago', 'factura', 'recibo', 'tarjeta', 'efectivo', 'transferencia',
            'mercadopago', 'reembolso', 'devolucion', 'devolución'
        ],
        'envio': [
            'envío', 'envio', 'delivery', 'entrega', 'dirección', 'direccion',
            'domicilio', 'tiempo', 'demora', 'retraso'
        ],
        'horario': [
            'horario', 'abierto', 'cerrado', 'atención', 'atencion',
            'disponibilidad', 'días', 'dias', 'horas'
        ],
        'reclamo': [
            'reclamo', 'queja', 'problema', 'error', 'incidencia', 'incidente',
            'insatisfecho', 'insatisfecha', 'mal', 'defectuoso'
        ]
    }
    
    # Respuestas predefinidas para cada categoría
    SUPPORT_RESPONSES = {
        'pedido': (
            "Entiendo que tienes una consulta sobre tu pedido. "
            "Para ayudarte mejor, necesito el número de pedido. "
            "Por favor, envíame el número que recibiste en tu confirmación de compra.\n\n"
            "Si no tienes el número, puedes proporcionarme la fecha aproximada "
            "y tu nombre completo para buscar tu pedido."
        ),
        'producto': (
            "Gracias por tu interés en nuestros productos. "
            "Todas nuestras milanesas son elaboradas con ingredientes frescos y de alta calidad. "
            "Si tienes alguna consulta específica sobre ingredientes, alérgenos o "
            "métodos de conservación, por favor háznoslo saber y te proporcionaremos "
            "la información detallada."
        ),
        'pago': (
            "Respecto a tu consulta sobre pagos, aceptamos múltiples formas de pago:\n"
            "- Efectivo (solo en entregas a domicilio)\n"
            "- Tarjetas de débito y crédito\n"
            "- Transferencia bancaria\n"
            "- MercadoPago\n\n"
            "Si tienes alguna consulta específica sobre facturación o reembolsos, "
            "por favor proporciona más detalles para poder ayudarte mejor."
        ),
        'envio': (
            "Sobre nuestro servicio de envío:\n"
            "- Realizamos entregas en toda la ciudad\n"
            "- El costo estándar es de $500\n"
            "- Envío gratis en compras superiores a $5000\n"
            "- Tiempo estimado de entrega: 30-45 minutos dependiendo de la zona\n\n"
            "Si necesitas información sobre el estado de tu envío, por favor "
            "proporciona tu número de pedido."
        ),
        'horario': (
            "Nuestro horario de atención es:\n"
            "- Lunes a viernes: 9:00 a 20:00 hs\n"
            "- Sábados: 9:00 a 14:00 hs\n"
            "- Domingos: Cerrado\n\n"
            "Los pedidos realizados fuera del horario de atención serán procesados "
            "al siguiente día hábil."
        ),
        'reclamo': (
            "Lamentamos mucho que hayas tenido un problema. Tu satisfacción es "
            "nuestra prioridad y queremos resolverlo lo antes posible.\n\n"
            "Por favor, describe detalladamente el inconveniente que tuviste, "
            "incluyendo el número de pedido si lo tienes disponible. "
            "Un representante de atención al cliente se pondrá en contacto contigo "
            "a la brevedad."
        ),
        'default': (
            "Gracias por contactar a nuestro servicio de atención al cliente. "
            "Estamos aquí para ayudarte con cualquier consulta o problema que tengas. "
            "Por favor, proporciona más detalles sobre tu consulta para que podamos "
            "asistirte mejor."
        )
    }
    
    @classmethod
    def detect_support_category(cls, message: str) -> Tuple[str, float]:
        """
        Detecta la categoría de soporte basada en el mensaje del usuario.
        
        Args:
            message: El mensaje del usuario
            
        Returns:
            Tupla con la categoría detectada y la puntuación de confianza
        """
        message = message.lower()
        
        # Contar coincidencias para cada categoría
        category_matches = {}
        for category, keywords in cls.SUPPORT_CATEGORIES.items():
            matches = sum(1 for keyword in keywords if keyword in message)
            if matches > 0:
                category_matches[category] = matches
        
        # Si no hay coincidencias, devolver categoría por defecto
        if not category_matches:
            return ('default', 0.1)
        
        # Encontrar la categoría con más coincidencias
        best_category = max(category_matches.items(), key=lambda x: x[1])
        category_name = best_category[0]
        match_count = best_category[1]
        
        # Calcular puntuación de confianza basada en el número de coincidencias
        # Más coincidencias = mayor confianza, hasta un máximo de 0.9
        confidence = min(0.9, 0.3 + (match_count * 0.15))
        
        return (category_name, confidence)
    
    @classmethod
    def get_support_response(cls, message: str) -> str:
        """
        Genera una respuesta de soporte basada en el mensaje del usuario.
        
        Args:
            message: El mensaje del usuario
            
        Returns:
            Texto de respuesta para el usuario
        """
        try:
            # Detectar categoría de soporte
            category, confidence = cls.detect_support_category(message)
            
            # Obtener respuesta predefinida para la categoría
            response = cls.SUPPORT_RESPONSES.get(category, cls.SUPPORT_RESPONSES['default'])
            
            # Agregar mensaje para volver al menú principal
            response += "\n\nPara volver al menú principal, escribe 'menu' o 'volver'."
            
            logger.info(f"Categoría de soporte detectada: {category} con confianza {confidence:.2f}")
            return response
            
        except Exception as e:
            logger.error(f"Error al generar respuesta de soporte: {str(e)}")
            return (
                "Lo siento, ocurrió un error al procesar tu consulta. "
                "Por favor, intenta nuevamente o escribe 'menu' para volver al menú principal."
            )
    
    @classmethod
    def is_returning_to_menu(cls, message: str) -> bool:
        """
        Verifica si el usuario está solicitando volver al menú principal.
        
        Args:
            message: El mensaje del usuario
            
        Returns:
            True si el usuario quiere volver al menú, False en caso contrario
        """
        message = message.lower()
        return any(keyword in message for keyword in PALABRAS_VOLVER)
