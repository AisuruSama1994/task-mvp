from sqlalchemy import Column, String, TIMESTAMP, ARRAY, Text, ForeignKey, Date, Time, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class Comunicado(Base):
    __tablename__ = "comunicados"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    titulo = Column(String(255), nullable=False)
    tipo = Column(String(20), nullable=False)  # whatsapp, email, ambos
    contenido = Column(Text, nullable=False)
    estado = Column(String(30), default="borrador")  # borrador, programado, enviado, parcialmente_enviado, error
    fecha_programada = Column(Date, nullable=True)
    hora_programada = Column(Time, nullable=True)
    fecha_envio_real = Column(TIMESTAMP(timezone=True), nullable=True)
    variables_disponibles = Column(ARRAY(Text), default=["{{nombre}}", "{{email}}", "{{whatsapp}}"])
    creado_en = Column(TIMESTAMP(timezone=True), server_default=func.now())
    creado_por = Column(String(255), nullable=True)
    
    # Relationships
    adjuntos = relationship("ComunicadoAdjunto", back_populates="comunicado", cascade="all, delete-orphan")
    destinatarios = relationship("ComunicadoDestinatario", back_populates="comunicado", cascade="all, delete-orphan")
    logs = relationship("ComunicadoLog", back_populates="comunicado", cascade="all, delete-orphan")


class ComunicadoAdjunto(Base):
    __tablename__ = "comunicado_adjuntos"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    comunicado_id = Column(UUID(as_uuid=True), ForeignKey("comunicados.id", ondelete="CASCADE"), nullable=False)
    nombre_archivo = Column(String(255), nullable=False)
    ruta_archivo = Column(String(500), nullable=False)
    fecha_agregado = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    # Relationships
    comunicado = relationship("Comunicado", back_populates="adjuntos")


class ComunicadoDestinatario(Base):
    __tablename__ = "comunicado_destinatarios"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    comunicado_id = Column(UUID(as_uuid=True), ForeignKey("comunicados.id", ondelete="CASCADE"), nullable=False)
    contacto_id = Column(UUID(as_uuid=True), ForeignKey("contactos.id"), nullable=True)
    grupo_id = Column(UUID(as_uuid=True), ForeignKey("grupos.id"), nullable=True)
    estado_envio = Column(String(20), default="pendiente")  # pendiente, enviado, error, reintentos
    intentos_fallidos = Column(Integer, default=0)
    error_mensaje = Column(Text, nullable=True)
    fecha_envio = Column(TIMESTAMP(timezone=True), nullable=True)
    
    # Relationships
    comunicado = relationship("Comunicado", back_populates="destinatarios")
    contacto = relationship("Contacto", back_populates="comunicado_destinatarios")
    grupo = relationship("Grupo", back_populates="comunicado_destinatarios")
