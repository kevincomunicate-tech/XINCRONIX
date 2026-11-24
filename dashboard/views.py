from datetime import timedelta
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from cuentas.forms import (
    EquipoForm,
    MiembroForm,
    ProyectoForm,
    ReferenciaGitHubForm,
    TareaForm,
)
from cuentas.models import Equipo, Usuario
from .models import Proyecto, ReferenciaGitHub, Tarea


def _empresa(usuario):
    if not usuario.empresa_id:
        raise PermissionDenied("Esta cuenta no pertenece a un espacio de trabajo.")
    return usuario.empresa


def requiere_empresa(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        _empresa(request.user)
        return view(request, *args, **kwargs)

    return wrapped


def _administrador_equipo(usuario):
    return usuario.rol in {Usuario.Rol.ADMIN, Usuario.Rol.MANAGER}


def _proyectos_visibles(usuario):
    proyectos = Proyecto.objects.filter(empresa_id=usuario.empresa_id)
    if usuario.rol == Usuario.Rol.COLABORADOR:
        proyectos = proyectos.filter(miembros=usuario)
    return proyectos.distinct()


def _puede_editar_proyecto(usuario, proyecto):
    return usuario.rol in {Usuario.Rol.ADMIN, Usuario.Rol.MANAGER} or (
        usuario.rol == Usuario.Rol.COLABORADOR
        and proyecto.miembros.filter(pk=usuario.pk).exists()
    )


def _formulario(request, form, titulo, cancelar, plantilla="dashboard/formulario.html"):
    return render(
        request,
        plantilla,
        {"form": form, "titulo": titulo, "cancelar": cancelar},
    )


@login_required
@requiere_empresa
def panel(request):
    proyectos = _proyectos_visibles(request.user)
    tareas = Tarea.objects.filter(proyecto__in=proyectos)
    contexto = {
        "cantidad_proyectos": proyectos.count(),
        "cantidad_tareas": tareas.count(),
        "tareas_completadas": tareas.filter(estado=Tarea.Estado.COMPLETADA).count(),
        "tareas_vencidas": tareas.exclude(estado=Tarea.Estado.COMPLETADA)
        .filter(fecha_limite__lt=timezone.localdate())
        .count(),
        "proyectos_recientes": proyectos.annotate(cantidad_tareas=Count("tareas"))
        .order_by("-actualizado_en")[:5],
        "tareas_recientes": tareas.select_related("proyecto", "responsable")[:6],
        "cantidad_miembros": Usuario.objects.filter(
            empresa=request.user.empresa, is_active=True
        ).count(),
        "cantidad_equipos": Equipo.objects.filter(empresa=request.user.empresa).count(),
    }
    return render(request, "dashboard/panel.html", contexto)


@login_required
@requiere_empresa
def analytics(request):
    proyectos = _proyectos_visibles(request.user)
    tareas = Tarea.objects.filter(proyecto__in=proyectos)
    total_proyectos = proyectos.count()
    total_tareas = tareas.count()
    fecha_hoy = timezone.localdate()

    conteo_proyectos = dict(
        proyectos.values("estado")
        .annotate(total=Count("pk"))
        .values_list("estado", "total")
    )
    estadisticas_proyectos = [
        {
            "nombre": nombre,
            "total": conteo_proyectos.get(estado, 0),
            "porcentaje": round(conteo_proyectos.get(estado, 0) * 100 / total_proyectos)
            if total_proyectos
            else 0,
        }
        for estado, nombre in Proyecto.Estado.choices
    ]

    conteo_tareas = dict(
        tareas.values("estado")
        .annotate(total=Count("pk"))
        .values_list("estado", "total")
    )
    estadisticas_tareas = [
        {
            "nombre": nombre,
            "total": conteo_tareas.get(estado, 0),
            "porcentaje": round(conteo_tareas.get(estado, 0) * 100 / total_tareas)
            if total_tareas
            else 0,
        }
        for estado, nombre in Tarea.Estado.choices
    ]

    proyectos_destacados = list(
        proyectos.annotate(
            total_tareas=Count("tareas", distinct=True),
            tareas_completadas=Count(
                "tareas",
                filter=Q(tareas__estado=Tarea.Estado.COMPLETADA),
                distinct=True,
            ),
        ).order_by("-total_tareas", "nombre")[:5]
    )
    for proyecto in proyectos_destacados:
        proyecto.porcentaje_completado = (
            round(proyecto.tareas_completadas * 100 / proyecto.total_tareas)
            if proyecto.total_tareas
            else 0
        )

    tareas_proximas = (
        tareas.exclude(estado=Tarea.Estado.COMPLETADA)
        .filter(fecha_limite__gte=fecha_hoy, fecha_limite__lte=fecha_hoy + timedelta(days=7))
        .select_related("proyecto", "responsable")
        .order_by("fecha_limite", "titulo")[:6]
    )

    contexto = {
        "cantidad_proyectos": total_proyectos,
        "cantidad_tareas": total_tareas,
        "porcentaje_completadas": (
            round(conteo_tareas.get(Tarea.Estado.COMPLETADA, 0) * 100 / total_tareas)
            if total_tareas
            else 0
        ),
        "tareas_vencidas": tareas.exclude(estado=Tarea.Estado.COMPLETADA)
        .filter(fecha_limite__lt=fecha_hoy)
        .count(),
        "estadisticas_proyectos": estadisticas_proyectos,
        "estadisticas_tareas": estadisticas_tareas,
        "proyectos_destacados": proyectos_destacados,
        "tareas_proximas": tareas_proximas,
    }
    return render(request, "dashboard/analytics.html", contexto)


@login_required
def proximamente(request, seccion):
    return render(request, "dashboard/proximamente.html", {"seccion": seccion})


@login_required
@requiere_empresa
def equipos(request):
    equipos_empresa = Equipo.objects.filter(empresa=request.user.empresa).annotate(
        cantidad_miembros=Count("miembros", distinct=True),
        cantidad_proyectos=Count("proyectos", distinct=True),
    )
    return render(
        request,
        "dashboard/equipos.html",
        {
            "equipos": equipos_empresa,
            "puede_administrar": _administrador_equipo(request.user),
        },
    )


@login_required
@requiere_empresa
def equipo_crear(request):
    if not _administrador_equipo(request.user):
        raise PermissionDenied
    form = EquipoForm(
        request.POST or None,
        empresa=request.user.empresa,
    )
    if request.method == "POST" and form.is_valid():
        equipo = form.save(commit=False)
        equipo.empresa = request.user.empresa
        equipo.creado_por = request.user
        equipo.save()
        form.save_m2m()
        messages.success(request, "El equipo se creó correctamente.")
        return redirect("equipo")
    return _formulario(request, form, "Crear equipo", "equipo")


@login_required
@requiere_empresa
def equipo_editar(request, equipo_id):
    if not _administrador_equipo(request.user):
        raise PermissionDenied
    equipo = get_object_or_404(Equipo, pk=equipo_id, empresa=request.user.empresa)
    form = EquipoForm(request.POST or None, instance=equipo, empresa=request.user.empresa)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "El equipo se actualizó correctamente.")
        return redirect("equipo")
    return _formulario(request, form, "Editar equipo", "equipo")


