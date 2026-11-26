"""Vistas de /app/: proyectos técnicos, colaboración y seguimiento."""

import json
import uuid
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.db.models import Count, Q
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import ensure_csrf_cookie

from .forms import CorreccionForm, DocumentoForm, EventoForm, InvitacionForm, OrientacionProyectoForm, ProyectoForm, ProyectoLiderForm, TareaForm
from .metricas import metricas_proyectos, porcentaje
from .models import DocumentoProyecto, InvitacionProyecto, Lienzo, Proyecto, ProyectoMiembro, Tarea


def _proyecto(request, pk, permiso="ver"):
    proyecto = get_object_or_404(Proyecto.objects.visibles_para(request.user), pk=pk)
    permisos = proyecto.permisos(request.user)
    if permiso not in permisos:
        raise PermissionDenied("No tienes permiso para realizar esta acción en este proyecto.")
    return proyecto, permisos


def _con_avance(proyectos, limite=None):
    resultado = proyectos.annotate(
        total_tareas=Count("tareas", distinct=True),
        tareas_hechas=Count("tareas", filter=Q(tareas__estado=Tarea.Estado.HECHA), distinct=True),
    ).select_related("creado_por", "supervisor")
    if limite:
        resultado = resultado[:limite]
    for proyecto in resultado:
        proyecto.avance = porcentaje(proyecto.tareas_hechas, proyecto.total_tareas)
    return resultado


@login_required
def panel(request):
    visibles = Proyecto.objects.visibles_para(request.user)
    tareas = Tarea.objects.filter(proyecto__in=visibles, asignado_a=request.user).exclude(estado=Tarea.Estado.HECHA)
    return render(request, "dashboard/panel.html", {
        "proyectos": _con_avance(visibles.order_by("-fecha_creacion"), 6),
        "metricas": metricas_proyectos(visibles),
        "mis_tareas": tareas.select_related("proyecto").order_by("fecha_vencimiento")[:6],
        "total_pendientes": tareas.count(),
    })


@login_required
def proyectos(request):
    busqueda = request.GET.get("q", "").strip()
    visibles = Proyecto.objects.visibles_para(request.user)
    if busqueda:
        visibles = visibles.filter(Q(nombre__icontains=busqueda) | Q(descripcion__icontains=busqueda) | Q(tecnologia__icontains=busqueda))
    return render(request, "dashboard/proyectos/lista.html", {"proyectos": _con_avance(visibles), "busqueda": busqueda})


@login_required
def proyecto_orientacion(request):
    form = OrientacionProyectoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        request.session["orientacion_proyecto"] = form.cleaned_data
        return redirect("proyecto_crear")
    return render(request, "dashboard/proyectos/orientacion.html", {"form": form})


@login_required
def proyecto_crear(request):
    orientacion = request.session.get("orientacion_proyecto", {})
    form = ProyectoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        proyecto = form.save(commit=False)
        proyecto.creado_por = request.user
        proyecto.finalidad = orientacion.get("finalidad") or Proyecto.Finalidad.OTRO
        proyecto.metodologia = orientacion.get("metodologia") or Proyecto.Metodologia.KANBAN
        proyecto.modalidad = orientacion.get("modalidad") or Proyecto.Modalidad.INDIVIDUAL
        proyecto.contexto_educativo = orientacion.get("contexto_educativo", "")
        correo_supervisor = orientacion.get("supervisor_email", "").lower()
        if correo_supervisor and not proyecto.supervisor_id:
            from cuentas.models import Usuario
            proyecto.supervisor = Usuario.objects.filter(email=correo_supervisor, perfil=Usuario.Perfil.PROFESOR, is_active=True).first()
        proyecto.save()
        ProyectoMiembro.objects.get_or_create(proyecto=proyecto, usuario=request.user, defaults={"rol": ProyectoMiembro.Rol.LIDER})
        request.session.pop("orientacion_proyecto", None)
        messages.success(request, "Proyecto creado. Ya puedes organizar el roadmap e invitar colaboradores.")
        return redirect("proyecto_detalle", pk=proyecto.pk)
    return render(request, "dashboard/proyectos/form.html", {"form": form, "orientacion": orientacion})


