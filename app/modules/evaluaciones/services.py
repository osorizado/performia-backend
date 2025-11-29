"""
Servicios de evaluaciones
Lógica de negocio para gestión de evaluaciones y resultados
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import datetime, date, timedelta
from decimal import Decimal

from app.modules.evaluaciones.models import Evaluacion, Resultado
from app.modules.evaluaciones.schemas import (
    EvaluacionCreate, EvaluacionUpdate, IniciarEvaluacionRequest, ResponderEvaluacionRequest,
    ResultadoCreate, ResultadoUpdate
)
from app.modules.formularios.models import Formulario, Pregunta
from app.modules.users.models import Usuario


# ============================================================================
# SERVICIOS DE EVALUACIONES
# ============================================================================

def get_evaluacion_by_id(db: Session, evaluacion_id: int) -> Optional[Evaluacion]:
    """Obtiene una evaluación por ID con todas sus relaciones"""
    return db.query(Evaluacion)\
        .options(
            joinedload(Evaluacion.formulario),
            joinedload(Evaluacion.evaluado),
            joinedload(Evaluacion.evaluador),
            joinedload(Evaluacion.resultados)
        )\
        .filter(Evaluacion.id_evaluacion == evaluacion_id)\
        .first()
def get_evaluaciones(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    id_evaluado: Optional[int] = None,
    id_evaluador: Optional[int] = None,
    estado: Optional[str] = None,
    periodo: Optional[str] = None,
    tipo: Optional[str] = None
) -> List[Evaluacion]:
    """Obtiene lista de evaluaciones con filtros opcionales"""
    query = db.query(Evaluacion)
    
    if id_evaluado:
        query = query.filter(Evaluacion.id_evaluado == id_evaluado)
    if id_evaluador:
        query = query.filter(Evaluacion.id_evaluador == id_evaluador)
    if estado:
        query = query.filter(Evaluacion.estado == estado)
    if periodo:
        query = query.filter(Evaluacion.periodo == periodo)
    if tipo:
        query = query.filter(Evaluacion.tipo_evaluacion == tipo)
    
    return query.offset(skip).limit(limit).all()


def iniciar_evaluacion(
    db: Session,
    request: IniciarEvaluacionRequest,
    evaluador_id: int
) -> Evaluacion:
    """Inicia una nueva evaluación"""
    
    # Verificar que el formulario existe y está activo
    formulario = db.query(Formulario).filter(
        Formulario.id_formulario == request.id_formulario
    ).first()
    
    if not formulario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Formulario no encontrado"
        )
    
    if formulario.estado != "Activo":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El formulario no está activo"
        )
    
    # Verificar que el evaluado existe
    evaluado = db.query(Usuario).filter(
        Usuario.id_usuario == request.id_evaluado
    ).first()
    
    if not evaluado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario evaluado no encontrado"
        )
    
    # Crear la evaluación
    db_evaluacion = Evaluacion(
        id_formulario=request.id_formulario,
        id_evaluado=request.id_evaluado,
        id_evaluador=evaluador_id,
        tipo_evaluacion=request.tipo_evaluacion,
        periodo=request.periodo,
        fecha_inicio=request.fecha_inicio,
        fecha_fin=request.fecha_fin,
        estado="Pendiente"
    )
    
    db.add(db_evaluacion)
    
    try:
        db.commit()
        db.refresh(db_evaluacion)
        return db_evaluacion
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al crear la evaluación"
        )


def responder_evaluacion(
    db: Session,
    evaluacion_id: int,
    request: ResponderEvaluacionRequest,
    evaluador_id: int
) -> Evaluacion:
    """Registra las respuestas de una evaluación"""
    
    # Obtener la evaluación
    evaluacion = get_evaluacion_by_id(db, evaluacion_id)
    if not evaluacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluación no encontrada"
        )
    
    # Verificar que el usuario tiene permiso para responder
    if evaluacion.id_evaluador != evaluador_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para responder esta evaluación"
        )
    
    # Verificar que la evaluación está en estado válido
    if evaluacion.estado not in ["Pendiente", "En Curso"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La evaluación está en estado '{evaluacion.estado}' y no puede ser respondida"
        )
    
    # Registrar o actualizar cada resultado
    for resultado_data in request.resultados:
        # Verificar que la pregunta existe y pertenece al formulario
        pregunta = db.query(Pregunta).filter(
            Pregunta.id_pregunta == resultado_data.id_pregunta,
            Pregunta.id_formulario == evaluacion.id_formulario
        ).first()
        
        if not pregunta:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Pregunta {resultado_data.id_pregunta} no pertenece a este formulario"
            )
        
        # Buscar si ya existe un resultado para esta pregunta
        resultado_existente = db.query(Resultado).filter(
            Resultado.id_evaluacion == evaluacion_id,
            Resultado.id_pregunta == resultado_data.id_pregunta
        ).first()
        
        if resultado_existente:
            # Actualizar resultado existente
            resultado_existente.respuesta = resultado_data.respuesta
            resultado_existente.puntaje = resultado_data.puntaje
            resultado_existente.comentario = resultado_data.comentario
            resultado_existente.fecha_registro = datetime.utcnow()
        else:
            # Crear nuevo resultado
            nuevo_resultado = Resultado(
                id_evaluacion=evaluacion_id,
                id_pregunta=resultado_data.id_pregunta,
                respuesta=resultado_data.respuesta,
                puntaje=resultado_data.puntaje,
                comentario=resultado_data.comentario
            )
            db.add(nuevo_resultado)
    
    # Actualizar estado de la evaluación
    evaluacion.estado = "En Curso"
    evaluacion.observaciones_generales = request.observaciones_generales
    evaluacion.fecha_modificacion = datetime.utcnow()
    
    try:
        db.commit()
        db.refresh(evaluacion)
        return evaluacion
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al registrar las respuestas"
        )


def completar_evaluacion(db: Session, evaluacion_id: int, evaluador_id: int) -> Evaluacion:
    """Marca una evaluación como completada y calcula el puntaje total"""
    
    evaluacion = get_evaluacion_by_id(db, evaluacion_id)
    if not evaluacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluación no encontrada"
        )
    
    # Verificar permisos
    if evaluacion.id_evaluador != evaluador_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para completar esta evaluación"
        )
    
    # Verificar que todas las preguntas requeridas tienen respuesta
    preguntas_requeridas = db.query(Pregunta).filter(
        Pregunta.id_formulario == evaluacion.id_formulario,
        Pregunta.requerido == True
    ).all()
    
    resultados_registrados = db.query(Resultado).filter(
        Resultado.id_evaluacion == evaluacion_id
    ).all()
    
    preguntas_respondidas = {r.id_pregunta for r in resultados_registrados}
    preguntas_faltantes = [
        p.id_pregunta for p in preguntas_requeridas 
        if p.id_pregunta not in preguntas_respondidas
    ]
    
    if preguntas_faltantes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Faltan responder {len(preguntas_faltantes)} pregunta(s) requerida(s)"
        )
    
    # Calcular puntaje total ponderado
    puntaje_total = calcular_puntaje_evaluacion(db, evaluacion_id)
    
    # Actualizar evaluación
    evaluacion.estado = "Completada"
    evaluacion.puntaje_total = puntaje_total
    evaluacion.fecha_fin = date.today()
    evaluacion.fecha_modificacion = datetime.utcnow()
    
    db.commit()
    db.refresh(evaluacion)
    
    return evaluacion


def calcular_puntaje_evaluacion(db: Session, evaluacion_id: int) -> Decimal:
    """Calcula el puntaje total ponderado de una evaluación"""
    
    # Obtener todos los resultados con sus preguntas
    resultados = db.query(Resultado, Pregunta).join(
        Pregunta, Resultado.id_pregunta == Pregunta.id_pregunta
    ).filter(
        Resultado.id_evaluacion == evaluacion_id
    ).all()
    
    if not resultados:
        return Decimal('0.00')
    
    suma_ponderada = Decimal('0.00')
    suma_pesos = Decimal('0.00')
    
    for resultado, pregunta in resultados:
        if resultado.puntaje is not None:
            suma_ponderada += Decimal(str(resultado.puntaje)) * Decimal(str(pregunta.peso))
            suma_pesos += Decimal(str(pregunta.peso))
    
    if suma_pesos == 0:
        return Decimal('0.00')
    
    puntaje_final = suma_ponderada / suma_pesos
    return round(puntaje_final, 2)


def cancelar_evaluacion(db: Session, evaluacion_id: int, motivo: str = None) -> Evaluacion:
    """Cancela una evaluación"""
    
    evaluacion = get_evaluacion_by_id(db, evaluacion_id)
    if not evaluacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluación no encontrada"
        )
    
    if evaluacion.estado == "Completada":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede cancelar una evaluación completada"
        )
    
    evaluacion.estado = "Cancelada"
    if motivo:
        evaluacion.observaciones_generales = f"CANCELADA: {motivo}"
    evaluacion.fecha_modificacion = datetime.utcnow()
    
    db.commit()
    db.refresh(evaluacion)
    
    return evaluacion


def get_evaluaciones_pendientes(db: Session, evaluador_id: int) -> List[Evaluacion]:
    """Obtiene las evaluaciones pendientes de un evaluador"""
    from sqlalchemy.orm import joinedload
    
    return db.query(Evaluacion).options(
        joinedload(Evaluacion.formulario)  # ⭐ Cargar el formulario relacionado
    ).filter(
        Evaluacion.id_evaluador == evaluador_id,
        Evaluacion.estado.in_(["Pendiente", "En Curso"])
    ).order_by(Evaluacion.fecha_fin).all()


def get_mis_evaluaciones(db: Session, usuario_id: int) -> List[Evaluacion]:
    """Obtiene todas las evaluaciones donde el usuario es el evaluado"""
    return db.query(Evaluacion).filter(
        Evaluacion.id_evaluado == usuario_id
    ).order_by(Evaluacion.fecha_creacion.desc()).all()


def get_evaluaciones_por_periodo(db: Session, periodo: str) -> List[Evaluacion]:
    """Obtiene todas las evaluaciones de un periodo específico"""
    return db.query(Evaluacion).filter(
        Evaluacion.periodo == periodo
    ).all()


def asignar_evaluacion_masiva(
    db: Session,
    request,  # AsignarEvaluacionMasivaRequest
    current_user_id: int
) -> dict:
    """
    Asigna un formulario a todos los usuarios de un rol específico
    """
    # Validar que el formulario existe
    formulario = db.query(Formulario).filter(
        Formulario.id_formulario == request.id_formulario
    ).first()
    
    if not formulario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Formulario no encontrado"
        )
    
    # Validar que el formulario esté activo
    if formulario.estado != 'Activo':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se pueden asignar formularios activos"
        )
    
    # Obtener todos los usuarios del rol especificado que estén activos
    usuarios = db.query(Usuario).filter(
        Usuario.id_rol == request.rol_id,
        Usuario.estado == 'Activo'
    ).all()
    
    if not usuarios:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontraron usuarios activos con el rol ID {request.rol_id}"
        )
    
    evaluaciones_creadas = []
    evaluaciones_existentes = []
    
    fecha_inicio = date.today()
    fecha_fin = fecha_inicio + timedelta(days=request.dias_plazo)
    
    # Crear una evaluación para cada usuario
    for usuario in usuarios:
        # Verificar si ya existe una evaluación pendiente o en curso para este usuario
        evaluacion_existente = db.query(Evaluacion).filter(
            Evaluacion.id_formulario == request.id_formulario,
            Evaluacion.id_evaluado == usuario.id_usuario,
            Evaluacion.periodo == request.periodo,
            Evaluacion.estado.in_(['Pendiente', 'En Curso'])
        ).first()
        
        if evaluacion_existente:
            evaluaciones_existentes.append({
                'usuario_id': usuario.id_usuario,
                'nombre': f"{usuario.nombre} {usuario.apellido}",
                'correo': usuario.correo,
                'razon': 'Ya tiene una evaluación pendiente o en curso'
            })
            continue
        
        # Crear nueva evaluación
        nueva_evaluacion = Evaluacion(
            id_formulario=request.id_formulario,
            id_evaluado=usuario.id_usuario,
            id_evaluador=usuario.id_usuario,  # Para autoevaluación
            tipo_evaluacion=request.tipo_evaluacion,
            periodo=request.periodo,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            estado='Pendiente'
        )
        
        db.add(nueva_evaluacion)
        evaluaciones_creadas.append({
            'usuario_id': usuario.id_usuario,
            'nombre': f"{usuario.nombre} {usuario.apellido}",
            'correo': usuario.correo
        })
    
    try:
        db.commit()
        
        return {
            "success": True,
            "message": f"Se asignaron {len(evaluaciones_creadas)} evaluaciones exitosamente",
            "total_usuarios": len(usuarios),
            "evaluaciones_creadas": evaluaciones_creadas,
            "evaluaciones_existentes": evaluaciones_existentes,
            "formulario_nombre": formulario.nombre_formulario,
            "periodo": request.periodo,
            "fecha_inicio": str(fecha_inicio),
            "fecha_fin": str(fecha_fin)
        }
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al asignar evaluaciones: {str(e)}"
        )


# ============================================================================
# SERVICIOS DE RESULTADOS
# ============================================================================

def get_resultado_by_id(db: Session, resultado_id: int) -> Optional[Resultado]:
    """Obtiene un resultado por ID"""
    return db.query(Resultado).filter(Resultado.id_resultado == resultado_id).first()


def get_resultados_by_evaluacion(db: Session, evaluacion_id: int) -> List[Resultado]:
    """Obtiene todos los resultados de una evaluación"""
    return db.query(Resultado).filter(
        Resultado.id_evaluacion == evaluacion_id
    ).all()


def update_resultado(
    db: Session,
    resultado_id: int,
    resultado_update: ResultadoUpdate
) -> Resultado:
    """Actualiza un resultado"""
    
    resultado = get_resultado_by_id(db, resultado_id)
    if not resultado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resultado no encontrado"
        )
    
    # Verificar que la evaluación no esté completada
    evaluacion = get_evaluacion_by_id(db, resultado.id_evaluacion)
    if evaluacion.estado == "Completada":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede modificar una evaluación completada"
        )
    
    # Actualizar campos
    update_data = resultado_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(resultado, field, value)
    
    resultado.fecha_registro = datetime.utcnow()
    
    try:
        db.commit()
        db.refresh(resultado)
        return resultado
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al actualizar el resultado"
        )
def get_evaluaciones_asignadas(
    db: Session, 
    usuario_id: int,
    skip: int = 0,
    limit: int = 100,
    estado: Optional[str] = None,
    periodo: Optional[str] = None
) -> List[Evaluacion]:
    """
    Obtiene las evaluaciones creadas/asignadas por un usuario específico
    Útil para RRHH, Managers y Directores para ver qué evaluaciones han asignado
    """
    query = db.query(Evaluacion).join(
        Formulario, Evaluacion.id_formulario == Formulario.id_formulario
    ).filter(
        Formulario.creado_por == usuario_id
    )
    
    # Aplicar filtros opcionales
    if estado:
        query = query.filter(Evaluacion.estado == estado)
    
    if periodo:
        query = query.filter(Evaluacion.periodo == periodo)
    
    # Ordenar por fecha de creación descendente
    query = query.order_by(Evaluacion.fecha_creacion.desc())
    
    return query.offset(skip).limit(limit).all()

# ============================================================================
# NUEVAS FUNCIONES PARA MANAGERS
# ============================================================================

def get_evaluaciones_equipo(
    db: Session, 
    manager_id: int,
    skip: int = 0,
    limit: int = 100,
    estado: Optional[str] = None,
    periodo: Optional[str] = None,
    tipo: Optional[str] = None
) -> List[Evaluacion]:
    """Obtiene las evaluaciones de los colaboradores directos de un manager"""
    from sqlalchemy.orm import joinedload
    from app.modules.users.models import Usuario
    
    colaboradores = db.query(Usuario.id_usuario).filter(
        Usuario.manager_id == manager_id,
        Usuario.estado == 'Activo'
    ).all()
    
    colaboradores_ids = [c.id_usuario for c in colaboradores]
    
    if not colaboradores_ids:
        return []
    
    query = db.query(Evaluacion).options(
        joinedload(Evaluacion.formulario),
        joinedload(Evaluacion.evaluado),
        joinedload(Evaluacion.evaluador)
    ).filter(
        Evaluacion.id_evaluado.in_(colaboradores_ids)
    )
    
    if estado:
        query = query.filter(Evaluacion.estado == estado)
    
    if periodo:
        query = query.filter(Evaluacion.periodo == periodo)
        
    if tipo:
        query = query.filter(Evaluacion.tipo_evaluacion == tipo)
    
    query = query.order_by(Evaluacion.fecha_fin.asc())
    
    return query.offset(skip).limit(limit).all()


def get_evaluaciones_pendientes_equipo(db: Session, manager_id: int) -> List[Evaluacion]:
    """Obtiene SOLO las evaluaciones pendientes que el manager debe completar"""
    from sqlalchemy.orm import joinedload
    from app.modules.users.models import Usuario
    
    colaboradores = db.query(Usuario.id_usuario).filter(
        Usuario.manager_id == manager_id,
        Usuario.estado == 'Activo'
    ).all()
    
    colaboradores_ids = [c.id_usuario for c in colaboradores]
    
    if not colaboradores_ids:
        return []
    
    return db.query(Evaluacion).options(
        joinedload(Evaluacion.formulario),
        joinedload(Evaluacion.evaluado)
    ).filter(
        Evaluacion.id_evaluador == manager_id,
        Evaluacion.id_evaluado.in_(colaboradores_ids),
        Evaluacion.estado.in_(["Pendiente", "En Curso"])
    ).order_by(Evaluacion.fecha_fin.asc()).all()


def get_autoevaluaciones_equipo(db: Session, manager_id: int, estado: Optional[str] = None) -> List[Evaluacion]:
    """Obtiene las autoevaluaciones de los colaboradores del manager"""
    from sqlalchemy.orm import joinedload
    from app.modules.users.models import Usuario
    
    colaboradores = db.query(Usuario.id_usuario).filter(
        Usuario.manager_id == manager_id,
        Usuario.estado == 'Activo'
    ).all()
    
    colaboradores_ids = [c.id_usuario for c in colaboradores]
    
    if not colaboradores_ids:
        return []
    
    query = db.query(Evaluacion).options(
        joinedload(Evaluacion.formulario),
        joinedload(Evaluacion.evaluado)
    ).filter(
        Evaluacion.id_evaluado.in_(colaboradores_ids),
        Evaluacion.tipo_evaluacion == 'Autoevaluación',
        Evaluacion.id_evaluador == Evaluacion.id_evaluado
    )
    
    if estado:
        query = query.filter(Evaluacion.estado == estado)
    
    return query.order_by(Evaluacion.fecha_fin.desc()).all()