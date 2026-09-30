from typing import Dict, Any
from datetime import datetime
import uuid
from app.services.base_provider import WhatsAppProvider
from app.config import settings


class PyWhatkitProvider(WhatsAppProvider):
    """
    Provider real de WhatsApp usando pywhatkit
    
    Requisitos:
    - pip install pywhatkit ✅
    - Tener WhatsApp Web abierto en el navegador
    - Chrome o Edge instalado
    """
    
    def __init__(self):
        self.wait_time = settings.PYWHATKIT_WAIT_TIME
        
    async def send_message(self, to: str, message: str) -> Dict[str, Any]:
        """
        Envía mensaje real usando pywhatkit
        
        Args:
            to: Número en formato internacional (ej: +5491112345678)
            message: Mensaje a enviar
        """
        try:
            # Importar aquí (lazy import) para evitar problemas de DISPLAY
            import pywhatkit
            
            phone_number = to.replace("+", "")
            
            print(f"\n{'='*60}")
            print(f"📱 [PYWHATKIT] Enviando WhatsApp")
            print(f"{'='*60}")
            print(f"Para: {to}")
            print(f"Mensaje: {message[:100]}{'...' if len(message) > 100 else ''}")
            print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*60}\n")
            
            pywhatkit.sendwhatmsg_instantly(
                phone_no=phone_number,
                message=message,
                wait_time=self.wait_time,
                tab_close=True
            )
            
            message_id = f"pywhatkit_{uuid.uuid4().hex[:8]}"
            
            print(f"✅ Mensaje enviado exitosamente a {to}")
            
            return {
                "status": "success",
                "message_id": message_id,
                "provider": "pywhatkit"
            }
            
        except Exception as e:
            error_msg = f"Error enviando WhatsApp con pywhatkit: {str(e)}"
            print(f"❌ {error_msg}")
            
            return {
                "status": "error",
                "error": error_msg,
                "provider": "pywhatkit"
            }
