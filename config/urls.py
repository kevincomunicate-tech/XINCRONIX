"""URLs principales de Xincronix: cada app trae las suyas."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),          # administración de Django
    path("", include("sitio.urls")),          # página pública (portada)
    path("cuentas/", include("cuentas.urls")),  # login, registro, recuperar, mi cuenta
    # Inicio de sesión con Google (django-allauth): solo las URLs necesarias
    path("cuentas/social/", include("cuentas.urls_google")),
    path("app/", include("dashboard.urls")),  # todo lo que requiere sesión
    # Solo el superadministrador (lo controla config/politica_accesos.json)
    path("administracion/", include("administracion.urls")),
]

# En desarrollo Django sirve las fotos de perfil subidas (en producción lo hace el servidor web)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
