"""
Middleware para el bot de WhatsApp

Este módulo proporciona middleware personalizado para manejar errores
y realizar otras tareas a nivel de solicitud.
"""
import logging
import json
import time
from django.http import HttpResponse
from twilio.twiml.messaging_response import MessagingResponse
from .utils.error_handler import log_error, get_error_message

logger = logging.getLogger(__name__)

class WhatsAppErrorMiddleware:
    """
    Middleware para manejar errores en las solicitudes del bot de WhatsApp.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Procesar la solicitud normalmente
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            # Solo manejar errores para rutas de WhatsApp
            if '/whatsapp/' in request.path:
                logger.error(f"Error no manejado en la solicitud de WhatsApp: {str(e)}")
                
                # Registrar el error con contexto
                context = {
                    'path': request.path,
                    'method': request.method,
                    'POST': request.POST.dict() if request.method == 'POST' else {},
                    'GET': request.GET.dict(),
                }
                log_error(e, context)
                
                # Crear respuesta de error de Twilio
                twiml_response = MessagingResponse()
                twiml_response.message(get_error_message('general'))
                
                return HttpResponse(str(twiml_response), content_type='text/xml')
            else:
                # Para otras rutas, dejar que Django maneje el error
                raise

class RequestLoggingMiddleware:
    """
    Middleware para registrar información sobre solicitudes y respuestas.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Registrar información de la solicitud
        start_time = time.time()
        
        if '/whatsapp/' in request.path:
            logger.info(f"Solicitud recibida: {request.method} {request.path}")
            
            # Registrar datos de la solicitud para rutas de WhatsApp
            if request.method == 'POST':
                # Evitar registrar información sensible
                safe_post = request.POST.dict()
                if 'Body' in safe_post:
                    # Truncar el cuerpo del mensaje para evitar registrar mensajes largos
                    safe_post['Body'] = safe_post['Body'][:50] + ('...' if len(safe_post['Body']) > 50 else '')
                
                logger.debug(f"Datos POST: {json.dumps(safe_post)}")
        
        # Procesar la solicitud
        response = self.get_response(request)
        
        # Registrar información de la respuesta
        if '/whatsapp/' in request.path:
            duration = time.time() - start_time
            logger.info(f"Respuesta enviada: {response.status_code} (tiempo: {duration:.3f}s)")
        
        return response
