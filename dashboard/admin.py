from django.contrib import admin

from .models import Proyecto, ReferenciaGitHub, Tarea


@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "empresa", "estado", "prioridad", "creado_en")
    list_filter = ("empresa", "estado", "prioridad")
    search_fields = ("nombre", "empresa__nombre")
    filter_horizontal = ("miembros",)


@admin.register(ReferenciaGitHub)
class ReferenciaGitHubAdmin(admin.ModelAdmin):
    list_display = ("titulo", "proyecto", "tipo", "creado_en")
    list_filter = ("tipo", "proyecto__empresa")
    search_fields = ("titulo", "url", "proyecto__nombre")


@admin.register(Tarea)
class TareaAdmin(admin.ModelAdmin):
    list_display = ("titulo", "proyecto", "estado", "prioridad", "responsable", "fecha_limite")
    list_filter = ("estado", "prioridad", "proyecto__empresa")
    search_fields = ("titulo", "proyecto__nombre", "responsable__email")
