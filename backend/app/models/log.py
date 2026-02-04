from sqlalchemy import Column, String, TIMESTAMP, Text, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class ComunicadoLog(Base):
    __tablename__ = "comunicados_log"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    comunicado_id = Column(UUID(as_uuid=True), ForeignKey("comunicados.id"), nullable=True)
    contacto_id = Column(UUID(as_uuid=True), ForeignKey("contactos.id"), nullable=True)
    tipo_comunicado = Column(String(20), nullable=True)  # whatsapp, email
    contenido_enviado = Column(Text, nullable=True)
    fecha_envio = Column(TIMESTAMP(timezone=True), server_default=func.now())
    resultado = Column(String(20), nullable=True)  # exitoso, fallido
    motivo_error = Column(Text, nullable=True)
    intento = Column(Integer, default=1)
    
    # Relationships
    comunicado = relationship("Comunicado", back_populates="logs")
    contacto = relationship("Contacto", back_populates="comunicados_log")
