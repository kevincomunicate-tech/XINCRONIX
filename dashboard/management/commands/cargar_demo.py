"""
Carga proyectos y tareas de ejemplo para ver el panel con datos.

    python manage.py cargar_demo tu@correo.com

El usuario debe existir (créalo antes con /cuentas/registro/ o createsuperuser).
Los proyectos quedan a su nombre (es el líder). Si ya existen con el mismo
nombre, no se duplican.
"""

from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from cuentas.models import Usuario
from dashboard.models import Proyecto, ProyectoMiembro, Tarea

E = Tarea.Estado
P = Tarea.Prioridad

# nombre, finalidad, metodología, [(título, estado, prioridad, días para vencer, ¿asignada al usuario?)]
DEMO = [
    ("Rediseño del sitio web", Proyecto.Finalidad.PERSONAL, Proyecto.Metodologia.KANBAN, [
        ("Definir paleta de colores", E.HECHA, P.MEDIA, -6, True),
        ("Maquetar página de inicio", E.HECHA, P.ALTA, -2, True),
        ("Adaptar a móviles", E.EN_PROGRESO, P.ALTA, 3, True),
        ("Revisar accesibilidad", E.POR_HACER, P.MEDIA, 8, False),
    ]),
    ("App de inventario", Proyecto.Finalidad.EDUCATIVO, Proyecto.Metodologia.SCRUM, [
        ("Modelo de datos", E.HECHA, P.ALTA, -10, False),
        ("Pantalla de productos", E.REVISION, P.ALTA, -1, True),
        ("Reportes en PDF", E.POR_HACER, P.BAJA, 12, True),
    ]),
    ("Campaña de lanzamiento", Proyecto.Finalidad.COMERCIAL, Proyecto.Metodologia.KANBAN, [
        ("Guion del video", E.POR_HACER, P.MEDIA, 5, False),
        ("Publicaciones en redes", E.POR_HACER, P.BAJA, None, True),
    ]),
]


class Command(BaseCommand):
    help = "Crea proyectos y tareas de ejemplo a nombre de un usuario."

    def add_arguments(self, parser):
        parser.add_argument("email", help="Correo del usuario que será líder de los proyectos de ejemplo")

    @transaction.atomic
    def handle(self, *args, email, **options):
        try:
            usuario = Usuario.objects.get(email=email.strip().lower())
        except Usuario.DoesNotExist:
            raise CommandError(f"No existe un usuario con el correo {email}.")

        hoy = timezone.localdate()
        creados = 0
        for nombre, finalidad, metodologia, tareas in DEMO:
            if Proyecto.objects.filter(creado_por=usuario, nombre=nombre).exists():
                continue
            proyecto = Proyecto.objects.create(
                nombre=nombre,
                finalidad=finalidad,
                metodologia=metodologia,
                modalidad=Proyecto.Modalidad.INDIVIDUAL,
                creado_por=usuario,
                fecha_inicio=hoy - timedelta(days=15),descripcion="Descripción de prueba")
            ProyectoMiembro.objects.create(proyecto=proyecto, usuario=usuario, rol=ProyectoMiembro.Rol.LIDER)
            for titulo, estado, prioridad, dias, mia in tareas:
                Tarea.objects.create(
                    proyecto=proyecto,
                    titulo=titulo,
                    estado=estado,
                    prioridad=prioridad,
                    fecha_vencimiento=hoy + timedelta(days=dias) if dias is not None else None,
                    asignado_a=usuario if mia else None,
                    creado_por=usuario,
                )
            creados += 1

        if creados:
            self.stdout.write(self.style.SUCCESS(f"Listo: {creados} proyecto(s) de ejemplo para {usuario.email}."))
        else:
            self.stdout.write("Ya existían los proyectos de ejemplo; no se duplicaron.")
