from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.models.contacto import Contacto
from app.schemas.contacto import (
    ContactoCreate,
    ContactoUpdate,
    ContactoResponse
)

router = APIRouter()


@router.post("/", response_model=ContactoResponse, status_code=201)
async def create_contacto(
    contacto: ContactoCreate,
    db: Session = Depends(get_db)
):
    """Crear un nuevo contacto"""
    db_contacto = Contacto(**contacto.model_dump())
    db.add(db_contacto)
    db.commit()
    db.refresh(db_contacto)
    return db_contacto


@router.get("/", response_model=List[ContactoResponse])
async def list_contactos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = Query(None, description="Buscar por nombre, email o whatsapp"),
    estado: Optional[str] = Query(None, description="Filtrar por estado: activo, inactivo"),
    etiqueta: Optional[str] = Query(None, description="Filtrar por etiqueta"),
    db: Session = Depends(get_db)
):
    """Listar contactos con filtros y búsqueda"""
    query = db.query(Contacto)
    
    # Filtro por búsqueda
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Contacto.nombre.ilike(search_filter)) |
            (Contacto.email.ilike(search_filter)) |
            (Contacto.whatsapp.ilike(search_filter))
        )
    
    # Filtro por estado
    if estado:
        query = query.filter(Contacto.estado == estado)
    
    # Filtro por etiqueta
    if etiqueta:
        query = query.filter(Contacto.etiquetas.contains([etiqueta]))
    
    contactos = query.offset(skip).limit(limit).all()
    return contactos


@router.get("/{contacto_id}", response_model=ContactoResponse)
async def get_contacto(
    contacto_id: UUID,
    db: Session = Depends(get_db)
):
    """Obtener un contacto por ID"""
    contacto = db.query(Contacto).filter(Contacto.id == contacto_id).first()
    if not contacto:
        raise HTTPException(status_code=404, detail="Contacto no encontrado")
    return contacto


@router.put("/{contacto_id}", response_model=ContactoResponse)
async def update_contacto(
    contacto_id: UUID,
    contacto_update: ContactoUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar un contacto"""
    contacto = db.query(Contacto).filter(Contacto.id == contacto_id).first()
    if not contacto:
        raise HTTPException(status_code=404, detail="Contacto no encontrado")
    
    # Actualizar solo campos proporcionados
    update_data = contacto_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(contacto, field, value)
    
    db.commit()
    db.refresh(contacto)
    return contacto


@router.delete("/{contacto_id}", status_code=204)
async def delete_contacto(
    contacto_id: UUID,
    db: Session = Depends(get_db)
):
    """Eliminar un contacto"""
    contacto = db.query(Contacto).filter(Contacto.id == contacto_id).first()
    if not contacto:
        raise HTTPException(status_code=404, detail="Contacto no encontrado")
    
    db.delete(contacto)
    db.commit()
    return None


@router.get("/stats/count")
async def get_contactos_stats(
    db: Session = Depends(get_db)
):
    """Obtener estadísticas de contactos"""
    total = db.query(Contacto).count()
    activos = db.query(Contacto).filter(Contacto.estado == "activo").count()
    inactivos = db.query(Contacto).filter(Contacto.estado == "inactivo").count()
    
    return {
        "total": total,
        "activos": activos,
        "inactivos": inactivos
    }
