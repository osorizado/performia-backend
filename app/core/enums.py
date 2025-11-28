from enum import Enum


class EstadoGeneral(str, Enum):
    """Estados generales (Activo/Inactivo)"""
    ACTIVO = "Activo"
    INACTIVO = "Inactivo"


class EstadoUsuario(str, Enum):
    """Estados de usuarios"""
    ACTIVO = "Activo"
    INACTIVO = "Inactivo"
    SUSPENDIDO = "Suspendido"


class TipoFormulario(str, Enum):
    """Tipos de formularios de evaluación"""
    AUTOEVALUACION = "Autoevaluación"
    EVALUACION_MANAGER = "Evaluación Manager"
    EVALUACION_360 = "Evaluación 360"
    EVALUACION_RRHH = "Evaluación RRHH"


class EstadoFormulario(str, Enum):
    """Estados de formularios"""
    BORRADOR = "Borrador"
    ACTIVO = "Activo"
    ARCHIVADO = "Archivado"


class TipoPregunta(str, Enum):
    """Tipos de preguntas en formularios"""
    ESCALA = "Escala"
    TEXTO = "Texto"
    SELECCION_MULTIPLE = "Selección múltiple"
    SI_NO = "Sí/No"


class TipoEvaluacion(str, Enum):
    """Tipos de evaluaciones"""
    AUTOEVALUACION = "Autoevaluación"
    MANAGER = "Manager"
    EVALUACION_360 = "360"
    RRHH = "RRHH"


class EstadoEvaluacion(str, Enum):
    """Estados de evaluaciones"""
    PENDIENTE = "Pendiente"
    EN_CURSO = "En Curso"
    COMPLETADA = "Completada"
    CANCELADA = "Cancelada"


class TipoObjetivo(str, Enum):
    """Tipos de objetivos"""
    INDIVIDUAL = "Individual"
    GRUPAL = "Grupal"
    DEPARTAMENTAL = "Departamental"


class EstadoObjetivo(str, Enum):
    """Estados de objetivos"""
    PENDIENTE = "Pendiente"
    EN_PROGRESO = "En Progreso"
    CUMPLIDO = "Cumplido"
    NO_CUMPLIDO = "No Cumplido"


class TipoRetroalimentacion(str, Enum):
    """Tipos de retroalimentación"""
    POSITIVA = "Positiva"
    CONSTRUCTIVA = "Constructiva"
    DESARROLLO = "Desarrollo"
    RECONOCIMIENTO = "Reconocimiento"


class TipoReporte(str, Enum):
    """Tipos de reportes"""
    INDIVIDUAL = "Individual"
    POR_AREA = "Por Área"
    GLOBAL = "Global"
    COMPARATIVO = "Comparativo"
    HISTORICO = "Histórico"


class FormatoReporte(str, Enum):
    """Formatos de exportación de reportes"""
    PDF = "PDF"
    EXCEL = "Excel"
    JSON = "JSON"


class TipoNotificacion(str, Enum):
    """Tipos de notificaciones"""
    INFO = "Info"
    RECORDATORIO = "Recordatorio"
    ALERTA = "Alerta"
    URGENTE = "Urgente"