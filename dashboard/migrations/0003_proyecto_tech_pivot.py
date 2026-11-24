# Generated manually for the tech/software project pivot

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0002_proyecto_rol_editor"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="proyecto",
            name="proposito",
            field=models.CharField(
                blank=True,
                choices=[
                    ("escolar", "Proyecto escolar / académico"),
                    ("personal", "Proyecto personal / aprendizaje"),
                    ("comercial", "Para vender / producto comercial"),
                    ("despliegue", "Para desplegar en producción"),
                    ("open_source", "Open source / comunidad"),
                    ("interno", "Interno de equipo / startup"),
                    ("otro", "Otro"),
                ],
                default="",
                help_text="Respuesta del cuestionario: ¿para qué es este proyecto?",
                max_length=20,
                verbose_name="propósito",
            ),
        ),
        migrations.AddField(
            model_name="proyecto",
            name="metodologia",
            field=models.CharField(
                blank=True,
                choices=[
                    ("scrum", "Scrum"),
                    ("kanban", "Kanban"),
                    ("gaes", "GAES (Grupos de Aprendizaje)"),
                    ("waterfall", "Cascada / Waterfall"),
                    ("pomodoro", "Pomodoro + sprints cortos"),
                    ("hybrid", "Híbrida"),
                    ("ninguna", "Sin metodología formal"),
                ],
                default="",
                help_text="Metodología de trabajo elegida en el cuestionario.",
                max_length=15,
                verbose_name="metodología",
            ),
        ),
        migrations.AddField(
            model_name="proyecto",
            name="es_educativo",
            field=models.BooleanField(
                default=False,
                help_text="Si es escolar/universitario: el supervisor (profesor) puede ver y comentar todo.",
                verbose_name="proyecto educativo",
            ),
        ),
        migrations.AddField(
            model_name="proyecto",
            name="es_grupal",
            field=models.BooleanField(default=False, verbose_name="es grupal"),
        ),
        migrations.AddField(
            model_name="proyecto",
            name="supervisor",
            field=models.ForeignKey(
                blank=True,
                db_column="id_supervisor",
                help_text="En proyectos educativos: el profesor o mentor que supervisa.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="proyectos_supervisados",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="proyecto",
            name="empresa",
            field=models.ForeignKey(
                blank=True,
                db_column="id_empresa",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="proyectos",
                to="cuentas.empresa",
            ),
        ),
        migrations.CreateModel(
            name="Hito",
            fields=[
                ("id", models.BigAutoField(db_column="id_hito", primary_key=True, serialize=False)),
                ("titulo", models.CharField(max_length=150)),
                ("descripcion", models.TextField(blank=True)),
                ("fecha_objetivo", models.DateField(blank=True, null=True)),
                (
                    "estado",
                    models.CharField(
                        choices=[
                            ("pendiente", "Pendiente"),
                            ("en_progreso", "En progreso"),
                            ("completado", "Completado"),
                            ("cancelado", "Cancelado"),
                        ],
                        default="pendiente",
                        max_length=15,
                    ),
                ),
                ("orden", models.PositiveSmallIntegerField(default=0)),
                ("fecha_creacion", models.DateTimeField(auto_now_add=True)),
                (
                    "proyecto",
                    models.ForeignKey(
                        db_column="id_proyecto",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="hitos",
                        to="dashboard.proyecto",
                    ),
                ),
            ],
            options={
                "verbose_name": "hito",
                "verbose_name_plural": "hitos",
                "db_table": "hito",
                "ordering": ["orden", "fecha_objetivo", "id"],
            },
        ),
        migrations.CreateModel(
            name="InvitacionProyecto",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("email", models.EmailField(max_length=254)),
                ("token", models.CharField(max_length=64, unique=True)),
                (
                    "rol",
                    models.CharField(
                        choices=[
                            ("responsable", "Responsable"),
                            ("editor", "Editor"),
                            ("observador", "Observador (solo lectura)"),
                        ],
                        default="editor",
                        max_length=15,
                    ),
                ),
                ("aceptada", models.BooleanField(default=False)),
                ("fecha_creacion", models.DateTimeField(auto_now_add=True)),
                ("fecha_expiracion", models.DateTimeField(blank=True, null=True)),
                (
                    "creada_por",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "proyecto",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="invitaciones",
                        to="dashboard.proyecto",
                    ),
                ),
            ],
            options={
                "verbose_name": "invitación a proyecto",
                "verbose_name_plural": "invitaciones a proyectos",
                "db_table": "invitacion_proyecto",
                "unique_together": {("proyecto", "email")},
            },
        ),
    ]
