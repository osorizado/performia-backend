"""
Rutas de autenticación
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.auth.schemas import (
    LoginRequest, 
    TokenResponse, 
    RegisterRequest, 
    RegisterResponse,
    ConfirmarCorreoRequest,
    ReenviarConfirmacionRequest,
    PasswordResetRequest,
    VerifyResetCodeRequest,
    PasswordResetConfirm
)
from app.modules.auth.services import (
    authenticate_user, 
    create_user_token,
    check_email_exists,
    create_user,
    confirm_user_email,
    regenerate_confirmation_token
)
from app.modules.auth.dependencies import get_current_user
from app.modules.users.models import Usuario
from app.modules.users.schemas import CambiarPasswordRequest
from app.core.security import verify_password, get_password_hash
from app.core.email import send_confirmation_email, send_password_reset_code_email
from datetime import datetime
import random

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=TokenResponse)
def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Endpoint de login
    """
    usuario = authenticate_user(db, credentials.correo, credentials.password)
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verificar que el usuario esté activo
    if usuario.estado != "Activo":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo o pendiente de confirmación"
        )
    
    # Verificar que el correo esté confirmado
    if not usuario.correo_confirmado:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Debes confirmar tu correo electrónico antes de iniciar sesión"
        )
    
    # Generar token
    access_token = create_user_token(usuario)
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        id_usuario=usuario.id_usuario,
        nombre=usuario.nombre,
        apellido=usuario.apellido,
        rol=usuario.rol.nombre_rol
    )


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_data: RegisterRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Registra un nuevo usuario
    """
    # Verificar si el email ya existe
    if check_email_exists(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está registrado"
        )
    
    # Crear usuario
    try:
        nuevo_usuario = create_user(db, user_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el usuario: {str(e)}"
        )
    
    # Enviar correo de confirmación en segundo plano
    background_tasks.add_task(
        send_confirmation_email,
        email=nuevo_usuario.correo,
        nombre=nuevo_usuario.nombre,
        token=nuevo_usuario.token_confirmacion
    )
    
    return RegisterResponse(
        message="Usuario registrado exitosamente. Por favor, confirma tu correo electrónico.",
        id_usuario=nuevo_usuario.id_usuario,
        email=nuevo_usuario.correo,
        requiere_confirmacion=True
    )


@router.post("/confirmar-correo")
def confirmar_correo(
    request: ConfirmarCorreoRequest,
    db: Session = Depends(get_db)
):
    """
    Confirma el correo electrónico del usuario
    """
    usuario = confirm_user_email(db, request.token)
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token de confirmación inválido o expirado"
        )
    
    return {
        "message": "Correo confirmado exitosamente. Ya puedes iniciar sesión.",
        "id_usuario": usuario.id_usuario,
        "email": usuario.correo
    }


@router.get("/confirmar-correo/{token}")
def confirmar_correo_get(
    token: str,
    db: Session = Depends(get_db)
):
    """
    Confirma el correo electrónico del usuario (GET)
    """
    usuario = confirm_user_email(db, token)
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token de confirmación inválido o expirado"
        )
    
    return {
        "message": "Correo confirmado exitosamente",
        "redirect": "/auth/login"
    }


@router.post("/reenviar-confirmacion")
def reenviar_confirmacion(
    request: ReenviarConfirmacionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Reenvía el correo de confirmación
    """
    usuario = db.query(Usuario).filter(Usuario.correo == request.email).first()
    
    if not usuario:
        # No revelar si el email existe
        return {"message": "Si el correo existe, recibirás un nuevo enlace de confirmación."}
    
    if usuario.correo_confirmado:
        return {"message": "Este correo ya está confirmado. Puedes iniciar sesión."}
    
    nuevo_token = regenerate_confirmation_token(db, request.email)
    
    if nuevo_token:
        # Enviar correo
        background_tasks.add_task(
            send_confirmation_email,
            email=usuario.correo,
            nombre=usuario.nombre,
            token=nuevo_token
        )
    
    return {"message": "Se ha enviado un nuevo correo de confirmación."}


# ============================================
# ENDPOINTS DE RECUPERACIÓN DE CONTRASEÑA
# ============================================

@router.post("/request-password-reset")
def request_password_reset(
    request: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Solicita reset de contraseña - envía código de 6 dígitos por email
    """
    usuario = db.query(Usuario).filter(Usuario.correo == request.email).first()
    
    # Siempre responder igual para no revelar si el email existe
    if not usuario:
        return {"message": "Si el correo existe, recibirás un código de recuperación."}
    
    # Generar código de 6 dígitos
    codigo = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    
    # Guardar código en token_confirmacion (temporal)
    usuario.token_confirmacion = codigo
    usuario.fecha_modificacion = datetime.utcnow()
    db.commit()
    
    # Enviar email con código
    background_tasks.add_task(
        send_password_reset_code_email,
        email=usuario.correo,
        nombre=usuario.nombre,
        codigo=codigo
    )
    
    return {"message": "Si el correo existe, recibirás un código de recuperación."}


@router.post("/verify-reset-token")
def verify_reset_token(
    request: VerifyResetCodeRequest,
    db: Session = Depends(get_db)
):
    """
    Verifica el código de reset
    """
    usuario = db.query(Usuario).filter(
        Usuario.correo == request.email,
        Usuario.token_confirmacion == request.codigo
    ).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Código inválido o expirado"
        )
    
    return {"valid": True}


@router.post("/reset-password")
def reset_password(
    request: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """
    Resetea la contraseña con el código
    """
    usuario = db.query(Usuario).filter(
        Usuario.correo == request.email,
        Usuario.token_confirmacion == request.codigo
    ).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Código inválido o expirado"
        )
    
    # Actualizar contraseña
    usuario.password_hash = get_password_hash(request.nueva_password)
    usuario.token_confirmacion = None
    usuario.fecha_modificacion = datetime.utcnow()
    db.commit()
    
    return {"message": "Contraseña actualizada exitosamente"}


# ============================================
# ENDPOINTS DE USUARIO ACTUAL
# ============================================

@router.get("/me")
def get_current_user_info(
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtiene la información del usuario actual
    """
    return {
        "id_usuario": current_user.id_usuario,
        "nombre": current_user.nombre,
        "apellido": current_user.apellido,
        "correo": current_user.correo,
        "rol": current_user.rol.nombre_rol,
        "area": current_user.area,
        "cargo": current_user.cargo,
        "estado": current_user.estado
    }


@router.get("/validar-token")
def validar_token(
    current_user: Usuario = Depends(get_current_user)
):
    """
    Valida si un token es válido
    """
    return {
        "valid": True,
        "id_usuario": current_user.id_usuario,
        "correo": current_user.correo,
        "rol": current_user.rol.nombre_rol
    }


@router.post("/cambiar-password")
def cambiar_password(
    request: CambiarPasswordRequest,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cambia la contraseña del usuario actual
    """
    if not verify_password(request.password_actual, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña actual es incorrecta"
        )
    
    if request.password_nueva != request.password_confirmacion:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Las contraseñas nuevas no coinciden"
        )
    
    current_user.password_hash = get_password_hash(request.password_nueva)
    current_user.fecha_modificacion = datetime.utcnow()
    db.commit()
    
    return {"message": "Contraseña cambiada exitosamente"}


@router.post("/logout")
def logout():
    """
    Logout
    """
    return {"message": "Sesión cerrada exitosamente"}