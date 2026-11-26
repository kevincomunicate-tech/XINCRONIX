"""Métricas calculadas sobre los proyectos que una persona puede consultar."""

from django.db.models import Count
from django.utils import timezone

from .models import Proyecto, Tarea


def porcentaje(parte, total):
    return round(parte * 100 / total) if total else 0


def metricas_proyectos(proyectos):
    tareas = Tarea.objects.filter(proyecto__in=proyectos)
    total = tareas.count()
    hechas = tareas.filter(estado=Tarea.Estado.HECHA).count()
    return {
        "proyectos": proyectos.count(),
        "activos": proyectos.exclude(estado__in=[Proyecto.Estado.COMPLETADO, Proyecto.Estado.CANCELADO]).count(),
        "completados": proyectos.filter(estado=Proyecto.Estado.COMPLETADO).count(),
        "tareas": total,
        "hechas": hechas,
        "en_progreso": tareas.filter(estado=Tarea.Estado.EN_PROGRESO).count(),
        "vencidas": tareas.exclude(estado=Tarea.Estado.HECHA).filter(fecha_vencimiento__lt=timezone.localdate()).count(),
        "avance": porcentaje(hechas, total),
        "por_estado": tareas.values("estado").annotate(total=Count("pk")).order_by("estado"),
    }