@login_required
def proyecto_detalle(request, pk):
    proyecto, permisos = _proyecto(request, pk)
    tareas = proyecto.tareas.select_related("asignado_a").all()
    return render(request, "dashboard/proyectos/detalle.html", {
        "proyecto": proyecto, "permisos": permisos, "tareas": tareas,
        "avance": proyecto.progreso, "miembros": proyecto.proyectomiembro_set.select_related("usuario"),
        "invitaciones": proyecto.invitaciones.filter(estado=InvitacionProyecto.Estado.PENDIENTE),
        "enlace_url": request.build_absolute_uri(reverse("proyecto_publico", args=[proyecto.enlace_publico])) if proyecto.visibilidad == Proyecto.Visibilidad.PUBLICO else "",
        "documentos": proyecto.documentos.select_related("subido_por")[:5],
        "correcciones": proyecto.correcciones.select_related("autor", "tarea")[:4],
    })


@login_required
def proyecto_editar(request, pk):
    proyecto, permisos = _proyecto(request, pk, "editar")
    # Modalidad y visibilidad las decide solo el líder (quien tiene el permiso "miembros").
    clase_form = ProyectoLiderForm if "miembros" in permisos else ProyectoForm
    form = clase_form(request.POST or None, instance=proyecto)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proyecto actualizado.")
        return redirect("proyecto_detalle", pk=pk)
    return render(request, "dashboard/proyectos/form.html", {"form": form, "proyecto": proyecto, "es_lider": "miembros" in permisos})


@require_GET
def proyecto_publico(request, enlace):
    """Vista de solo lectura para quien tenga el enlace. Sin sesión. Solo si el proyecto es público."""
    proyecto = get_object_or_404(Proyecto, enlace_publico=enlace, visibilidad=Proyecto.Visibilidad.PUBLICO)
    respuesta = render(request, "dashboard/proyectos/publico.html", {
        "proyecto": proyecto,
        "tareas": proyecto.tareas.only("titulo", "estado").order_by("pk"),
        "avance": proyecto.progreso,
    })
    respuesta["X-Robots-Tag"] = "noindex, nofollow"
    return respuesta


@login_required
@require_POST
def proyecto_enlace_nuevo(request, pk):
    """Invalida el enlace público actual y crea uno nuevo."""
    proyecto, permisos = _proyecto(request, pk)
    if "miembros" not in permisos:
        raise PermissionDenied("Solo el líder puede cambiar el enlace público.")
    proyecto.enlace_publico = uuid.uuid4()
    proyecto.save(update_fields=["enlace_publico"])
    messages.success(request, "Enlace nuevo creado. El enlace anterior ya no funciona.")
    return redirect("proyecto_detalle", pk=pk)


@login_required
@require_POST
def miembro_cambiar_rol(request, pk, miembro_pk):
    """El líder da o quita permisos a un integrante: colaborador (editor) o solo lectura."""
    proyecto, permisos = _proyecto(request, pk)
    if "miembros" not in permisos:
        raise PermissionDenied("Solo el líder puede cambiar los permisos de los integrantes.")
    miembro = get_object_or_404(ProyectoMiembro, pk=miembro_pk, proyecto=proyecto)
    nuevo_rol = request.POST.get("rol", "")
    if miembro.usuario_id == proyecto.creado_por_id:
        messages.error(request, "El líder siempre conserva su rol.")
    elif nuevo_rol not in {ProyectoMiembro.Rol.EDITOR, ProyectoMiembro.Rol.LECTOR}:
        messages.error(request, "Elige Colaborador o Solo lectura.")
    else:
        miembro.rol = nuevo_rol
        miembro.save(update_fields=["rol"])
        messages.success(request, f"Permisos de {miembro.usuario} actualizados.")
    return redirect("proyecto_detalle", pk=pk)


@login_required
def proyecto_eliminar(request, pk):
    proyecto, _ = _proyecto(request, pk, "eliminar")
    if request.method == "POST":
        proyecto.delete()
        messages.success(request, "El proyecto y sus datos asociados fueron eliminados.")
        return redirect("proyectos")
    return render(request, "confirmar_eliminar.html", {"titulo": "Eliminar proyecto", "objeto": proyecto.nombre, "consecuencias": ["Se eliminarán tareas, documentos, eventos, invitaciones, correcciones y canvas."], "url_cancelar": reverse("proyecto_detalle", args=[pk])})


