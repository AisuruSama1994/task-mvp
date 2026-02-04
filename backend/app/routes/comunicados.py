from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date, time as datetime_time
from uuid import UUID

from app.database import get_db
from app.models.comunicado import Comunicado, ComunicadoDestinatario
from app.models.contacto import Contacto, Grupo, GrupoMiembro
from app.models.log import ComunicadoLog
from app.schemas.comunicado import (
    ComunicadoCreate,
    ComunicadoUpdate,
    ComunicadoResponse,
    VistaPreviaResponse,
    VistaPreviaItem,
    ProgramarEnvio,
    EstadisticasEnvio,
    ComunicadoLogResponse
)
from app.services.envio_service import replace_variables, send_comunicado

router = APIRouter()


@router.post("/", response_model=ComunicadoResponse, status_code=201)
async def create_comunicado(
    comunicado: ComunicadoCreate,
    db: Session = Depends(get_db)
):
    """Crear un nuevo comunicado (borrador)"""
    # Crear comunicado
    comunicado_data = comunicado.model_dump(exclude={'destinatarios_contactos', 'destinatarios_grupos'})
    db_comunicado = Comunicado(**comunicado_data)
    db.add(db_comunicado)
    db.commit()
    db.refresh(db_comunicado)
    
    # Agregar destinatarios (contactos individuales)
    for contacto_id in comunicado.destinatarios_contactos:
        destinatario = ComunicadoDestinatario(
            comunicado_id=db_comunicado.id,
            contacto_id=contacto_id
        )
        db.add(destinatario)
    
    # Agregar destinatarios (grupos)
    for grupo_id in comunicado.destinatarios_grupos:
        destinatario = ComunicadoDestinatario(
            comunicado_id=db_comunicado.id,
            grupo_id=grupo_id
        )
        db.add(destinatario)
    
    db.commit()
    db.refresh(db_comunicado)
    
    return db_comunicado


@router.get("/", response_model=List[ComunicadoResponse])
async def list_comunicados(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    tipo: Optional[str] = Query(None, description="Filtrar por tipo"),
    db: Session = Depends(get_db)
):
    """Listar comunicados con filtros"""
    query = db.query(Comunicado)
    
    if estado:
        query = query.filter(Comunicado.estado == estado)
    
    if tipo:
        query = query.filter(Comunicado.tipo == tipo)
    
    query = query.order_by(Comunicado.creado_en.desc())
    
    comunicados = query.offset(skip).limit(limit).all()
    return comunicados


@router.get("/{comunicado_id}", response_model=ComunicadoResponse)
async def get_comunicado(
    comunicado_id: UUID,
    db: Session = Depends(get_db)
):
    """Obtener un comunicado por ID"""
    comunicado = db.query(Comunicado).filter(Comunicado.id == comunicado_id).first()
    if not comunicado:
        raise HTTPException(status_code=404, detail="Comunicado no encontrado")
    return comunicado


