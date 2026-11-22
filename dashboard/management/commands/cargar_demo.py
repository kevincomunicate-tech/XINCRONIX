"""
Carga un equipo, proyectos, tareas y actividad de ejemplo para ver el
panel con datos.

    python manage.py cargar_demo tu@correo.com

El usuario debe existir (créalo antes con /cuentas/registro/ o
createsuperuser). Los datos se crean en la empresa del usuario; si no
tiene empresa, se le crea "Empresa demo" y queda como su PROPIETARIO
(su rol no cambia: el rol Administrador solo lo da el superadministrador,
ver config/politica_accesos.json). Si ya tiene los proyectos de ejemplo,
no los duplica.

Versión original: Felipe (Fase 2). Adaptada a los modelos actuales.
"""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from cuentas.models import Empresa, Equipo, MiembroEquipo
from dashboard.models import Actividad, Proyecto, Tarea

E = Tarea.Estado
P = Tarea.Prioridad
I = Proyecto.Importancia
T = Proyecto.Tipo

# nombre, importancia, tipo, [(título, estado, prioridad, días para vencer, ¿asignada al usuario?)]
DEMO = [
    ("Rediseño del sitio web", I.ALTA, T.FRONTEND, [
        ("Definir paleta de colores", E.COMPLETADA, P.MEDIA, -6, True),
        ("Maquetar página de inicio", E.COMPLETADA, P.ALTA, -2, True),
        ("Adaptar a móviles", E.EN_PROGRESO, P.ALTA, 3, True),
        ("Revisar accesibilidad", E.POR_HACER, P.MEDIA, 8, False),
    ]),
    ("App de inventario", I.CRITICA, T.FULL_STACK, [
        ("Modelo de datos", E.COMPLETADA, P.ALTA, -10, False),
        ("Pantalla de productos", E.EN_REVISION, P.ALTA, -1, True),
        ("Reportes en PDF", E.POR_HACER, P.BAJA, 12, True),
    ]),
    ("Campaña de lanzamiento", I.MEDIA, T.OTRO, [
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
            usuario = Usuario.objects.select_related("empresa").get(email=email.strip().lower())
        except Usuario.DoesNotExist:
            raise CommandError(f"No existe un usuario con el correo {email}.")

        if usuario.empresa is None:
            usuario.empresa = Empresa.objects.create(nombre="Empresa demo", email=usuario.email, propietario=usuario)
            usuario.save(update_fields=["empresa"])
            self.stdout.write(f"{usuario.email} no tenía empresa: se creó «Empresa demo» y quedó como propietario.")
        empresa = usuario.empresa

        equipo, _ = Equipo.objects.get_or_create(empresa=empresa, nombre="Equipo de producto")
        MiembroEquipo.objects.get_or_create(
            equipo=equipo, usuario=usuario, defaults={"rol_en_equipo": MiembroEquipo.RolEquipo.LIDER}
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
                creado_por=usuario,
                fecha_inicio=hoy - timedelta(days=15),
            )
            creados += 1
            paso += 1
            self._registrar(Actividad.Tipo.PROYECTO, f"{usuario} creó el proyecto «{proyecto}»",
                            usuario, proyecto, ahora, paso)

            for titulo, estado, prioridad, dias, mia in tareas:
                tarea = Tarea.objects.create(
                    proyecto=proyecto,
                    titulo=titulo,
                    estado=estado,
                    prioridad=prioridad,
                    fecha_vencimiento=hoy + timedelta(days=dias) if dias is not None else None,
                    asignado_a=usuario if mia else None,
                    creado_por=usuario,
                )
                paso += 1
                # Las completadas se registran como "completó"; el resto, como "creó"
                verbo = "completó" if estado == E.COMPLETADA else "creó"
                self._registrar(Actividad.Tipo.TAREA, f"{usuario} {verbo} la tarea «{tarea}»",
                                usuario, proyecto, ahora, paso)

        if creados:
            self.stdout.write(self.style.SUCCESS(
                f"Listo: {creados} proyecto(s) de ejemplo en «{empresa}» para {usuario.email}."
            ))
        else:
            self.stdout.write(f"«{empresa}» ya tenía los proyectos de ejemplo; no se creó nada.")

    @staticmethod
    def _registrar(tipo, descripcion, usuario, proyecto, ahora, paso):
        actividad = Actividad.objects.create(
            tipo=tipo, descripcion=descripcion[:255], empresa=proyecto.empresa, usuario=usuario, proyecto=proyecto,
        )
        # Fechas hacia atrás (de 3 en 3 horas) para que el historial se vea
        # realista; la última actividad queda de hace unos minutos.
        Actividad.objects.filter(pk=actividad.pk).update(
            fecha=ahora - timedelta(hours=3 * (TOTAL_PASOS - paso), minutes=10)
        )
