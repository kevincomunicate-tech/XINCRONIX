from django.urls import path

from . import views

urlpatterns = [
    path("", views.panel, name="panel"),

    # Mi empresa: crearla, ver sus métricas, editarla y eliminarla
    path("empresa/", views.mi_empresa, name="mi_empresa"),
    path("empresa/editar/", views.mi_empresa_editar, name="mi_empresa_editar"),
    path("empresa/eliminar/", views.mi_empresa_eliminar, name="mi_empresa_eliminar"),

    # Proyectos (CRUD) con sus miembros y tareas
    path("proyectos/", views.proyectos, name="proyectos"),
    path("proyectos/nuevo/", views.proyecto_crear, name="proyecto_crear"),
    path("proyectos/<int:pk>/", views.proyecto_detalle, name="proyecto_detalle"),
    path("proyectos/<int:pk>/editar/", views.proyecto_editar, name="proyecto_editar"),
    path("proyectos/<int:pk>/eliminar/", views.proyecto_eliminar, name="proyecto_eliminar"),
    path("proyectos/<int:pk>/miembros/", views.miembro_agregar, name="miembro_agregar"),
    path("proyectos/<int:pk>/miembros/<int:miembro_pk>/quitar/", views.miembro_quitar, name="miembro_quitar"),
    path("proyectos/<int:pk>/tareas/nueva/", views.tarea_crear, name="tarea_crear"),
    path("tareas/", views.tareas, name="tareas"),
    path("tareas/<int:pk>/editar/", views.tarea_editar, name="tarea_editar"),
    path("tareas/<int:pk>/eliminar/", views.tarea_eliminar, name="tarea_eliminar"),

    # Secciones que todavía se están migrando
    path("ideas/", views.proximamente, {"seccion": "Tablero de ideas"}, name="ideas"),
    path("canvas/", views.proximamente, {"seccion": "Canvas"}, name="canvas"),
    path("analytics/", views.proximamente, {"seccion": "Analytics"}, name="analytics"),
    path("equipo/", views.proximamente, {"seccion": "Equipo"}, name="equipo"),
    path("asistente/", views.proximamente, {"seccion": "Asistente virtual"}, name="asistente"),
    path("automatizaciones/", views.proximamente, {"seccion": "Automatizaciones"}, name="automatizaciones"),
]