@router.put("/{comunicado_id}", response_model=ComunicadoResponse)
async def update_comunicado(
    comunicado_id: UUID,
    comunicado_update: ComunicadoUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar un comunicado (solo si es borrador)"""
    comunicado = db.query(Comunicado).filter(Comunicado.id == comunicado_id).first()
    if not comunicado:
        raise HTTPException(status_code=404, detail="Comunicado no encontrado")
    
    if comunicado.estado != "borrador":
        raise HTTPException(
            status_code=400,
            detail="Solo se pueden editar comunicados en estado borrador"
        )
    
    update_data = comunicado_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(comunicado, field, value)
    
    db.commit()
    db.refresh(comunicado)
    return comunicado


@router.delete("/{comunicado_id}", status_code=204)
async def delete_comunicado(
    comunicado_id: UUID,
    db: Session = Depends(get_db)
):
    """Eliminar un comunicado (solo si es borrador)"""
    comunicado = db.query(Comunicado).filter(Comunicado.id == comunicado_id).first()
    if not comunicado:
        raise HTTPException(status_code=404, detail="Comunicado no encontrado")
    
    if comunicado.estado != "borrador":
        raise HTTPException(
            status_code=400,
            detail="Solo se pueden eliminar comunicados en estado borrador"
        )
    
    db.delete(comunicado)
    db.commit()
    return None


# ============================================
# VISTA PREVIA
# ============================================

@router.post("/{comunicado_id}/vista-previa", response_model=VistaPreviaResponse)
async def preview_comunicado(
    comunicado_id: UUID,
    db: Session = Depends(get_db)
):
    """Generar vista previa del comunicado con variables reemplazadas"""
    comunicado = db.query(Comunicado).filter(Comunicado.id == comunicado_id).first()
    if not comunicado:
        raise HTTPException(status_code=404, detail="Comunicado no encontrado")
    
    # Obtener destinatarios
    destinatarios = db.query(ComunicadoDestinatario).filter(
        ComunicadoDestinatario.comunicado_id == comunicado_id
    ).all()
    
    # Expandir contactos (incluir grupos)
    contactos_preview = []
    for dest in destinatarios[:3]:  # Máximo 3 para preview
        if dest.contacto_id:
            contacto = db.query(Contacto).filter(Contacto.id == dest.contacto_id).first()
            if contacto:
                contactos_preview.append(contacto)
        elif dest.grupo_id:
            # Tomar primer miembro del grupo
            miembro = db.query(GrupoMiembro).filter(
                GrupoMiembro.grupo_id == dest.grupo_id
            ).first()
            if miembro:
                contacto = db.query(Contacto).filter(Contacto.id == miembro.contacto_id).first()
                if contacto:
                    contactos_preview.append(contacto)
    
    # Generar previews
    previews = []
    for contacto in contactos_preview[:4]:  # Máximo 4 previews
        mensaje_final = replace_variables(comunicado.contenido, contacto)
        previews.append(VistaPreviaItem(
            contacto_nombre=contacto.nombre,
            contacto_email=contacto.email,
            contacto_whatsapp=contacto.whatsapp,
            mensaje_final=mensaje_final
        ))
    
    # Contar total de destinatarios
    total = 0
    for dest in destinatarios:
        if dest.contacto_id:
            total += 1
        elif dest.grupo_id:
            count = db.query(GrupoMiembro).filter(
                GrupoMiembro.grupo_id == dest.grupo_id
            ).count()
            total += count
    
    return VistaPreviaResponse(
        comunicado_id=comunicado_id,
        titulo=comunicado.titulo,
        tipo=comunicado.tipo,
        total_destinatarios=total,
        previews=previews
    )


# ============================================
# PROGRAMAR Y ENVIAR
# ============================================

@router.post("/{comunicado_id}/programar", response_model=ComunicadoResponse)
async def programar_envio(
    comunicado_id: UUID,
    programacion: ProgramarEnvio,
    db: Session = Depends(get_db)
):
    """Programar un comunicado para envío futuro"""
    comunicado = db.query(Comunicado).filter(Comunicado.id == comunicado_id).first()
    if not comunicado:
        raise HTTPException(status_code=404, detail="Comunicado no encontrado")
    
    if comunicado.estado not in ["borrador", "programado"]:
        raise HTTPException(
            status_code=400,
            detail="Solo se pueden programar comunicados en estado borrador"
        )
    
    # Validar que la fecha/hora sea futura
    ahora = datetime.now()
    fecha_hora_programada = datetime.combine(programacion.fecha_programada, programacion.hora_programada)
    
    if fecha_hora_programada <= ahora:
        raise HTTPException(
            status_code=400,
            detail="La fecha y hora programada debe ser futura"
        )
    
    # Actualizar comunicado
    comunicado.fecha_programada = programacion.fecha_programada
    comunicado.hora_programada = programacion.hora_programada
    comunicado.estado = "programado"
    
    db.commit()
    db.refresh(comunicado)
    
    return comunicado


@router.post("/{comunicado_id}/enviar-ahora")
async def enviar_ahora(
    comunicado_id: UUID,
    db: Session = Depends(get_db)
):
    """Enviar un comunicado inmediatamente"""
    comunicado = db.query(Comunicado).filter(Comunicado.id == comunicado_id).first()
    if not comunicado:
        raise HTTPException(status_code=404, detail="Comunicado no encontrado")
    
    if comunicado.estado not in ["borrador", "programado"]:
        raise HTTPException(
            status_code=400,
            detail="Este comunicado ya fue enviado"
        )
    
    # Enviar
    stats = await send_comunicado(str(comunicado_id), db)
    
    return {
        "message": "Comunicado enviado",
        "comunicado_id": str(comunicado_id),
        "stats": stats
    }


# ============================================
# ESTADO Y LOGS
# ============================================

@router.get("/{comunicado_id}/estado-envios")
async def get_estado_envios(
    comunicado_id: UUID,
    db: Session = Depends(get_db)
):
    """Ver estado de envío para cada destinatario"""
    comunicado = db.query(Comunicado).filter(Comunicado.id == comunicado_id).first()
    if not comunicado:
        raise HTTPException(status_code=404, detail="Comunicado no encontrado")
    
    destinatarios = db.query(ComunicadoDestinatario).filter(
        ComunicadoDestinatario.comunicado_id == comunicado_id
    ).all()
    
    result = []
    for dest in destinatarios:
        contacto_info = None
        if dest.contacto_id:
            contacto = db.query(Contacto).filter(Contacto.id == dest.contacto_id).first()
            if contacto:
                contacto_info = {
                    "tipo": "contacto",
                    "nombre": contacto.nombre,
                    "email": contacto.email,
                    "whatsapp": contacto.whatsapp
                }
        elif dest.grupo_id:
            grupo = db.query(Grupo).filter(Grupo.id == dest.grupo_id).first()
            if grupo:
                contacto_info = {
                    "tipo": "grupo",
                    "nombre": grupo.nombre
                }
        
        result.append({
            "destinatario": contacto_info,
            "estado_envio": dest.estado_envio,
            "intentos_fallidos": dest.intentos_fallidos,
            "error_mensaje": dest.error_mensaje,
            "fecha_envio": dest.fecha_envio
        })
    
    return result


@router.get("/{comunicado_id}/log", response_model=List[ComunicadoLogResponse])
async def get_log(
    comunicado_id: UUID,
    db: Session = Depends(get_db)
):
    """Obtener historial de envíos del comunicado"""
    comunicado = db.query(Comunicado).filter(Comunicado.id == comunicado_id).first()
    if not comunicado:
        raise HTTPException(status_code=404, detail="Comunicado no encontrado")
    
    logs = db.query(ComunicadoLog).filter(
        ComunicadoLog.comunicado_id == comunicado_id
    ).order_by(ComunicadoLog.fecha_envio.desc()).all()
    
    return logs


@router.get("/{comunicado_id}/estadisticas", response_model=EstadisticasEnvio)
async def get_estadisticas(
    comunicado_id: UUID,
    db: Session = Depends(get_db)
):
    """Obtener estadísticas de envío del comunicado"""
    comunicado = db.query(Comunicado).filter(Comunicado.id == comunicado_id).first()
    if not comunicado:
        raise HTTPException(status_code=404, detail="Comunicado no encontrado")
    
    destinatarios = db.query(ComunicadoDestinatario).filter(
        ComunicadoDestinatario.comunicado_id == comunicado_id
    ).all()
    
    total = len(destinatarios)
    enviados = sum(1 for d in destinatarios if d.estado_envio == "enviado")
    errores = sum(1 for d in destinatarios if d.estado_envio == "error")
    pendientes = sum(1 for d in destinatarios if d.estado_envio == "pendiente")
    
    porcentaje_exito = (enviados / total * 100) if total > 0 else 0
    
    return EstadisticasEnvio(
        comunicado_id=comunicado_id,
        titulo=comunicado.titulo,
        total_destinatarios=total,
        enviados=enviados,
        errores=errores,
        pendientes=pendientes,
        porcentaje_exito=round(porcentaje_exito, 2)
    )
