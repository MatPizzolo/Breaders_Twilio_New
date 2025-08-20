"""
Manejador Base

Este módulo proporciona la clase BaseConversationHandler que sirve como base
para todos los manejadores de conversación en el bot de WhatsApp.
"""
import logging
from typing import Optional, Dict, Any
from django.core.cache import cache

logger = logging.getLogger(__name__)

class BaseConversationHandler:
    """
    Clase base para manejadores de conversación.
    Proporciona funcionalidad básica para gestionar estados de usuario.
    """
    
    # Definir el estado predeterminado a nivel de clase para que sea accesible globalmente
    _default_state = "menu_principal"
    
    def __init__(self):
        """
        Inicializa la clase base con estructuras para gestionar estados de usuario
        """
        # Inicializar el diccionario de estados de usuario en memoria
        self._user_states = {}
        # Establecer el estado predeterminado (no cambiar el valor, solo asegurar acceso desde la instancia)
        # self._default_state ya está definido a nivel de clase
        logger.info(f"BaseConversationHandler inicializado con estado predeterminado: {self._default_state}")
        
    def _get_user_state(self, user_id: str) -> str:
        """
        Obtiene el estado actual del usuario.
        
        Args:
            user_id: Identificador único del usuario
            
        Returns:
            El estado actual del usuario o un estado predeterminado si no existe
        """
        # Asegurarnos de que _user_states esté inicializado
        if not hasattr(self, '_user_states'):
            self._user_states = {}
            
        # Determinar el estado predeterminado (priorizar el que establece la subclase)
        default_state = getattr(self, '_default_state', "menu_principal")  # Cambiado para usar menu_principal por defecto
            
        # Primero intentar obtener del caché de memoria
        if user_id in self._user_states:
            return self._user_states[user_id]
        
        # Si no está en memoria, intentar recuperar de la caché de Django
        cache_key = f"user_state_{user_id}"
        cached_state = cache.get(cache_key)
        if cached_state:
            # Actualizar también la caché en memoria
            self._user_states[user_id] = cached_state
            return cached_state
        
        # Si no hay estado en ninguna caché, inicializar con el estado por defecto
        # Guardar el estado por defecto en ambas cachés
        self._user_states[user_id] = default_state
        cache.set(cache_key, default_state, 3600)  # 1 hora de timeout
        
        logger.info(f"Inicializando estado para usuario {user_id}: {default_state}")
        return default_state
        
    def _set_user_state(self, from_number: str, state: str) -> None:
        """
        Establece el estado de un usuario.
        
        Args:
            from_number: El número de teléfono del usuario
            state: El nuevo estado del usuario
        """
        logger.info(f"Cambiando estado del usuario {from_number}: {state}")
        
        # Guardar en memoria
        self._user_states[from_number] = state
        
        # Guardar en caché
        cache_key = f"user_state_{from_number}"
        cache.set(cache_key, state, timeout=3600)  # 1 hora de timeout
    
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
