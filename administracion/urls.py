from django.urls import path

from . import views

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
]
