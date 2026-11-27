"""
Integraciones externas de cada proyecto:

* Asistente IA (Google Gemini): preguntas sobre el proyecto con sus datos.
* Repositorio (GitHub): datos del repositorio enlazado en el proyecto.

Las dos funcionan solo si se configuran en .env; sin claves, cada página explica
cómo activarlas y el resto del sistema sigue igual.
"""

import json

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from django.http import Http404, JsonResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_http_methods

from . import gemini, github
from .forms import PreguntaAsistenteForm, RenombrarChatForm
from .models import ChatAsistente
from .views import _proyecto


@transaction.atomic
def _guardar_turno(chat, proyecto, usuario, pregunta, respuesta, titulo):
    if chat is None:
        chat = ChatAsistente.objects.create(
            proyecto=proyecto, usuario=usuario, titulo=titulo or f"Consulta sobre {proyecto.nombre}"[:100],
        )
    actualizados = ChatAsistente.objects.filter(pk=chat.pk, version=chat.version).update(
        actualizado=timezone.now(), version=F("version") + 1,
    )
    if not actualizados:
        raise gemini.GeminiError("Este chat recibió otra respuesta mientras esperabas. Vuelve a abrirlo e intenta de nuevo.")
    chat.turnos.create(pregunta=pregunta, respuesta=respuesta)
    return chat


def _url_chat(proyecto, chat):
    base = reverse("proyecto_asistente", args=[proyecto.pk])
    return f"{base}?chat={chat.pk}" if chat else f"{base}?nuevo=1"


def _asistente_en_vivo(request, proyecto, chat, contexto, pregunta):
    def emitir(datos):
        return json.dumps(datos, ensure_ascii=False) + "\n"

    def eventos():
        fragmentos = []
        try:
            flujo = gemini.preguntar_en_vivo(proyecto, pregunta, contexto, titular=chat is None)
            titulo, flujo = gemini.separar_titulo(flujo) if chat is None else ("", flujo)
            for fragmento in flujo:
                if fragmento:
                    fragmentos.append(fragmento)
                    yield emitir({"texto": fragmento})
            respuesta = "".join(fragmentos).strip()
            if not respuesta:
                raise gemini.GeminiError("Gemini devolvió una respuesta vacía. Intenta de nuevo.")
            guardado = _guardar_turno(chat, proyecto, request.user, pregunta, respuesta, titulo)
            yield emitir({"final": True, "url": _url_chat(proyecto, guardado) + "#ultima"})
        except gemini.GeminiError as error:
            yield emitir({"error": str(error)})

    return StreamingHttpResponse(eventos(), content_type="application/x-ndjson; charset=utf-8", headers={
        "Cache-Control": "no-store",
        "X-Accel-Buffering": "no",
    })


