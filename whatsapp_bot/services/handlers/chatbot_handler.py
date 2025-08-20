"""
Manejador de Chatbot

Este módulo proporciona la clase ChatbotHandler que maneja las respuestas básicas
del chatbot para intenciones conocidas.
"""
import logging
import json
from typing import Dict, Optional, Callable, Any

from django.core.cache import cache

from whatsapp_bot.services.constants import (
    MENSAJE_BIENVENIDA,
    MENSAJE_MENU_PRINCIPAL,
    MENSAJE_VER_PRODUCTOS,
    MENSAJE_HACER_PEDIDO,
    MENSAJE_CONSULTAR_ESTADO,
    MENSAJE_OFERTAS_ESPECIALES,
    MENSAJE_ATENCION_CLIENTE,
    MENSAJE_MANIPULACION,
    MENSAJE_RECETAS,
    MENSAJE_FORMAS_PAGO,
    MENSAJE_PRODUCTOS_POR_CATEGORIAS,
    MENSAJE_MILANESAS, 
    MENSAJE_CONGELADOS, 
    MENSAJE_ACOMPAÑAMIENTOS, 
    MENSAJE_TARTAS,
    MENSAJE_PIZZAS, 
    MENSAJE_CONSULTA_ZONA, 
    MENSAJE_MONTO_MINIMO, 
    MENSAJE_NO_ESTOY,
    MENSAJE_MANIPULACION, 
    MENSAJE_RECETAS,
    MENSAJE_PROMOCIONES_GENERALES,
    MENSAJE_COMBOS_SIN_GLUTEN,
    MENSAJE_CONGELADOS_GUARNICIONES,
    ESTADO_SALUDO, 
    ESTADO_MENU_PRINCIPAL, 
    ESTADO_NAVEGANDO_PRODUCTOS,
    ESTADO_AGREGANDO_AL_CARRITO, 
    ESTADO_ESTADO_PEDIDO, 
    ESTADO_OFERTAS_ESPECIALES,
    ESTADO_ATENCION_CLIENTE, 
    MAPEO_INTENCION_ESTADO
)
from .base_handler import BaseConversationHandler

logger = logging.getLogger(__name__)

