from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.contacto import Contacto, Grupo, GrupoMiembro
from app.models.comunicado import Comunicado, ComunicadoDestinatario
from app.models.log import ComunicadoLog
from app.services.base_provider import WhatsAppProvider, EmailProvider
from app.services.simulated_provider import SimulatedWhatsAppProvider, SimulatedEmailProvider
from app.services.gmail_provider import GmailProvider
from app.services.twilio_provider import TwilioWhatsAppProvider
from app.config import settings


def get_whatsapp_provider() -> WhatsAppProvider:
    """Factory para obtener el provider de WhatsApp según configuración"""
    if settings.WHATSAPP_PROVIDER == "twilio":
        return TwilioWhatsAppProvider()
    else:  # simulated por defecto
        return SimulatedWhatsAppProvider()


def get_email_provider() -> EmailProvider:
    """Factory para obtener el provider de Email según configuración"""
    if settings.EMAIL_PROVIDER == "gmail":
        return GmailProvider()
    else:  # simulated por defecto
        return SimulatedEmailProvider()


def replace_variables(template: str, contacto: Contacto) -> str:
    """
    Reemplaza variables en el template con datos del contacto
    
    Variables disponibles:
    - {{nombre}}
    - {{email}}
    - {{whatsapp}}
    """
    replacements = {
        "{{nombre}}": contacto.nombre or "",
        "{{email}}": contacto.email or "",
        "{{whatsapp}}": contacto.whatsapp or "",
    }
    
    result = template
    for variable, value in replacements.items():
        result = result.replace(variable, value)
    
    return result


async def send_to_contacto(
    contacto: Contacto,
    comunicado: Comunicado,
    tipo_envio: str,
    db: Session
) -> Dict[str, Any]:
    """
    Envía un comunicado a un contacto específico
    
    Args:
        contacto: Contacto destinatario
        comunicado: Comunicado a enviar
        tipo_envio: 'whatsapp' o 'email'
        db: Sesión de base de datos
        
    Returns:
        Dict con resultado del envío
    """
    # Reemplazar variables
    mensaje_final = replace_variables(comunicado.contenido, contacto)
    
    try:
        if tipo_envio == "whatsapp":
            if not contacto.whatsapp:
                raise ValueError(f"Contacto {contacto.nombre} no tiene WhatsApp")
            
            if not settings.WHATSAPP_ENABLED:
                raise ValueError("WhatsApp no está habilitado")
            
            provider = get_whatsapp_provider()
            result = await provider.send_message(contacto.whatsapp, mensaje_final)
            
        elif tipo_envio == "email":
            if not contacto.email:
                raise ValueError(f"Contacto {contacto.nombre} no tiene email")
            
            if not settings.EMAIL_ENABLED:
                raise ValueError("Email no está habilitado")
            
            provider = get_email_provider()
            result = await provider.send_email(
                to=contacto.email,
                subject=comunicado.titulo,
                body=mensaje_final
            )
        else:
            raise ValueError(f"Tipo de envío inválido: {tipo_envio}")
        
        # Registrar en log
        log = ComunicadoLog(
            comunicado_id=comunicado.id,
            contacto_id=contacto.id,
            tipo_comunicado=tipo_envio,
            contenido_enviado=mensaje_final,
            resultado="exitoso" if result["status"] == "success" else "fallido",
            motivo_error=result.get("error"),
            intento=1
        )
        db.add(log)
        db.commit()
        
        return result
        
    except Exception as e:
        # Registrar error en log
        log = ComunicadoLog(
            comunicado_id=comunicado.id,
            contacto_id=contacto.id,
            tipo_comunicado=tipo_envio,
            contenido_enviado=mensaje_final,
            resultado="fallido",
            motivo_error=str(e),
            intento=1
        )
        db.add(log)
        db.commit()
        
        return {
            "status": "error",
            "error": str(e)
        }


async def send_comunicado(comunicado_id: str, db: Session) -> Dict[str, Any]:
    """
    Procesa y envía un comunicado a todos sus destinatarios
    
    Args:
        comunicado_id: ID del comunicado
        db: Sesión de base de datos
        
    Returns:
        Dict con estadísticas del envío
    """
    from uuid import UUID
    
    # Obtener comunicado
    comunicado = db.query(Comunicado).filter(
        Comunicado.id == UUID(comunicado_id)
    ).first()
    
    if not comunicado:
        return {"error": "Comunicado no encontrado"}
    
    # Obtener destinatarios
    destinatarios = db.query(ComunicadoDestinatario).filter(
        ComunicadoDestinatario.comunicado_id == comunicado.id
    ).all()
    
    stats = {
        "total": 0,
        "exitosos": 0,
        "fallidos": 0,
        "tipos": {}
    }
    
    for dest in destinatarios:
        # Obtener contacto (puede ser directo o de un grupo)
        contactos_a_enviar = []
        
        if dest.contacto_id:
            contacto = db.query(Contacto).filter(Contacto.id == dest.contacto_id).first()
            if contacto and contacto.estado == "activo":
                contactos_a_enviar.append(contacto)
        
        elif dest.grupo_id:
            # Obtener todos los contactos del grupo
            miembros = db.query(GrupoMiembro).filter(
                GrupoMiembro.grupo_id == dest.grupo_id
            ).all()
            
            for miembro in miembros:
                contacto = db.query(Contacto).filter(
                    Contacto.id == miembro.contacto_id,
                    Contacto.estado == "activo"
                ).first()
                if contacto:
                    contactos_a_enviar.append(contacto)
        
        # Enviar a cada contacto
        for contacto in contactos_a_enviar:
            stats["total"] += 1
            
            # Determinar tipos de envío
            tipos_envio = []
            if comunicado.tipo == "whatsapp":
                tipos_envio = ["whatsapp"]
            elif comunicado.tipo == "email":
                tipos_envio = ["email"]
            else:  # ambos
                tipos_envio = ["whatsapp", "email"]
            
            # Enviar por cada tipo
            for tipo in tipos_envio:
                try:
                    result = await send_to_contacto(contacto, comunicado, tipo, db)
                    
                    if result["status"] == "success":
                        stats["exitosos"] += 1
                        dest.estado_envio = "enviado"
                    else:
                        stats["fallidos"] += 1
                        dest.intentos_fallidos += 1
                        dest.error_mensaje = result.get("error", "Error desconocido")
                        
                        if dest.intentos_fallidos >= 3:
                            dest.estado_envio = "error"
                        else:
                            dest.estado_envio = "reintentos"
                    
                    dest.fecha_envio = datetime.now()
                    
                    # Actualizar stats por tipo
                    if tipo not in stats["tipos"]:
                        stats["tipos"][tipo] = {"exitosos": 0, "fallidos": 0}
                    
                    if result["status"] == "success":
                        stats["tipos"][tipo]["exitosos"] += 1
                    else:
                        stats["tipos"][tipo]["fallidos"] += 1
                        
                except Exception as e:
                    print(f"Error enviando a {contacto.nombre}: {e}")
                    stats["fallidos"] += 1
                    dest.intentos_fallidos += 1
                    dest.error_mensaje = str(e)
                    dest.estado_envio = "error"
    
    # Actualizar estado del comunicado
    if stats["fallidos"] == 0:
        comunicado.estado = "enviado"
    elif stats["exitosos"] == 0:
        comunicado.estado = "error"
    else:
        comunicado.estado = "parcialmente_enviado"
    
    comunicado.fecha_envio_real = datetime.now()
    
    db.commit()
    
    return stats