@login_required
@requiere_empresa
def equipo_eliminar(request, equipo_id):
    if not _administrador_equipo(request.user):
        raise PermissionDenied
    equipo = get_object_or_404(Equipo, pk=equipo_id, empresa=request.user.empresa)
    if request.method == "POST":
        equipo.delete()
        messages.success(request, "El equipo se eliminó correctamente.")
        return redirect("equipo")
    return render(
        request,
        "dashboard/confirmar_eliminacion.html",
        {"objeto": equipo, "titulo": "Eliminar equipo", "cancelar": "equipo"},
    )


@login_required
@requiere_empresa
def miembros(request):
    integrantes = Usuario.objects.filter(empresa=request.user.empresa).prefetch_related("equipos")
    return render(
        request,
        "dashboard/miembros.html",
        {
            "miembros": integrantes,
            "puede_administrar": _administrador_equipo(request.user),
        },
    )


def _puede_administrar_miembro(actor, miembro):
    if not _administrador_equipo(actor) or miembro.is_superuser:
        return False
    if actor.rol == Usuario.Rol.MANAGER and miembro.rol in {
        Usuario.Rol.ADMIN,
        Usuario.Rol.MANAGER,
    }:
        return False
    return miembro.empresa_id == actor.empresa_id


@login_required
@requiere_empresa
def miembro_crear(request):
    if not _administrador_equipo(request.user):
        raise PermissionDenied
    form = MiembroForm(request.POST or None, empresa=request.user.empresa, actor=request.user)
    if request.method == "POST" and form.is_valid():
        miembro = form.save()
        messages.success(request, f"Se agregó a {miembro.get_full_name() or miembro.email} al equipo.")
        return redirect("miembros")
    return _formulario(request, form, "Agregar integrante", "miembros")


