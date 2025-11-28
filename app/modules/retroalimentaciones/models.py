"""
Modelos de retroalimentación
"""
from sqlalchemy import Column, Integer, Text, Enum, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Retroalimentacion(Base):
    """Tabla: retroalimentaciones"""
    __tablename__ = "retroalimentaciones"
    
    id_retroalimentacion = Column(Integer, primary_key=True, autoincrement=True)
    id_evaluacion = Column(Integer, ForeignKey("evaluaciones.id_evaluacion"), nullable=False)
    id_emisor = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    id_receptor = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    comentario = Column(Text, nullable=False)
    tipo = Column(
        Enum('Positiva', 'Constructiva', 'Desarrollo', 'Reconocimiento'),
        default='Constructiva'
    )
    fecha_retroalimentacion = Column(DateTime, default=datetime.utcnow)
    leido = Column(Boolean, default=False)
    
    # Relaciones (CORREGIDO: nombres coinciden con Usuario)
    evaluacion = relationship("Evaluacion", back_populates="retroalimentaciones")
    emisor = relationship("Usuario", foreign_keys=[id_emisor], back_populates="retroalimentaciones_emitidas")
    receptor = relationship("Usuario", foreign_keys=[id_receptor], back_populates="retroalimentaciones_recibidas")