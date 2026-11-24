"""
Vistas del espacio de trabajo: panel, Mi empresa, proyectos y tareas.

Las vistas NO deciden quién puede qué: lo preguntan a la política
(config/politica_accesos.json) con politica.puede(...) / permisos_*(...)
y cortan con 403 usando exigir(...).
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from cuentas.decoradores import exigir, requiere_accion
from cuentas.forms import EmpresaForm
from cuentas.politica import obtener_politica

from .forms import MiembroForm, ProyectoForm, TareaForm
from .metricas import metricas_empresa, porcentaje
from .models import Proyecto, ProyectoMiembro, Tarea

COMPLETADA = Tarea.Estado.COMPLETADA


def con_avance(proyectos, limite=None):
    """Agrega total de tareas, hechas y % de avance a cada proyecto (en una consulta)."""
    anotados = proyectos.annotate(
        total_tareas=Count("tareas", distinct=True),
        tareas_hechas=Count("tareas", filter=Q(tareas__estado=COMPLETADA), distinct=True),
    ).select_related("empresa", "creado_por").order_by("-fecha_creacion")
    for proyecto in anotados[:limite]:
        proyecto.avance = porcentaje(proyecto.tareas_hechas, proyecto.total_tareas)
        yield proyecto


# ---------------------------------------------------------------------------
# Panel
# ---------------------------------------------------------------------------

@login_required
def panel(request):
    usuario = request.user
    politica = obtener_politica()
    empresa = usuario.empresa
    permisos_empresa = politica.permisos_empresa(usuario, empresa) if empresa else frozenset()
    visibles = Proyecto.objects.visibles_para(usuario)
    pendientes = Tarea.objects.filter(asignado_a=usuario).exclude(estado=COMPLETADA).select_related("proyecto")

    return render(request, "dashboard/panel.html", {
        "empresa": empresa,
        "metricas": metricas_empresa(empresa) if "metricas" in permisos_empresa else None,
        "proyectos": list(con_avance(visibles, limite=6)),
        "total_proyectos": visibles.count(),
        "mis_tareas": pendientes.order_by("fecha_vencimiento")[:6],
        "total_pendientes": pendientes.count(),
        "puede_crear_empresa": politica.puede(usuario, "crear_empresa"),
        "puede_crear_proyecto": politica.puede(usuario, "crear_proyecto"),
    })


@login_required
def proximamente(request, seccion):
    return render(request, "dashboard/proximamente.html", {"seccion": seccion})


@login_required
def canvas(request):
    """Canvas interactivo + vista de hitos próximos (calendario simple)."""
    from .models import Hito
    from django.utils import timezone
    hitos = (
        Hito.objects.filter(
            proyecto__in=Proyecto.objects.visibles_para(request.user),
            fecha_objetivo__gte=timezone.now().date(),
        )
        .select_related("proyecto")
        .order_by("fecha_objetivo")[:15]
    )
    return render(request, "dashboard/canvas/tablero.html", {"hitos": hitos})


# ---------------------------------------------------------------------------
# Mi empresa (compatibilidad; ya no es el eje de la plataforma)
# ---------------------------------------------------------------------------

@login_required
def mi_empresa(request):
    empresa = request.user.empresa
    if empresa is None:
        return _crear_mi_empresa(request)

    permisos = obtener_politica().permisos_empresa(request.user, empresa)
    exigir(permisos, "ver")
    return render(request, "dashboard/empresa/detalle.html", {
        "empresa": empresa,
        "permisos": permisos,
        "metricas": metricas_empresa(empresa) if "metricas" in permisos else None,
        "integrantes": empresa.usuarios.select_related("rol").order_by("first_name", "email"),
    })


def _crear_mi_empresa(request):
    """Quien no tiene empresa puede crear la suya (acción "crear_empresa")."""
    puede = obtener_politica().puede(request.user, "crear_empresa")
    form = EmpresaForm(request.POST or None)
    if request.method == "POST":
        exigir({"crear_empresa"} if puede else set(), "crear_empresa")
        if form.is_valid():
            empresa = form.save(commit=False)
            empresa.propietario = request.user
            empresa.save()
            request.user.empresa = empresa
            request.user.save(update_fields=["empresa"])
            messages.success(request, f"¡Listo! «{empresa}» es tu empresa. Ya puedes crear proyectos.")
            return redirect("mi_empresa")
    return render(request, "dashboard/empresa/crear.html", {"form": form, "puede": puede})


def _empresa_con_permiso(request, permiso):
    empresa = request.user.empresa
    if empresa is None:
        return None
    exigir(obtener_politica().permisos_empresa(request.user, empresa), permiso)
    return empresa


@login_required
def mi_empresa_editar(request):
    empresa = _empresa_con_permiso(request, "editar")
    if empresa is None:
        return redirect("mi_empresa")
    form = EmpresaForm(request.POST or None, instance=empresa)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Los datos de la empresa quedaron actualizados.")
        return redirect("mi_empresa")
    return render(request, "dashboard/empresa/editar.html", {"form": form, "empresa": empresa})


@login_required
def mi_empresa_eliminar(request):
    empresa = _empresa_con_permiso(request, "eliminar")
    if empresa is None:
        return redirect("mi_empresa")
    if request.method == "POST":
        nombre = empresa.nombre
        empresa.delete()
        messages.success(request, f"Se eliminó la empresa «{nombre}».")
        return redirect("panel")
    return render(request, "confirmar_eliminar.html", {
        "titulo": "Eliminar empresa",
        "objeto": empresa.nombre,
        "consecuencias": consecuencias_de_eliminar_empresa(empresa),
        "url_cancelar": reverse("mi_empresa"),
    })


def consecuencias_de_eliminar_empresa(empresa):
    return [
        f"Se eliminan sus {empresa.proyectos.count()} proyecto(s) con todas sus tareas, ideas y lienzos.",
        f"Sus {empresa.usuarios.count()} integrante(s) conservan su cuenta, pero quedan sin empresa.",
    ]


# ---------------------------------------------------------------------------
# Proyectos
# ---------------------------------------------------------------------------

def _proyecto_con_permiso(request, pk, permiso):
    """El proyecto (si lo puede ver) y sus permisos; 403 si le falta el permiso pedido."""
    proyecto = get_object_or_404(Proyecto.objects.visibles_para(request.user).select_related("empresa"), pk=pk)
    permisos = proyecto.permisos(request.user)
    exigir(permisos, permiso)
    return proyecto, permisos


@login_required
def proyectos(request):
    busqueda = request.GET.get("q", "").strip()
    visibles = Proyecto.objects.visibles_para(request.user)
    if busqueda:
        visibles = visibles.filter(Q(nombre__icontains=busqueda) | Q(descripcion__icontains=busqueda))
    return render(request, "dashboard/proyectos/lista.html", {
        "proyectos": list(con_avance(visibles)),
        "busqueda": busqueda,
        "puede_crear": obtener_politica().puede(request.user, "crear_proyecto"),
    })


@requiere_accion("crear_proyecto")
def proyecto_crear(request):
    """
    Flujo de creación:
    1. Cuestionario opcional (propósito, metodología, educativo, grupal).
    2. Formulario principal del proyecto.
    Los datos del cuestionario se pasan por sesión o por POST oculto.
    """
    from .forms import CuestionarioProyectoForm, ProyectoForm

    # Paso 1: cuestionario (GET o POST con step=cuestionario)
    step = request.POST.get("step") or request.GET.get("step") or "cuestionario"

    if step == "cuestionario" and request.method == "GET":
        form_q = CuestionarioProyectoForm()
        return render(request, "dashboard/proyectos/cuestionario.html", {"form": form_q})

    if step == "cuestionario" and request.method == "POST":
        form_q = CuestionarioProyectoForm(request.POST)
        if form_q.is_valid():
            # Guardamos respuestas en sesión para el siguiente paso
            request.session["proyecto_cuestionario"] = form_q.cleaned_data
            form = ProyectoForm(initial={
                "proposito": form_q.cleaned_data.get("proposito") or "",
                "metodologia": form_q.cleaned_data.get("metodologia") or "",
                "es_educativo": form_q.cleaned_data.get("es_educativo") or False,
                "es_grupal": form_q.cleaned_data.get("es_grupal") or False,
                "descripcion": form_q.cleaned_data.get("notas") or "",
            })
            return render(request, "dashboard/proyectos/form.html", {
                "form": form,
                "desde_cuestionario": True,
            })
        return render(request, "dashboard/proyectos/cuestionario.html", {"form": form_q})

    # Paso 2: formulario final
    form = ProyectoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        proyecto = form.save(commit=False)
        # Empresa opcional (ya no es obligatoria)
        if getattr(request.user, "empresa_id", None):
            proyecto.empresa = request.user.empresa
        proyecto.creado_por = request.user
        # Recuperar del cuestionario si quedó algo
        datos_q = request.session.pop("proyecto_cuestionario", {}) or {}
        if not proyecto.proposito and datos_q.get("proposito"):
            proyecto.proposito = datos_q["proposito"]
        if not proyecto.metodologia and datos_q.get("metodologia"):
            proyecto.metodologia = datos_q["metodologia"]
        if datos_q.get("es_educativo"):
            proyecto.es_educativo = True
        if datos_q.get("es_grupal"):
            proyecto.es_grupal = True
        proyecto.save()
        messages.success(
            request,
            f"Proyecto «{proyecto}» creado. "
            + ("Puedes invitar a tu equipo por correo." if proyecto.es_grupal else "Agrega tareas cuando quieras.")
        )
        return redirect("proyecto_detalle", pk=proyecto.pk)
    return render(request, "dashboard/proyectos/form.html", {"form": form})


@login_required
def proyecto_detalle(request, pk, miembro_form=None):
    proyecto, permisos = _proyecto_con_permiso(request, pk, "ver")
    tareas = proyecto.tareas.select_related("asignado_a").order_by("estado", "fecha_vencimiento", "-fecha_creacion")
    total = tareas.count()
    hechas = tareas.filter(estado=COMPLETADA).count()
    return render(request, "dashboard/proyectos/detalle.html", {
        "proyecto": proyecto,
        "permisos": permisos,
        "tareas": tareas,
        "avance": porcentaje(hechas, total),
        "hechas": hechas,
        "miembros": proyecto.proyectomiembro_set.select_related("usuario", "usuario__empresa").order_by("rol", "usuario__first_name"),
        "miembro_form": miembro_form or MiembroForm(proyecto=proyecto),
    })


@login_required
def proyecto_editar(request, pk):
    proyecto, _ = _proyecto_con_permiso(request, pk, "editar")
    form = ProyectoForm(request.POST or None, instance=proyecto)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proyecto actualizado.")
        return redirect("proyecto_detalle", pk=proyecto.pk)
    return render(request, "dashboard/proyectos/form.html", {"form": form, "proyecto": proyecto})


@login_required
def proyecto_eliminar(request, pk):
    proyecto, _ = _proyecto_con_permiso(request, pk, "eliminar")
    if request.method == "POST":
        nombre = proyecto.nombre
        proyecto.delete()
        messages.success(request, f"Se eliminó el proyecto «{nombre}».")
        return redirect("proyectos")
    return render(request, "confirmar_eliminar.html", {
        "titulo": "Eliminar proyecto",
        "objeto": proyecto.nombre,
        "consecuencias": [
            f"Se eliminan sus {proyecto.tareas.count()} tarea(s).",
            f"Sus {proyecto.proyectomiembro_set.count()} miembro(s) dejan de verlo.",
        ],
        "url_cancelar": reverse("proyecto_detalle", args=[proyecto.pk]),
    })


@require_POST
@login_required
def miembro_agregar(request, pk):
    proyecto, _ = _proyecto_con_permiso(request, pk, "miembros")
    form = MiembroForm(request.POST, proyecto=proyecto)
    if not form.is_valid():
        return proyecto_detalle(request, pk, miembro_form=form)
    miembro = form.save()
    messages.success(request, f"{miembro.usuario} ahora es {miembro.get_rol_display().lower()} del proyecto.")
    return redirect("proyecto_detalle", pk=pk)


@require_POST
@login_required
def miembro_quitar(request, pk, miembro_pk):
    proyecto, permisos = _proyecto_con_permiso(request, pk, "ver")
    miembro = get_object_or_404(ProyectoMiembro, pk=miembro_pk, proyecto=proyecto)
    # Quien gestiona miembros puede quitar a cualquiera; cada persona puede salirse
    exigir(permisos | ({"miembros"} if miembro.usuario_id == request.user.pk else set()), "miembros")
    miembro.delete()
    if miembro.usuario_id == request.user.pk:
        messages.success(request, "Saliste del proyecto.")
        return redirect("proyectos")
    messages.success(request, f"{miembro.usuario} ya no está en el proyecto.")
    return redirect("proyecto_detalle", pk=pk)


# ---------------------------------------------------------------------------
# Tareas
# ---------------------------------------------------------------------------

@login_required
def tareas(request):
    ver = request.GET.get("ver", "mias")
    visibles = Tarea.objects.filter(proyecto__in=Proyecto.objects.visibles_para(request.user))
    filtros = {"mias": Q(asignado_a=request.user), "pendientes": ~Q(estado=COMPLETADA), "todas": Q()}
    lista = visibles.filter(filtros.get(ver, filtros["mias"])).select_related("proyecto", "asignado_a")
    return render(request, "dashboard/tareas/lista.html", {
        "tareas": lista.order_by("estado", "fecha_vencimiento"),
        "ver": ver if ver in filtros else "mias",
    })


def _tarea_con_permiso(request, pk):
    tarea = get_object_or_404(
        Tarea.objects.filter(proyecto__in=Proyecto.objects.visibles_para(request.user)).select_related("proyecto"), pk=pk
    )
    exigir(tarea.proyecto.permisos(request.user), "tareas")
    return tarea


@login_required
def tarea_crear(request, pk):
    proyecto, _ = _proyecto_con_permiso(request, pk, "tareas")
    form = TareaForm(request.POST or None, proyecto=proyecto)
    if request.method == "POST" and form.is_valid():
        tarea = form.save(commit=False)
        tarea.proyecto = proyecto
        tarea.creado_por = request.user
        tarea.save()
        messages.success(request, f"Tarea «{tarea}» creada.")
        return redirect("proyecto_detalle", pk=proyecto.pk)
    return render(request, "dashboard/tareas/form.html", {"form": form, "proyecto": proyecto})


@login_required
def tarea_editar(request, pk):
    tarea = _tarea_con_permiso(request, pk)
    form = TareaForm(request.POST or None, instance=tarea, proyecto=tarea.proyecto)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Tarea actualizada.")
        return redirect("proyecto_detalle", pk=tarea.proyecto_id)
    return render(request, "dashboard/tareas/form.html", {"form": form, "proyecto": tarea.proyecto, "tarea": tarea})


@login_required
def tarea_eliminar(request, pk):
    tarea = _tarea_con_permiso(request, pk)
    if request.method == "POST":
        tarea.delete()
        messages.success(request, f"Se eliminó la tarea «{tarea}».")
        return redirect("proyecto_detalle", pk=tarea.proyecto_id)
    return render(request, "confirmar_eliminar.html", {
        "titulo": "Eliminar tarea",
        "objeto": tarea.titulo,
        "consecuencias": [f"Sale del proyecto «{tarea.proyecto}» y de sus métricas."],
        "url_cancelar": reverse("proyecto_detalle", args=[tarea.proyecto_id]),
    })
