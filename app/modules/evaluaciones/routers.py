"""
Rutas de evaluaciones y resultados
Endpoints CRUD para gestión de evaluaciones
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user, require_role
from app.modules.users.models import Usuario
from app.modules.evaluaciones.schemas import (
    EvaluacionResponse, EvaluacionResumen,
    IniciarEvaluacionRequest, ResponderEvaluacionRequest,
    ResultadoResponse, ResultadoUpdate,
    AsignarEvaluacionMasivaRequest  # ⭐ NUEVO
)
from app.modules.evaluaciones import services

router = APIRouter(prefix="/evaluaciones", tags=["Evaluaciones"])


# ============================================================================
# ENDPOINTS DE EVALUACIONES
# ============================================================================

@router.get("/", response_model=List[EvaluacionResumen])
def listar_evaluaciones(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    id_evaluado: Optional[int] = Query(None),
    id_evaluador: Optional[int] = Query(None),
    estado: Optional[str] = Query(None),
    periodo: Optional[str] = Query(None),
    tipo: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("Administrador", "RRHH", "Manager", "Director"))
):
    """
    Lista evaluaciones con filtros opcionales
    Requiere: Administrador, RRHH, Manager o Director
    """
    return services.get_evaluaciones(
        db,
        skip=skip,
        limit=limit,
        id_evaluado=id_evaluado,
        id_evaluador=id_evaluador,
        estado=estado,
        periodo=periodo,
        tipo=tipo
    )


@router.get("/pendientes", response_model=List[EvaluacionResumen])
def mis_evaluaciones_pendientes(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtiene las evaluaciones pendientes del usuario actual como evaluador
    """
    return services.get_evaluaciones_pendientes(db, current_user.id_usuario)


@router.get("/mis-evaluaciones", response_model=List[EvaluacionResumen])
def mis_evaluaciones(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtiene todas las evaluaciones donde el usuario actual es el evaluado
    """
    return services.get_mis_evaluaciones(db, current_user.id_usuario)
@router.get("/asignadas", response_model=List[EvaluacionResumen])
def evaluaciones_asignadas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    estado: Optional[str] = Query(None),
    periodo: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("Administrador", "RRHH", "Manager", "Director"))
):
    """
    Obtiene las evaluaciones asignadas/creadas por el usuario actual
    Requiere: Administrador, RRHH, Manager o Director
    """
    return services.get_evaluaciones_asignadas(
        db, 
        current_user.id_usuario,
        skip=skip,
        limit=limit,
        estado=estado,
        periodo=periodo
    )

@router.get("/periodo/{periodo}", response_model=List[EvaluacionResumen])
def evaluaciones_por_periodo(
    periodo: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("Administrador", "RRHH", "Director"))
):
    """
    Obtiene todas las evaluaciones de un periodo
    Requiere: Administrador, RRHH o Director
    """
    return services.get_evaluaciones_por_periodo(db, periodo)


@router.get("/{evaluacion_id}", response_model=EvaluacionResponse)
def obtener_evaluacion(
    evaluacion_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtiene una evaluación por ID con todos sus resultados
    """
    evaluacion = services.get_evaluacion_by_id(db, evaluacion_id)
    if not evaluacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluación no encontrada"
        )
    
    # Verificar si el usuario es manager del evaluado
    es_manager_del_evaluado = False
    if evaluacion.evaluado and evaluacion.evaluado.manager_id == current_user.id_usuario:
        es_manager_del_evaluado = True
    
    # Verificar permisos: evaluador, evaluado, manager del evaluado, o roles administrativos
    tiene_permiso = (
        current_user.id_usuario == evaluacion.id_evaluador or
        current_user.id_usuario == evaluacion.id_evaluado or
        es_manager_del_evaluado or
        current_user.rol.nombre_rol in ["Administrador", "RRHH", "Director"]
    )
    
    if not tiene_permiso:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver esta evaluación"
        )
    
    return evaluacion
@router.post("/iniciar", response_model=EvaluacionResponse)
def iniciar_evaluacion(
    request: IniciarEvaluacionRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("Administrador", "RRHH", "Manager"))
):
    """
    Inicia una nueva evaluación
    Requiere: Administrador, RRHH o Manager
    """
    return services.iniciar_evaluacion(db, request, current_user.id_usuario)


