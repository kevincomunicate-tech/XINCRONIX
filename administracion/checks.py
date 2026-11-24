"""
Revisión de config/monitoreo.json al correr "python manage.py check" (y runserver).

Si el JSON tiene un error (un modelo que no existe, un filtro mal escrito...),
Django lo avisa antes de arrancar, en lugar de fallar al abrir el monitoreo.
"""

from django.core.checks import Error, register

from .monitoreo import MonitoreoInvalido, leer_monitoreo


@register()
def revisar_monitoreo(app_configs, **kwargs):
    from django.conf import settings

    try:
        leer_monitoreo(settings.MONITOREO)
    except MonitoreoInvalido as error:
        return [Error(mensaje, id="administracion.E001") for mensaje in error.errores]
    return []
