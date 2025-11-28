"""
Modelos de evaluaciones y resultados
"""
from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey, DateTime, Date, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Evaluacion(Base):
    """Tabla: evaluaciones"""
    __tablename__ = "evaluaciones"
    
    id_evaluacion = Column(Integer, primary_key=True, autoincrement=True)
    id_formulario = Column(Integer, ForeignKey("formularios.id_formulario"), nullable=False)
    id_evaluado = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    id_evaluador = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    tipo_evaluacion = Column(
        Enum('Autoevaluación', 'Manager', '360', 'RRHH'),
        nullable=False
    )
    periodo = Column(String(50), nullable=False)
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date)
    estado = Column(
        Enum('Pendiente', 'En Curso', 'Completada', 'Cancelada'),
        default='Pendiente'
    )
    puntaje_total = Column(Numeric(5, 2))
    observaciones_generales = Column(Text)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_modificacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    formulario = relationship("Formulario", back_populates="evaluaciones")
    evaluado = relationship("Usuario", foreign_keys=[id_evaluado], back_populates="evaluaciones_como_evaluado")
    evaluador = relationship("Usuario", foreign_keys=[id_evaluador], back_populates="evaluaciones_como_evaluador")
    resultados = relationship("Resultado", back_populates="evaluacion", cascade="all, delete-orphan")
    retroalimentaciones = relationship("Retroalimentacion", back_populates="evaluacion")


class Resultado(Base):
    """Tabla: resultados"""
    __tablename__ = "resultados"
    
    id_resultado = Column(Integer, primary_key=True, autoincrement=True)
    id_evaluacion = Column(Integer, ForeignKey("evaluaciones.id_evaluacion"), nullable=False)
    id_pregunta = Column(Integer, ForeignKey("preguntas.id_pregunta"), nullable=False)
    respuesta = Column(Text)
    puntaje = Column(Numeric(5, 2))
    comentario = Column(Text)
    fecha_registro = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    evaluacion = relationship("Evaluacion", back_populates="resultados")
    pregunta = relationship("Pregunta", back_populates="resultados")