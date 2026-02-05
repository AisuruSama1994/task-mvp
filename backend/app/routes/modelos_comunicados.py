from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel

from app.database import get_db
from app.models.modelo_comunicado import ModeloComunicado

router = APIRouter()

class ModeloCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    tipo: str = "email"
    contenido: str

class ModeloUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    tipo: Optional[str] = None
    contenido: Optional[str] = None

class ModeloResponse(BaseModel):
    id: str
    nombre: str
    descripcion: Optional[str]
    tipo: str
    contenido: str
    
    class Config:
        from_attributes = True

@router.post("/", status_code=201, response_model=ModeloResponse)
async def create_modelo(
    modelo: ModeloCreate,
    db: Session = Depends(get_db)
):
    """Crear un nuevo modelo de comunicado"""
    db_modelo = ModeloComunicado(**modelo.dict())
    db.add(db_modelo)
    db.commit()
    db.refresh(db_modelo)
    return db_modelo

@router.get("/", response_model=List[ModeloResponse])
async def list_modelos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    tipo: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Listar todos los modelos"""
    query = db.query(ModeloComunicado)
    
    if tipo:
        query = query.filter(ModeloComunicado.tipo == tipo)
    
    modelos = query.offset(skip).limit(limit).all()
    return modelos

@router.get("/{modelo_id}", response_model=ModeloResponse)
async def get_modelo(
    modelo_id: UUID,
    db: Session = Depends(get_db)
):
    """Obtener un modelo por ID"""
    modelo = db.query(ModeloComunicado).filter(ModeloComunicado.id == modelo_id).first()
    if not modelo:
        raise HTTPException(status_code=404, detail="Modelo no encontrado")
    return modelo

@router.put("/{modelo_id}", response_model=ModeloResponse)
async def update_modelo(
    modelo_id: UUID,
    modelo: ModeloUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar un modelo"""
    db_modelo = db.query(ModeloComunicado).filter(ModeloComunicado.id == modelo_id).first()
    if not db_modelo:
        raise HTTPException(status_code=404, detail="Modelo no encontrado")
    
    update_data = modelo.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_modelo, field, value)
    
    db.commit()
    db.refresh(db_modelo)
    return db_modelo

@router.delete("/{modelo_id}", status_code=204)
async def delete_modelo(
    modelo_id: UUID,
    db: Session = Depends(get_db)
):
    """Eliminar un modelo"""
    modelo = db.query(ModeloComunicado).filter(ModeloComunicado.id == modelo_id).first()
    if not modelo:
        raise HTTPException(status_code=404, detail="Modelo no encontrado")
    
    db.delete(modelo)
    db.commit()
    return None
