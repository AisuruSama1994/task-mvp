from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime, date, time
from uuid import UUID


# ============================================
# TAREA SCHEMAS
# ============================================

class TareaBase(BaseModel):
    titulo: str
    descripcion: Optional[str] = None
    fecha_creacion: date
    hora_creacion: Optional[time] = None
    fecha_termino: Optional[date] = None
    hora_termino: Optional[time] = None
    prioridad: str = "media"
    estado: str = "pendiente"
    etiquetas: List[str] = []
    
    @field_validator('prioridad')
    @classmethod
    def validate_prioridad(cls, v):
        if v not in ['baja', 'media', 'alta', 'urgente']:
            raise ValueError('Prioridad debe ser: baja, media, alta o urgente')
        return v
    
    @field_validator('estado')
    @classmethod
    def validate_estado(cls, v):
        if v not in ['pendiente', 'en_progreso', 'completada', 'cancelada']:
            raise ValueError('Estado debe ser: pendiente, en_progreso, completada o cancelada')
        return v


class TareaCreate(TareaBase):
    pass


class TareaUpdate(BaseModel):
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    fecha_creacion: Optional[date] = None
    hora_creacion: Optional[time] = None
    fecha_termino: Optional[date] = None
    hora_termino: Optional[time] = None
    prioridad: Optional[str] = None
    estado: Optional[str] = None
    etiquetas: Optional[List[str]] = None


class TareaResponse(TareaBase):
    id: UUID
    fecha_creacion_record: datetime
    fecha_actualizacion: datetime
    fecha_completacion: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TareaConUrgencia(TareaResponse):
    """Tarea con cálculo de días restantes y urgencia"""
    dias_restantes: Optional[int] = None
    urgencia: str = "sin_fecha"  # sin_fecha, vencida, hoy, urgente, normal


# ============================================
# TAREA ADJUNTO SCHEMAS
# ============================================

class TareaAdjuntoCreate(BaseModel):
    nombre_archivo: str
    ruta_archivo: str


class TareaAdjuntoResponse(BaseModel):
    id: UUID
    tarea_id: UUID
    nombre_archivo: str
    ruta_archivo: str
    fecha_agregado: datetime
    
    class Config:
        from_attributes = True


# ============================================
# TAREA LOG SCHEMAS
# ============================================

class TareaLogResponse(BaseModel):
    id: UUID
    tarea_id: UUID
    accion: str
    datos_anteriores: Optional[dict] = None
    datos_nuevos: Optional[dict] = None
    fecha_cambio: datetime
    usuario: Optional[str] = None
    
    class Config:
        from_attributes = True


# ============================================
# CAMBIO DE ESTADO
# ============================================

class CambioEstadoTarea(BaseModel):
    nuevo_estado: str
    usuario: Optional[str] = None
    
    @field_validator('nuevo_estado')
    @classmethod
    def validate_estado(cls, v):
        if v not in ['pendiente', 'en_progreso', 'completada', 'cancelada']:
            raise ValueError('Estado debe ser: pendiente, en_progreso, completada o cancelada')
        return v