@login_required
@require_POST
def invitacion_crear(request, pk):
    proyecto, _ = _proyecto(request, pk, "invitaciones")
    form = InvitacionForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Revisa el correo y el tipo de acceso de la invitación.")
        return redirect("proyecto_detalle", pk=pk)
    correo = form.cleaned_data["email"]
    if correo == request.user.email.lower():
        messages.error(request, "No puedes invitarte a ti mismo: ya eres parte del proyecto.")
        return redirect("proyecto_detalle", pk=pk)
    if proyecto.proyectomiembro_set.filter(usuario__email__iexact=correo).exists():
        messages.error(request, "Esa persona ya es parte del proyecto.")
        return redirect("proyecto_detalle", pk=pk)
    if proyecto.invitaciones.filter(email=correo, estado=InvitacionProyecto.Estado.PENDIENTE, vence_en__gt=timezone.now()).exists():
        messages.error(request, "Ya hay una invitación pendiente para ese correo.")
        return redirect("proyecto_detalle", pk=pk)
    if proyecto.modalidad == Proyecto.Modalidad.INDIVIDUAL:
        # Invitar siempre está disponible: al invitar, el proyecto pasa a grupal automáticamente.
        proyecto.modalidad = Proyecto.Modalidad.GRUPAL
        proyecto.save(update_fields=["modalidad"])
        messages.info(request, "El proyecto ahora es grupal porque tiene colaboradores.")
    invitacion = form.save(commit=False)
    invitacion.proyecto = proyecto
    invitacion.creado_por = request.user
    invitacion.vence_en = timezone.now() + timedelta(days=7)
    invitacion.save()
    enlace = request.build_absolute_uri(reverse("invitacion_aceptar", args=[invitacion.token]))
    send_mail(
        subject=f"Invitación a {proyecto.nombre} en Xincronix",
        message=(f"{request.user} te invitó al proyecto «{proyecto.nombre}».\n\n"
                 f"Accede o crea una cuenta con {invitacion.email} y abre este enlace:\n{enlace}\n\n"
                 "La invitación vence en 7 días."),
        from_email=None, recipient_list=[invitacion.email], fail_silently=False,
    )
    messages.success(request, f"Invitación enviada a {invitacion.email}.")
    return redirect("proyecto_detalle", pk=pk)


@login_required
def invitacion_aceptar(request, token):
    invitacion = get_object_or_404(InvitacionProyecto, token=token)
    if invitacion.estado != InvitacionProyecto.Estado.PENDIENTE or invitacion.vencida:
        messages.error(request, "Esta invitación ya no está disponible.")
        return redirect("panel")
    if request.user.email.lower() != invitacion.email.lower():
        raise PermissionDenied("Inicia sesión con el correo al que se envió esta invitación.")
    ProyectoMiembro.objects.get_or_create(proyecto=invitacion.proyecto, usuario=request.user, defaults={"rol": invitacion.rol})
    invitacion.estado = InvitacionProyecto.Estado.ACEPTADA
    invitacion.save(update_fields=["estado"])
    messages.success(request, f"Ahora haces parte de «{invitacion.proyecto}».")
    return redirect("proyecto_detalle", pk=invitacion.proyecto_id)


@login_required
@require_POST
def miembro_quitar(request, pk, miembro_pk):
    proyecto, permisos = _proyecto(request, pk)
    miembro = get_object_or_404(ProyectoMiembro, pk=miembro_pk, proyecto=proyecto)
    if "miembros" not in permisos and miembro.usuario_id != request.user.pk:
        raise PermissionDenied("No puedes cambiar los integrantes de este proyecto.")
    if miembro.usuario_id == proyecto.creado_por_id:
        messages.error(request, "El creador no puede salir; transfiere el proyecto antes de eliminarlo.")
    else:
        # Quien sale deja de ser responsable de sus tareas: quedan sin asignar, no apuntando a alguien ajeno.
        Tarea.objects.filter(proyecto=proyecto, asignado_a_id=miembro.usuario_id).update(asignado_a=None)
        miembro.delete()
        messages.success(request, "Integrante retirado del proyecto.")
    return redirect("proyecto_detalle", pk=pk)


