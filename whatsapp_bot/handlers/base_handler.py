from typing import Optional

class BaseConversationHandler:
    """
    Clase base para todos los manejadores de conversación.
    Define la interfaz común que deben implementar todos los manejadores.
    """
    
    def process_message(self, from_number: str, message: str, 
                        intent: Optional[str] = None, 
                        confidence: Optional[float] = None) -> Optional[str]:
        """
        Procesa un mensaje y genera una respuesta.
        
        Args:
            from_number: Número de teléfono del remitente
            message: Contenido del mensaje
            intent: Intención detectada (opcional)
            confidence: Nivel de confianza de la intención (opcional)
            
        Returns:
            Respuesta al mensaje o None si no hay respuesta
        """
        raise NotImplementedError("Las subclases deben implementar este método")
