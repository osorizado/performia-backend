"""
Schemas Pydantic para evaluaciones y resultados
✅ CORREGIDO: EvaluacionResumen ahora incluye id_formulario, id_evaluado, id_evaluador y formulario
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


# ⭐ NUEVO: Schema para formulario básico
class FormularioBasico(BaseModel):
    """Schema básico del formulario para incluir en evaluaciones"""
    id_formulario: int
    nombre_formulario: str
    descripcion: Optional[str] = None
    tipo_formulario: str
    estado: str
    
    class Config:
        from_attributes = True


# ⭐ CORREGIDO: Ahora incluye todos los campos necesarios
class EvaluacionResumen(BaseModel):
    """Schema resumido de evaluación"""
    id_evaluacion: int
    id_formulario: int        # ⭐ AGREGADO
    id_evaluado: int          # ⭐ AGREGADO
    id_evaluador: int         # ⭐ AGREGADO
    tipo_evaluacion: str
    periodo: str
    estado: str
    puntaje_total: Optional[Decimal] = None
    fecha_inicio: date
    fecha_fin: Optional[date] = None
    
    # ⭐ AGREGADO - Objeto del formulario anidado (tipado correctamente)
    formulario: Optional[FormularioBasico] = None
    
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


class AsignarEvaluacionMasivaRequest(BaseModel):
    """Schema para asignar evaluaciones masivamente"""
    id_formulario: int
    rol_id: int
    periodo: str = Field(default_factory=lambda: str(datetime.now().year))
    tipo_evaluacion: str = "Autoevaluación"
    dias_plazo: int = Field(21, ge=1, le=90)
    

class AsignarEvaluacionMasivaResponse(BaseModel):
    """Schema de respuesta para asignación masiva"""
    success: bool
    message: str
    total_usuarios: int
    evaluaciones_creadas: List[dict]
    evaluaciones_existentes: List[dict]
    formulario_nombre: str
    periodo: str
    fecha_inicio: str
    fecha_fin: str