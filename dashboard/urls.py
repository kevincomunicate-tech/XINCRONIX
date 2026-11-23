from django.urls import path

from . import views

urlpatterns = [
    path("", views.panel, name="panel"),
    path("proyectos/", views.proyectos, name="proyectos"),
    path("proyectos/nuevo/", views.proyecto_crear, name="proyecto_crear"),
    path("proyectos/<int:proyecto_id>/github/", views.github_referencias, name="github_referencias"),
    path(
        "proyectos/<int:proyecto_id>/github/<int:referencia_id>/eliminar/",
        views.github_referencia_eliminar,
        name="github_referencia_eliminar",
    ),
    path("proyectos/<int:proyecto_id>/editar/", views.proyecto_editar, name="proyecto_editar"),
    path("proyectos/<int:proyecto_id>/eliminar/", views.proyecto_eliminar, name="proyecto_eliminar"),
    path("tareas/", views.tareas, name="tareas"),
    path("tareas/nueva/", views.tarea_crear, name="tarea_crear"),
    path("tareas/<int:tarea_id>/editar/", views.tarea_editar, name="tarea_editar"),
    path("tareas/<int:tarea_id>/eliminar/", views.tarea_eliminar, name="tarea_eliminar"),
    path("tareas/<int:tarea_id>/estado/", views.tarea_cambiar_estado, name="tarea_cambiar_estado"),
    path("ideas/", views.proximamente, {"seccion": "Tablero de ideas"}, name="ideas"),
    path("canvas/", views.proximamente, {"seccion": "Canvas"}, name="canvas"),
    path("analytics/", views.proximamente, {"seccion": "Analytics"}, name="analytics"),
    path("equipo/", views.equipos, name="equipo"),
    path("equipo/nuevo/", views.equipo_crear, name="equipo_crear"),
    path("equipo/<int:equipo_id>/editar/", views.equipo_editar, name="equipo_editar"),
    path("equipo/<int:equipo_id>/eliminar/", views.equipo_eliminar, name="equipo_eliminar"),
    path("equipo/miembros/", views.miembros, name="miembros"),
    path("equipo/miembros/nuevo/", views.miembro_crear, name="miembro_crear"),
    path("equipo/miembros/<int:miembro_id>/editar/", views.miembro_editar, name="miembro_editar"),
    path("equipo/miembros/<int:miembro_id>/eliminar/", views.miembro_eliminar, name="miembro_eliminar"),
    path("asistente/", views.proximamente, {"seccion": "Asistente virtual"}, name="asistente"),
    path("automatizaciones/", views.proximamente, {"seccion": "Automatizaciones"}, name="automatizaciones"),
]
