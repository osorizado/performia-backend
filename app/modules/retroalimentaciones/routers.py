"""
Rutas de retroalimentaciones
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.users.models import Usuario
from app.modules.retroalimentaciones.schemas import (
    RetroalimentacionCreate, RetroalimentacionResponse
)
from app.modules.retroalimentaciones import services

router = APIRouter(prefix="/retroalimentaciones", tags=["Retroalimentaciones"])


@router.get("/", response_model=List[RetroalimentacionResponse])
def listar_retroalimentaciones(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    id_emisor: Optional[int] = Query(None),
    id_receptor: Optional[int] = Query(None),
    id_evaluacion: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista retroalimentaciones"""
    return services.get_retroalimentaciones(
        db,
        skip=skip,
        limit=limit,
        id_emisor=id_emisor,
        id_receptor=id_receptor,
        id_evaluacion=id_evaluacion
    )


@router.get("/mis-retroalimentaciones", response_model=List[RetroalimentacionResponse])
def mis_retroalimentaciones(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtiene las retroalimentaciones recibidas"""
    return services.get_mis_retroalimentaciones(db, current_user.id_usuario)


@router.post("/", response_model=RetroalimentacionResponse)
def crear_retroalimentacion(
    retro: RetroalimentacionCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Crea una nueva retroalimentación"""
    return services.create_retroalimentacion(db, retro, current_user.id_usuario)


@router.post("/{retro_id}/marcar-leida", response_model=RetroalimentacionResponse)
def marcar_leida(
    retro_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Marca una retroalimentación como leída"""
    return services.marcar_como_leida(db, retro_id, current_user.id_usuario)