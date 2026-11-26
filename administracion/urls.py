from django.urls import path

from . import views, views_importacion as importacion, views_monitoreo as monitoreo, views_reportes as reportes

app_name = "administracion"

urlpatterns = [
    # Usuarios
    path("", views.inicio, name="inicio"),
    path("usuarios/nuevo/", views.crear_usuario, name="crear_usuario"),
    path("usuarios/<int:pk>/", views.editar_usuario, name="editar_usuario"),
    path("usuarios/<int:pk>/eliminar/", views.eliminar_usuario, name="eliminar_usuario"),
    # Carga masiva desde CSV (validación previa, todo o nada)
    path("importar/", importacion.importar, name="importar"),
    path("importar/plantilla/<str:tipo>/", importacion.plantilla, name="importar_plantilla"),
    # Reportes con filtros de varios criterios (Excel y PDF)
    path("reportes/", reportes.reportes, name="reportes"),
    path("reportes/exportar/<str:formato>/", reportes.reportes_exportar, name="reportes_exportar"),
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
