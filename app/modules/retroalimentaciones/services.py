"""
Servicios de retroalimentaciones
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import List, Optional
from app.modules.retroalimentaciones.models import Retroalimentacion
from app.modules.retroalimentaciones.schemas import RetroalimentacionCreate, RetroalimentacionUpdate
from datetime import datetime


def get_retroalimentacion_by_id(db: Session, retro_id: int) -> Optional[Retroalimentacion]:
    """Obtiene una retroalimentación por ID"""
    return db.query(Retroalimentacion).filter(
        Retroalimentacion.id_retroalimentacion == retro_id
    ).first()


def get_retroalimentaciones(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    id_emisor: Optional[int] = None,
    id_receptor: Optional[int] = None,
    id_evaluacion: Optional[int] = None
) -> List[Retroalimentacion]:
    """Obtiene retroalimentaciones con filtros"""
    query = db.query(Retroalimentacion)
    
    if id_emisor:
        query = query.filter(Retroalimentacion.id_emisor == id_emisor)
    if id_receptor:
        query = query.filter(Retroalimentacion.id_receptor == id_receptor)
    if id_evaluacion:
        query = query.filter(Retroalimentacion.id_evaluacion == id_evaluacion)
    
    return query.offset(skip).limit(limit).all()


def create_retroalimentacion(
    db: Session,
    retro: RetroalimentacionCreate,
    emisor_id: int
) -> Retroalimentacion:
    """Crea una nueva retroalimentación"""
    
    db_retro = Retroalimentacion(
        **retro.model_dump(),
        id_emisor=emisor_id
    )
    
    db.add(db_retro)
    
    try:
        db.commit()
        db.refresh(db_retro)
        return db_retro
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al crear la retroalimentación"
        )


def marcar_como_leida(db: Session, retro_id: int, usuario_id: int) -> Retroalimentacion:
    """Marca una retroalimentación como leída"""
    
    retro = get_retroalimentacion_by_id(db, retro_id)
    if not retro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Retroalimentación no encontrada"
        )
    
    if retro.id_receptor != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para marcar esta retroalimentación"
        )
    
    retro.leido = True
    db.commit()
    db.refresh(retro)
    
    return retro


def get_mis_retroalimentaciones(db: Session, usuario_id: int) -> List[Retroalimentacion]:
    """Obtiene las retroalimentaciones recibidas por un usuario"""
    return db.query(Retroalimentacion).filter(
        Retroalimentacion.id_receptor == usuario_id
    ).order_by(Retroalimentacion.fecha_retroalimentacion.desc()).all()