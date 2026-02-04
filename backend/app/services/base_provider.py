from abc import ABC, abstractmethod
from typing import Dict, Any


class WhatsAppProvider(ABC):
    """Interfaz abstracta para providers de WhatsApp"""
    
    @abstractmethod
    async def send_message(self, to: str, message: str) -> Dict[str, Any]:
        """
        Enviar mensaje por WhatsApp
        
        Args:
            to: Número de WhatsApp (formato: +5491112345678)
            message: Contenido del mensaje
            
        Returns:
            Dict con status, message_id, y error si aplica
        """
        pass


class EmailProvider(ABC):
    """Interfaz abstracta para providers de Email"""
    
    @abstractmethod
    async def send_email(self, to: str, subject: str, body: str) -> Dict[str, Any]:
        """
        Enviar email
        
        Args:
            to: Email del destinatario
            subject: Asunto del email
            body: Cuerpo del email
            
        Returns:
            Dict con status, message_id, y error si aplica
        """
        pass
