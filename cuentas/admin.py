from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Empresa, Equipo, Usuario


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "creada_en")
    search_fields = ("nombre",)


@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "empresa", "creado_en")
    list_filter = ("empresa",)
    search_fields = ("nombre", "empresa__nombre")
    filter_horizontal = ("miembros",)


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """Panel de administración de usuarios adaptado a 'login con correo'."""

    ordering = ("email",)
    list_display = ("email", "first_name", "last_name", "empresa", "rol", "is_active", "date_joined")
    list_filter = ("empresa", "rol", "is_active", "is_staff")
    search_fields = ("email", "first_name", "last_name", "empresa__nombre")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Datos personales", {"fields": ("first_name", "last_name", "empresa", "rol")}),
        ("Permisos", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Fechas", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "first_name", "last_name", "empresa", "rol", "password1", "password2")}),
    )
