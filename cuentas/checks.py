"""
Revisión de la política al correr "python manage.py check" (y runserver).

Si config/politica_accesos.json tiene un error, Django lo avisa antes de
arrancar, en lugar de fallar cuando alguien inicia sesión.
"""

from django.core.checks import Error, register
from django.urls import NoReverseMatch, reverse

from .politica import PoliticaInvalida, leer_politica


@register()
def revisar_politica_accesos(app_configs, **kwargs):
    from django.conf import settings

    try:
        politica = leer_politica(settings.POLITICA_ACCESOS)
    except PoliticaInvalida as error:
        return [Error(mensaje, id="cuentas.E001") for mensaje in error.errores]

    nombres_url = [perfil["inicio"] for perfil in politica.perfiles.values()]
    nombres_url += [item["url"] for perfil in politica.perfiles.values() for item in perfil.get("menu", [])]
    return [
        Error(f"La URL '{nombre}' de la política no existe en urls.py.", id="cuentas.E002")
        for nombre in sorted(set(nombres_url))
        if not _existe_url(nombre)
    ]


def _existe_url(nombre):
    try:
        reverse(nombre)
    except NoReverseMatch:
        return False
    return True
