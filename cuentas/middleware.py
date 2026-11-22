"""
Enrutamiento por perfil.

Revisa cada petición contra "rutas_restringidas" de config/politica_accesos.json:
  * Ruta libre                       -> sigue normal.
  * Ruta restringida y sin sesión    -> al login (y vuelve después).
  * Ruta restringida y perfil no permitido -> 403 Prohibido.

Las vistas no repiten esta regla: la ruta se protege en un solo lugar.
"""

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied

from .politica import obtener_politica


class PoliticaAccesoMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        politica = obtener_politica()
        permitidos = politica.perfiles_permitidos(request.path_info)

        if permitidos is not None and not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if permitidos is not None and politica.perfil_de(request.user) not in permitidos:
            raise PermissionDenied("Tu perfil no tiene acceso a esta sección.")

        return self.get_response(request)
