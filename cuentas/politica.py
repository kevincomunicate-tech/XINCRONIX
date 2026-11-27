"""Reglas pequeñas y explícitas para separar el área administrativa del /app/."""

from django.urls import reverse

from .models import Usuario


class Politica:
    def perfil_de(self, usuario):
        if not usuario or not usuario.is_authenticated:
            return "anonimo"
        if not usuario.is_active:
            return None
        return usuario.rol

    def es_superadministrador(self, usuario):
        return bool(getattr(usuario, "es_admin", False))

    def puede(self, usuario, accion):
        return bool(usuario.is_authenticated and usuario.is_active)

    def url_inicio(self, usuario):
        return reverse("administracion:inicio") if getattr(usuario, "es_admin", False) else reverse("panel")

    def menu(self, usuario, ruta_actual=""):
        if not getattr(usuario, "es_admin", False):
            return []
        href = reverse("administracion:inicio")
        return [{"texto": "Administración", "href": href, "icono": "bi-shield-lock", "activo": ruta_actual.startswith(href)}]

    def perfiles_permitidos(self, ruta):
        if ruta.startswith("/administracion/"):
            return frozenset({Usuario.Rol.ADMIN})
        if ruta.startswith("/app/"):
            return frozenset(Usuario.Rol.values)
        return None


_POLITICA = Politica()


def obtener_politica():
    return _POLITICA
