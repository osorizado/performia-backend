"""
Servicios de objetivos
Lógica de negocio para gestión de objetivos de desempeño
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import List, Optional
from app.modules.objetivos.models import Objetivo
from app.modules.objetivos.schemas import ObjetivoCreate, ObjetivoUpdate
from datetime import datetime


def get_objetivo_by_id(db: Session, objetivo_id: int) -> Optional[Objetivo]:
    """Obtiene un objetivo por ID"""
    return db.query(Objetivo).filter(Objetivo.id_objetivo == objetivo_id).first()


def get_objetivos(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    id_usuario: Optional[int] = None,
    periodo: Optional[str] = None,
    estado: Optional[str] = None,
    tipo: Optional[str] = None
) -> List[Objetivo]:
    """Obtiene lista de objetivos con filtros"""
    query = db.query(Objetivo)
    
    if id_usuario:
        query = query.filter(Objetivo.id_usuario == id_usuario)
    if periodo:
        query = query.filter(Objetivo.periodo == periodo)
    if estado:
        query = query.filter(Objetivo.estado == estado)
    if tipo:
        query = query.filter(Objetivo.tipo == tipo)
    
    return query.offset(skip).limit(limit).all()


def create_objetivo(
    db: Session,
    objetivo: ObjetivoCreate,
    creado_por_id: int
) -> Objetivo:
    """Crea un nuevo objetivo"""
    
    db_objetivo = Objetivo(
        **objetivo.model_dump(),
        creado_por=creado_por_id
    )
    
    db.add(db_objetivo)
    
    try:
        db.commit()
        db.refresh(db_objetivo)
        return db_objetivo
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al crear el objetivo"
        )


def update_objetivo(
    db: Session,
    objetivo_id: int,
    objetivo_update: ObjetivoUpdate
) -> Objetivo:
    """Actualiza un objetivo"""
    
    db_objetivo = get_objetivo_by_id(db, objetivo_id)
    if not db_objetivo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Objetivo no encontrado"
        )
    
    update_data = objetivo_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_objetivo, field, value)
    
    db_objetivo.fecha_modificacion = datetime.utcnow()
    
    try:
        db.commit()
        db.refresh(db_objetivo)
        return db_objetivo
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al actualizar el objetivo"
        )


def delete_objetivo(db: Session, objetivo_id: int) -> dict:
    """Elimina un objetivo"""
    
    db_objetivo = get_objetivo_by_id(db, objetivo_id)
    if not db_objetivo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Objetivo no encontrado"
        )
    
    db.delete(db_objetivo)
    db.commit()
    
    return {"message": "Objetivo eliminado exitosamente"}


def get_mis_objetivos(db: Session, usuario_id: int) -> List[Objetivo]:
    """Obtiene los objetivos de un usuario"""
    return db.query(Objetivo).filter(
        Objetivo.id_usuario == usuario_id
    ).order_by(Objetivo.fecha_fin).all()