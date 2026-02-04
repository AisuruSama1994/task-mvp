from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.models.contacto import Grupo, GrupoMiembro, Contacto
from app.schemas.contacto import (
    GrupoCreate,
    GrupoUpdate,
    GrupoResponse,
    GrupoConMiembros,
    ContactoResponse
)

router = APIRouter()


@router.post("/", response_model=GrupoResponse, status_code=201)
async def create_grupo(
    grupo: GrupoCreate,
    db: Session = Depends(get_db)
):
    """Crear un nuevo grupo"""
    db_grupo = Grupo(**grupo.model_dump())
    db.add(db_grupo)
    db.commit()
    db.refresh(db_grupo)
    return db_grupo


@router.get("/", response_model=List[GrupoResponse])
async def list_grupos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    tipo: Optional[str] = Query(None, description="Filtrar por tipo: email, whatsapp, ambos"),
    estado: Optional[str] = Query(None, description="Filtrar por estado: activo, inactivo"),
    db: Session = Depends(get_db)
):
    """Listar grupos con filtros"""
    query = db.query(Grupo)
    
    if tipo:
        query = query.filter(Grupo.tipo == tipo)
    
    if estado:
        query = query.filter(Grupo.estado == estado)
    
    grupos = query.offset(skip).limit(limit).all()
    return grupos


@router.get("/{grupo_id}", response_model=GrupoResponse)
async def get_grupo(
    grupo_id: UUID,
    db: Session = Depends(get_db)
):
    """Obtener un grupo por ID"""
    grupo = db.query(Grupo).filter(Grupo.id == grupo_id).first()
    if not grupo:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    return grupo


@router.put("/{grupo_id}", response_model=GrupoResponse)
async def update_grupo(
    grupo_id: UUID,
    grupo_update: GrupoUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar un grupo"""
    grupo = db.query(Grupo).filter(Grupo.id == grupo_id).first()
    if not grupo:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    
    update_data = grupo_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(grupo, field, value)
    
    db.commit()
    db.refresh(grupo)
    return grupo


@router.delete("/{grupo_id}", status_code=204)
async def delete_grupo(
    grupo_id: UUID,
    db: Session = Depends(get_db)
):
    """Eliminar un grupo"""
    grupo = db.query(Grupo).filter(Grupo.id == grupo_id).first()
    if not grupo:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    
    db.delete(grupo)
    db.commit()
    return None


# ============================================
# GESTIÓN DE MIEMBROS
# ============================================

@router.post("/{grupo_id}/miembros/{contacto_id}", status_code=201)
async def add_member(
    grupo_id: UUID,
    contacto_id: UUID,
    db: Session = Depends(get_db)
):
    """Agregar un contacto al grupo"""
    # Verificar que el grupo existe
    grupo = db.query(Grupo).filter(Grupo.id == grupo_id).first()
    if not grupo:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    
    # Verificar que el contacto existe
    contacto = db.query(Contacto).filter(Contacto.id == contacto_id).first()
    if not contacto:
        raise HTTPException(status_code=404, detail="Contacto no encontrado")
    
    # Verificar si ya es miembro
    existing = db.query(GrupoMiembro).filter(
        GrupoMiembro.grupo_id == grupo_id,
        GrupoMiembro.contacto_id == contacto_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="El contacto ya es miembro del grupo")
    
    # Agregar miembro
    miembro = GrupoMiembro(grupo_id=grupo_id, contacto_id=contacto_id)
    db.add(miembro)
    db.commit()
    
    return {
        "message": "Contacto agregado al grupo exitosamente",
        "grupo_id": str(grupo_id),
        "contacto_id": str(contacto_id)
    }


@router.delete("/{grupo_id}/miembros/{contacto_id}", status_code=204)
async def remove_member(
    grupo_id: UUID,
    contacto_id: UUID,
    db: Session = Depends(get_db)
):
    """Remover un contacto del grupo"""
    miembro = db.query(GrupoMiembro).filter(
        GrupoMiembro.grupo_id == grupo_id,
        GrupoMiembro.contacto_id == contacto_id
    ).first()
    
    if not miembro:
        raise HTTPException(status_code=404, detail="El contacto no es miembro del grupo")
    
    db.delete(miembro)
    db.commit()
    return None


@router.get("/{grupo_id}/miembros", response_model=List[ContactoResponse])
async def get_members(
    grupo_id: UUID,
    db: Session = Depends(get_db)
):
    """Obtener todos los miembros de un grupo"""
    grupo = db.query(Grupo).filter(Grupo.id == grupo_id).first()
    if not grupo:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    
    # Obtener miembros
    miembros = db.query(Contacto).join(GrupoMiembro).filter(
        GrupoMiembro.grupo_id == grupo_id
    ).all()
    
    return miembros


@router.get("/{grupo_id}/stats")
async def get_grupo_stats(
    grupo_id: UUID,
    db: Session = Depends(get_db)
):
    """Obtener estadísticas del grupo"""
    grupo = db.query(Grupo).filter(Grupo.id == grupo_id).first()
    if not grupo:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    
    total_miembros = db.query(GrupoMiembro).filter(
        GrupoMiembro.grupo_id == grupo_id
    ).count()
    
    miembros_activos = db.query(GrupoMiembro).join(Contacto).filter(
        GrupoMiembro.grupo_id == grupo_id,
        Contacto.estado == "activo"
    ).count()
    
    return {
        "grupo_id": str(grupo_id),
        "nombre": grupo.nombre,
        "total_miembros": total_miembros,
        "miembros_activos": miembros_activos,
        "miembros_inactivos": total_miembros - miembros_activos
    }
