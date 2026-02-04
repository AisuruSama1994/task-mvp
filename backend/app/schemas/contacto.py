from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID
import re


# ============================================
# CONTACTO SCHEMAS
# ============================================

class ContactoBase(BaseModel):
    nombre: str
    whatsapp: Optional[str] = None
    email: Optional[EmailStr] = None
    estado: str = "activo"
    etiquetas: List[str] = []
    notas: Optional[str] = None
    
    @field_validator('whatsapp')
    @classmethod
    def validate_whatsapp(cls, v):
        if v is not None and v != "":
            # Formato: +5491112345678
            if not re.match(r'^\+[0-9]{10,15}$', v):
                raise ValueError('WhatsApp debe tener formato: +código_país + número (ej: +5491112345678)')
        return v
    
    @field_validator('estado')
    @classmethod
    def validate_estado(cls, v):
        if v not in ['activo', 'inactivo']:
            raise ValueError('Estado debe ser: activo o inactivo')
        return v


class ContactoCreate(ContactoBase):
    pass


class ContactoUpdate(BaseModel):
    nombre: Optional[str] = None
    whatsapp: Optional[str] = None
    email: Optional[EmailStr] = None
    estado: Optional[str] = None
    etiquetas: Optional[List[str]] = None
    notas: Optional[str] = None
    
    @field_validator('whatsapp')
    @classmethod
    def validate_whatsapp(cls, v):
        if v is not None and v != "":
            if not re.match(r'^\+[0-9]{10,15}$', v):
                raise ValueError('WhatsApp debe tener formato: +código_país + número')
        return v


class ContactoResponse(ContactoBase):
    id: UUID
    fecha_agregado: datetime
    
    class Config:
        from_attributes = True


# ============================================
# GRUPO SCHEMAS
# ============================================

class GrupoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    tipo: str  # email, whatsapp, ambos
    estado: str = "activo"
    
    @field_validator('tipo')
    @classmethod
    def validate_tipo(cls, v):
        if v not in ['email', 'whatsapp', 'ambos']:
            raise ValueError('Tipo debe ser: email, whatsapp o ambos')
        return v
    
    @field_validator('estado')
    @classmethod
    def validate_estado(cls, v):
        if v not in ['activo', 'inactivo']:
            raise ValueError('Estado debe ser: activo o inactivo')
        return v


class GrupoCreate(GrupoBase):
    pass


class GrupoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    tipo: Optional[str] = None
    estado: Optional[str] = None


class GrupoResponse(GrupoBase):
    id: UUID
    fecha_creacion: datetime
    
    class Config:
        from_attributes = True


class GrupoConMiembros(GrupoResponse):
    cantidad_miembros: int = 0


# ============================================
# GRUPO MIEMBRO SCHEMAS
# ============================================

class GrupoMiembroCreate(BaseModel):
    contacto_id: UUID


class GrupoMiembroResponse(BaseModel):
    grupo_id: UUID
    contacto_id: UUID
    fecha_agregado: datetime
    
    class Config:
        from_attributes = True
