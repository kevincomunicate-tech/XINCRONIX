"""Datos del espacio de trabajo disponibles en todas las plantillas."""

from django.utils.functional import SimpleLazyObject

from .models import InvitacionProyecto


def invitaciones(request):
    """Invitaciones pendientes de quien está conectado (campana de notificaciones).

    Es perezoso: la consulta solo se hace si la plantilla lo usa.
    """
    usuario = getattr(request, "user", None)
    if not usuario or not usuario.is_authenticated:
        return {}
    return {"invitaciones_pendientes": SimpleLazyObject(lambda: list(InvitacionProyecto.pendientes_para(usuario)[:10]))}
