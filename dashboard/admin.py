from django.contrib import admin

from .models import (
    Actividad, Idea, Lienzo, LienzoColaborador, MetricaRendimiento,
    Notificacion, Proyecto, ProyectoMiembro, Tarea, VotoIdea,
)


class ProyectoMiembroInline(admin.TabularInline):
    model = ProyectoMiembro
    extra = 1
    autocomplete_fields = ("usuario",)


class TareaInline(admin.TabularInline):
    model = Tarea
    extra = 0
    fields = ("titulo", "estado", "prioridad", "asignado_a", "fecha_vencimiento")
    autocomplete_fields = ("asignado_a",)


@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "empresa", "estado", "nivel_importancia", "equipo", "progreso_txt", "fecha_fin")
    list_filter = ("estado", "tipo_proyecto", "empresa")
    search_fields = ("nombre", "descripcion")
    autocomplete_fields = ("equipo", "creado_por")
    inlines = [ProyectoMiembroInline, TareaInline]

    @admin.display(description="progreso")
    def progreso_txt(self, obj):
        return f"{obj.progreso}%"


@admin.register(Tarea)
class TareaAdmin(admin.ModelAdmin):
    list_display = ("titulo", "proyecto", "estado", "prioridad", "asignado_a", "fecha_vencimiento")
    list_filter = ("estado", "prioridad", "proyecto__empresa")
    search_fields = ("titulo", "descripcion")
    autocomplete_fields = ("proyecto", "asignado_a", "creado_por")


@admin.register(Idea)
class IdeaAdmin(admin.ModelAdmin):
    list_display = ("titulo", "empresa", "categoria", "estado", "autor", "total_votos")
    list_filter = ("estado", "categoria", "empresa")
    search_fields = ("titulo",)

    @admin.display(description="votos")
    def total_votos(self, obj):
        return obj.votantes.count()


class LienzoColaboradorInline(admin.TabularInline):
    model = LienzoColaborador
    extra = 1
    autocomplete_fields = ("usuario",)


@admin.register(Lienzo)
class LienzoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "empresa", "proyecto", "equipo", "compartido_con_empresa", "version", "fecha_actualizacion")
    list_filter = ("empresa", "compartido_con_empresa")
    search_fields = ("nombre",)
    readonly_fields = ("version", "actualizado_por", "fecha_creacion", "fecha_actualizacion")
    inlines = [LienzoColaboradorInline]


@admin.register(Actividad)
class ActividadAdmin(admin.ModelAdmin):
    list_display = ("descripcion", "tipo", "usuario", "empresa", "fecha")
    list_filter = ("tipo", "empresa")


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ("titulo", "usuario", "tipo", "leida", "fecha_envio")
    list_filter = ("tipo", "leida")


@admin.register(MetricaRendimiento)
class MetricaAdmin(admin.ModelAdmin):
    list_display = ("tipo_metrica", "empresa", "valor", "meta", "unidad", "fecha_inicio_periodo", "fecha_fin_periodo")
    list_filter = ("empresa",)


admin.site.register(VotoIdea)
