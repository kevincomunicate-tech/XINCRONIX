from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("salir/", auth_views.LogoutView.as_view(), name="logout"),
    path("registro/", views.registro, name="registro"),

    # Recuperar contraseña: pedir enlace -> enviado -> nueva contraseña -> listo
    path("recuperar/", views.RecuperarView.as_view(), name="recuperar"),
    path("recuperar/enviado/", views.RecuperarEnviadoView.as_view(), name="recuperar_enviado"),
    path("recuperar/<uidb64>/<token>/", views.NuevaContrasenaView.as_view(), name="password_reset_confirm"),
    path("recuperar/listo/", views.RecuperarListoView.as_view(), name="recuperar_listo"),
]
