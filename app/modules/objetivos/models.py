"""
Modelos de objetivos
"""
from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey, DateTime, Date, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Objetivo(Base):
    """Tabla: objetivos"""
    __tablename__ = "objetivos"
    
    id_objetivo = Column(Integer, primary_key=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    descripcion = Column(Text, nullable=False)
    tipo = Column(
        Enum('Individual', 'Grupal', 'Departamental'),
        default='Individual'
    )
    periodo = Column(String(50), nullable=False)
    peso = Column(Numeric(5, 2), default=1.00)
    estado = Column(
        Enum('Pendiente', 'En Progreso', 'Cumplido', 'No Cumplido'),
        default='Pendiente'
    )
    fecha_inicio = Column(Date)
    fecha_fin = Column(Date)
    resultado_obtenido = Column(Text)
    creado_por = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_modificacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    usuario = relationship("Usuario", foreign_keys=[id_usuario], back_populates="objetivos")