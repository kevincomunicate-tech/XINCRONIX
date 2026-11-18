from django.urls import path

from . import views

urlpatterns = [
    path("", views.panel, name="panel"),
    path("proyectos/", views.proximamente, {"seccion": "Proyectos"}, name="proyectos"),
    path("tareas/", views.proximamente, {"seccion": "Tareas"}, name="tareas"),
    path("ideas/", views.proximamente, {"seccion": "Tablero de ideas"}, name="ideas"),
    path("canvas/", views.proximamente, {"seccion": "Canvas"}, name="canvas"),
    path("analytics/", views.proximamente, {"seccion": "Analytics"}, name="analytics"),
    path("equipo/", views.proximamente, {"seccion": "Equipo"}, name="equipo"),
    path("asistente/", views.proximamente, {"seccion": "Asistente virtual"}, name="asistente"),
    path("automatizaciones/", views.proximamente, {"seccion": "Automatizaciones"}, name="automatizaciones"),
]
