"""Decoradores para las vistas: piden sesión y consultan la política."""

from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from .politica import obtener_politica


def requiere_accion(accion):
    """La vista exige sesión y que el perfil tenga la acción en el JSON.

        @requiere_accion("crear_proyecto")
        def proyecto_crear(request): ...
    """
    def decorador(vista):
        @wraps(vista)
        @login_required
        def envoltura(request, *args, **kwargs):
            if not obtener_politica().puede(request.user, accion):
                raise PermissionDenied(f"El perfil no tiene la acción '{accion}'.")
            return vista(request, *args, **kwargs)
        return envoltura
    return decorador


def exigir(permisos, permiso):
    """Corta la petición con 403 si el permiso no está en el conjunto."""
    if permiso not in permisos:
        raise PermissionDenied(f"Falta el permiso '{permiso}'.")