@login_required
@require_http_methods(["GET", "POST"])
def proyecto_asistente(request, pk):
    proyecto, permisos = _proyecto(request, pk)
    chats = ChatAsistente.objects.filter(proyecto=proyecto, usuario=request.user)
    url_nuevo = _url_chat(proyecto, None)
    if request.method == "POST" and request.POST.get("accion") == "limpiar":
        return redirect(url_nuevo)

    chat_id = request.GET.get("chat")
    if chat_id is not None:
        if not chat_id.isascii() or not chat_id.isdigit() or len(chat_id) > 18:
            raise Http404
        chat = get_object_or_404(chats, pk=chat_id)
    else:
        chat = None if request.GET.get("nuevo") == "1" else chats.first()
    url_actual = _url_chat(proyecto, chat)
    form = PreguntaAsistenteForm()

    if request.method == "POST":
        en_vivo = request.headers.get("Accept") == "application/x-ndjson"
        if not gemini.disponible():
            if en_vivo:
                return JsonResponse({"error": "El asistente no está configurado."}, status=503)
            messages.error(request, "El asistente no está configurado: falta GEMINI_API_KEY en el archivo .env.")
            return redirect(url_actual)
        form = PreguntaAsistenteForm(request.POST)
        if form.is_valid():
            if not gemini.registrar_uso(request.user):
                aviso = f"Llegaste al límite de {settings.GEMINI_LIMITE_POR_HORA} preguntas por hora. Intenta más tarde."
                if en_vivo:
                    return JsonResponse({"error": aviso}, status=429)
                messages.error(request, aviso)
                return redirect(url_actual)
            pregunta = form.cleaned_data["pregunta"]
            contexto = []
            if chat:
                recientes = chat.turnos.order_by("-pk").values("pregunta", "respuesta")[:gemini.MAX_TURNOS]
                contexto = list(reversed(list(recientes)))
            if en_vivo:
                return _asistente_en_vivo(request, proyecto, chat, contexto, pregunta)
            try:
                respuesta = gemini.preguntar(proyecto, pregunta, contexto, titular=chat is None)
                titulo = ""
                if chat is None:
                    titulo, fragmentos = gemini.separar_titulo(iter((respuesta,)))
                    respuesta = "".join(fragmentos).strip()
                    if not respuesta:
                        raise gemini.GeminiError("Gemini devolvió una respuesta vacía. Intenta de nuevo.")
                guardado = _guardar_turno(chat, proyecto, request.user, pregunta, respuesta, titulo)
            except gemini.GeminiError as error:
                messages.error(request, str(error))
                return redirect(url_actual)
            return redirect(_url_chat(proyecto, guardado) + "#ultima")

        if en_vivo:
            return JsonResponse({"error": "Escribe una pregunta de hasta 1000 caracteres."}, status=400)

    return render(request, "dashboard/proyectos/asistente.html", {
        "proyecto": proyecto, "permisos": permisos, "form": form, "chats": chats, "chat": chat,
        "url_nuevo": url_nuevo, "url_actual": url_actual,
        "conversacion": chat.turnos.all() if chat else [],
        "disponible": gemini.disponible(), "sugerencias": gemini.SUGERENCIAS, "modelo": settings.GEMINI_MODEL,
        "restantes": gemini.usos_restantes(request.user), "limite": settings.GEMINI_LIMITE_POR_HORA,
    })


@login_required
@require_http_methods(["GET", "POST"])
def gestionar_chat(request, pk, chat_id, accion):
    proyecto, _ = _proyecto(request, pk)
    chats = ChatAsistente.objects.filter(proyecto=proyecto, usuario=request.user)
    chat = get_object_or_404(chats, pk=chat_id)
    url_actual = _url_chat(proyecto, chat)

    if accion == "eliminar":
        if request.method == "POST":
            chats.filter(pk=chat.pk).delete()
            messages.success(request, "Conversación eliminada.")
            return redirect(reverse("proyecto_asistente", args=[proyecto.pk]))
        return render(request, "confirmar_eliminar.html", {
            "titulo": "Eliminar conversación",
            "objeto": chat.titulo,
            "consecuencias": ["Se eliminarán todas las preguntas y respuestas de esta conversación."],
            "url_cancelar": url_actual,
        })

    form = RenombrarChatForm(
        request.POST if request.method == "POST" else None,
        initial={"titulo": chat.titulo},
    )
    if request.method == "POST" and form.is_valid():
        if not chats.filter(pk=chat.pk).update(titulo=form.cleaned_data["titulo"]):
            raise Http404
        messages.success(request, "Título actualizado.")
        return redirect(url_actual)

    return render(request, "dashboard/proyectos/renombrar_chat.html", {
        "form": form, "url_cancelar": url_actual,
    })


@login_required
@require_GET
def proyecto_repositorio(request, pk):
    proyecto, permisos = _proyecto(request, pk)
    destino = github.analizar_url(proyecto.repositorio_url)
    usar_token = request.user.es_admin
    contexto = {
        "proyecto": proyecto, "permisos": permisos, "enlace": proyecto.repositorio_url,
        "es_github": destino is not None, "con_token": usar_token and bool(settings.GITHUB_TOKEN),
    }
    if destino:
        dueno, repo = destino
        elegido = request.GET.get("repo", "")
        if repo is None and github.nombre_valido(elegido):
            repo = elegido  # se eligió un repositorio de la lista del usuario u organización
            contexto["desde_lista"] = True
        contexto["dueno"] = dueno
        try:
            if repo:
                contexto["repo"] = github.repositorio(dueno, repo, usar_token=usar_token)
            else:
                contexto["lista"] = github.repositorios_de(dueno)
        except github.GitHubError as error:
            contexto["error"] = str(error)
    return render(request, "dashboard/proyectos/repositorio.html", contexto)
