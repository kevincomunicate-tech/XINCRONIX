from django.contrib import admin

from .models import Actividad, Equipo, MiembroEquipo, MiembroProyecto, Proyecto, Tarea


class MiembroEquipoInline(admin.TabularInline):
    model = MiembroEquipo
    extra = 1
    autocomplete_fields = ("usuario",)


@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "empresa", "fecha_creacion")
    list_filter = ("empresa",)
    search_fields = ("nombre",)
    inlines = (MiembroEquipoInline,)


class MiembroProyectoInline(admin.TabularInline):
    model = MiembroProyecto
    extra = 1
    autocomplete_fields = ("usuario",)


class TareaInline(admin.TabularInline):
    model = Tarea
    extra = 0
    fields = ("titulo", "estado", "prioridad", "asignada_a", "fecha_vencimiento")
    autocomplete_fields = ("asignada_a",)
    show_change_link = True


@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "empresa", "estado", "nivel_importancia", "tipo_proyecto", "fecha_fin", "progreso_txt")
    list_filter = ("estado", "nivel_importancia", "tipo_proyecto", "empresa")
    search_fields = ("nombre", "descripcion")
    autocomplete_fields = ("creador", "equipo")
    inlines = (MiembroProyectoInline, TareaInline)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("empresa").con_progreso()

    @admin.display(description="avance")
    def progreso_txt(self, obj):
        return f"{obj.progreso}%"

    def get_changeform_initial_data(self, request):
        iniciales = {"creador": request.user.pk}
        if request.user.empresa_id:
            iniciales["empresa"] = request.user.empresa_id
        return {**iniciales, **super().get_changeform_initial_data(request)}

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change:
            Actividad.registrar_proyecto_creado(request.user, obj)


@admin.register(Tarea)
class TareaAdmin(admin.ModelAdmin):
    list_display = ("titulo", "proyecto", "estado", "prioridad", "asignada_a", "fecha_vencimiento")
    list_filter = ("estado", "prioridad", "proyecto")
    search_fields = ("titulo", "descripcion")
    autocomplete_fields = ("proyecto", "asignada_a")
    readonly_fields = ("creador", "fecha_creacion", "fecha_completada")
    list_select_related = ("proyecto", "asignada_a")

    def save_model(self, request, obj, form, change):
        if not change:
            obj.creador = request.user
        super().save_model(request, obj, form, change)
        if not change or "estado" in form.changed_data:
            Actividad.registrar_tarea(request.user, obj, creada=not change)


@admin.register(Actividad)
class ActividadAdmin(admin.ModelAdmin):
    """Solo lectura: el historial no se edita a mano."""

    list_display = ("fecha", "usuario", "tipo", "descripcion", "proyecto", "empresa")
    list_filter = ("tipo", "empresa")
    search_fields = ("descripcion",)
    list_select_related = ("usuario", "proyecto", "empresa")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
