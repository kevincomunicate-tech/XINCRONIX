from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.shortcuts import render
from django.utils import timezone

from .models import Actividad, Proyecto, Tarea


@login_required
def panel(request):
    usuario = request.user
    hoy = timezone.localdate()
    inicio_semana = hoy - timedelta(days=hoy.weekday())  # lunes
    inicio_mes = hoy.replace(day=1)

    proyectos = Proyecto.objects.visibles_para(usuario)
    tareas = Tarea.objects.filter(proyecto__in=proyectos)
    completadas = tareas.filter(estado=Tarea.Estado.COMPLETADA)
    mis_pendientes = tareas.filter(asignada_a=usuario).exclude(estado=Tarea.Estado.COMPLETADA)

    estadisticas = {
        "proyectos_activos": proyectos.filter(estado=Proyecto.Estado.ACTIVO).count(),
        "proyectos_este_mes": proyectos.filter(fecha_creacion__date__gte=inicio_mes).count(),
        "tareas_completadas": completadas.count(),
        "completadas_semana": completadas.filter(fecha_completada__date__gte=inicio_semana).count(),
        "mis_pendientes": mis_pendientes.count(),
        "mis_vencidas": mis_pendientes.filter(fecha_vencimiento__lt=hoy).count(),
    }

    # Actividad de la empresa, solo de los proyectos que el usuario puede ver
    actividades = Actividad.objects.filter(proyecto__in=proyectos).select_related("usuario")[:6]
    # Orden explícito: Django no aplica Meta.ordering a consultas que agrupan (Count)
    progreso = (
        proyectos.filter(estado=Proyecto.Estado.ACTIVO)
        .con_progreso()
        .order_by("-nivel_importancia", "nombre")[:5]
    )

    return render(request, "dashboard/panel.html", {
        "estadisticas": estadisticas,
        "actividades": actividades,
        "progreso": progreso,
        # Las tareas sin fecha van al final; a igual fecha, la más urgente primero
        "proximas": mis_pendientes.select_related("proyecto")
        .order_by(F("fecha_vencimiento").asc(nulls_last=True), Tarea.orden_prioridad().desc())[:5],
        "sin_empresa": usuario.empresa_id is None,
    })


@login_required
def proximamente(request, seccion):
    return render(request, "dashboard/proximamente.html", {"seccion": seccion})
