"""
Configuración de la base de datos con SQLAlchemy
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from app.core.config import settings

# Crear engine de SQLAlchemy
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Mostrar SQL en consola si DEBUG=True
    pool_pre_ping=True,   # Verificar conexión antes de usar
    pool_recycle=3600,    # Reciclar conexiones cada hora
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base para los modelos
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependencia para obtener una sesión de base de datos
    Se usa en FastAPI con Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Inicializa la base de datos
    Crea todas las tablas si no existen
    """
    Base.metadata.create_all(bind=engine)