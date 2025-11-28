"""
Rutas de reportes y notificaciones
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user, require_role
from app.modules.users.models import Usuario
from app.modules.reportes.schemas import (
    NotificacionResponse, 
    ReporteCreate, 
    ReporteResponse,
    EstadisticasGenerales,
    EstadisticasCompetencias,
    FiltrosReporte
)
from app.modules.reportes import services

# ========================================
# ROUTER DE NOTIFICACIONES
# ========================================
router_notificaciones = APIRouter(prefix="/notificaciones", tags=["Notificaciones"])


@router_notificaciones.get("/", response_model=List[NotificacionResponse])
def mis_notificaciones(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtiene las notificaciones del usuario actual"""
    return services.get_mis_notificaciones(db, current_user.id_usuario)


@router_notificaciones.post("/{notif_id}/marcar-leida", response_model=NotificacionResponse)
def marcar_leida(
    notif_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Marca una notificación como leída"""
    return services.marcar_notificacion_leida(db, notif_id)


# ========================================
# ROUTER DE REPORTES
# ========================================
router_reportes = APIRouter(prefix="/reportes", tags=["Reportes"])


@router_reportes.get("/estadisticas-generales", response_model=EstadisticasGenerales)
def obtener_estadisticas_generales(
    periodo: Optional[str] = Query(None, description="Período: '2024-Q1', '2024-01', 'Anual 2024'"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("Administrador", "RRHH", "Director"))  # ✅ AGREGADO "Director"
):
    """
    Obtiene estadísticas generales del sistema:
    - Promedio general
    - Total de evaluaciones completadas
    - Tasa de completitud
    - Top performers
    """
    return services.get_estadisticas_generales(db, periodo)


@router_reportes.get("/estadisticas-competencias", response_model=List[EstadisticasCompetencias])
def obtener_estadisticas_competencias(
    periodo: Optional[str] = Query(None),
    area: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("Administrador", "RRHH", "Director"))  # ✅ AGREGADO "Director"
):
    """
    Obtiene el promedio de calificación por competencia.
    Útil para gráficos de radar.
    """
    return services.get_estadisticas_competencias(db, periodo, area)


@router_reportes.get("/distribucion-calificaciones")
def obtener_distribucion_calificaciones(
    periodo: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("Administrador", "RRHH", "Director"))  # ✅ AGREGADO "Director"
):
    """
    Obtiene la distribución de colaboradores por rango de calificación.
    Retorna: { "1.0-2.0": 5, "2.1-3.0": 12, "3.1-4.0": 45, "4.1-5.0": 90 }
    """
    return services.get_distribucion_calificaciones(db, periodo)


@router_reportes.get("/top-performers")
def obtener_top_performers(
    limite: int = Query(10, ge=1, le=50),
    periodo: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("Administrador", "RRHH", "Director"))  # ✅ AGREGADO "Director"
):
    """
    Obtiene el ranking de los mejores colaboradores.
    Retorna lista con: nombre, área, promedio, evaluaciones_completas
    """
    return services.get_top_performers(db, limite, periodo)


@router_reportes.get("/areas-ranking")
def obtener_areas_ranking(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("Administrador", "RRHH", "Director"))  # ✅ AGREGADO "Director"
):
    """
    Obtiene el ranking de áreas por desempeño promedio.
    """
    return services.get_areas_ranking(db)


@router_reportes.post("/generar")
def generar_reporte(
    filtros: FiltrosReporte,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("Administrador", "RRHH", "Director"))  # ✅ AGREGADO "Director"
):
    """
    Genera un reporte según los filtros especificados y lo descarga automáticamente.
    Tipos disponibles: 'Individual', 'Por Área', 'Global', 'Comparativo', 'Histórico'
    Formatos: 'PDF', 'Excel'
    """
    import os
    from datetime import datetime
    
    # Generar el reporte
    reporte = services.generar_reporte(db, filtros, current_user.id_usuario)
    
    # Verificar que el archivo existe
    if not reporte.ruta_archivo or not os.path.exists(reporte.ruta_archivo):
        raise HTTPException(status_code=500, detail="Error al generar el archivo del reporte")
    
    # Determinar el media type según el formato
    if filtros.formato == "PDF":
        media_type = "application/pdf"
    elif filtros.formato == "Excel":
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    else:
        media_type = "application/octet-stream"
    
    # Nombre del archivo para descarga
    extension = "pdf" if filtros.formato == "PDF" else "xlsx"
    filename = f"Reporte_{filtros.tipo_reporte.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{extension}"
    
    # Devolver el archivo para descarga automática
    return FileResponse(
        path=reporte.ruta_archivo,
        filename=filename,
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router_reportes.get("/descargar/{reporte_id}")
def descargar_reporte(
    reporte_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("Administrador", "RRHH", "Director"))  # ✅ AGREGADO "Director"
):
    """
    Descarga un reporte previamente generado.
    """
    reporte = services.get_reporte_by_id(db, reporte_id)
    
    if not reporte:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    
    if not reporte.ruta_archivo:
        raise HTTPException(status_code=404, detail="Archivo de reporte no disponible")
    
    return FileResponse(
        path=reporte.ruta_archivo,
        filename=f"{reporte.nombre_reporte}.{reporte.formato.lower()}",
        media_type="application/octet-stream"
    )


@router_reportes.get("/historial", response_model=List[ReporteResponse])
def obtener_historial_reportes(
    limite: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("Administrador", "RRHH", "Director"))  # ✅ AGREGADO "Director"
):
    """
    Obtiene el historial de reportes generados.
    """
    return services.get_historial_reportes(db, limite)


@router_reportes.delete("/{reporte_id}")
def eliminar_reporte(
    reporte_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("Administrador", "RRHH", "Director"))  # ✅ AGREGADO "Director"
):
    """
    Elimina un reporte del historial (soft delete).
    """
    success = services.eliminar_reporte(db, reporte_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    
    return {"message": "Reporte eliminado correctamente"}