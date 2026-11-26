from django.urls import path

from . import views

urlpatterns = [
    path("", views.panel, name="panel"),
    path("proyectos/", views.proyectos, name="proyectos"),
    path("proyectos/nuevo/", views.proyecto_orientacion, name="proyecto_orientacion"),
    path("proyectos/nuevo/detalles/", views.proyecto_crear, name="proyecto_crear"),
    path("proyectos/<int:pk>/", views.proyecto_detalle, name="proyecto_detalle"),
    path("proyectos/<int:pk>/editar/", views.proyecto_editar, name="proyecto_editar"),
    path("proyectos/<int:pk>/enlace/nuevo/", views.proyecto_enlace_nuevo, name="proyecto_enlace_nuevo"),
    path("proyectos/<int:pk>/eliminar/", views.proyecto_eliminar, name="proyecto_eliminar"),
    path("proyectos/<int:pk>/invitaciones/", views.invitacion_crear, name="invitacion_crear"),
    path("invitaciones/<uuid:token>/aceptar/", views.invitacion_aceptar, name="invitacion_aceptar"),
    path("proyectos/<int:pk>/miembros/<int:miembro_pk>/quitar/", views.miembro_quitar, name="miembro_quitar"),
    path("proyectos/<int:pk>/miembros/<int:miembro_pk>/rol/", views.miembro_cambiar_rol, name="miembro_cambiar_rol"),
    path("proyectos/<int:pk>/tareas/nueva/", views.tarea_crear, name="tarea_crear"),
    path("tareas/", views.tareas, name="tareas"),
    path("tareas/<int:pk>/editar/", views.tarea_editar, name="tarea_editar"),
    path("tareas/<int:pk>/eliminar/", views.tarea_eliminar, name="tarea_eliminar"),
    path("proyectos/<int:pk>/tablero/", views.proyecto_tablero, name="proyecto_tablero"),
    path("proyectos/<int:pk>/tablero/tareas/<int:tarea_pk>/mover/", views.tarea_mover, name="tarea_mover"),
    path("proyectos/<int:pk>/calendario/", views.proyecto_calendario, name="proyecto_calendario"),
    path("proyectos/<int:pk>/calendario/eventos/", views.evento_crear, name="evento_crear"),
    path("proyectos/<int:pk>/roadmap/", views.proyecto_roadmap, name="proyecto_roadmap"),
    path("proyectos/<int:pk>/estadisticas/", views.proyecto_analytics, name="proyecto_analytics"),
    path("proyectos/<int:pk>/canvas/", views.proyecto_canvas, name="proyecto_canvas"),
    path("proyectos/<int:pk>/canvas/guardar/", views.canvas_guardar, name="canvas_guardar"),
    path("proyectos/<int:pk>/documentos/subir/", views.documento_subir, name="documento_subir"),
    path("proyectos/<int:pk>/documentos/<int:documento_pk>/eliminar/", views.documento_eliminar, name="documento_eliminar"),
    path("proyectos/<int:pk>/correcciones/", views.correccion_crear, name="correccion_crear"),
]