@login_required
def tareas(request):
    visibles = Proyecto.objects.visibles_para(request.user)
    vista = request.GET.get("ver", "mias")
    consulta = Tarea.objects.filter(proyecto__in=visibles).select_related("proyecto", "asignado_a")
    if vista == "mias":
        consulta = consulta.filter(asignado_a=request.user)
    elif vista == "pendientes":
        consulta = consulta.exclude(estado=Tarea.Estado.HECHA)
    return render(request, "dashboard/tareas/lista.html", {"tareas": consulta, "ver": vista})


@login_required
def tarea_crear(request, pk):
    proyecto, _ = _proyecto(request, pk, "tareas")
    form = TareaForm(request.POST or None, proyecto=proyecto)
    if request.method == "POST" and form.is_valid():
        tarea = form.save(commit=False)
        tarea.proyecto, tarea.creado_por = proyecto, request.user
        tarea.save()
        return redirect("proyecto_tablero", pk=pk)
    return render(request, "dashboard/tareas/form.html", {"form": form, "proyecto": proyecto})


def _tarea(request, pk):
    tarea = get_object_or_404(Tarea.objects.select_related("proyecto"), pk=pk)
    _proyecto(request, tarea.proyecto_id, "tareas")
    return tarea


@login_required
def tarea_editar(request, pk):
    tarea = _tarea(request, pk)
    form = TareaForm(request.POST or None, instance=tarea, proyecto=tarea.proyecto)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("proyecto_tablero", pk=tarea.proyecto_id)
    return render(request, "dashboard/tareas/form.html", {"form": form, "proyecto": tarea.proyecto, "tarea": tarea})


@login_required
def tarea_eliminar(request, pk):
    tarea = _tarea(request, pk)
    proyecto_id = tarea.proyecto_id
    if request.method == "POST":
        tarea.delete()
        return redirect("proyecto_tablero", pk=proyecto_id)
    return render(request, "confirmar_eliminar.html", {"titulo": "Eliminar tarea", "objeto": tarea.titulo, "consecuencias": ["La tarea desaparecerá del tablero, calendario y estadísticas."], "url_cancelar": reverse("proyecto_tablero", args=[proyecto_id])})


@login_required
@ensure_csrf_cookie
def proyecto_tablero(request, pk):
    proyecto, permisos = _proyecto(request, pk)
    columnas = [(estado, etiqueta, proyecto.tareas.filter(estado=estado)) for estado, etiqueta in Tarea.Estado.choices]
    return render(request, "dashboard/proyectos/tablero.html", {"proyecto": proyecto, "permisos": permisos, "columnas": columnas})


@login_required
@require_POST
def tarea_mover(request, pk, tarea_pk):
    proyecto, permisos = _proyecto(request, pk, "tareas")
    try:
        estado = json.loads(request.body).get("estado")
    except (json.JSONDecodeError, AttributeError):
        return HttpResponseBadRequest("JSON inválido")
    if estado not in Tarea.Estado.values:
        return HttpResponseBadRequest("Estado inválido")
    tarea = get_object_or_404(Tarea, pk=tarea_pk, proyecto=proyecto)
    tarea.estado = estado
    tarea.save(update_fields=["estado", "fecha_completada"])
    return JsonResponse({"ok": True, "estado": tarea.estado, "progreso": proyecto.progreso})


@login_required
def proyecto_calendario(request, pk):
    proyecto, permisos = _proyecto(request, pk)
    tareas = proyecto.tareas.exclude(fecha_vencimiento__isnull=True)
    return render(request, "dashboard/proyectos/calendario.html", {"proyecto": proyecto, "permisos": permisos, "eventos": proyecto.eventos.all(), "tareas": tareas, "form": EventoForm()})


@login_required
@require_POST
def evento_crear(request, pk):
    proyecto, _ = _proyecto(request, pk, "calendario")
    form = EventoForm(request.POST)
    if form.is_valid():
        evento = form.save(commit=False)
        evento.proyecto, evento.creado_por = proyecto, request.user
        evento.save()
        messages.success(request, "Evento agregado al calendario.")
    else:
        messages.error(request, "No se pudo crear el evento. Revisa las fechas.")
    return redirect("proyecto_calendario", pk=pk)


@login_required
def proyecto_roadmap(request, pk):
    proyecto, permisos = _proyecto(request, pk)
    return render(request, "dashboard/proyectos/roadmap.html", {"proyecto": proyecto, "permisos": permisos, "hitos": proyecto.tareas.exclude(fecha_vencimiento__isnull=True).order_by("fecha_vencimiento")})


