"""
Servicios de usuarios
Lógica de negocio para gestión de usuarios y roles
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from fastapi import HTTPException, status
from typing import List, Optional
from app.modules.users.models import Usuario, Rol
from app.modules.users.schemas import UsuarioCreate, UsuarioUpdate, RolCreate, RolUpdate
from app.modules.users.schemas import UsuarioResponse

from app.core.security import get_password_hash
from datetime import datetime


# ============================================================================
# SERVICIOS DE ROLES
# ============================================================================

def get_rol_by_id(db: Session, rol_id: int) -> Optional[Rol]:
    """Obtiene un rol por ID"""
    return db.query(Rol).filter(Rol.id_rol == rol_id).first()


def get_rol_by_nombre(db: Session, nombre_rol: str) -> Optional[Rol]:
    """Obtiene un rol por nombre"""
    return db.query(Rol).filter(Rol.nombre_rol == nombre_rol).first()


def get_roles(db: Session, skip: int = 0, limit: int = 100) -> List[Rol]:
    """Obtiene lista de roles con paginación"""
    return db.query(Rol).offset(skip).limit(limit).all()


def create_rol(db: Session, rol: RolCreate) -> Rol:
    """Crea un nuevo rol"""
    # Verificar que no exista un rol con el mismo nombre
    existing_rol = get_rol_by_nombre(db, rol.nombre_rol)
    if existing_rol:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un rol con el nombre '{rol.nombre_rol}'"
        )
    
    db_rol = Rol(**rol.model_dump())
    db.add(db_rol)
    
    try:
        db.commit()
        db.refresh(db_rol)
        return db_rol
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al crear el rol"
        )


def update_rol(db: Session, rol_id: int, rol_update: RolUpdate) -> Rol:
    """Actualiza un rol existente"""
    db_rol = get_rol_by_id(db, rol_id)
    if not db_rol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol no encontrado"
        )
    
    # Actualizar solo los campos proporcionados
    update_data = rol_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_rol, field, value)
    
    db_rol.fecha_modificacion = datetime.utcnow()
    
    try:
        db.commit()
        db.refresh(db_rol)
        return db_rol
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al actualizar el rol"
        )


def delete_rol(db: Session, rol_id: int) -> dict:
    """Elimina un rol (soft delete cambiando estado a Inactivo)"""
    db_rol = get_rol_by_id(db, rol_id)
    if not db_rol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol no encontrado"
        )
    
    # Verificar que no haya usuarios con este rol
    usuarios_count = db.query(Usuario).filter(Usuario.id_rol == rol_id).count()
    if usuarios_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede eliminar el rol porque tiene {usuarios_count} usuario(s) asociado(s)"
        )
    
    db_rol.estado = "Inactivo"
    db_rol.fecha_modificacion = datetime.utcnow()
    db.commit()
    
    return {"message": "Rol eliminado exitosamente"}


# ============================================================================
# SERVICIOS DE USUARIOS
# ============================================================================

def get_usuario_by_id(db: Session, usuario_id: int) -> Optional[Usuario]:
    """Obtiene un usuario por ID"""
    return db.query(Usuario).filter(Usuario.id_usuario == usuario_id).first()


def get_usuario_by_correo(db: Session, correo: str) -> Optional[Usuario]:
    """Obtiene un usuario por correo"""
    return db.query(Usuario).filter(Usuario.correo == correo).first()


def get_usuarios(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    rol_id: Optional[int] = None,
    area: Optional[str] = None,
    estado: Optional[str] = None
) -> List[UsuarioResponse]:
    """
    Obtiene lista de usuarios con filtros opcionales
    e incluye el nombre completo del manager.
    """
    
    query = db.query(Usuario).options(
        joinedload(Usuario.manager)  # ⭐ carga el manager en la misma consulta
    )
    
    if rol_id:
        query = query.filter(Usuario.id_rol == rol_id)
    if area:
        query = query.filter(Usuario.area == area)
    if estado:
        query = query.filter(Usuario.estado == estado)
    
    usuarios = query.offset(skip).limit(limit).all()

    # ⭐ Construimos la respuesta incluyendo manager_nombre
    usuarios_out = []
    for u in usuarios:
        manager_nombre = None
        if u.manager:
            manager_nombre = f"{u.manager.nombre} {u.manager.apellido}"

        usuarios_out.append(
            UsuarioResponse(
                **u.__dict__,
                manager_nombre=manager_nombre
            )
        )

    return usuarios_out


def create_usuario(db: Session, usuario: UsuarioCreate, creado_por_id: int) -> Usuario:
    """Crea un nuevo usuario"""
    # Verificar que no exista un usuario con el mismo correo
    existing_usuario = get_usuario_by_correo(db, usuario.correo)
    if existing_usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un usuario con el correo '{usuario.correo}'"
        )
    
    # Verificar que el rol exista
    rol = get_rol_by_id(db, usuario.id_rol)
    if not rol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol no encontrado"
        )
    
    # Si tiene manager, verificar que exista
    if usuario.manager_id:
        manager = get_usuario_by_id(db, usuario.manager_id)
        if not manager:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Manager no encontrado"
            )
    
    # Hashear la contraseña
    hashed_password = get_password_hash(usuario.password)
    
    # Crear usuario
    usuario_data = usuario.model_dump(exclude={'password'})
    db_usuario = Usuario(
        **usuario_data,
        password_hash=hashed_password
    )
    
    db.add(db_usuario)
    
    try:
        db.commit()
        db.refresh(db_usuario)
        return db_usuario
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al crear el usuario"
        )


def update_usuario(db: Session, usuario_id: int, usuario_update: UsuarioUpdate) -> Usuario:
    """Actualiza un usuario existente"""
    db_usuario = get_usuario_by_id(db, usuario_id)
    if not db_usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Actualizar solo los campos proporcionados
    update_data = usuario_update.model_dump(exclude_unset=True)
    
    # Si se actualiza el correo, verificar que no exista otro usuario con ese correo
    if "correo" in update_data:
        existing = get_usuario_by_correo(db, update_data["correo"])
        if existing and existing.id_usuario != usuario_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un usuario con el correo '{update_data['correo']}'"
            )
    
    # Si se actualiza el rol, verificar que exista
    if "id_rol" in update_data:
        rol = get_rol_by_id(db, update_data["id_rol"])
        if not rol:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rol no encontrado"
            )
    
    # Si se actualiza el manager, verificar que exista
    if "manager_id" in update_data and update_data["manager_id"]:
        manager = get_usuario_by_id(db, update_data["manager_id"])
        if not manager:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Manager no encontrado"
            )
    
    for field, value in update_data.items():
        setattr(db_usuario, field, value)
    
    db_usuario.fecha_modificacion = datetime.utcnow()
    
    try:
        db.commit()
        db.refresh(db_usuario)
        return db_usuario
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al actualizar el usuario"
        )


def delete_usuario(db: Session, usuario_id: int) -> dict:
    """Elimina un usuario (soft delete cambiando estado a Inactivo)"""
    db_usuario = get_usuario_by_id(db, usuario_id)
    if not db_usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    db_usuario.estado = "Inactivo"
    db_usuario.fecha_modificacion = datetime.utcnow()
    db.commit()
    
    return {"message": "Usuario eliminado exitosamente"}


def get_subordinados(db: Session, manager_id: int) -> List[Usuario]:
    """Obtiene la lista de subordinados de un manager"""
    return db.query(Usuario).filter(Usuario.manager_id == manager_id).all()


def get_usuarios_by_area(db: Session, area: str) -> List[Usuario]:
    """Obtiene todos los usuarios de un área"""
    return db.query(Usuario).filter(Usuario.area == area).all()