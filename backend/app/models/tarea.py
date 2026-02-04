from sqlalchemy import Column, String, TIMESTAMP, ARRAY, Text, ForeignKey, Date, Time, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class Tarea(Base):
    __tablename__ = "tareas"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    titulo = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=True)
    fecha_creacion = Column(Date, nullable=False)
    hora_creacion = Column(Time, nullable=True)
    fecha_termino = Column(Date, nullable=True)
    hora_termino = Column(Time, nullable=True)
    prioridad = Column(String(20), default="media")  # baja, media, alta, urgente
    estado = Column(String(20), default="pendiente")  # pendiente, en_progreso, completada, cancelada
    etiquetas = Column(ARRAY(Text), default=[])
    fecha_creacion_record = Column(TIMESTAMP(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    fecha_completacion = Column(TIMESTAMP(timezone=True), nullable=True)
    
    # Relationships
    adjuntos = relationship("TareaAdjunto", back_populates="tarea", cascade="all, delete-orphan")
    logs = relationship("TareaLog", back_populates="tarea", cascade="all, delete-orphan")


class TareaAdjunto(Base):
    __tablename__ = "tarea_adjuntos"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tarea_id = Column(UUID(as_uuid=True), ForeignKey("tareas.id", ondelete="CASCADE"), nullable=False)
    nombre_archivo = Column(String(255), nullable=False)
    ruta_archivo = Column(String(500), nullable=False)
    fecha_agregado = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    # Relationships
    tarea = relationship("Tarea", back_populates="adjuntos")


class TareaLog(Base):
    __tablename__ = "tareas_log"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tarea_id = Column(UUID(as_uuid=True), ForeignKey("tareas.id"), nullable=False)
    accion = Column(String(50), nullable=False)  # creada, actualizada, completada, cancelada, estado_cambio
    datos_anteriores = Column(JSONB, nullable=True)
    datos_nuevos = Column(JSONB, nullable=True)
    fecha_cambio = Column(TIMESTAMP(timezone=True), server_default=func.now())
    usuario = Column(String(255), nullable=True)
    
    # Relationships
    tarea = relationship("Tarea", back_populates="logs")