@login_required
def proyecto_analytics(request, pk):
    proyecto, permisos = _proyecto(request, pk)
    tareas = proyecto.tareas.all()
    total = tareas.count()
    estados = [{"codigo": codigo, "nombre": nombre, "total": tareas.filter(estado=codigo).count()} for codigo, nombre in Tarea.Estado.choices]
    return render(request, "dashboard/proyectos/analytics.html", {"proyecto": proyecto, "permisos": permisos, "total": total, "hechas": tareas.filter(estado=Tarea.Estado.HECHA).count(), "vencidas": sum(1 for tarea in tareas if tarea.vencida), "estados": estados, "avance": proyecto.progreso})


@login_required
@ensure_csrf_cookie
def proyecto_canvas(request, pk):
    proyecto, permisos = _proyecto(request, pk, "canvas")
    lienzo, _ = Lienzo.objects.get_or_create(proyecto=proyecto)
    return render(request, "dashboard/proyectos/canvas.html", {"proyecto": proyecto, "permisos": permisos, "lienzo": lienzo})


TAMANO_MAXIMO_CANVAS = 512 * 1024  # 512 KB
PROFUNDIDAD_MAXIMA_CANVAS = 20


def _profundidad(valor, nivel=0):
    """Niveles de anidación de un JSON (listas y objetos). Evita estructuras absurdas."""
    if nivel > PROFUNDIDAD_MAXIMA_CANVAS:
        return nivel
    if isinstance(valor, dict):
        return max([nivel + 1] + [_profundidad(v, nivel + 1) for v in valor.values()])
    if isinstance(valor, list):
        return max([nivel + 1] + [_profundidad(v, nivel + 1) for v in valor])
    return nivel


@login_required
@require_POST
def canvas_guardar(request, pk):
    proyecto, _ = _proyecto(request, pk, "canvas")
    if len(request.body) > TAMANO_MAXIMO_CANVAS:
        return HttpResponse("El canvas supera el tamaño máximo permitido.", status=413)
    try:
        datos = json.loads(request.body)
        contenido = datos.get("contenido", {})
        nombre = str(datos.get("nombre", "Canvas del proyecto"))[:100]
        if not isinstance(contenido, dict) or _profundidad(contenido) > PROFUNDIDAD_MAXIMA_CANVAS:
            raise ValueError
    except (json.JSONDecodeError, ValueError, AttributeError, RecursionError):
        return HttpResponseBadRequest("Contenido de canvas inválido")
    lienzo, _ = Lienzo.objects.get_or_create(proyecto=proyecto)
    lienzo.nombre, lienzo.contenido, lienzo.actualizado_por = nombre, contenido, request.user
    lienzo.version += 1
    lienzo.save()
    return JsonResponse({"ok": True, "version": lienzo.version, "actualizado": lienzo.fecha_actualizacion.isoformat()})


@login_required
@require_POST
def documento_subir(request, pk):
    proyecto, _ = _proyecto(request, pk, "documentos")
    form = DocumentoForm(request.POST, request.FILES)
    if form.is_valid():
        documento = form.save(commit=False)
        documento.proyecto, documento.subido_por = proyecto, request.user
        documento.save()
        messages.success(request, "Documento guardado en el proyecto.")
    else:
        messages.error(request, "No se pudo subir el documento.")
    return redirect("proyecto_detalle", pk=pk)


@login_required
@require_POST
def documento_eliminar(request, pk, documento_pk):
    proyecto, _ = _proyecto(request, pk, "documentos")
    documento = get_object_or_404(DocumentoProyecto, pk=documento_pk, proyecto=proyecto)
    documento.archivo.delete(save=False)
    documento.delete()
    messages.success(request, "Documento eliminado.")
    return redirect("proyecto_detalle", pk=pk)


@login_required
@require_POST
def correccion_crear(request, pk):
    proyecto, _ = _proyecto(request, pk, "correcciones")
    form = CorreccionForm(request.POST, proyecto=proyecto)
    if form.is_valid():
        correccion = form.save(commit=False)
        correccion.proyecto, correccion.autor = proyecto, request.user
        correccion.save()
        messages.success(request, "Corrección registrada. Es una observación, no una calificación automática.")
    else:
        messages.error(request, "No se pudo guardar la corrección.")
    return redirect("proyecto_detalle", pk=pk)
