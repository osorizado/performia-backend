"""
Servicios de formularios
✅ CORREGIDO: Ahora carga las preguntas con joinedload Y actualiza las preguntas
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import List, Optional
from app.modules.formularios.models import Formulario, Pregunta
from app.modules.formularios.schemas import (
    FormularioCreate, FormularioUpdate,
    PreguntaCreate, PreguntaUpdate
)
from datetime import datetime


def get_formulario_by_id(db: Session, formulario_id: int) -> Optional[Formulario]:
    """Obtiene un formulario por ID con sus preguntas"""
    return db.query(Formulario)\
        .options(joinedload(Formulario.preguntas))\
        .filter(Formulario.id_formulario == formulario_id)\
        .first()


def get_formularios(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    tipo: Optional[str] = None,
    estado: Optional[str] = None,
    periodo: Optional[str] = None
) -> List[Formulario]:
    """
    Obtiene lista de formularios con filtros opcionales
    ✅ CORREGIDO: Ahora incluye las preguntas con joinedload
    """
    query = db.query(Formulario).options(joinedload(Formulario.preguntas))
    
    if tipo:
        query = query.filter(Formulario.tipo_formulario == tipo)
    if estado:
        query = query.filter(Formulario.estado == estado)
    if periodo:
        query = query.filter(Formulario.periodo == periodo)
    
    return query.offset(skip).limit(limit).all()


def create_formulario(
    db: Session, 
    formulario: FormularioCreate, 
    creado_por_id: int
) -> Formulario:
    """Crea un nuevo formulario con sus preguntas"""
    
    # Crear el formulario
    formulario_data = formulario.model_dump(exclude={'preguntas'})
    db_formulario = Formulario(
        **formulario_data,
        creado_por=creado_por_id
    )
    
    db.add(db_formulario)
    
    try:
        db.flush()
        
        # Crear las preguntas asociadas
        if formulario.preguntas:
            for idx, pregunta_data in enumerate(formulario.preguntas):
                # Convertir a dict y actualizar el orden
                pregunta_dict = pregunta_data.model_dump()
                pregunta_dict['orden'] = idx + 1
                
                db_pregunta = Pregunta(
                    id_formulario=db_formulario.id_formulario,
                    **pregunta_dict
                )
                db.add(db_pregunta)
        
        db.commit()
        db.refresh(db_formulario)
        return db_formulario
        
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear el formulario: {str(e)}"
        )


# ✅ FUNCIÓN CRÍTICA CORREGIDA
def update_formulario(
    db: Session, 
    formulario_id: int, 
    formulario_update: FormularioUpdate
) -> Formulario:
    """
    Actualiza un formulario existente
    ✅ CORREGIDO: Ahora también actualiza las preguntas
    """
    db_formulario = get_formulario_by_id(db, formulario_id)
    if not db_formulario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Formulario no encontrado"
        )
    
    # Actualizar los datos del formulario (excluyendo preguntas)
    update_data = formulario_update.model_dump(exclude_unset=True, exclude={'preguntas'})
    for field, value in update_data.items():
        setattr(db_formulario, field, value)
    
    db_formulario.fecha_modificacion = datetime.utcnow()
    
    # ✅ NUEVO: Actualizar preguntas si se enviaron
    if hasattr(formulario_update, 'preguntas') and formulario_update.preguntas is not None:
        print(f"🔄 Actualizando preguntas del formulario {formulario_id}")
        
        # 1. Eliminar todas las preguntas existentes
        db.query(Pregunta).filter(Pregunta.id_formulario == formulario_id).delete()
        
        # 2. Crear las nuevas preguntas
        for idx, pregunta_data in enumerate(formulario_update.preguntas):
            pregunta_dict = pregunta_data.model_dump() if hasattr(pregunta_data, 'model_dump') else pregunta_data
            pregunta_dict['orden'] = idx + 1
            
            print(f"  📝 Pregunta {idx + 1}: tipo='{pregunta_dict.get('tipo_pregunta')}', texto='{pregunta_dict.get('texto_pregunta')[:50]}...'")
            
            nueva_pregunta = Pregunta(
                id_formulario=formulario_id,
                **pregunta_dict
            )
            db.add(nueva_pregunta)
    
    try:
        db.commit()
        db.refresh(db_formulario)
        print(f"✅ Formulario {formulario_id} actualizado correctamente")
        return db_formulario
    except IntegrityError as e:
        db.rollback()
        print(f"❌ Error al actualizar formulario: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al actualizar el formulario"
        )


def delete_formulario(db: Session, formulario_id: int) -> dict:
    """Elimina un formulario (soft delete)"""
    db_formulario = get_formulario_by_id(db, formulario_id)
    if not db_formulario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Formulario no encontrado"
        )
    
    from app.modules.evaluaciones.models import Evaluacion
    evaluaciones_count = db.query(Evaluacion).filter(
        Evaluacion.id_formulario == formulario_id
    ).count()
    
    if evaluaciones_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede eliminar el formulario porque tiene {evaluaciones_count} evaluación(es) asociada(s)"
        )
    
    db_formulario.estado = "Archivado"
    db_formulario.fecha_modificacion = datetime.utcnow()
    db.commit()
    
    return {"message": "Formulario archivado exitosamente"}


def activar_formulario(db: Session, formulario_id: int) -> Formulario:
    """Activa un formulario"""
    db_formulario = get_formulario_by_id(db, formulario_id)
    if not db_formulario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Formulario no encontrado"
        )
    
    db_formulario.estado = "Activo"
    db_formulario.fecha_modificacion = datetime.utcnow()
    db.commit()
    db.refresh(db_formulario)
    
    return db_formulario


def duplicar_formulario(
    db: Session, 
    formulario_id: int, 
    nuevo_nombre: str,
    creado_por_id: int
) -> Formulario:
    """Duplica un formulario con todas sus preguntas"""
    formulario_original = get_formulario_by_id(db, formulario_id)
    if not formulario_original:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Formulario no encontrado"
        )
    
    nuevo_formulario = Formulario(
        nombre_formulario=nuevo_nombre,
        descripcion=formulario_original.descripcion,
        tipo_formulario=formulario_original.tipo_formulario,
        periodo=formulario_original.periodo,
        rol_aplicable=formulario_original.rol_aplicable,
        estado="Borrador",
        creado_por=creado_por_id
    )
    
    db.add(nuevo_formulario)
    db.flush()
    
    for pregunta_original in formulario_original.preguntas:
        nueva_pregunta = Pregunta(
            id_formulario=nuevo_formulario.id_formulario,
            texto_pregunta=pregunta_original.texto_pregunta,
            tipo_pregunta=pregunta_original.tipo_pregunta,
            peso=pregunta_original.peso,
            opciones=pregunta_original.opciones,
            orden=pregunta_original.orden,
            requerido=pregunta_original.requerido,
            competencia=pregunta_original.competencia
        )
        db.add(nueva_pregunta)
    
    try:
        db.commit()
        db.refresh(nuevo_formulario)
        return nuevo_formulario
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al duplicar el formulario"
        )


# ============================================================================
# SERVICIOS DE PREGUNTAS
# ============================================================================

def get_pregunta_by_id(db: Session, pregunta_id: int) -> Optional[Pregunta]:
    """Obtiene una pregunta por ID"""
    return db.query(Pregunta).filter(Pregunta.id_pregunta == pregunta_id).first()


def get_preguntas_by_formulario(db: Session, formulario_id: int) -> List[Pregunta]:
    """Obtiene todas las preguntas de un formulario ordenadas"""
    return db.query(Pregunta).filter(
        Pregunta.id_formulario == formulario_id
    ).order_by(Pregunta.orden).all()


def create_pregunta(db: Session, pregunta: PreguntaCreate) -> Pregunta:
    """Crea una nueva pregunta"""
    formulario = get_formulario_by_id(db, pregunta.id_formulario)
    if not formulario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Formulario no encontrado"
        )
    
    if pregunta.orden == 0:
        max_orden = db.query(Pregunta).filter(
            Pregunta.id_formulario == pregunta.id_formulario
        ).count()
        pregunta.orden = max_orden + 1
    
    db_pregunta = Pregunta(**pregunta.model_dump())
    db.add(db_pregunta)
    
    try:
        db.commit()
        db.refresh(db_pregunta)
        return db_pregunta
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al crear la pregunta"
        )


def update_pregunta(db: Session, pregunta_id: int, pregunta_update: PreguntaUpdate) -> Pregunta:
    """Actualiza una pregunta existente"""
    db_pregunta = get_pregunta_by_id(db, pregunta_id)
    if not db_pregunta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pregunta no encontrada"
        )
    
    update_data = pregunta_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_pregunta, field, value)
    
    try:
        db.commit()
        db.refresh(db_pregunta)
        return db_pregunta
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al actualizar la pregunta"
        )


def delete_pregunta(db: Session, pregunta_id: int) -> dict:
    """Elimina una pregunta"""
    db_pregunta = get_pregunta_by_id(db, pregunta_id)
    if not db_pregunta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pregunta no encontrada"
        )
    
    from app.modules.evaluaciones.models import Resultado
    resultados_count = db.query(Resultado).filter(
        Resultado.id_pregunta == pregunta_id
    ).count()
    
    if resultados_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede eliminar la pregunta porque tiene {resultados_count} respuesta(s) asociada(s)"
        )
    
    db.delete(db_pregunta)
    db.commit()
    
    return {"message": "Pregunta eliminada exitosamente"}


def reordenar_preguntas(db: Session, formulario_id: int, nuevos_ordenes: dict[int, int]) -> List[Pregunta]:
    """Reordena las preguntas de un formulario"""
    formulario = get_formulario_by_id(db, formulario_id)
    if not formulario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Formulario no encontrado"
        )
    
    for pregunta_id, nuevo_orden in nuevos_ordenes.items():
        pregunta = get_pregunta_by_id(db, pregunta_id)
        if pregunta and pregunta.id_formulario == formulario_id:
            pregunta.orden = nuevo_orden
    
    try:
        db.commit()
        return get_preguntas_by_formulario(db, formulario_id)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al reordenar las preguntas"
        )