@login_required
@requiere_empresa
def miembro_editar(request, miembro_id):
    miembro = get_object_or_404(Usuario, pk=miembro_id, empresa=request.user.empresa)
    if not _puede_administrar_miembro(request.user, miembro):
        raise PermissionDenied
    rol_original = miembro.rol
    form = MiembroForm(
        request.POST or None,
        instance=miembro,
        empresa=request.user.empresa,
        actor=request.user,
    )
    if request.method == "POST" and form.is_valid():
        ultimo_administrador = (
            miembro.is_active
            and rol_original == Usuario.Rol.ADMIN
            and form.cleaned_data["rol"] != Usuario.Rol.ADMIN
            and Usuario.objects.filter(
                empresa=request.user.empresa,
                rol=Usuario.Rol.ADMIN,
                is_active=True,
            ).count()
            <= 1
        )
        if ultimo_administrador:
            form.add_error("rol", "La empresa debe conservar al menos un administrador activo.")
        else:
            miembro = form.save()
            messages.success(request, f"Se actualizó a {miembro.get_full_name() or miembro.email}.")
            return redirect("miembros")
    return _formulario(request, form, "Editar integrante", "miembros")


@login_required
@requiere_empresa
def miembro_eliminar(request, miembro_id):
    miembro = get_object_or_404(Usuario, pk=miembro_id, empresa=request.user.empresa)
    if miembro.pk == request.user.pk or not _puede_administrar_miembro(request.user, miembro):
        raise PermissionDenied
    if miembro.rol == Usuario.Rol.ADMIN and Usuario.objects.filter(
        empresa=request.user.empresa, rol=Usuario.Rol.ADMIN, is_active=True
    ).count() <= 1:
        raise PermissionDenied("No se puede desactivar al único administrador de la empresa.")
    if request.method == "POST":
        miembro.is_active = False
        miembro.save(update_fields=("is_active",))
        messages.success(request, "El integrante se desactivó; su historial se conservó.")
        return redirect("miembros")
    return render(
        request,
        "dashboard/confirmar_eliminacion.html",
        {
            "objeto": miembro,
            "titulo": "Desactivar integrante",
            "cancelar": "miembros",
            "aviso": "La cuenta no podrá iniciar sesión. Su historial se conservará.",
        },
    )


@login_required
@requiere_empresa
def proyectos(request):
    lista = _proyectos_visibles(request.user).annotate(
        cantidad_tareas=Count("tareas", distinct=True),
        cantidad_miembros=Count("miembros", distinct=True),
    )
    filas = [
        {"proyecto": proyecto, "editable": _puede_editar_proyecto(request.user, proyecto)}
        for proyecto in lista
    ]
    return render(
        request,
        "dashboard/proyectos.html",
        {
            "proyectos": filas,
        },
    )


