from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
from uuid import UUID

from app.database import get_db
from app.models.tarea import Tarea, TareaLog
from app.schemas.tarea import (
    TareaCreate,
    TareaUpdate,
    TareaResponse,
    TareaConUrgencia,
    TareaLogResponse,
    CambioEstadoTarea
)

router = APIRouter()


def calcular_urgencia(tarea: Tarea) -> dict:
    """Calcula días restantes y nivel de urgencia de una tarea"""
    if not tarea.fecha_termino:
        return {
            "dias_restantes": None,
            "urgencia": "sin_fecha"
        }
    
    hoy = date.today()
    dias_restantes = (tarea.fecha_termino - hoy).days
    
    if dias_restantes < 0:
        urgencia = "vencida"
    elif dias_restantes == 0:
        urgencia = "hoy"
    elif dias_restantes <= 3:
        urgencia = "urgente"
    else:
        urgencia = "normal"
    
    return {
        "dias_restantes": dias_restantes,
        "urgencia": urgencia
    }


@router.post("/", response_model=TareaResponse, status_code=201)
async def create_tarea(
    tarea: TareaCreate,
    db: Session = Depends(get_db)
):
    """Crear una nueva tarea"""
    db_tarea = Tarea(**tarea.model_dump())
    db.add(db_tarea)
    db.commit()
    db.refresh(db_tarea)
    
    # Registrar en log
    log = TareaLog(
        tarea_id=db_tarea.id,
        accion="creada",
        datos_nuevos=tarea.model_dump(mode='json'),
        usuario="sistema"
    )
    db.add(log)
    db.commit()
    
    return db_tarea


@router.get("/", response_model=List[TareaResponse])
async def list_tareas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    prioridad: Optional[str] = Query(None, description="Filtrar por prioridad"),
    etiqueta: Optional[str] = Query(None, description="Filtrar por etiqueta"),
    db: Session = Depends(get_db)
):
    """Listar tareas con filtros"""
    query = db.query(Tarea)
    
    if estado:
        query = query.filter(Tarea.estado == estado)
    
    if prioridad:
        query = query.filter(Tarea.prioridad == prioridad)
    
    if etiqueta:
        query = query.filter(Tarea.etiquetas.contains([etiqueta]))
    
    # Ordenar por prioridad y fecha
    query = query.order_by(
        Tarea.fecha_termino.asc().nullslast(),
        Tarea.prioridad.desc()
    )
    
    tareas = query.offset(skip).limit(limit).all()
    return tareas


@router.get("/con-urgencia", response_model=List[TareaConUrgencia])
async def list_tareas_con_urgencia(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    estado: Optional[str] = Query(None),
    prioridad: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Listar tareas con cálculo de urgencia"""
    query = db.query(Tarea)
    
    if estado:
        query = query.filter(Tarea.estado == estado)
    
    if prioridad:
        query = query.filter(Tarea.prioridad == prioridad)
    
    query = query.order_by(
        Tarea.fecha_termino.asc().nullslast(),
        Tarea.prioridad.desc()
    )
    
    tareas = query.offset(skip).limit(limit).all()
    
    # Agregar cálculo de urgencia
    result = []
    for tarea in tareas:
        tarea_dict = TareaResponse.model_validate(tarea).model_dump()
        urgencia_data = calcular_urgencia(tarea)
        tarea_dict.update(urgencia_data)
        result.append(TareaConUrgencia(**tarea_dict))
    
    return result


@router.get("/{tarea_id}", response_model=TareaResponse)
async def get_tarea(
    tarea_id: UUID,
    db: Session = Depends(get_db)
):
    """Obtener una tarea por ID"""
    tarea = db.query(Tarea).filter(Tarea.id == tarea_id).first()
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return tarea


@router.put("/{tarea_id}", response_model=TareaResponse)
async def update_tarea(
    tarea_id: UUID,
    tarea_update: TareaUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar una tarea"""
    tarea = db.query(Tarea).filter(Tarea.id == tarea_id).first()
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    # Guardar datos anteriores para log
    datos_anteriores = TareaResponse.model_validate(tarea).model_dump(mode='json')
    
    # Actualizar campos
    update_data = tarea_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tarea, field, value)
    
    db.commit()
    db.refresh(tarea)
    
    # Registrar en log
    datos_nuevos = TareaResponse.model_validate(tarea).model_dump(mode='json')
    log = TareaLog(
        tarea_id=tarea.id,
        accion="actualizada",
        datos_anteriores=datos_anteriores,
        datos_nuevos=datos_nuevos,
        usuario="sistema"
    )
    db.add(log)
    db.commit()
    
    return tarea


