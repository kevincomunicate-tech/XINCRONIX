"""Reglas pequeñas y explícitas para separar el área administrativa del /app/."""

from django.urls import reverse


class Politica:
    def perfil_de(self, usuario):
        if not usuario or not usuario.is_authenticated:
            return "anonimo"
        if usuario.is_superuser:
            return "administrador"
        return usuario.perfil

    def es_superadministrador(self, usuario):
        return bool(usuario.is_authenticated and usuario.is_superuser)

    def puede(self, usuario, accion):
        return bool(usuario.is_authenticated)

    def url_inicio(self, usuario):
        return reverse("administracion:inicio") if usuario.is_superuser else reverse("panel")

    def menu(self, usuario, ruta_actual=""):
        if not getattr(usuario, "is_superuser", False):
            return []
        href = reverse("administracion:inicio")
        return [{"texto": "Administración", "href": href, "icono": "bi-shield-lock", "activo": ruta_actual.startswith(href)}]

    def perfiles_permitidos(self, ruta):
        if ruta.startswith("/administracion/"):
            return frozenset({"administrador"})
        if ruta.startswith("/app/"):
            return frozenset({"administrador", "profesional", "estudiante", "profesor"})
        return None


_POLITICA = Politica()


def obtener_politica():
    return _POLITICA
