from django.core.management.base import BaseCommand, CommandError

from dashboard.auditoria import problemas


class Command(BaseCommand):
    help = "Revisa que todos los registros cumplan los campos obligatorios y las relaciones entre tablas."

    def handle(self, *args, **options):
        encontrados = problemas()
        if not encontrados:
            self.stdout.write(self.style.SUCCESS("Auditoría correcta: ningún problema en los datos."))
            return
        for linea in encontrados:
            self.stdout.write(f"- {linea}")
        raise CommandError(f"Se encontraron {len(encontrados)} problema(s) en los datos.")
