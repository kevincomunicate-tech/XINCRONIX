"""
Carga proyectos, tareas y actividad de ejemplo para ver el panel con datos.

    python manage.py cargar_demo tu@correo.com

El usuario debe existir (créalo antes con /cuentas/registro/ o createsuperuser).
Si ya tiene los proyectos de ejemplo, no los duplica.
"""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from dashboard.models import Actividad, Prioridad, Proyecto, Tarea

E = Tarea.Estado

# nombre, prioridad, [(título, estado, días para vencer, ¿asignada al usuario?)]
DEMO = [
    ("Rediseño del sitio web", Prioridad.ALTA, [
        ("Definir paleta de colores", E.COMPLETADA, -6, True),
        ("Maquetar página de inicio", E.COMPLETADA, -2, True),
        ("Adaptar a móviles", E.EN_PROGRESO, 3, True),
        ("Revisar accesibilidad", E.POR_HACER, 8, False),
    ]),
    ("App de inventario", Prioridad.MEDIA, [
        ("Modelo de datos", E.COMPLETADA, -10, False),
        ("Pantalla de productos", E.EN_REVISION, -1, True),
        ("Reportes en PDF", E.POR_HACER, 12, True),
    ]),
    ("Campaña de lanzamiento", Prioridad.BAJA, [
        ("Guion del video", E.POR_HACER, 5, False),
        ("Publicaciones en redes", E.POR_HACER, None, True),
    ]),
]

# Cuántas actividades se crean en total (1 por proyecto + 1 por tarea)
TOTAL_PASOS = sum(1 + len(tareas) for _, _, tareas in DEMO)


class Command(BaseCommand):
    help = "Crea proyectos, tareas y actividad de ejemplo para un usuario."

    def add_arguments(self, parser):
        parser.add_argument("email", help="Correo del usuario dueño de los datos de ejemplo")

    @transaction.atomic
    def handle(self, *args, email, **options):
        Usuario = get_user_model()
        try:
            usuario = Usuario.objects.get(email=email.lower())
        except Usuario.DoesNotExist:
            raise CommandError(f"No existe un usuario con el correo {email}.")

        ahora = timezone.now()
        hoy = timezone.localdate()
        creados = 0
        paso = 0  # para escalonar las fechas de la actividad

        for nombre, prioridad, tareas in DEMO:
            if Proyecto.objects.filter(propietario=usuario, nombre=nombre).exists():
                continue
            proyecto = Proyecto.objects.create(
                nombre=nombre, prioridad=prioridad, propietario=usuario, fecha_inicio=hoy - timedelta(days=15)
            )
            creados += 1
            paso += 1
            self._actividad(usuario, Actividad.Accion.PROYECTO_CREADO, proyecto, None, ahora, paso)

            for titulo, estado, dias, mia in tareas:
                tarea = Tarea.objects.create(
                    proyecto=proyecto,
                    titulo=titulo,
                    estado=estado,
                    fecha_vencimiento=hoy + timedelta(days=dias) if dias is not None else None,
                    asignada_a=usuario if mia else None,
                    creada_por=usuario,
                )
                accion = Actividad.Accion.TAREA_COMPLETADA if estado == E.COMPLETADA else Actividad.Accion.TAREA_CREADA
                paso += 1
                self._actividad(usuario, accion, proyecto, tarea, ahora, paso)

        if creados:
            self.stdout.write(self.style.SUCCESS(f"Listo: {creados} proyecto(s) de ejemplo para {usuario.email}."))
        else:
            self.stdout.write(f"{usuario.email} ya tenía los proyectos de ejemplo; no se creó nada.")

    @staticmethod
    def _actividad(usuario, accion, proyecto, tarea, ahora, paso):
        # Fechas hacia atrás (de 3 en 3 horas) para que el historial se vea
        # realista; la última actividad queda de hace unos minutos.
        a = Actividad.registrar(usuario, accion, proyecto, tarea)
        a.fecha = ahora - timedelta(hours=3 * (TOTAL_PASOS - paso), minutes=10)
        a.save(update_fields=["fecha"])
