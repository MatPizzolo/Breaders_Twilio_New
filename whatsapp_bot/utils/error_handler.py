"""
Manejador de Errores

Este módulo proporciona funciones para manejar errores de manera consistente
en toda la aplicación del bot de WhatsApp.
"""
import logging
import traceback
import sys
from typing import Dict, Any, Optional, Callable
from functools import wraps
from django.conf import settings

logger = logging.getLogger(__name__)

# Mensajes de error predefinidos
ERROR_MESSAGES = {
    'general': "Lo siento, ocurrió un error al procesar tu solicitud. Por favor, intenta nuevamente más tarde.",
    'timeout': "Lo siento, la operación está tomando más tiempo del esperado. Por favor, intenta nuevamente más tarde.",
    'validation': "La información proporcionada no es válida. Por favor, verifica e intenta nuevamente.",
    'not_found': "No se encontró la información solicitada. Por favor, verifica e intenta nuevamente.",
    'twilio': "Estamos experimentando problemas de comunicación. Por favor, intenta nuevamente más tarde.",
    'database': "Estamos experimentando problemas con nuestra base de datos. Por favor, intenta nuevamente más tarde."
}

def log_error(error: Exception, context: Dict[str, Any] = None) -> None:
    """
    Registra un error con contexto adicional.
    
    Args:
        error: La excepción que ocurrió
        context: Contexto adicional para el registro
    """
    exc_type, exc_value, exc_traceback = sys.exc_info()
    stack_trace = traceback.format_exception(exc_type, exc_value, exc_traceback)
    
    error_message = f"Error: {str(error)}"
    if context:
        error_message += f"\nContexto: {context}"
    error_message += f"\nStack trace: {''.join(stack_trace)}"
    
    logger.error(error_message)

def get_error_message(error_type: str = 'general') -> str:
    """
    Obtiene un mensaje de error predefinido según el tipo.
    
    Args:
        error_type: Tipo de error
        
    Returns:
        Mensaje de error predefinido
    """
    return ERROR_MESSAGES.get(error_type, ERROR_MESSAGES['general'])

def handle_exceptions(error_type: str = 'general') -> Callable:
    """
    Decorador para manejar excepciones en funciones.
    
    Args:
        error_type: Tipo de error para el mensaje predefinido
        
    Returns:
        Decorador que maneja excepciones
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Registrar el error
                context = {
                    'function': func.__name__,
                    'args': args,
                    'kwargs': kwargs
                }
                log_error(e, context)
                
                # Devolver mensaje de error predefinido
                return get_error_message(error_type)
        return wrapper
    return decorator

def safe_execute(func: Callable, *args, error_type: str = 'general', default_return: Any = None, **kwargs) -> Any:
    """
    Ejecuta una función de manera segura, manejando cualquier excepción.
    
    Args:
        func: Función a ejecutar
        *args: Argumentos posicionales para la función
        error_type: Tipo de error para el mensaje predefinido
        default_return: Valor por defecto a devolver en caso de error
        **kwargs: Argumentos de palabra clave para la función
        
    Returns:
        Resultado de la función o valor por defecto en caso de error
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        # Registrar el error
        context = {
            'function': func.__name__,
            'args': args,
            'kwargs': kwargs
        }
        log_error(e, context)
        
        # Devolver valor por defecto
        return default_return
