"""Métricas de una empresa, calculadas en la base de datos (nada se guarda duplicado)."""

from django.db.models import Count, Q
from django.utils import timezone

from .models import Proyecto, Tarea

EN_CURSO = [Proyecto.Estado.ACTIVO, Proyecto.Estado.PENDIENTE, Proyecto.Estado.EN_PROGRESO, Proyecto.Estado.EN_ESPERA]


def porcentaje(parte, total):
    return round(parte * 100 / total) if total else 0


def metricas_empresa(empresa):
    proyectos = Proyecto.objects.filter(empresa=empresa)
    tareas = Tarea.objects.filter(proyecto__empresa=empresa)
    completada = Q(estado=Tarea.Estado.COMPLETADA)

    resumen_proyectos = proyectos.aggregate(
        total=Count("pk"),
        activos=Count("pk", filter=Q(estado__in=EN_CURSO)),
        completados=Count("pk", filter=Q(estado=Proyecto.Estado.COMPLETADO)),
    )
    resumen_tareas = tareas.aggregate(
        total=Count("pk"),
        completadas=Count("pk", filter=completada),
        en_progreso=Count("pk", filter=Q(estado=Tarea.Estado.EN_PROGRESO)),
        vencidas=Count("pk", filter=~completada & Q(fecha_vencimiento__lt=timezone.localdate())),
    )
    por_proyecto = [
        {**p, "avance": porcentaje(p["hechas"], p["total"])}
        for p in proyectos.annotate(total=Count("tareas"), hechas=Count("tareas", filter=Q(tareas__estado=Tarea.Estado.COMPLETADA)))
        .values("pk", "nombre", "total", "hechas").order_by("-total", "nombre")[:8]
    ]

    return {
        "proyectos": resumen_proyectos["total"],
        "proyectos_activos": resumen_proyectos["activos"],
        "proyectos_completados": resumen_proyectos["completados"],
        "tareas": resumen_tareas["total"],
        "tareas_completadas": resumen_tareas["completadas"],
        "tareas_en_progreso": resumen_tareas["en_progreso"],
        "tareas_vencidas": resumen_tareas["vencidas"],
        "avance": porcentaje(resumen_tareas["completadas"], resumen_tareas["total"]),
        "integrantes": empresa.usuarios.filter(is_active=True).count(),
        "por_proyecto": por_proyecto,
    }
