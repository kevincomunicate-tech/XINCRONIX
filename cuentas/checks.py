"""Comprobaciones locales de la aplicación de cuentas."""

from django.core.checks import register


@register()
def revisar_cuentas(app_configs, **kwargs):
    return []
