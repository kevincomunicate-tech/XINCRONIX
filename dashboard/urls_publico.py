from django.urls import path

from . import views

urlpatterns = [
    path("<uuid:enlace>/", views.proyecto_publico, name="proyecto_publico"),
]
