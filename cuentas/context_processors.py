"""Datos de la política disponibles en todas las plantillas."""

from django.conf import settings

from .politica import obtener_politica


def politica_usuario(request):
    politica = obtener_politica()
    return {
        "perfil_actual": politica.perfil_de(request.user),
        "menu_perfil": politica.menu(request.user, request.path_info),
    }


def inicio_google(request):
    """¿Está configurado el inicio de sesión con Google? (credenciales en .env)"""
    return {"google_activo": bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET)}
