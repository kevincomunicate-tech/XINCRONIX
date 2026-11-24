from django.apps import AppConfig


class AdministracionConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "administracion"
    verbose_name = "Administración de usuarios y roles"

    def ready(self):
        # Registra la revisión de config/monitoreo.json en "manage.py check"
        from . import checks  # noqa: F401
