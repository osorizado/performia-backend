"""
Rutas de usuarios
SOLO ENDPOINTS - Los modelos están en models.py
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.modules.users.models import Usuario, Rol
from app.modules.users.schemas import UsuarioResponse, UsuarioUpdate
from app.modules.auth.dependencies import get_current_user, require_role

router = APIRouter(prefix="/users", tags=["Usuarios"])


@router.get("/", response_model=List[UsuarioResponse])
def get_all_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("Administrador", "RRHH"))
):
    """
    Obtiene todos los usuarios (solo admin y RRHH)
    """
    usuarios = db.query(Usuario).offset(skip).limit(limit).all()
    return usuarios


@router.get("/{user_id}", response_model=UsuarioResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtiene un usuario por ID
    """
    usuario = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return usuario


@router.put("/{user_id}", response_model=UsuarioResponse)
def update_user(
    user_id: int,
    user_data: UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Actualiza un usuario
    """
    usuario = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Solo admin puede actualizar otros usuarios
    if current_user.id_usuario != user_id and current_user.rol.nombre_rol != "Administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para actualizar este usuario"
        )
    
    # Actualizar campos
    for field, value in user_data.dict(exclude_unset=True).items():
        setattr(usuario, field, value)
    
    db.commit()
    db.refresh(usuario)
    return usuario


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("Administrador"))
):
    """
    Elimina un usuario (solo admin)
    """
    usuario = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    db.delete(usuario)
    db.commit()
    return {"message": "Usuario eliminado exitosamente"}


@router.get("/roles/", response_model=List[dict])
def get_all_roles(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtiene todos los roles
    """
    roles = db.query(Rol).all()
    return [{"id_rol": r.id_rol, "nombre_rol": r.nombre_rol} for r in roles]