@login_required
@requiere_empresa
def proyecto_crear(request):
    form = ProyectoForm(request.POST or None, empresa=request.user.empresa)
    if request.method == "POST" and form.is_valid():
        proyecto = form.save(commit=False)
        proyecto.empresa = request.user.empresa
        proyecto.creado_por = request.user
        proyecto.save()
        form.save_m2m()
        proyecto.miembros.add(request.user)
        messages.success(request, "El proyecto se creó correctamente.")
        return redirect("proyectos")
    return _formulario(request, form, "Crear proyecto", "proyectos")


@login_required
@requiere_empresa
def proyecto_editar(request, proyecto_id):
    proyecto = get_object_or_404(_proyectos_visibles(request.user), pk=proyecto_id)
    if not _puede_editar_proyecto(request.user, proyecto):
        raise PermissionDenied
    form = ProyectoForm(request.POST or None, instance=proyecto, empresa=request.user.empresa)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "El proyecto se actualizó correctamente.")
        return redirect("proyectos")
    return _formulario(request, form, "Editar proyecto", "proyectos")


@login_required
@requiere_empresa
def proyecto_eliminar(request, proyecto_id):
    proyecto = get_object_or_404(_proyectos_visibles(request.user), pk=proyecto_id)
    if not _puede_editar_proyecto(request.user, proyecto):
        raise PermissionDenied
    if request.method == "POST":
        proyecto.delete()
        messages.success(request, "El proyecto y sus tareas se eliminaron correctamente.")
        return redirect("proyectos")
    return render(
        request,
        "dashboard/confirmar_eliminacion.html",
        {"objeto": proyecto, "titulo": "Eliminar proyecto", "cancelar": "proyectos"},
    )


@login_required
@requiere_empresa
def github_referencias(request, proyecto_id):
    proyecto = get_object_or_404(_proyectos_visibles(request.user), pk=proyecto_id)
    editable = _puede_editar_proyecto(request.user, proyecto)
    form = None
    if request.method == "POST":
        if not editable:
            raise PermissionDenied
        if not proyecto.repositorio_url:
            raise PermissionDenied("Vincula un repositorio público antes de agregar referencias.")
        form = ReferenciaGitHubForm(request.POST, proyecto=proyecto)
        if form.is_valid():
            referencia = form.save(commit=False)
            referencia.proyecto = proyecto
            referencia.creado_por = request.user
            referencia.save()
            messages.success(request, "La referencia de GitHub se agregó al proyecto.")
            return redirect("github_referencias", proyecto_id=proyecto.pk)
    elif editable and proyecto.repositorio_url:
        form = ReferenciaGitHubForm(proyecto=proyecto)
    referencias = proyecto.referencias_github.select_related("creado_por").all()
    return render(
        request,
        "dashboard/github_referencias.html",
        {
            "proyecto": proyecto,
            "referencias": referencias,
            "form": form,
            "editable": editable,
        },
    )


@login_required
@requiere_empresa
@require_POST
def github_referencia_eliminar(request, proyecto_id, referencia_id):
    proyecto = get_object_or_404(_proyectos_visibles(request.user), pk=proyecto_id)
    if not _puede_editar_proyecto(request.user, proyecto):
        raise PermissionDenied
    referencia = get_object_or_404(
        ReferenciaGitHub,
        pk=referencia_id,
        proyecto=proyecto,
    )
    referencia.delete()
    messages.success(request, "La referencia se quitó del proyecto.")
    return redirect("github_referencias", proyecto_id=proyecto.pk)