class ChatbotHandler(BaseConversationHandler):
    """
    Manejador de chatbot que proporciona respuestas para intenciones conocidas.
    Implementa un sistema de estados para gestionar el flujo de conversación.
    """
    
    def __init__(self):
        """Inicializa el manejador de chatbot con mapeos de estados y opciones"""
        # Inicializar la clase base primero para configurar la gestión de estados
        super().__init__()
        
        # Asegurar que el estado predeterminado sea 'menu_principal'
        self._default_state = "menu_principal"
        # Estructura de estados y transiciones
        self.state_handlers = {
            # Estado inicial y menú principal
            'initial': {
                'default': self._handle_greeting,
                'next_state': 'menu_principal'
            },
            'menu_principal': {
                'options': {
                    '1': {'handler': self._handle_view_products, 'next_state': 'menu_productos'},
                    '2': {'handler': self._handle_make_order, 'next_state': 'menu_delivery'},
                    '3': {'handler': self._handle_manipulacion, 'next_state': 'menu_manipulacion'},
                    '4': {'handler': self._handle_recetas, 'next_state': 'menu_recetas'},
                    '5': {'handler': self._handle_customer_support, 'next_state': 'menu_atencion'}
                },
                'default': self._handle_greeting
            },
            
            # Menú de productos
            'menu_productos': {
                'options': {
                    '1': {'handler': self._handle_productos_categorias, 'next_state': 'menu_categorias'},
                    '2': {'handler': self._handle_promociones_generales, 'next_state': 'menu_productos'},
                    '3': {'handler': self._handle_combos_sin_gluten, 'next_state': 'menu_productos'},
                    '4': {'handler': self._handle_congelados_guarniciones, 'next_state': 'menu_productos'},
                    '5': {'handler': self._handle_formas_pago, 'next_state': 'menu_productos'}
                },
                'default': self._handle_view_products,
                'back': {'handler': self._handle_greeting, 'next_state': 'menu_principal'}
            },
            
            # Menú de categorías de productos
            'menu_categorias': {
                'options': {
                    '1': {'handler': self._handle_milanesas, 'next_state': 'menu_milanesas'},
                    '2': {'handler': self._handle_congelados, 'next_state': 'menu_congelados'}
                },
                'default': self._handle_productos_categorias,
                'back': {'handler': self._handle_view_products, 'next_state': 'menu_productos'}
            },
            
            # Menú de congelados
            'menu_congelados': {
                'options': {
                    '1': {'handler': self._handle_acompanamientos, 'next_state': 'menu_acompanamientos'},
                    '2': {'handler': self._handle_tartas, 'next_state': 'menu_tartas'},
                    '3': {'handler': self._handle_pizzas, 'next_state': 'menu_pizzas'}
                },
                'default': self._handle_congelados,
                'back': {'handler': self._handle_productos_categorias, 'next_state': 'menu_categorias'}
            },
            
            # Estados finales para productos específicos
            'menu_milanesas': {
                'default': self._handle_milanesas,
                'back': {'handler': self._handle_productos_categorias, 'next_state': 'menu_categorias'}
            },
            'menu_acompanamientos': {
                'default': self._handle_acompanamientos,
                'back': {'handler': self._handle_congelados, 'next_state': 'menu_congelados'}
            },
            'menu_tartas': {
                'default': self._handle_tartas,
                'back': {'handler': self._handle_congelados, 'next_state': 'menu_congelados'}
            },
            'menu_pizzas': {
                'default': self._handle_pizzas,
                'back': {'handler': self._handle_congelados, 'next_state': 'menu_congelados'}
            },
            
            # Menú de delivery
            'menu_delivery': {
                'options': {
                    '1': {'handler': self._handle_consulta_zona, 'next_state': 'menu_consulta_zona'},
                    '2': {'handler': self._handle_monto_minimo, 'next_state': 'menu_monto_minimo'},
                    '3': {'handler': self._handle_no_estoy, 'next_state': 'menu_no_estoy'}
                },
                'default': self._handle_make_order,
                'back': {'handler': self._handle_greeting, 'next_state': 'menu_principal'}
            },
            
            # Estados finales para opciones de delivery
            'menu_consulta_zona': {
                'default': self._handle_consulta_zona,
                'back': {'handler': self._handle_make_order, 'next_state': 'menu_delivery'}
            },
            'menu_monto_minimo': {
                'default': self._handle_monto_minimo,
                'back': {'handler': self._handle_make_order, 'next_state': 'menu_delivery'}
            },
            'menu_no_estoy': {
                'default': self._handle_no_estoy,
                'back': {'handler': self._handle_make_order, 'next_state': 'menu_delivery'}
            },
            
            # Otros menús
            'menu_manipulacion': {
                'default': self._handle_manipulacion,
                'back': {'handler': self._handle_greeting, 'next_state': 'menu_principal'}
            },
            'menu_recetas': {
                'default': self._handle_recetas,
                'back': {'handler': self._handle_greeting, 'next_state': 'menu_principal'}
            },
            'menu_atencion': {
                'default': self._handle_customer_support,
                'back': {'handler': self._handle_greeting, 'next_state': 'menu_principal'}
            }
        }
        
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
        Procesa un mensaje entrante y devuelve una respuesta apropiada usando el sistema de estados.
        
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
            # Limpiar el mensaje
            message_clean = message.strip().lower()
            
            # Obtener el estado actual del usuario
            current_state = self._get_user_state(from_number)
            logger.info(f"ChatbotHandler procesando mensaje '{message_clean}' en estado '{current_state}'")
            
            # DEBUG: Registrar el estado actual y el mensaje para diagnóstico
            logger.info(f"DEBUG - Estado actual: {current_state} | Mensaje: '{message_clean}'")
            if hasattr(self, "_user_states"):
                logger.info(f"DEBUG - Estados de usuario: {self._user_states}")
            
            # Si no hay estado actual, establecer el estado inicial
            if not current_state:
                current_state = 'initial'
                self._set_user_state(from_number, current_state)
                logger.info(f"Estado inicial establecido: {current_state}")
            
            # 1. Comando "volver" (prioridad máxima para navegación)
            if message_clean == "volver":
                logger.info(f"Procesando comando 'volver' desde estado {current_state}")
                return self._handle_back_navigation(from_number, current_state)
            
            # 2. Opciones numéricas en el contexto del estado actual (prioridad alta)
            if message_clean.isdigit():
                logger.info(f"Procesando opción numérica '{message_clean}' en estado '{current_state}'")
                
                # IMPORTANTE: Validar explícitamente que estamos en un estado válido
                if current_state not in self.state_handlers:
                    logger.error(f"Estado actual '{current_state}' no encontrado en state_handlers")
                    # Restablecer al menú principal si el estado es inválido
                    self._set_user_state(from_number, 'menu_principal')
                    return MENSAJE_MENU_PRINCIPAL
                
                # Manejar la opción ESTRICTAMENTE en el contexto del estado actual
                option_response = self._handle_state_option(from_number, current_state, message_clean)
                
                # Siempre devolver la respuesta para opciones numéricas
                # Esto evita que las opciones numéricas se procesen como otros tipos de mensajes
                return option_response
            
            # 3. Intenciones explícitas con confianza alta
            if intent and intent != "desconocido" and confidence and confidence > 0.65:
                handler = self.intent_handlers.get(intent)
                if handler:
                    logger.info(f"Manejando intención explícita '{intent}' con confianza {confidence}")
                    
                    # Actualizar el estado según la intención
                    if intent == 'saludo':
                        self._set_user_state(from_number, 'menu_principal')
                    elif intent == 'ver_productos':
                        self._set_user_state(from_number, 'menu_productos')
                    elif intent == 'hacer_pedido':
                        self._set_user_state(from_number, 'menu_delivery')
                    
                    response = handler(from_number, message)
                    return response
            
            # 4. Respuesta por defecto para el estado actual
            state_config = self.state_handlers.get(current_state)
            if state_config and 'default' in state_config:
                default_handler = state_config['default']
                logger.info(f"Usando manejador por defecto para estado '{current_state}'")
                return default_handler(from_number, message)
            
            # 5. Intentar usar el manejador por defecto del estado padre si existe
            # SOLO para mensajes de texto, NO para opciones numéricas (ya manejadas arriba)
            menu_hierarchy = self._get_menu_hierarchy()
            if current_state in menu_hierarchy and menu_hierarchy[current_state].get("parent"):
                parent_state = menu_hierarchy[current_state]["parent"]
                parent_config = self.state_handlers.get(parent_state)
                if parent_config and 'default' in parent_config:
                    logger.info(f"Usando manejador por defecto del estado padre '{parent_state}'")
                    return parent_config['default'](from_number, message)
            
            # Si llegamos aquí, no pudimos manejar el mensaje
            logger.info(f"No se pudo manejar el mensaje '{message_clean}' en estado '{current_state}', delegando al AI")
            return None
            
        except Exception as e:
            logger.error(f"Error en el manejador de chatbot: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def _handle_state_option(self, from_number: str, current_state: str, option: str) -> Optional[str]:
        """
        Maneja una opción numérica en el contexto del estado actual.
        
        Args:
            from_number: Número de teléfono del usuario
            current_state: Estado actual del usuario
            option: Opción numérica seleccionada
            
        Returns:
            Respuesta para el usuario o None si no se puede manejar
        """
        logger.info(f"Procesando opción {option} en estado {current_state}")
        
        # DEBUG: Registrar información detallada para diagnóstico
        logger.info(f"DEBUG - _handle_state_option: Estado={current_state}, Opción={option}")
        
        # Validación explícita del estado actual
        if current_state not in self.state_handlers:
            logger.error(f"Estado '{current_state}' no encontrado en state_handlers")
            # Restablecer al menú principal si el estado es inválido
            self._set_user_state(from_number, 'menu_principal')
            return MENSAJE_MENU_PRINCIPAL
        
        # Obtener la configuración del estado actual
        state_config = self.state_handlers.get(current_state)
        logger.info(f"DEBUG - Configuración del estado: {state_config}")
        
        # Si hay configuración para el estado actual y tiene opciones definidas
        if state_config and 'options' in state_config:
            # DEBUG: Registrar todas las opciones disponibles en este estado
            logger.info(f"DEBUG - Opciones disponibles en {current_state}: {list(state_config['options'].keys())}")
            
            # Verificar si la opción existe en este estado
            if option in state_config['options']:
                option_config = state_config['options'][option]
                handler = option_config.get('handler')
                next_state = option_config.get('next_state')
                
                logger.info(f"DEBUG - Opción {option} encontrada en estado {current_state}")
                logger.info(f"DEBUG - Handler: {handler.__name__ if handler else None}, Next state: {next_state}")
                
                # Actualizar el estado si es necesario
                if next_state:
                    # Guardar el estado anterior antes de actualizarlo
                    previous_state = current_state
                    self._set_user_state(from_number, next_state)
                    logger.info(f"Transición de estado: {previous_state} -> {next_state}")
                
                # Ejecutar el manejador si existe
                if handler:
                    logger.info(f"Ejecutando manejador para opción {option} en estado {current_state}")
                    return handler(from_number, option)
                
                # Si no hay handler pero hay next_state, usar el default del nuevo estado
                if next_state and not handler:
                    new_state_config = self.state_handlers.get(next_state)
                    if new_state_config and 'default' in new_state_config:
                        logger.info(f"Usando manejador por defecto del nuevo estado {next_state}")
                        return new_state_config['default'](from_number, option)
                
                # Si llegamos aquí, la opción existe pero no tiene handler ni next_state
                # Devolver un mensaje genérico para evitar que se pase al fallback
                return f"Opción {option} seleccionada en {current_state}"
            else:
                logger.warning(f"Opción {option} no encontrada en estado {current_state}")
        else:
            logger.warning(f"No hay opciones definidas para el estado {current_state}")
        
        # Si no hay opciones definidas para este estado o la opción no está en ellas,
        # verificar si hay un manejador por defecto para este estado específico
        if state_config and 'default' in state_config:
            logger.info(f"Usando manejador por defecto para estado '{current_state}' con opción no reconocida '{option}'")
            return state_config['default'](from_number, option)
        
        # IMPORTANTE: NO buscar en menús padre para mantener el contexto estricto
        logger.info(f"Búsqueda en menús padre desactivada para mantener contexto estricto del menú")
        
        # Devolver un mensaje informativo claro para el usuario
        return f"La opción {option} no está disponible en este menú. Por favor, selecciona una opción válida."

    
    def _get_menu_hierarchy(self):
        """
        Devuelve la jerarquía de navegación del menú.
        
        Returns:
            Diccionario con la jerarquía de menús
        """
        return {
            # Nivel 1: Menú principal y sus opciones directas
            "menu_principal": {
                "parent": None,  # No tiene padre, es el nivel superior
                "message": MENSAJE_MENU_PRINCIPAL
            },
            
            # Nivel 2: Submenús principales que dependen del menú principal
            "menu_productos": {"parent": "menu_principal", "message": MENSAJE_MENU_PRINCIPAL},  # Ver productos
            "menu_delivery": {"parent": "menu_principal", "message": MENSAJE_MENU_PRINCIPAL},  # Hacer pedido
            "menu_manipulacion": {"parent": "menu_principal", "message": MENSAJE_MENU_PRINCIPAL},  # Manipulación
            "menu_recetas": {"parent": "menu_principal", "message": MENSAJE_MENU_PRINCIPAL},  # Recetas
            "menu_atencion": {"parent": "menu_principal", "message": MENSAJE_MENU_PRINCIPAL},  # Atención al cliente
            
            # Nivel 3: Opciones del menú de productos
            "menu_categorias": {"parent": "menu_productos", "message": MENSAJE_VER_PRODUCTOS},  # Categorías
            "menu_promociones_generales": {"parent": "menu_productos", "message": MENSAJE_VER_PRODUCTOS},  # Promociones
            "menu_combos_sin_gluten": {"parent": "menu_productos", "message": MENSAJE_VER_PRODUCTOS},  # Combos
            "menu_congelados_guarniciones": {"parent": "menu_productos", "message": MENSAJE_VER_PRODUCTOS},  # Congelados
            "menu_formas_pago": {"parent": "menu_productos", "message": MENSAJE_VER_PRODUCTOS},  # Formas de pago
            
            # Nivel 4: Categorías de productos
            "menu_milanesas": {"parent": "menu_categorias", "message": MENSAJE_PRODUCTOS_POR_CATEGORIAS},  # Milanesas
            "menu_congelados": {"parent": "menu_categorias", "message": MENSAJE_PRODUCTOS_POR_CATEGORIAS},  # Congelados
            
            # Nivel 5: Opciones de congelados
            "menu_acompanamientos": {"parent": "menu_congelados", "message": MENSAJE_CONGELADOS},  # Acompañamientos
            "menu_tartas": {"parent": "menu_congelados", "message": MENSAJE_CONGELADOS},  # Tartas individuales
            "menu_pizzas": {"parent": "menu_congelados", "message": MENSAJE_CONGELADOS},  # Pizzas masa madre
            
            # Nivel 3: Opciones del menú de delivery
            "menu_consulta_zona": {"parent": "menu_delivery", "message": MENSAJE_HACER_PEDIDO},  # Consultar zona
            "menu_monto_minimo": {"parent": "menu_delivery", "message": MENSAJE_HACER_PEDIDO},  # Monto mínimo
            "menu_no_estoy": {"parent": "menu_delivery", "message": MENSAJE_HACER_PEDIDO},  # No estoy en CABA
        }
        
    def _handle_back_navigation(self, from_number: str, current_state: str) -> str:
        """
        Maneja la navegación hacia atrás según el estado actual.
        
        Args:
            from_number: Número de teléfono del usuario
            current_state: Estado actual del usuario
            
        Returns:
            Respuesta para el usuario
        """
        # Obtener la jerarquía de navegación del menú
        menu_hierarchy = self._get_menu_hierarchy()
        
        # Si el estado actual está en la jerarquía y tiene un padre, navegar a él
        if current_state in menu_hierarchy and menu_hierarchy[current_state].get("parent") is not None:
            parent_state = menu_hierarchy[current_state]["parent"]
            parent_message = menu_hierarchy[parent_state]["message"]
            
            # Actualizar el estado del usuario
            self._set_user_state(from_number, parent_state)
            logger.info(f"Navegación hacia atrás: {current_state} -> {parent_state}")
            
            # Devolver el mensaje correspondiente al estado padre
            return parent_message
        
        # Si el estado no está en la jerarquía o no tiene padre, volver al menú principal
        logger.info(f"Navegación hacia menú principal desde: {current_state}")
        self._set_user_state(from_number, "menu_principal")
        return MENSAJE_MENU_PRINCIPAL
    
    # Manejadores adicionales para las nuevas opciones de menú
    def _handle_promociones_generales(self, from_number: str, message: str) -> str:
        """Maneja la opción de ver promociones generales"""
        # Establecer estado del usuario
        self._set_user_state(from_number, "menu_promociones_generales")
        return MENSAJE_PROMOCIONES_GENERALES
    
    def _handle_combos_sin_gluten(self, from_number: str, message: str) -> str:
        """Maneja la opción de ver combos sin gluten"""
        # Establecer estado del usuario
        self._set_user_state(from_number, "menu_combos_sin_gluten")
        return MENSAJE_COMBOS_SIN_GLUTEN
    
    def _handle_congelados_guarniciones(self, from_number: str, message: str) -> str:
        """Maneja la opción de ver congelados y guarniciones"""
        # Establecer estado del usuario
        self._set_user_state(from_number, "menu_congelados_guarniciones")
        return MENSAJE_CONGELADOS_GUARNICIONES
    
    def _handle_formas_pago(self, from_number: str, message: str) -> str:
        """Maneja la opción de ver formas de pago"""
        # Establecer estado del usuario
        self._set_user_state(from_number, "menu_formas_pago")
        return MENSAJE_FORMAS_PAGO
    
    def _get_user_state(self, from_number: str) -> str:
        """Obtiene el estado actual del usuario de forma persistente usando cache"""
        # Usar un prefijo para evitar colisiones con otras claves de cache
        cache_key = f"whatsapp_user_state:{from_number}"
        state = cache.get(cache_key)
        
        # Si no hay estado en cache, usar el valor por defecto
        if state is None:
            state = "menu_principal"
            # Guardar el estado por defecto en cache
            self._set_user_state(from_number, state)
        
        logger.info(f"_get_user_state: Recuperado estado '{state}' para usuario {from_number}")
        return state
    
    def _set_user_state(self, from_number: str, state: str) -> None:
        """Establece el estado del usuario de forma persistente usando cache"""
        # Usar un prefijo para evitar colisiones con otras claves de cache
        cache_key = f"whatsapp_user_state:{from_number}"
        
        # Guardar en cache con un tiempo de expiración de 24 horas (86400 segundos)
        # Esto evita acumular estados de usuarios que ya no interactúan con el bot
        cache.set(cache_key, state, timeout=86400)
        
        logger.info(f"Estado del usuario {from_number} actualizado a: {state}")
        
        # También mantener una copia en memoria para debugging
        if not hasattr(self, "_user_states"):
            self._user_states = {}
        self._user_states[from_number] = state
    
    # Manejadores de intenciones
    def _handle_greeting(self, from_number: str, message: str) -> str:
        """Maneja los saludos"""
        # Establecer estado inicial
        self._set_user_state(from_number, "menu_principal")
        return MENSAJE_BIENVENIDA
    
    def _handle_view_products(self, from_number: str, message: str) -> str:
        """Maneja las solicitudes para ver productos"""
        self._set_user_state(from_number, "menu_productos")
        return MENSAJE_VER_PRODUCTOS
    
    def _handle_make_order(self, from_number: str, message: str) -> str:
        """Maneja las solicitudes para hacer un pedido"""
        self._set_user_state(from_number, "menu_delivery")
        return MENSAJE_HACER_PEDIDO
    
    def _handle_order_status(self, from_number: str, message: str) -> str:
        """Maneja las consultas de estado de pedido"""
        return MENSAJE_CONSULTAR_ESTADO
    
    def _handle_special_offers(self, from_number: str, message: str) -> str:
        """Maneja las solicitudes para ver ofertas especiales"""
        return MENSAJE_OFERTAS_ESPECIALES
    
    def _handle_customer_support(self, from_number: str, message: str) -> str:
        """Maneja las solicitudes de atención al cliente"""
        return MENSAJE_ATENCION_CLIENTE
        
    def _handle_back_command(self, from_number: str) -> str:
        """Maneja el comando 'volver'"""
        current_state = self._get_user_state(from_number)
        logger.info(f"Manejando comando 'volver' en estado '{current_state}'")
        
        # Usar el método _handle_back_navigation para manejar la navegación hacia atrás
        return self._handle_back_navigation(from_number, current_state)
        
    # Manejadores de menú de productos
    def _handle_productos_categorias(self, from_number: str, message: str) -> str:
        """Maneja la opción de ver productos por categorías"""
        return MENSAJE_PRODUCTOS_POR_CATEGORIAS
    
    def _handle_milanesas(self, from_number: str, message: str) -> str:
        """Maneja la opción de ver milanesas"""
        return MENSAJE_MILANESAS
    
    def _handle_congelados(self, from_number: str, message: str) -> str:
        """Maneja la opción de ver congelados"""
        return MENSAJE_CONGELADOS
    
    def _handle_acompanamientos(self, from_number: str, message: str) -> str:
        """Maneja la opción de ver acompañamientos"""
        return MENSAJE_ACOMPAÑAMIENTOS
    
    def _handle_tartas(self, from_number: str, message: str) -> str:
        """Maneja la opción de ver tartas"""
        return MENSAJE_TARTAS
    
    def _handle_pizzas(self, from_number: str, message: str) -> str:
        """Maneja la opción de ver pizzas"""
        return MENSAJE_PIZZAS
    
    # Manejadores de menú de delivery
    def _handle_consulta_zona(self, from_number: str, message: str) -> str:
        """Maneja la opción de consultar zona de entrega"""
        return MENSAJE_CONSULTA_ZONA
    
    def _handle_monto_minimo(self, from_number: str, message: str) -> str:
        """Maneja la opción de consultar monto mínimo"""
        return MENSAJE_MONTO_MINIMO
    
    def _handle_no_estoy(self, from_number: str, message: str) -> str:
        """Maneja la opción de qué pasa si no está en casa"""
        return MENSAJE_NO_ESTOY
    
    # Manejadores adicionales
    def _handle_manipulacion(self, from_number: str, message: str) -> str:
        """Maneja la opción de cómo manipular productos"""
        return MENSAJE_MANIPULACION
    
    def _handle_recetas(self, from_number: str, message: str) -> str:
        """Maneja la opción de ver recetas"""
        return MENSAJE_RECETAS
        
    # Eliminamos el método _handle_non_menu_message ya que delegaremos al AI Assistant
