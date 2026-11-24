from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Empresa, Equipo, MiembroEquipo, Rol, Usuario
from .politica import obtener_politica


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "nit", "propietario", "sector", "num_empleados", "total_usuarios", "fecha_creacion")
    autocomplete_fields = ("propietario",)
    list_filter = ("sector", "num_empleados")
    search_fields = ("nombre", "nit", "email")

    @admin.display(description="usuarios")
    def total_usuarios(self, obj):
        return obj.usuarios.count()


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ("nombre", "codigo", "descripcion")


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """Administración de usuarios adaptada a 'login con correo'."""

    ordering = ("email",)
    list_display = ("email", "first_name", "last_name", "empresa", "rol", "is_active")
    list_filter = ("rol", "empresa", "is_active", "is_staff")
    search_fields = ("email", "first_name", "last_name")
    autocomplete_fields = ("empresa",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Datos personales", {"fields": ("first_name", "last_name", "cargo", "telefono", "avatar")}),
        ("Empresa", {"fields": ("empresa", "rol")}),
        ("Permisos", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Fechas", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "first_name", "last_name", "empresa", "rol", "password1", "password2")}),
    )

    # Campos de permisos globales: solo el superadministrador los cambia
    CAMPOS_DE_PODER = ("is_superuser", "is_staff", "groups", "user_permissions")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # En "rol" solo aparecen los roles que la política deja asignar a quien edita
        if db_field.name == "rol":
            kwargs["queryset"] = Rol.objects.filter(codigo__in=obtener_politica().roles_asignables(request.user))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        bloqueados = () if obtener_politica().es_superadministrador(request.user) else self.CAMPOS_DE_PODER
        return tuple(super().get_readonly_fields(request, obj)) + bloqueados


class MiembroEquipoInline(admin.TabularInline):
    model = MiembroEquipo
    extra = 1
    autocomplete_fields = ("usuario",)


@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "empresa", "total_miembros", "fecha_creacion")
    list_filter = ("empresa",)
    search_fields = ("nombre",)
    inlines = [MiembroEquipoInline]

    @admin.display(description="miembros")
    def total_miembros(self, obj):
        return obj.miembros.count()  # se cuenta: no se guarda
