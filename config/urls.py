"""URLs principales de Xincronix: cada app trae las suyas."""

from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

urlpatterns = [
    path("", include("sitio.urls")),          # página pública (portada)
    path("cuentas/", include("cuentas.urls")),  # login, registro, recuperar, mi cuenta
    # Inicio de sesión con Google (django-allauth): solo las URLs necesarias
    path("cuentas/social/", include("cuentas.urls_google")),
    path("app/", include("dashboard.urls")),  # todo lo que requiere sesión
    # Vista pública de un proyecto: fuera de /app/ para que no pida inicio de sesión.
    path("publico/", include("dashboard.urls_publico")),
    # Administradores activos de Xincronix
    path("administracion/", include("administracion.urls")),
]

# En desarrollo Django sirve las fotos de perfil subidas (en producción lo hace el servidor web)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
