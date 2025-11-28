"""
Schemas Pydantic para objetivos
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
from decimal import Decimal


class ObjetivoBase(BaseModel):
    """Schema base para objetivos"""
    descripcion: str
    tipo: Optional[str] = "Individual"
    periodo: str = Field(..., max_length=50)
    peso: Optional[Decimal] = Field(default=1.00, ge=0, le=10)
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None


class ObjetivoCreate(ObjetivoBase):
    """Schema para crear un objetivo"""
    id_usuario: int


class ObjetivoUpdate(BaseModel):
    """Schema para actualizar un objetivo"""
    descripcion: Optional[str] = None
    tipo: Optional[str] = None
    periodo: Optional[str] = None
    peso: Optional[Decimal] = None
    estado: Optional[str] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    resultado_obtenido: Optional[str] = None


class ObjetivoResponse(ObjetivoBase):
    """Schema de respuesta para objetivos"""
    id_objetivo: int
    id_usuario: int
    estado: str
    resultado_obtenido: Optional[str] = None
    creado_por: int
    fecha_creacion: datetime
    fecha_modificacion: datetime
    
    class Config:
        from_attributes = True