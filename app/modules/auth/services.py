"""
Servicios de autenticación
Lógica de negocio para login, registro y manejo de sesiones
"""
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import secrets

from app.modules.users.models import Usuario
from app.core.security import verify_password, create_access_token, get_password_hash
from app.modules.auth.schemas import RegisterRequest


def authenticate_user(db: Session, correo: str, password: str) -> Usuario | None:
    """
    Autentica un usuario verificando email y contraseña
    """
    usuario = db.query(Usuario).filter(Usuario.correo == correo).first()
    
    if not usuario:
        return None
    
    if not verify_password(password, usuario.password_hash):
        return None
    
    # Actualizar último acceso
    usuario.ultimo_acceso = datetime.utcnow()
    db.commit()
    
    return usuario


def create_user_token(usuario: Usuario) -> str:
    """
    Crea un token JWT para un usuario
    """
    token_data = {
        "sub": str(usuario.id_usuario),
        "correo": usuario.correo,
        "rol": usuario.rol.nombre_rol
    }
    
    access_token = create_access_token(data=token_data)
    
    return access_token


# ============================================
# SERVICIOS DE REGISTRO
# ============================================

def check_email_exists(db: Session, email: str) -> bool:
    """
    Verifica si un email ya está registrado
    """
    usuario = db.query(Usuario).filter(Usuario.correo == email).first()
    return usuario is not None


def create_user(db: Session, user_data: RegisterRequest) -> Usuario:
    """
    Crea un nuevo usuario en la base de datos
    """
    # Hashear contraseña
    password_hash = get_password_hash(user_data.password)
    
    # Generar token de confirmación
    token_confirmacion = secrets.token_urlsafe(32)
    
    # Crear usuario con los campos correctos
    nuevo_usuario = Usuario(
        nombre=user_data.nombre,
        apellido=user_data.apellido,
        correo=user_data.email,
        telefono=user_data.telefono,
        password_hash=password_hash,
        cargo=user_data.puesto,           # puesto -> cargo
        area=user_data.area,              # área como texto
        id_rol=user_data.id_rol,
        estado="Activo",                  # Activo directamente (o "Pendiente" si usas confirmación)
        token_confirmacion=token_confirmacion,
        correo_confirmado=False,
        fecha_creacion=datetime.utcnow(),
        fecha_ingreso=datetime.utcnow().date()
    )
    
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    
    return nuevo_usuario


def confirm_user_email(db: Session, token: str) -> Optional[Usuario]:
    """
    Confirma el correo de un usuario usando el token
    """
    usuario = db.query(Usuario).filter(
        Usuario.token_confirmacion == token
    ).first()
    
    if not usuario:
        return None
    
    # Activar usuario
    usuario.estado = "Activo"  # ✅ Cambiar a Activo
    usuario.token_confirmacion = None
    usuario.correo_confirmado = True
    usuario.fecha_modificacion = datetime.utcnow()
    
    db.commit()
    db.refresh(usuario)
    
    return usuario

def regenerate_confirmation_token(db: Session, email: str) -> Optional[str]:
    """
    Regenera el token de confirmación para un usuario
    """
    usuario = db.query(Usuario).filter(Usuario.correo == email).first()
    
    if not usuario:
        return None
    
    if usuario.estado == "Activo":
        return None
    
    nuevo_token = secrets.token_urlsafe(32)
    usuario.token_confirmacion = nuevo_token
    usuario.fecha_modificacion = datetime.utcnow()
    
    db.commit()
    
    return nuevo_token