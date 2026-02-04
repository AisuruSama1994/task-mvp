from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime, date, time
from uuid import UUID


# ============================================
# COMUNICADO SCHEMAS
# ============================================

class ComunicadoBase(BaseModel):
    titulo: str
    tipo: str  # whatsapp, email, ambos
    contenido: str
    fecha_programada: Optional[date] = None
    hora_programada: Optional[time] = None
    creado_por: Optional[str] = None
    
    @field_validator('tipo')
    @classmethod
    def validate_tipo(cls, v):
        if v not in ['whatsapp', 'email', 'ambos']:
            raise ValueError('Tipo debe ser: whatsapp, email o ambos')
        return v


class ComunicadoCreate(ComunicadoBase):
    destinatarios_contactos: List[UUID] = []
    destinatarios_grupos: List[UUID] = []


class ComunicadoUpdate(BaseModel):
    titulo: Optional[str] = None
    tipo: Optional[str] = None
    contenido: Optional[str] = None
    fecha_programada: Optional[date] = None
    hora_programada: Optional[time] = None


class ComunicadoResponse(ComunicadoBase):
    id: UUID
    estado: str
    fecha_envio_real: Optional[datetime] = None
    variables_disponibles: List[str] = []
    creado_en: datetime
    
    class Config:
        from_attributes = True


# ============================================
# DESTINATARIO SCHEMAS
# ============================================

class DestinatarioResponse(BaseModel):
    id: UUID
    comunicado_id: UUID
    contacto_id: Optional[UUID] = None
    grupo_id: Optional[UUID] = None
    estado_envio: str
    intentos_fallidos: int
    error_mensaje: Optional[str] = None
    fecha_envio: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============================================
# VISTA PREVIA
# ============================================

class VistaPreviaItem(BaseModel):
    contacto_nombre: str
    contacto_email: Optional[str] = None
    contacto_whatsapp: Optional[str] = None
    mensaje_final: str


class VistaPreviaResponse(BaseModel):
    comunicado_id: UUID
    titulo: str
    tipo: str
    total_destinatarios: int
    previews: List[VistaPreviaItem]


# ============================================
# PROGRAMAR ENVÍO
# ============================================

class ProgramarEnvio(BaseModel):
    fecha_programada: date
    hora_programada: time


# ============================================
# COMUNICADO LOG SCHEMAS
# ============================================

class ComunicadoLogResponse(BaseModel):
    id: UUID
    comunicado_id: Optional[UUID] = None
    contacto_id: Optional[UUID] = None
    tipo_comunicado: Optional[str] = None
    contenido_enviado: Optional[str] = None
    fecha_envio: datetime
    resultado: Optional[str] = None
    motivo_error: Optional[str] = None
    intento: int
    
    class Config:
        from_attributes = True


# ============================================
# ESTADÍSTICAS
# ============================================

class EstadisticasEnvio(BaseModel):
    comunicado_id: UUID
    titulo: str
    total_destinatarios: int
    enviados: int
    errores: int
    pendientes: int
    porcentaje_exito: float
