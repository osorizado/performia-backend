"""
Rutas de objetivos
Endpoints CRUD para gestión de objetivos
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user, require_role
from app.modules.users.models import Usuario
from app.modules.objetivos.schemas import ObjetivoCreate, ObjetivoUpdate, ObjetivoResponse
from app.modules.objetivos import services

router = APIRouter(prefix="/objetivos", tags=["Objetivos"])


@router.get("/", response_model=List[ObjetivoResponse])
def listar_objetivos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    id_usuario: Optional[int] = Query(None),
    periodo: Optional[str] = Query(None),
    estado: Optional[str] = Query(None),
    tipo: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("Administrador", "RRHH", "Manager", "Director"))
):
    """Lista objetivos con filtros"""
    return services.get_objetivos(
        db,
        skip=skip,
        limit=limit,
        id_usuario=id_usuario,
        periodo=periodo,
        estado=estado,
        tipo=tipo
    )


@router.get("/mis-objetivos", response_model=List[ObjetivoResponse])
def mis_objetivos(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtiene los objetivos del usuario actual"""
    return services.get_mis_objetivos(db, current_user.id_usuario)


@router.get("/{objetivo_id}", response_model=ObjetivoResponse)
def obtener_objetivo(
    objetivo_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtiene un objetivo por ID"""
    objetivo = services.get_objetivo_by_id(db, objetivo_id)
    if not objetivo:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Objetivo no encontrado"
        )
    return objetivo


@router.post("/", response_model=ObjetivoResponse)
def crear_objetivo(
    objetivo: ObjetivoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("Administrador", "RRHH", "Manager"))
):
    """Crea un nuevo objetivo"""
    return services.create_objetivo(db, objetivo, current_user.id_usuario)


@router.put("/{objetivo_id}", response_model=ObjetivoResponse)
def actualizar_objetivo(
    objetivo_id: int,
    objetivo_update: ObjetivoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("Administrador", "RRHH", "Manager"))
):
    """Actualiza un objetivo"""
    return services.update_objetivo(db, objetivo_id, objetivo_update)


@router.delete("/{objetivo_id}")
def eliminar_objetivo(
    objetivo_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("Administrador", "RRHH"))
):
    """Elimina un objetivo"""
    return services.delete_objetivo(db, objetivo_id)