from django.core.management.base import BaseCommand, CommandError

from administracion import importacion


class Command(BaseCommand):
    help = "Carga usuarios o proyectos desde un CSV. Valida todo primero; si algo falla, no guarda nada."

    def add_arguments(self, parser):
        parser.add_argument("tipo", choices=["usuarios", "proyectos"])
        parser.add_argument("archivo", help="Ruta del archivo CSV (UTF-8)")
        parser.add_argument("--simular", action="store_true", help="Solo valida, no guarda")

    def handle(self, *args, tipo, archivo, simular, **options):
        try:
            with open(archivo, "rb") as f:
                contenido = f.read()
            if simular:
                resultado = importacion.validar(tipo, contenido)
            else:
                resultado = importacion.importar(tipo, contenido)
        except (OSError, importacion.ErrorImportacion) as error:
            raise CommandError(str(error))
        if resultado.errores:
            for linea, mensaje in resultado.errores:
                self.stdout.write(f"Línea {linea}: {mensaje}")
            raise CommandError(f"{len(resultado.errores)} error(es). No se guardó nada.")
        if simular:
            self.stdout.write(self.style.SUCCESS(f"Simulación correcta: {resultado.total} fila(s) válidas. No se guardó nada."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Listo: se crearon {resultado.creados} registro(s)."))
