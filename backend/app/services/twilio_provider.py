from typing import Dict, Any

# Twilio (comentado para futuro uso)
# from twilio.rest import Client
from app.services.base_provider import WhatsAppProvider
from app.config import settings


class TwilioWhatsAppProvider(WhatsAppProvider):
    """
    Provider real de WhatsApp usando Twilio API
    
    Configuración requerida en .env:
    TWILIO_ACCOUNT_SID=your_account_sid
    TWILIO_AUTH_TOKEN=your_auth_token
    TWILIO_WHATSAPP_NUMBER=+14155238886
    
    NOTA: Por ahora está comentado porque requiere cuenta Twilio.
    Para activarlo:
    1. Crea cuenta en https://www.twilio.com
    2. Obtén tus credenciales
    3. Descomenta el código
    4. pip install twilio
    5. Configura .env
    """
    
    def __init__(self):
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.from_number = settings.TWILIO_WHATSAPP_NUMBER
        
        if not all([self.account_sid, self.auth_token, self.from_number]):
            raise ValueError(
                "Twilio no configurado. Necesitas TWILIO_ACCOUNT_SID, "
                "TWILIO_AUTH_TOKEN y TWILIO_WHATSAPP_NUMBER en .env"
            )
        
        # Descomentar cuando tengas Twilio configurado:
        # self.client = Client(self.account_sid, self.auth_token)
    
    async def send_message(self, to: str, message: str) -> Dict[str, Any]:
        """
        Envía mensaje real por WhatsApp usando Twilio
        """
        try:
            # DESCOMENTAR CUANDO TENGAS TWILIO:
            # msg = self.client.messages.create(
            #     from_=f'whatsapp:{self.from_number}',
            #     to=f'whatsapp:{to}',
            #     body=message
            # )
            # 
            # print(f"✅ WhatsApp enviado exitosamente a {to}")
            # 
            # return {
            #     "status": "success",
            #     "message_id": msg.sid,
            #     "provider": "twilio"
            # }
            
            # Por ahora, simular:
            print(f"⚠️ Twilio no configurado. Simulando envío a {to}")
            return {
                "status": "simulated",
                "message_id": "twilio_not_configured",
                "provider": "twilio_simulated"
            }
            
        except Exception as e:
            error_msg = f"Error enviando WhatsApp: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "status": "error",
                "error": error_msg,
                "provider": "twilio"
            }
