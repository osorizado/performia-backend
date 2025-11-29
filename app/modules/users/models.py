"""
Modelos de usuarios y roles
ARCHIVO PRINCIPAL - Todos los demás módulos importan de aquí
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Rol(Base):
    """Tabla: roles"""
    __tablename__ = "roles"
    
    id_rol = Column(Integer, primary_key=True, autoincrement=True)
    nombre_rol = Column(String(50), nullable=False, unique=True)
    descripcion = Column(Text)
    permisos = Column(Text)
    estado = Column(Enum('Activo', 'Inactivo'), default='Activo')
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_modificacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    usuarios = relationship("Usuario", back_populates="rol")


class Usuario(Base):
    """Tabla: usuarios"""
    __tablename__ = "usuarios"
    
    id_usuario = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    correo = Column(String(150), unique=True, nullable=False)
    telefono = Column(String(20), nullable=True)
    password_hash = Column(String(255), nullable=False)
    area = Column(String(100), nullable=True)
    cargo = Column(String(100), nullable=True)
    manager_id = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=True)
    id_rol = Column(Integer, ForeignKey("roles.id_rol"), nullable=False)
    estado = Column(Enum('Activo', 'Inactivo', 'Suspendido'), default="Activo")
    fecha_ingreso = Column(Date, nullable=True)
    
    # Campos para confirmación de correo
    token_confirmacion = Column(String(255), nullable=True)
    correo_confirmado = Column(Boolean, default=False)
    
    # Timestamps
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_modificacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ultimo_acceso = Column(DateTime, nullable=True)
    
    # ============================================
    # RELACIONES
    # ============================================
    rol = relationship("Rol", back_populates="usuarios")
    # Relación self-referenciada (manager-subordinados)
    # Relación self-referenciada (manager-subordinados)
    manager = relationship(
        "Usuario",
        remote_side=[id_usuario],
        back_populates="subordinados",
        foreign_keys="Usuario.manager_id"
    )

    subordinados = relationship(
        "Usuario",
        back_populates="manager",
        foreign_keys="Usuario.manager_id"
    )


    
    # Evaluaciones
    evaluaciones_como_evaluado = relationship(
        "Evaluacion", 
        foreign_keys="Evaluacion.id_evaluado",
        back_populates="evaluado"
    )
    evaluaciones_como_evaluador = relationship(
        "Evaluacion", 
        foreign_keys="Evaluacion.id_evaluador",
        back_populates="evaluador"
    )
    
    # Objetivos
    objetivos = relationship(
        "Objetivo",
        foreign_keys="Objetivo.id_usuario",
        back_populates="usuario"
    )
    
    # Retroalimentaciones (CORREGIDO: nombres coinciden con retroalimentaciones/models.py)
    retroalimentaciones_emitidas = relationship(
        "Retroalimentacion",
        foreign_keys="Retroalimentacion.id_emisor",
        back_populates="emisor"
    )
    retroalimentaciones_recibidas = relationship(
        "Retroalimentacion",
        foreign_keys="Retroalimentacion.id_receptor",
        back_populates="receptor"
    )
    
    # Notificaciones
    notificaciones = relationship("Notificacion", back_populates="usuario")
    
    # Formularios creados (CORREGIDO: agregar back_populates en Formulario)
    formularios_creados = relationship(
        "Formulario",
        foreign_keys="Formulario.creado_por",
        back_populates="creador"
    )