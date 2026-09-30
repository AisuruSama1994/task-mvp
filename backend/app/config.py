from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/recordatorios_db"
    
    # Environment
    ENVIRONMENT: str = "development"
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    
    # Upload
    UPLOAD_DIR: str = "./uploads"
    
    # WhatsApp
    WHATSAPP_PROVIDER: str = "pywhatkit"  # simulated | twilio | pywhatkit
    WHATSAPP_ENABLED: bool = True
    
    # Email
    EMAIL_PROVIDER: str = "gmail"  # simulated | gmail | sendgrid
    EMAIL_ENABLED: bool = True
    
    # Gmail (para cuando conectes tu email)
    GMAIL_USER: str = ""
    GMAIL_APP_PASSWORD: str = ""
    
    # Twilio (para futuro)
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_WHATSAPP_NUMBER: str = ""
    
    # SendGrid (alternativa)
    SENDGRID_API_KEY: str = ""
    SENDGRID_FROM_EMAIL: str = ""
    
    # PyWhatkit
    PYWHATKIT_WAIT_TIME: int = 15
    PYWHATKIT_TAB_CLOSE: bool = True
    
    # Scheduler
    SCHEDULER_ENABLED: bool = True
    SCHEDULER_CHECK_INTERVAL: int = 60
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
