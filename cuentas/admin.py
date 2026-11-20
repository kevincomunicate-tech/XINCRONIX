from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Empresa, Rol, Usuario


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "nit", "email", "sector", "fecha_creacion")
    search_fields = ("nombre", "nit", "email")


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    """Los roles los crea la migración; aquí solo se consultan."""

    list_display = ("codigo", "nombre", "descripcion")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """Panel de administración de usuarios adaptado a 'login con correo'."""

    ordering = ("email",)
    list_display = ("email", "nombres", "apellidos", "empresa", "rol", "is_active", "fecha_creacion")
    list_filter = ("rol", "empresa", "is_active", "is_staff")
    search_fields = ("email", "nombres", "apellidos")
    list_select_related = ("empresa", "rol")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Datos personales", {"fields": ("nombres", "apellidos", "cargo", "telefono", "avatar")}),
        ("Empresa", {"fields": ("empresa", "rol")}),
        ("Permisos", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Fechas", {"fields": ("last_login", "fecha_creacion")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "nombres", "apellidos", "empresa", "rol", "password1", "password2"),
        }),
    )
