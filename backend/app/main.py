from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.tasks.scheduler import start_scheduler, stop_scheduler

# Importar routers
from app.routes import contactos, grupos, tareas, comunicados

app = FastAPI(
    title="Sistema de Recordatorios",
    description="API para gestión de tareas y envío de recordatorios por WhatsApp y Email",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Ejecutar al iniciar la aplicación"""
    print("\n" + "="*60)
    print("🚀 Iniciando Sistema de Recordatorios")
    print("="*60)
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"WhatsApp Provider: {settings.WHATSAPP_PROVIDER}")
    print(f"Email Provider: {settings.EMAIL_PROVIDER}")
    print(f"Scheduler: {'Enabled' if settings.SCHEDULER_ENABLED else 'Disabled'}")
    print("="*60 + "\n")
    
    # Iniciar scheduler
    start_scheduler()


@app.on_event("shutdown")
async def shutdown_event():
    """Ejecutar al cerrar la aplicación"""
    print("\n🛑 Cerrando Sistema de Recordatorios...")
    stop_scheduler()


@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "Sistema de Recordatorios API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running",
        "providers": {
            "whatsapp": settings.WHATSAPP_PROVIDER,
            "email": settings.EMAIL_PROVIDER
        }
    }


@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "scheduler": settings.SCHEDULER_ENABLED
    }


# Incluir routers
app.include_router(contactos.router, prefix="/api/contactos", tags=["Contactos"])
app.include_router(grupos.router, prefix="/api/grupos", tags=["Grupos"])
app.include_router(tareas.router, prefix="/api/tareas", tags=["Tareas"])
app.include_router(comunicados.router, prefix="/api/comunicados", tags=["Comunicados"])



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
