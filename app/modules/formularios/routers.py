"""
Rutas de formularios y preguntas
Endpoints CRUD para gestión de formularios y preguntas
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user, require_role
from app.modules.users.models import Usuario
from app.modules.formularios.schemas import (
    FormularioCreate, FormularioUpdate, FormularioResponse, FormularioResumen,
    PreguntaCreate, PreguntaUpdate, PreguntaResponse
)
from app.modules.formularios import services

router = APIRouter(prefix="/formularios", tags=["Formularios"])


# ============================================================================
# ENDPOINTS DE FORMULARIOS
# ============================================================================

@router.get("/", response_model=List[FormularioResponse])
def listar_formularios(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    tipo: Optional[str] = Query(None),
    estado: Optional[str] = Query(None),
    periodo: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("Administrador", "RRHH", "Manager"))
):
    """
    Lista todos los formularios con filtros opcionales
    Requiere: Administrador, RRHH o Manager
    """
    formularios = services.get_formularios(
        db,
        skip=skip,
        limit=limit,
        tipo=tipo,
        estado=estado,
        periodo=periodo
    )
    
    return formularios


@router.get("/{formulario_id}", response_model=FormularioResponse)
def obtener_formulario(
    formulario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtiene un formulario por ID con todas sus preguntas
    """
    formulario = services.get_formulario_by_id(db, formulario_id)
    if not formulario:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Formulario no encontrado"
        )
    return formulario


@router.post("/", response_model=FormularioResponse)
def crear_formulario(
    formulario: FormularioCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("Administrador", "RRHH"))
):
    """
    Crea un nuevo formulario con sus preguntas
    Requiere: Administrador o RRHH
    """
    return services.create_formulario(db, formulario, current_user.id_usuario)


@router.put("/{formulario_id}", response_model=FormularioResponse)
def actualizar_formulario(
    formulario_id: int,
    formulario_update: FormularioUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("Administrador", "RRHH"))
):
    """
    Actualiza un formulario
    Requiere: Administrador o RRHH
    """
    return services.update_formulario(db, formulario_id, formulario_update)


@router.delete("/{formulario_id}")
def eliminar_formulario(
    formulario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("Administrador", "RRHH"))
):
    """
    Elimina un formulario (soft delete - lo archiva)
    Requiere: Administrador o RRHH
    """
    return services.delete_formulario(db, formulario_id)


@router.post("/{formulario_id}/activar", response_model=FormularioResponse)
def activar_formulario(
    formulario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("Administrador", "RRHH"))
):
    """
    Activa un formulario
    Requiere: Administrador o RRHH
    """
    return services.activar_formulario(db, formulario_id)


@router.post("/{formulario_id}/duplicar", response_model=FormularioResponse)
def duplicar_formulario(
    formulario_id: int,
    nuevo_nombre: str = Query(..., description="Nombre para el formulario duplicado"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("Administrador", "RRHH"))
):
    """
    Duplica un formulario con todas sus preguntas
    Requiere: Administrador o RRHH
    """
    return services.duplicar_formulario(
        db, 
        formulario_id, 
        nuevo_nombre, 
        current_user.id_usuario
    )


# ============================================================================
# ENDPOINTS DE PREGUNTAS
# ============================================================================

@router.get("/{formulario_id}/preguntas", response_model=List[PreguntaResponse])
def listar_preguntas_formulario(
    formulario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Lista todas las preguntas de un formulario ordenadas
    """
    return services.get_preguntas_by_formulario(db, formulario_id)


@router.get("/preguntas/{pregunta_id}", response_model=PreguntaResponse)
def obtener_pregunta(
    pregunta_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtiene una pregunta por ID
    """
    pregunta = services.get_pregunta_by_id(db, pregunta_id)
    if not pregunta:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pregunta no encontrada"
        )
    return pregunta


@router.post("/preguntas", response_model=PreguntaResponse)
def crear_pregunta(
    pregunta: PreguntaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("Administrador", "RRHH"))
):
    """
    Crea una nueva pregunta en un formulario
    Requiere: Administrador o RRHH
    """
    return services.create_pregunta(db, pregunta)


@router.put("/preguntas/{pregunta_id}", response_model=PreguntaResponse)
def actualizar_pregunta(
    pregunta_id: int,
    pregunta_update: PreguntaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("Administrador", "RRHH"))
):
    """
    Actualiza una pregunta
    Requiere: Administrador o RRHH
    """
    return services.update_pregunta(db, pregunta_id, pregunta_update)


@router.delete("/preguntas/{pregunta_id}")
def eliminar_pregunta(
    pregunta_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("Administrador", "RRHH"))
):
    """
    Elimina una pregunta
    Requiere: Administrador o RRHH
    """
    return services.delete_pregunta(db, pregunta_id)


@router.post("/{formulario_id}/preguntas/reordenar", response_model=List[PreguntaResponse])
def reordenar_preguntas(
    formulario_id: int,
    nuevos_ordenes: dict[int, int],
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("Administrador", "RRHH"))
):
    """
    Reordena las preguntas de un formulario
    Formato: {"id_pregunta": nuevo_orden}
    Requiere: Administrador o RRHH
    """
    return services.reordenar_preguntas(db, formulario_id, nuevos_ordenes)