@router.post("/{evaluacion_id}/responder", response_model=EvaluacionResponse)
def responder_evaluacion(
    evaluacion_id: int,
    request: ResponderEvaluacionRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Registra respuestas para una evaluación
    Solo el evaluador puede responder
    """
    return services.responder_evaluacion(db, evaluacion_id, request, current_user.id_usuario)


@router.post("/{evaluacion_id}/completar", response_model=EvaluacionResponse)
def completar_evaluacion(
    evaluacion_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Marca una evaluación como completada y calcula el puntaje
    Solo el evaluador puede completar
    """
    return services.completar_evaluacion(db, evaluacion_id, current_user.id_usuario)


@router.post("/{evaluacion_id}/cancelar", response_model=EvaluacionResponse)
def cancelar_evaluacion(
    evaluacion_id: int,
    motivo: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("Administrador", "RRHH"))
):
    """
    Cancela una evaluación
    Requiere: Administrador o RRHH
    """
    return services.cancelar_evaluacion(db, evaluacion_id, motivo)

@router.post("/asignar-masiva")
def asignar_evaluacion_masiva(
    request: AsignarEvaluacionMasivaRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("Administrador", "RRHH"))
):
    """
    Asigna un formulario a todos los usuarios de un rol específico
    Requiere: Administrador o RRHH
    
    Body esperado:
    {
        "id_formulario": 1,
        "rol_id": 4,
        "periodo": "2025",
        "tipo_evaluacion": "Autoevaluación",
        "dias_plazo": 21
    }
    """
    return services.asignar_evaluacion_masiva(db, request, current_user.id_usuario)
# ============================================================================
# ENDPOINTS DE RESULTADOS
# ============================================================================

@router.get("/{evaluacion_id}/resultados", response_model=List[ResultadoResponse])
def listar_resultados(
    evaluacion_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Lista todos los resultados de una evaluación
    """
    # Verificar que la evaluación existe y el usuario tiene permiso
    evaluacion = services.get_evaluacion_by_id(db, evaluacion_id)
    if not evaluacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluación no encontrada"
        )
    
    if (current_user.id_usuario != evaluacion.id_evaluador and
        current_user.id_usuario != evaluacion.id_evaluado and
        current_user.rol.nombre_rol not in ["Administrador", "RRHH", "Director"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver estos resultados"
        )
    
    return services.get_resultados_by_evaluacion(db, evaluacion_id)


@router.put("/resultados/{resultado_id}", response_model=ResultadoResponse)
def actualizar_resultado(
    resultado_id: int,
    resultado_update: ResultadoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Actualiza un resultado específico
    Solo el evaluador puede actualizar antes de completar la evaluación
    """
    return services.update_resultado(db, resultado_id, resultado_update)

# ============================================================================
# ENDPOINTS ESPECÍFICOS PARA MANAGERS
# ============================================================================

@router.get("/equipo/todas", response_model=List[EvaluacionResumen])
def evaluaciones_mi_equipo(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    estado: Optional[str] = Query(None),
    periodo: Optional[str] = Query(None),
    tipo: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("Manager", "Director"))
):
    """
    Obtiene TODAS las evaluaciones de los colaboradores directos del manager
    Incluye:
    - Evaluaciones donde el manager es el evaluador (debe completar)
    - Autoevaluaciones de sus colaboradores (solo lectura)
    
    Requiere: Manager o Director
    """
    return services.get_evaluaciones_equipo(
        db,
        current_user.id_usuario,
        skip=skip,
        limit=limit,
        estado=estado,
        periodo=periodo,
        tipo=tipo
    )


@router.get("/equipo/pendientes-manager", response_model=List[EvaluacionResumen])
def evaluaciones_pendientes_manager(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("Manager", "Director"))
):
    """
    Obtiene SOLO las evaluaciones pendientes que el manager debe completar
    (donde el manager es el evaluador)
    
    Requiere: Manager o Director
    """
    return services.get_evaluaciones_pendientes_equipo(db, current_user.id_usuario)


@router.get("/equipo/autoevaluaciones", response_model=List[EvaluacionResumen])
def autoevaluaciones_equipo(
    estado: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("Manager", "Director"))
):
    """
    Obtiene las autoevaluaciones de los colaboradores del manager
    (para monitoreo, sin capacidad de editar)
    
    Requiere: Manager o Director
    """
    return services.get_autoevaluaciones_equipo(db, current_user.id_usuario, estado)