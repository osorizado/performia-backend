"""
Schemas Pydantic para evaluaciones y resultados
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal


class ResultadoBase(BaseModel):
    """Schema base para resultados"""
    respuesta: Optional[str] = None
    puntaje: Optional[Decimal] = Field(None, ge=0, le=10)
    comentario: Optional[str] = None


class ResultadoCreate(ResultadoBase):
    """Schema para crear un resultado"""
    id_pregunta: int


class ResultadoUpdate(BaseModel):
    """Schema para actualizar un resultado"""
    respuesta: Optional[str] = None
    puntaje: Optional[Decimal] = None
    comentario: Optional[str] = None


class ResultadoResponse(ResultadoBase):
    """Schema de respuesta para resultados"""
    id_resultado: int
    id_evaluacion: int
    id_pregunta: int
    fecha_registro: datetime
    
    class Config:
        from_attributes = True


class EvaluacionBase(BaseModel):
    """Schema base para evaluaciones"""
    id_formulario: int
    id_evaluado: int
    tipo_evaluacion: str
    periodo: str = Field(..., max_length=50)
    fecha_inicio: date
    fecha_fin: Optional[date] = None
    observaciones_generales: Optional[str] = None


class EvaluacionCreate(EvaluacionBase):
    """Schema para crear una evaluación"""
    resultados: Optional[List[ResultadoCreate]] = []


class EvaluacionUpdate(BaseModel):
    """Schema para actualizar una evaluación"""
    estado: Optional[str] = None
    fecha_fin: Optional[date] = None
    puntaje_total: Optional[Decimal] = None
    observaciones_generales: Optional[str] = None


class EvaluacionResponse(EvaluacionBase):
    """Schema de respuesta para evaluaciones"""
    id_evaluacion: int
    id_evaluador: int
    estado: str
    puntaje_total: Optional[Decimal] = None
    fecha_creacion: datetime
    fecha_modificacion: datetime
    
    # Incluir resultados si es necesario
    resultados: List[ResultadoResponse] = []
    
    class Config:
        from_attributes = True


class EvaluacionResumen(BaseModel):
    """Schema resumido de evaluación"""
    id_evaluacion: int
    tipo_evaluacion: str
    periodo: str
    estado: str
    puntaje_total: Optional[Decimal] = None
    fecha_inicio: date
    fecha_fin: Optional[date] = None
    
    class Config:
        from_attributes = True


class IniciarEvaluacionRequest(BaseModel):
    """Schema para iniciar una evaluación"""
    id_formulario: int
    id_evaluado: int
    tipo_evaluacion: str
    periodo: str
    fecha_inicio: date
    fecha_fin: date


class ResponderEvaluacionRequest(BaseModel):
    """Schema para responder una evaluación"""
    resultados: List[ResultadoCreate]
    observaciones_generales: Optional[str] = None