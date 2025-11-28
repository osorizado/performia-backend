"""
Archivo principal de la aplicación FastAPI
Performia - Sistema de Evaluación de Desempeño
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import Base, engine

# ⚠️ IMPORTANTE: Importar TODOS los modelos para que SQLAlchemy los registre
from app.modules.users.models import Usuario, Rol
from app.modules.formularios.models import Formulario, Pregunta
from app.modules.evaluaciones.models import Evaluacion, Resultado
from app.modules.objetivos.models import Objetivo
from app.modules.retroalimentaciones.models import Retroalimentacion
from app.modules.reportes.models import Reporte, Notificacion, LogAuditoria

# Importar todos los routers
from app.modules.auth.routers import router as auth_router
from app.modules.users.routers import router as users_router
from app.modules.formularios.routers import router as formularios_router
from app.modules.evaluaciones.routers import router as evaluaciones_router
from app.modules.objetivos.routers import router as objetivos_router
from app.modules.retroalimentaciones.routers import router as retroalimentaciones_router

# ✅ CAMBIO: Importar los DOS routers de reportes
from app.modules.reportes import routers as reportes_routers

# Crear aplicación FastAPI (UNA SOLA VEZ)
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API REST para el sistema de evaluación de desempeño Performia",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://127.0.0.1:4200",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Evento de inicio
@app.on_event("startup")
def on_startup():
    """Evento que se ejecuta al iniciar la aplicación"""
    print("\n" + "="*60)
    print(f"🚀 Iniciando {settings.APP_NAME} v{settings.APP_VERSION}")
    print("="*60)
    print(f"📊 Base de datos: {settings.DB_NAME}")
    print(f"🔑 Debug mode: {settings.DEBUG}")
    print("="*60)
    print("✅ Modelos registrados correctamente")
    print("="*60 + "\n")


# Incluir todos los routers
app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(formularios_router, prefix="/api")
app.include_router(evaluaciones_router, prefix="/api")
app.include_router(objetivos_router, prefix="/api")
app.include_router(retroalimentaciones_router, prefix="/api")

# ✅ CAMBIO: Registrar los DOS routers de reportes (notificaciones y reportes)
app.include_router(
    reportes_routers.router_notificaciones,
    prefix="/api",
    tags=["Notificaciones"]
)

app.include_router(
    reportes_routers.router_reportes,
    prefix="/api",
    tags=["Reportes"]
)


# Endpoint raíz
@app.get("/")
def root():
    """Endpoint raíz - Información de la API"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }


# Endpoint de salud
@app.get("/health")
def health_check():
    """Endpoint para verificar el estado de la API"""
    return {
        "status": "healthy",
        "database": settings.DB_NAME,
        "version": settings.APP_VERSION
    }


# Manejador de errores global
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Manejador global de excepciones"""
    import traceback
    error_trace = traceback.format_exc()
    print(f"\n❌ Error no manejado:")
    print(error_trace)
    
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=500,
        content={
            "detail": str(exc),
            "type": type(exc).__name__,
            "trace": error_trace if settings.DEBUG else None
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )