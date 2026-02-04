from typing import Dict, Any
from datetime import datetime
import uuid

from app.services.base_provider import WhatsAppProvider, EmailProvider


class SimulatedWhatsAppProvider(WhatsAppProvider):
    """Provider simulado de WhatsApp para MVP"""
    
    async def send_message(self, to: str, message: str) -> Dict[str, Any]:
        """
        Simula el envío de WhatsApp
        Solo imprime en consola y retorna éxito
        """
        print(f"\n{'='*60}")
        print(f"📱 [SIMULADO] WhatsApp")
        print(f"{'='*60}")
        print(f"Para: {to}")
        print(f"Mensaje: {message[:200]}{'...' if len(message) > 200 else ''}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        return {
            "status": "success",
            "message_id": f"sim_wa_{uuid.uuid4().hex[:8]}",
            "provider": "simulated_whatsapp"
        }


class SimulatedEmailProvider(EmailProvider):
    """Provider simulado de Email para MVP"""
    
    async def send_email(self, to: str, subject: str, body: str) -> Dict[str, Any]:
        """
        Simula el envío de Email
        Solo imprime en consola y retorna éxito
        """
        print(f"\n{'='*60}")
        print(f"📧 [SIMULADO] Email")
        print(f"{'='*60}")
        print(f"Para: {to}")
        print(f"Asunto: {subject}")
        print(f"Cuerpo: {body[:200]}{'...' if len(body) > 200 else ''}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        return {
            "status": "success",
            "message_id": f"sim_email_{uuid.uuid4().hex[:8]}",
            "provider": "simulated_email"
        }
