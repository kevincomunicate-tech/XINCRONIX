"""URLs principales de Xincronix: cada app trae las suyas."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),          # administración de Django
    path("", include("sitio.urls")),          # página de inicio pública
    path("cuentas/", include("cuentas.urls")),  # login, registro, recuperar
    path("app/", include("dashboard.urls")),  # todo lo que requiere sesión
]
