"""
Schemas Pydantic para usuarios y roles
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, date
from app.core.enums import EstadoUsuario


class RolBase(BaseModel):
    """Schema base para roles"""
    nombre_rol: str = Field(..., max_length=50)
    descripcion: Optional[str] = None
    permisos: Optional[str] = None  # JSON como string
    estado: Optional[str] = "Activo"


class RolCreate(RolBase):
    """Schema para crear un rol"""
    pass


class RolUpdate(BaseModel):
    """Schema para actualizar un rol"""
    nombre_rol: Optional[str] = None
    descripcion: Optional[str] = None
    permisos: Optional[str] = None
    estado: Optional[str] = None


class RolResponse(RolBase):
    """Schema de respuesta para roles"""
    id_rol: int
    fecha_creacion: datetime
    fecha_modificacion: datetime
    
    class Config:
        from_attributes = True


class UsuarioBase(BaseModel):
    """Schema base para usuarios"""
    nombre: str = Field(..., max_length=100)
    apellido: str = Field(..., max_length=100)
    correo: EmailStr
    area: Optional[str] = Field(None, max_length=100)
    cargo: Optional[str] = Field(None, max_length=100)
    fecha_ingreso: Optional[date] = None


class UsuarioCreate(UsuarioBase):
    """Schema para crear un usuario"""
    password: str = Field(..., min_length=8)
    id_rol: int
    manager_id: Optional[int] = None


class UsuarioUpdate(BaseModel):
    """Schema para actualizar un usuario"""
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    correo: Optional[EmailStr] = None
    area: Optional[str] = None
    cargo: Optional[str] = None
    id_rol: Optional[int] = None
    manager_id: Optional[int] = None
    estado: Optional[str] = None


class UsuarioResponse(UsuarioBase):
    """Schema de respuesta para usuarios"""
    id_usuario: int
    id_rol: int
    manager_id: Optional[int] = None
    estado: str
    fecha_creacion: datetime
    fecha_modificacion: datetime
    ultimo_acceso: Optional[datetime] = None
    
    # Datos del rol
    rol: Optional[RolResponse] = None
    
    class Config:
        from_attributes = True


class UsuarioLogin(BaseModel):
    """Schema para login"""
    correo: EmailStr
    password: str


class CambiarPasswordRequest(BaseModel):
    """Schema para cambiar contraseña"""
    password_actual: str
    password_nueva: str = Field(..., min_length=8)
    password_confirmacion: str = Field(..., min_length=8)