from django.apps import AppConfig


class CuentasConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "cuentas"

    def ready(self):
        # Registra la revisión de config/politica_accesos.json en "manage.py check"
        from . import checks  # noqa: F401
