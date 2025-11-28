"""
Schemas Pydantic para reportes y notificaciones
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ========================================
# SCHEMAS DE REPORTES
# ========================================

class ReporteBase(BaseModel):
    """Schema base para reportes"""
    nombre_reporte: str = Field(..., max_length=150)
    tipo_reporte: str  # Individual, Por Área, Global, Comparativo, Histórico
    periodo: Optional[str] = Field(None, max_length=50)
    parametros: Optional[str] = None  # JSON como string
    formato: Optional[str] = "PDF"  # PDF, Excel, JSON


class ReporteCreate(ReporteBase):
    """Schema para crear un reporte"""
    pass


class ReporteResponse(ReporteBase):
    """Schema de respuesta para reportes"""
    id_reporte: int
    ruta_archivo: Optional[str] = None
    generado_por: int
    fecha_generacion: datetime
    
    class Config:
        from_attributes = True


# ========================================
# SCHEMAS DE ESTADÍSTICAS
# ========================================

class EstadisticasGenerales(BaseModel):
    """Estadísticas generales del sistema"""
    promedio_general: float
    evaluaciones_completas: int
    evaluaciones_pendientes: int
    tasa_completitud: float  # Porcentaje
    top_performers: int  # Cantidad de colaboradores con promedio >= 4.5
    total_colaboradores: int
    total_evaluadores: int


class EstadisticasCompetencias(BaseModel):
    """Estadísticas por competencia"""
    competencia: str
    promedio: float
    cantidad_evaluaciones: int


class DistribucionCalificaciones(BaseModel):
    """Distribución de calificaciones"""
    rango: str  # "1.0-2.0", "2.1-3.0", etc.
    cantidad: int


class TopPerformer(BaseModel):
    """Colaborador destacado"""
    id_usuario: int
    nombre: str
    apellido: str
    area: Optional[str]
    cargo: Optional[str]
    promedio: float
    evaluaciones_completas: int


class AreaRanking(BaseModel):
    """Ranking de áreas"""
    area: str
    promedio: float
    total_colaboradores: int
    evaluaciones_completas: int


# ========================================
# SCHEMAS DE FILTROS
# ========================================

class FiltrosReporte(BaseModel):
    """Filtros para generar reportes"""
    tipo_reporte: str  # Individual, Por Área, Global, Comparativo, Histórico
    formato: str = "PDF"  # PDF, Excel, JSON
    periodo: Optional[str] = None  # "2024-Q1", "2024-01", "Anual 2024"
    area: Optional[str] = None
    id_colaborador: Optional[int] = None
    id_formulario: Optional[int] = None
    incluir_graficos: bool = True
    incluir_detalles: bool = True


# ========================================
# SCHEMAS DE NOTIFICACIONES
# ========================================

class NotificacionBase(BaseModel):
    """Schema base para notificaciones"""
    titulo: str = Field(..., max_length=150)
    mensaje: str
    tipo: Optional[str] = "Info"  # Info, Recordatorio, Alerta, Urgente
    enlace: Optional[str] = Field(None, max_length=255)


class NotificacionCreate(NotificacionBase):
    """Schema para crear una notificación"""
    id_usuario: int


class NotificacionUpdate(BaseModel):
    """Schema para actualizar una notificación"""
    leida: bool


class NotificacionResponse(NotificacionBase):
    """Schema de respuesta para notificaciones"""
    id_notificacion: int
    id_usuario: int
    leida: bool
    fecha_envio: datetime
    
    class Config:
        from_attributes = True