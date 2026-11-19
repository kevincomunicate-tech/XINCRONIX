from django.contrib import admin

from .models import Actividad, MiembroProyecto, Proyecto, Tarea


class MiembroInline(admin.TabularInline):
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
    list_display = ("nombre", "propietario", "estado", "prioridad", "fecha_fin", "progreso_txt")
    list_filter = ("estado", "prioridad")
    search_fields = ("nombre", "descripcion")
    autocomplete_fields = ("propietario",)
    inlines = (MiembroInline, TareaInline)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("propietario").con_progreso()

    @admin.display(description="avance")
    def progreso_txt(self, obj):
        return f"{obj.progreso}%"

    def get_changeform_initial_data(self, request):
        return {"propietario": request.user.pk, **super().get_changeform_initial_data(request)}

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change:
            Actividad.registrar(request.user, Actividad.Accion.PROYECTO_CREADO, obj)


@admin.register(Tarea)
class TareaAdmin(admin.ModelAdmin):
    list_display = ("titulo", "proyecto", "estado", "prioridad", "asignada_a", "fecha_vencimiento")
    list_filter = ("estado", "prioridad", "proyecto")
    search_fields = ("titulo", "descripcion")
    autocomplete_fields = ("proyecto", "asignada_a")
    readonly_fields = ("creada_por", "creada", "completada_en")
    list_select_related = ("proyecto", "asignada_a")

    def save_model(self, request, obj, form, change):
        if not change:
            obj.creada_por = request.user
        super().save_model(request, obj, form, change)

        if not change:
            accion = Actividad.Accion.TAREA_CREADA
        elif "estado" in form.changed_data:
            completada = obj.estado == Tarea.Estado.COMPLETADA
            accion = Actividad.Accion.TAREA_COMPLETADA if completada else Actividad.Accion.TAREA_MOVIDA
        else:
            return
        Actividad.registrar(request.user, accion, obj.proyecto, obj)


@admin.register(Actividad)
class ActividadAdmin(admin.ModelAdmin):
    """Solo lectura: el historial no se edita a mano."""

    list_display = ("fecha", "usuario", "accion", "detalle", "proyecto")
    list_filter = ("accion",)
    search_fields = ("detalle",)
    list_select_related = ("usuario", "proyecto")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
