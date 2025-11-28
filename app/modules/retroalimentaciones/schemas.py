"""
Schemas Pydantic para retroalimentaciones
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RetroalimentacionBase(BaseModel):
    """Schema base para retroalimentaciones"""
    comentario: str
    tipo: Optional[str] = "Constructiva"


class RetroalimentacionCreate(RetroalimentacionBase):
    """Schema para crear una retroalimentación"""
    id_evaluacion: int
    id_receptor: int


class RetroalimentacionUpdate(BaseModel):
    """Schema para actualizar una retroalimentación"""
    comentario: Optional[str] = None
    tipo: Optional[str] = None
    leido: Optional[bool] = None


class RetroalimentacionResponse(RetroalimentacionBase):
    """Schema de respuesta para retroalimentaciones"""
    id_retroalimentacion: int
    id_evaluacion: int
    id_emisor: int
    id_receptor: int
    fecha_retroalimentacion: datetime
    leido: bool
    
    class Config:
        from_attributes = True