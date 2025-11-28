"""
Modelos de formularios y preguntas
"""
from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey, DateTime, Numeric, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Formulario(Base):
    """Tabla: formularios"""
    __tablename__ = "formularios"
    
    id_formulario = Column(Integer, primary_key=True, autoincrement=True)
    nombre_formulario = Column(String(150), nullable=False)
    descripcion = Column(Text)
    tipo_formulario = Column(String(100), nullable=False)

    periodo = Column(String(50))
    rol_aplicable = Column(Integer, ForeignKey("roles.id_rol"))
    estado = Column(String(50), default='Borrador')

    creado_por = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_modificacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    preguntas = relationship("Pregunta", back_populates="formulario", cascade="all, delete-orphan")
    evaluaciones = relationship("Evaluacion", back_populates="formulario")
    
    # AGREGADO: Relación con Usuario (creador)
    creador = relationship("Usuario", foreign_keys=[creado_por], back_populates="formularios_creados")


class Pregunta(Base):
    """Tabla: preguntas"""
    __tablename__ = "preguntas"
    
    id_pregunta = Column(Integer, primary_key=True, autoincrement=True)
    id_formulario = Column(Integer, ForeignKey("formularios.id_formulario"), nullable=False)
    texto_pregunta = Column(Text, nullable=False)
    tipo_pregunta = Column(String(50), default='Escala')

    peso = Column(Numeric(5, 2), default=1.00)
    opciones = Column(Text)
    orden = Column(Integer, default=0)
    requerido = Column(Boolean, default=True)
    competencia = Column(String(100))
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    formulario = relationship("Formulario", back_populates="preguntas")
    resultados = relationship("Resultado", back_populates="pregunta")