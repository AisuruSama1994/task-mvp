from typing import Dict, Any
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.services.base_provider import EmailProvider
from app.config import settings


class GmailProvider(EmailProvider):
    """
    Provider real de Gmail usando SMTP
    
    Configuración requerida en .env:
    GMAIL_USER=maria@escribanoschaco.com
    GMAIL_APP_PASSWORD=tu_app_password_aqui
    
    IMPORTANTE: No uses tu contraseña normal de Gmail.
    Debes crear una "App Password" desde tu cuenta de Google:
    1. Ve a https://myaccount.google.com/security
    2. Activa "2-Step Verification" si no está activado
    3. Ve a "App passwords"
    4. Genera una nueva password para "Mail"
    5. Usa esa password en GMAIL_APP_PASSWORD
    """
    
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.user = settings.GMAIL_USER
        self.password = settings.GMAIL_APP_PASSWORD
        
        if not self.user or not self.password:
            raise ValueError(
                "Gmail no configurado. Necesitas GMAIL_USER y GMAIL_APP_PASSWORD en .env"
            )
    
    async def send_email(self, to: str, subject: str, body: str) -> Dict[str, Any]:
        """
        Envía email real usando Gmail SMTP
        """
        try:
            # Crear mensaje
            msg = MIMEMultipart()
            msg['From'] = self.user
            msg['To'] = to
            msg['Subject'] = subject
            
            # Agregar cuerpo
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # Conectar y enviar
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.user, self.password)
                server.send_message(msg)
            
            print(f"✅ Email enviado exitosamente a {to}")
            
            return {
                "status": "success",
                "message_id": f"gmail_{hash(to + subject)}",
                "provider": "gmail"
            }
            
        except smtplib.SMTPAuthenticationError:
            error_msg = "Error de autenticación Gmail. Verifica GMAIL_USER y GMAIL_APP_PASSWORD"
            print(f"❌ {error_msg}")
            return {
                "status": "error",
                "error": error_msg,
                "provider": "gmail"
            }
            
        except Exception as e:
            error_msg = f"Error enviando email: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "status": "error",
                "error": error_msg,
                "provider": "gmail"
            }
