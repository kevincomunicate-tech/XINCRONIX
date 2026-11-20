"""
Carga un equipo, proyectos, tareas y actividad de ejemplo para ver el
panel con datos.

    python manage.py cargar_demo tu@correo.com

El usuario debe existir (créalo antes con /cuentas/registro/ o
createsuperuser). Los datos se crean en la empresa del usuario; si no
tiene empresa (por ejemplo, un superusuario), se le crea "Empresa demo"
y queda como administrador. Si ya tiene los proyectos de ejemplo, no los
duplica.
"""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from cuentas.models import Empresa, Rol
from dashboard.models import Actividad, Equipo, MiembroEquipo, Proyecto, Tarea

E = Tarea.Estado
P = Tarea.Prioridad
I = Proyecto.Importancia
T = Proyecto.Tipo

# nombre, importancia, tipo, [(título, estado, prioridad, días para vencer, ¿asignada al usuario?)]
DEMO = [
    ("Rediseño del sitio web", I.ALTA, T.DISENO, [
        ("Definir paleta de colores", E.COMPLETADA, P.MEDIA, -6, True),
        ("Maquetar página de inicio", E.COMPLETADA, P.ALTA, -2, True),
        ("Adaptar a móviles", E.EN_PROGRESO, P.ALTA, 3, True),
        ("Revisar accesibilidad", E.POR_HACER, P.MEDIA, 8, False),
    ]),
    ("App de inventario", I.CRITICA, T.DESARROLLO, [
        ("Modelo de datos", E.COMPLETADA, P.ALTA, -10, False),
        ("Pantalla de productos", E.EN_REVISION, P.URGENTE, -1, True),
        ("Reportes en PDF", E.POR_HACER, P.BAJA, 12, True),
    ]),
    ("Campaña de lanzamiento", I.MEDIA, T.MARKETING, [
        ("Guion del video", E.POR_HACER, P.MEDIA, 5, False),
        ("Publicaciones en redes", E.POR_HACER, P.BAJA, None, True),
    ]),
]

# Cuántas actividades se crean en total (1 por proyecto + 1 por tarea)
TOTAL_PASOS = sum(1 + len(tareas) for *_, tareas in DEMO)


class Command(BaseCommand):
    help = "Crea un equipo, proyectos, tareas y actividad de ejemplo para un usuario."

    def add_arguments(self, parser):
        parser.add_argument("email", help="Correo del usuario dueño de los datos de ejemplo")

    @transaction.atomic
    def handle(self, *args, email, **options):
        Usuario = get_user_model()
        try:
            usuario = Usuario.objects.select_related("empresa").get(email=email.lower())
        except Usuario.DoesNotExist:
            raise CommandError(f"No existe un usuario con el correo {email}.")

        if usuario.empresa is None:
            usuario.empresa = Empresa.objects.create(nombre="Empresa demo", email=usuario.email)
            usuario.rol = Rol.objects.get(codigo=Rol.ADMIN)
            usuario.save(update_fields=["empresa", "rol"])
            self.stdout.write(f"{usuario.email} no tenía empresa: se creó «Empresa demo».")
        empresa = usuario.empresa

        equipo, _ = Equipo.objects.get_or_create(empresa=empresa, nombre="Equipo de producto")
        MiembroEquipo.objects.get_or_create(
            equipo=equipo, usuario=usuario, defaults={"rol_en_equipo": MiembroEquipo.Rol.LIDER}
        )

        ahora = timezone.now()
        hoy = timezone.localdate()
        creados = 0
        paso = 0  # para escalonar las fechas de la actividad

        for nombre, importancia, tipo, tareas in DEMO:
            if Proyecto.objects.filter(empresa=empresa, nombre=nombre).exists():
                continue
            proyecto = Proyecto.objects.create(
                nombre=nombre,
                nivel_importancia=importancia,
                tipo_proyecto=tipo,
                empresa=empresa,
                equipo=equipo,
                creador=usuario,
                fecha_inicio=hoy - timedelta(days=15),
            )
            creados += 1
            paso += 1
            self._fechar(Actividad.registrar_proyecto_creado(usuario, proyecto), ahora, paso)

            for titulo, estado, prioridad, dias, mia in tareas:
                tarea = Tarea.objects.create(
                    proyecto=proyecto,
                    titulo=titulo,
                    estado=estado,
                    prioridad=prioridad,
                    fecha_vencimiento=hoy + timedelta(days=dias) if dias is not None else None,
                    asignada_a=usuario if mia else None,
                    creador=usuario,
                )
                paso += 1
                # Las completadas se registran como "completó"; el resto, como "creó"
                creada = estado != E.COMPLETADA
                self._fechar(Actividad.registrar_tarea(usuario, tarea, creada=creada), ahora, paso)

        if creados:
            self.stdout.write(self.style.SUCCESS(
                f"Listo: {creados} proyecto(s) de ejemplo en «{empresa}» para {usuario.email}."
            ))
        else:
            self.stdout.write(f"«{empresa}» ya tenía los proyectos de ejemplo; no se creó nada.")

    @staticmethod
    def _fechar(actividad, ahora, paso):
        # Fechas hacia atrás (de 3 en 3 horas) para que el historial se vea
        # realista; la última actividad queda de hace unos minutos.
        actividad.fecha = ahora - timedelta(hours=3 * (TOTAL_PASOS - paso), minutes=10)
        actividad.save(update_fields=["fecha"])
