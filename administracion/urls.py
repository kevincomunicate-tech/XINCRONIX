from django.urls import path

from . import views, views_monitoreo as monitoreo

app_name = "administracion"

urlpatterns = [
    # Usuarios
    path("", views.inicio, name="inicio"),
    path("usuarios/nuevo/", views.crear_usuario, name="crear_usuario"),
    path("usuarios/<int:pk>/", views.editar_usuario, name="editar_usuario"),
    path("usuarios/<int:pk>/eliminar/", views.eliminar_usuario, name="eliminar_usuario"),
    # Empresas
    path("empresas/", views.empresas, name="empresas"),
    path("empresas/nueva/", views.crear_empresa, name="crear_empresa"),
    path("empresas/<int:pk>/", views.empresa_detalle, name="empresa_detalle"),
    path("empresas/<int:pk>/editar/", views.editar_empresa, name="editar_empresa"),
    path("empresas/<int:pk>/eliminar/", views.eliminar_empresa, name="eliminar_empresa"),
    path("empresas/<int:pk>/vincular/", views.vincular_usuario, name="vincular_usuario"),
    path("empresas/<int:pk>/desvincular/<int:usuario_pk>/", views.desvincular_usuario, name="desvincular_usuario"),
    # Monitoreo de la base de datos (solo lectura, salvo cerrar sesiones)
    path("monitoreo/", monitoreo.resumen, name="monitoreo"),
    path("monitoreo/tablas/", monitoreo.tablas, name="monitoreo_tablas"),
    path("monitoreo/tablas/<str:app_label>/<str:modelo>/", monitoreo.tabla, name="monitoreo_tabla"),
    path("monitoreo/tablas/<str:app_label>/<str:modelo>/exportar/", monitoreo.exportar, name="monitoreo_exportar"),
    path("monitoreo/tablas/<str:app_label>/<str:modelo>/<str:pk>/", monitoreo.registro, name="monitoreo_registro"),
    path("monitoreo/sesiones/", monitoreo.sesiones, name="monitoreo_sesiones"),
    path("monitoreo/sesiones/cerrar/", monitoreo.cerrar_sesiones, name="monitoreo_cerrar_sesiones"),
    path("monitoreo/sistema/", monitoreo.sistema, name="monitoreo_sistema"),
]
