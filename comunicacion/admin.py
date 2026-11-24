from django.contrib import admin

from .models import ConversacionIA, EventoCalendario, Mensaje, MensajeIA, Reunion, TicketSoporte


@admin.register(Mensaje)
class MensajeAdmin(admin.ModelAdmin):
    list_display = ("__str__", "remitente", "destinatario", "equipo", "leido", "fecha_envio")
    list_filter = ("leido",)


@admin.register(Reunion)
class ReunionAdmin(admin.ModelAdmin):
    list_display = ("nombre", "fecha", "estado", "equipo", "organizador")
    list_filter = ("estado",)


@admin.register(EventoCalendario)
class EventoAdmin(admin.ModelAdmin):
    list_display = ("__str__", "usuario", "fecha_evento")


class MensajeIAInline(admin.TabularInline):
    model = MensajeIA
    extra = 0


@admin.register(ConversacionIA)
class ConversacionAdmin(admin.ModelAdmin):
    list_display = ("titulo", "usuario", "activa", "fecha_ultima")
    inlines = [MensajeIAInline]


@admin.register(TicketSoporte)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("asunto", "empresa", "creado_por", "prioridad", "estado", "fecha_creacion")
    list_filter = ("estado", "prioridad")
