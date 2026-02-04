from sqlalchemy import Column, String, TIMESTAMP, ARRAY, Text, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class Contacto(Base):
    __tablename__ = "contactos"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(255), nullable=False)
    whatsapp = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    fecha_agregado = Column(TIMESTAMP(timezone=True), server_default=func.now())
    estado = Column(String(20), default="activo")
    etiquetas = Column(ARRAY(Text), default=[])
    notas = Column(Text, nullable=True)
    
    # Relationships
    grupo_miembros = relationship("GrupoMiembro", back_populates="contacto", cascade="all, delete-orphan")
    comunicado_destinatarios = relationship("ComunicadoDestinatario", back_populates="contacto")
    comunicados_log = relationship("ComunicadoLog", back_populates="contacto")


class Grupo(Base):
    __tablename__ = "grupos"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=True)
    tipo = Column(String(20), nullable=False)  # email, whatsapp, ambos
    fecha_creacion = Column(TIMESTAMP(timezone=True), server_default=func.now())
    estado = Column(String(20), default="activo")
    
    # Relationships
    grupo_miembros = relationship("GrupoMiembro", back_populates="grupo", cascade="all, delete-orphan")
    comunicado_destinatarios = relationship("ComunicadoDestinatario", back_populates="grupo")


class GrupoMiembro(Base):
    __tablename__ = "grupo_miembros"
    
    grupo_id = Column(UUID(as_uuid=True), ForeignKey("grupos.id", ondelete="CASCADE"), primary_key=True)
    contacto_id = Column(UUID(as_uuid=True), ForeignKey("contactos.id", ondelete="CASCADE"), primary_key=True)
    fecha_agregado = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    # Relationships
    grupo = relationship("Grupo", back_populates="grupo_miembros")
    contacto = relationship("Contacto", back_populates="grupo_miembros")
