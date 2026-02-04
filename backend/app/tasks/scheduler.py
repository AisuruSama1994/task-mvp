from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, time as datetime_time
import asyncio

from app.database import SessionLocal
from app.models.comunicado import Comunicado
from app.services.envio_service import send_comunicado
from app.config import settings


# Scheduler global
scheduler = BackgroundScheduler()


def check_scheduled_comunicados():
    """
    Verifica si hay comunicados programados para enviar
    Se ejecuta cada minuto (configurable)
    """
    if not settings.SCHEDULER_ENABLED:
        return
    
    db = SessionLocal()
    
    try:
        now = datetime.now()
        current_date = now.date()
        current_time = now.time()
        
        print(f"🔍 Verificando comunicados programados... {now.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Buscar comunicados programados para hoy que aún no se enviaron
        comunicados = db.query(Comunicado).filter(
            Comunicado.estado == "programado",
            Comunicado.fecha_programada == current_date
        ).all()
        
        for comunicado in comunicados:
            # Verificar si ya es hora de enviar
            if comunicado.hora_programada and comunicado.hora_programada <= current_time:
                print(f"📤 Enviando comunicado: {comunicado.titulo} (ID: {comunicado.id})")
                
                # Enviar comunicado (asyncio para manejar async)
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    stats = loop.run_until_complete(
                        send_comunicado(str(comunicado.id), db)
                    )
                    loop.close()
                    
                    print(f"✅ Comunicado enviado: {stats}")
                    
                except Exception as e:
                    print(f"❌ Error enviando comunicado {comunicado.id}: {e}")
                    comunicado.estado = "error"
                    db.commit()
        
        if not comunicados:
            print("   No hay comunicados programados para enviar ahora")
            
    except Exception as e:
        print(f"❌ Error en scheduler: {e}")
        
    finally:
        db.close()


def start_scheduler():
    """Inicia el scheduler de tareas programadas"""
    if not settings.SCHEDULER_ENABLED:
        print("⚠️ Scheduler deshabilitado en configuración")
        return
    
    print(f"🚀 Iniciando scheduler (intervalo: {settings.SCHEDULER_CHECK_INTERVAL}s)")
    
    # Agregar job que se ejecuta cada X segundos
    scheduler.add_job(
        check_scheduled_comunicados,
        trigger=IntervalTrigger(seconds=settings.SCHEDULER_CHECK_INTERVAL),
        id="check_comunicados",
        name="Verificar comunicados programados",
        replace_existing=True
    )
    
    scheduler.start()
    print("✅ Scheduler iniciado correctamente")


def stop_scheduler():
    """Detiene el scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        print("🛑 Scheduler detenido")