@login_required
@requiere_empresa
def tareas(request):
    proyectos = _proyectos_visibles(request.user)
    tareas_empresa = Tarea.objects.filter(proyecto__in=proyectos)
    proyecto_id = request.GET.get("proyecto")
    proyecto_seleccionado = None
    if proyecto_id:
        proyecto_seleccionado = get_object_or_404(proyectos, pk=proyecto_id)
        tareas_empresa = tareas_empresa.filter(proyecto=proyecto_seleccionado)
    tareas_empresa = tareas_empresa.select_related("proyecto", "responsable")
    filas = [
        {"tarea": tarea, "editable": _puede_editar_proyecto(request.user, tarea.proyecto)}
        for tarea in tareas_empresa
    ]
    columnas = [
        {
            "estado": estado,
            "nombre": nombre,
            "tareas": [fila for fila in filas if fila["tarea"].estado == estado],
        }
        for estado, nombre in Tarea.Estado.choices
    ]
    return render(
        request,
        "dashboard/tareas.html",
        {
            "columnas": columnas,
            "estados": Tarea.Estado.choices,
            "proyecto_seleccionado": proyecto_seleccionado,
        },
    )


def _formulario_tarea(request, instance=None, initial=None):
    proyectos = _proyectos_visibles(request.user)
    form = TareaForm(
        request.POST or None,
        instance=instance,
        initial=initial,
        empresa=request.user.empresa,
        proyectos=proyectos,
    )
    return form


@login_required
@requiere_empresa
def tarea_crear(request):
    initial = {}
    proyecto_id = request.GET.get("proyecto")
    if proyecto_id and _proyectos_visibles(request.user).filter(pk=proyecto_id).exists():
        initial["proyecto"] = proyecto_id
    form = _formulario_tarea(request, initial=initial)
    if request.method == "POST" and form.is_valid():
        tarea = form.save(commit=False)
        tarea.creado_por = request.user
        tarea.save()
        messages.success(request, "La tarea se creó correctamente.")
        return redirect("tareas")
    return _formulario(request, form, "Crear tarea", "tareas")


@login_required
@requiere_empresa
def tarea_editar(request, tarea_id):
    tarea = get_object_or_404(
        Tarea.objects.select_related("proyecto").filter(
            proyecto__in=_proyectos_visibles(request.user)
        ),
        pk=tarea_id,
    )
    if not _puede_editar_proyecto(request.user, tarea.proyecto):
        raise PermissionDenied
    form = _formulario_tarea(request, instance=tarea)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "La tarea se actualizó correctamente.")
        return redirect("tareas")
    return _formulario(request, form, "Editar tarea", "tareas")


@login_required
@requiere_empresa
def tarea_eliminar(request, tarea_id):
    tarea = get_object_or_404(
        Tarea.objects.select_related("proyecto").filter(
            proyecto__in=_proyectos_visibles(request.user)
        ),
        pk=tarea_id,
    )
    if not _puede_editar_proyecto(request.user, tarea.proyecto):
        raise PermissionDenied
    if request.method == "POST":
        tarea.delete()
        messages.success(request, "La tarea se eliminó correctamente.")
        return redirect("tareas")
    return render(
        request,
        "dashboard/confirmar_eliminacion.html",
        {"objeto": tarea, "titulo": "Eliminar tarea", "cancelar": "tareas"},
    )


@login_required
@requiere_empresa
@require_POST
def tarea_cambiar_estado(request, tarea_id):
    tarea = get_object_or_404(
        Tarea.objects.select_related("proyecto").filter(
            proyecto__in=_proyectos_visibles(request.user)
        ),
        pk=tarea_id,
    )
    if not _puede_editar_proyecto(request.user, tarea.proyecto):
        raise PermissionDenied
    nuevo_estado = request.POST.get("estado")
    if nuevo_estado not in Tarea.Estado.values:
        messages.error(request, "Selecciona un estado válido para la tarea.")
    else:
        tarea.estado = nuevo_estado
        tarea.save(update_fields=("estado", "actualizado_en"))
        messages.success(request, "Se actualizó el estado de la tarea.")
    return redirect(f"{reverse('tareas')}?proyecto={tarea.proyecto_id}")
