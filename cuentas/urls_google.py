"""
URLs de django-allauth que de verdad usamos (montadas en /cuentas/social/).

No se incluye allauth.urls completo: sus páginas de contraseña, correos y
conexiones duplicarían las nuestras. Solo queda:
  * el flujo de Google (google/login/ y google/login/callback/),
  * las páginas de error o cancelación (con nuestro diseño, en templates/socialaccount/),
  * los nombres de URL que allauth necesita, apuntando a nuestras páginas.
"""

from allauth.socialaccount import views as social_views
from allauth.socialaccount.providers.google.provider import GoogleProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from django.urls import path
from django.views.generic import RedirectView

from . import views

urlpatterns = default_urlpatterns(GoogleProvider) + [
    path("login/cancelado/", social_views.login_cancelled, name="socialaccount_login_cancelled"),
    path("login/error/", social_views.login_error, name="socialaccount_login_error"),
    # Si Google no entregara datos suficientes para crear la cuenta, se usa nuestro registro
    path("registro/", RedirectView.as_view(pattern_name="registro"), name="socialaccount_signup"),
    # Nombres internos de allauth -> nuestras páginas
    path("login/", RedirectView.as_view(pattern_name="login", query_string=True), name="account_login"),
    path("signup/", RedirectView.as_view(pattern_name="registro"), name="account_signup"),
    path("inactiva/", views.cuenta_inactiva, name="account_inactive"),
]
