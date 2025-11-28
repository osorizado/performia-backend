"""
Modelos de reportes y notificaciones
"""
from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Reporte(Base):
    """Tabla: reportes"""
    __tablename__ = "reportes"
    
    id_reporte = Column(Integer, primary_key=True, autoincrement=True)
    nombre_reporte = Column(String(150), nullable=False)
    tipo_reporte = Column(
        Enum('Individual', 'Por Área', 'Global', 'Comparativo', 'Histórico'),
        nullable=False
    )
    periodo = Column(String(50))
    parametros = Column(Text)
    ruta_archivo = Column(String(255))
    formato = Column(Enum('PDF', 'Excel', 'JSON'), default='PDF')
    generado_por = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    fecha_generacion = Column(DateTime, default=datetime.utcnow)
    
    # Sin back_populates para simplificar (relación unidireccional)


class Notificacion(Base):
    """Tabla: notificaciones"""
    __tablename__ = "notificaciones"
    
    id_notificacion = Column(Integer, primary_key=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    titulo = Column(String(150), nullable=False)
    mensaje = Column(Text, nullable=False)
    tipo = Column(
        Enum('Info', 'Recordatorio', 'Alerta', 'Urgente'),
        default='Info'
    )
    leida = Column(Boolean, default=False)
    enlace = Column(String(255))
    fecha_envio = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    usuario = relationship("Usuario", back_populates="notificaciones")


class LogAuditoria(Base):
    """Tabla: log_auditoria"""
    __tablename__ = "log_auditoria"
    
    id_log = Column(Integer, primary_key=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    accion = Column(String(100), nullable=False)
    modulo = Column(String(50))
    entidad_afectada = Column(String(50))
    id_entidad = Column(Integer)
    detalles = Column(Text)
    ip_origen = Column(String(45))
    fecha_accion = Column(DateTime, default=datetime.utcnow)