@router.delete("/{tarea_id}", status_code=204)
async def delete_tarea(
    tarea_id: UUID,
    db: Session = Depends(get_db)
):
    """Eliminar una tarea"""
    tarea = db.query(Tarea).filter(Tarea.id == tarea_id).first()
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    db.delete(tarea)
    db.commit()
    return None


# ============================================
# GESTIÓN DE ESTADO
# ============================================

@router.put("/{tarea_id}/estado", response_model=TareaResponse)
async def change_estado(
    tarea_id: UUID,
    cambio: CambioEstadoTarea,
    db: Session = Depends(get_db)
):
    """Cambiar el estado de una tarea"""
    tarea = db.query(Tarea).filter(Tarea.id == tarea_id).first()
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    estado_anterior = tarea.estado
    tarea.estado = cambio.nuevo_estado
    
    # Si se completa, registrar fecha
    if cambio.nuevo_estado == "completada" and not tarea.fecha_completacion:
        tarea.fecha_completacion = datetime.now()
    
    db.commit()
    db.refresh(tarea)
    
    # Registrar en log
    log = TareaLog(
        tarea_id=tarea.id,
        accion="estado_cambio",
        datos_anteriores={"estado": estado_anterior},
        datos_nuevos={"estado": cambio.nuevo_estado},
        usuario=cambio.usuario or "sistema"
    )
    db.add(log)
    db.commit()
    
    return tarea


@router.get("/{tarea_id}/historial", response_model=List[TareaLogResponse])
async def get_historial(
    tarea_id: UUID,
    db: Session = Depends(get_db)
):
    """Obtener historial de cambios de una tarea"""
    tarea = db.query(Tarea).filter(Tarea.id == tarea_id).first()
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    logs = db.query(TareaLog).filter(
        TareaLog.tarea_id == tarea_id
    ).order_by(TareaLog.fecha_cambio.desc()).all()
    
    return logs


# ============================================
# ESTADÍSTICAS
# ============================================

@router.get("/stats/dashboard")
async def get_dashboard_stats(
    db: Session = Depends(get_db)
):
    """Obtener estadísticas para dashboard"""
    hoy = date.today()
    
    # Tareas pendientes
    pendientes = db.query(Tarea).filter(
        Tarea.estado == "pendiente"
    ).count()
    
    # Tareas completadas hoy
    completadas_hoy = db.query(Tarea).filter(
        Tarea.fecha_completacion >= datetime.combine(hoy, datetime.min.time())
    ).count()
    
    # Tareas próximas a vencer (< 3 días)
    from datetime import timedelta
    proximas_vencer = db.query(Tarea).filter(
        Tarea.estado.in_(["pendiente", "en_progreso"]),
        Tarea.fecha_termino.isnot(None),
        Tarea.fecha_termino <= hoy + timedelta(days=3)
    ).count()
    
    # Tareas vencidas
    vencidas = db.query(Tarea).filter(
        Tarea.estado.in_(["pendiente", "en_progreso"]),
        Tarea.fecha_termino.isnot(None),
        Tarea.fecha_termino < hoy
    ).count()
    
    # Por prioridad
    por_prioridad = {}
    for prioridad in ["baja", "media", "alta", "urgente"]:
        count = db.query(Tarea).filter(
            Tarea.prioridad == prioridad,
            Tarea.estado.in_(["pendiente", "en_progreso"])
        ).count()
        por_prioridad[prioridad] = count
    
    return {
        "pendientes": pendientes,
        "completadas_hoy": completadas_hoy,
        "proximas_vencer": proximas_vencer,
        "vencidas": vencidas,
        "por_prioridad": por_prioridad
    }
