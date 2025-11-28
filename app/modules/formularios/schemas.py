"""
Schemas Pydantic para formularios y preguntas
✅ CORREGIDO: FormularioUpdate ahora acepta preguntas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class PreguntaBase(BaseModel):
    """Schema base para preguntas"""
    texto_pregunta: str
    tipo_pregunta: Optional[str] = "Escala"
    peso: Optional[Decimal] = Field(default=Decimal("1.00"), ge=0, le=10)
    opciones: Optional[str] = None  # JSON como string
    orden: Optional[int] = 0
    requerido: Optional[bool] = True
    competencia: Optional[str] = Field(None, max_length=100)


class PreguntaCreate(PreguntaBase):
    """Schema para crear una pregunta"""
    id_formulario: int


class PreguntaUpdate(BaseModel):
    """Schema para actualizar una pregunta"""
    texto_pregunta: Optional[str] = None
    tipo_pregunta: Optional[str] = None
    peso: Optional[Decimal] = None
    opciones: Optional[str] = None
    orden: Optional[int] = None
    requerido: Optional[bool] = None
    competencia: Optional[str] = None


class PreguntaResponse(PreguntaBase):
    """Schema de respuesta para preguntas"""
    id_pregunta: int
    id_formulario: int
    fecha_creacion: datetime
    
    class Config:
        from_attributes = True


class FormularioBase(BaseModel):
    """Schema base para formularios"""
    nombre_formulario: str = Field(..., max_length=150)
    descripcion: Optional[str] = None
    tipo_formulario: str
    periodo: Optional[str] = Field(None, max_length=50)
    rol_aplicable: Optional[int] = None


class FormularioCreate(FormularioBase):
    """Schema para crear un formulario"""
    preguntas: Optional[List[PreguntaBase]] = []


class FormularioUpdate(BaseModel):
    """
    Schema para actualizar un formulario
    ✅ CORREGIDO: Ahora acepta preguntas para actualizarlas
    """
    nombre_formulario: Optional[str] = None
    descripcion: Optional[str] = None
    tipo_formulario: Optional[str] = None
    periodo: Optional[str] = None
    rol_aplicable: Optional[int] = None
    estado: Optional[str] = None
    preguntas: Optional[List[PreguntaBase]] = None  # ✅ AGREGADO


class FormularioResponse(FormularioBase):
    """Schema de respuesta para formularios"""
    id_formulario: int
    estado: str
    creado_por: int
    fecha_creacion: datetime
    fecha_modificacion: datetime
    
    # Lista de preguntas
    preguntas: List[PreguntaResponse] = []
    
    class Config:
        from_attributes = True


class FormularioResumen(BaseModel):
    """Schema resumido de formulario (sin preguntas)"""
    id_formulario: int
    nombre_formulario: str
    tipo_formulario: str
    periodo: Optional[str] = None
    estado: str
    fecha_creacion: datetime
    
    class Config:
        from_attributes = True