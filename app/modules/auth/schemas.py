"""
Schemas para autenticación
"""
from pydantic import BaseModel, EmailStr
from typing import Optional


class LoginRequest(BaseModel):
    """Schema para login"""
    correo: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Schema de respuesta del token"""
    access_token: str
    token_type: str = "bearer"
    id_usuario: int
    nombre: str
    apellido: str
    rol: str


# ============================================
# SCHEMAS DE REGISTRO
# ============================================

class RegisterRequest(BaseModel):
    """Schema para registro de nuevo usuario"""
    nombre: str
    apellido: str
    email: EmailStr
    telefono: Optional[str] = None
    password: str
    puesto: str              # Cargo/Puesto
    area: str                # Área como texto (Gerencia, Ventas, etc.)
    id_rol: int = 4          # Por defecto Colaborador


class RegisterResponse(BaseModel):
    """Schema de respuesta del registro"""
    message: str
    id_usuario: int
    email: str
    requiere_confirmacion: bool = True


class ConfirmarCorreoRequest(BaseModel):
    """Schema para confirmar correo"""
    token: str


class ReenviarConfirmacionRequest(BaseModel):
    """Schema para reenviar correo de confirmación"""
    email: EmailStr


# ============================================
# SCHEMAS DE RECUPERACIÓN DE CONTRASEÑA
# ============================================

class PasswordResetRequest(BaseModel):
    """Schema para solicitar reset de contraseña"""
    email: EmailStr


class VerifyResetCodeRequest(BaseModel):
    """Schema para verificar código de reset"""
    email: EmailStr
    codigo: str


class PasswordResetConfirm(BaseModel):
    """Schema para confirmar reset con código"""
    email: EmailStr
    codigo: str
    nueva_password: str