import uuid

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="Proyecto",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nombre", models.CharField(max_length=150)),
                ("descripcion", models.TextField(blank=True, verbose_name="descripción")),
                ("tecnologia", models.CharField(blank=True, help_text="Ej.: Django, React, PostgreSQL", max_length=180, verbose_name="tecnologías")),
                ("repositorio_url", models.URLField(blank=True, verbose_name="repositorio")),
                ("estado", models.CharField(choices=[("planificacion", "Planificación"), ("en_progreso", "En progreso"), ("en_pausa", "En pausa"), ("completado", "Completado"), ("cancelado", "Cancelado")], default="planificacion", max_length=20)),
                ("finalidad", models.CharField(choices=[("educativo", "Educativo"), ("comercial", "Producto comercial"), ("despliegue", "Despliegue / producción"), ("personal", "Portafolio o personal"), ("otro", "Otro")], default="otro", max_length=15)),
                ("metodologia", models.CharField(choices=[("scrum", "Scrum"), ("gaes", "GAES"), ("pomodoro", "Pomodoro"), ("kanban", "Kanban"), ("propia", "Propia")], default="kanban", max_length=15)),
                ("modalidad", models.CharField(choices=[("individual", "Individual"), ("grupal", "Grupal")], default="individual", max_length=12)),
                ("contexto_educativo", models.CharField(blank=True, max_length=180, verbose_name="curso o contexto educativo")),
                ("fecha_inicio", models.DateField(blank=True, null=True)),
                ("fecha_fin", models.DateField(blank=True, null=True)),
                ("fecha_creacion", models.DateTimeField(auto_now_add=True)),
                ("creado_por", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="proyectos_creados", to=settings.AUTH_USER_MODEL)),
                ("supervisor", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="proyectos_supervisados", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-fecha_creacion"]},
        ),
        migrations.CreateModel(
            name="ProyectoMiembro",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("rol", models.CharField(choices=[("lider", "Líder"), ("editor", "Colaborador"), ("lector", "Solo lectura")], default="editor", max_length=10)),
                ("fecha_ingreso", models.DateTimeField(auto_now_add=True)),
                ("proyecto", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="dashboard.proyecto")),
                ("usuario", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["rol", "usuario__first_name"]},
        ),
        migrations.AddField(name="proyecto", model_name="proyecto", field=models.ManyToManyField(blank=True, related_name="proyectos", through="dashboard.ProyectoMiembro", to=settings.AUTH_USER_MODEL)),
        migrations.CreateModel(
            name="Tarea",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("titulo", models.CharField(max_length=200)), ("descripcion", models.TextField(blank=True)),
                ("estado", models.CharField(choices=[("por_hacer", "Por hacer"), ("en_progreso", "En progreso"), ("revision", "En revisión"), ("hecha", "Hecha")], default="por_hacer", max_length=15)),
                ("prioridad", models.CharField(choices=[("baja", "Baja"), ("media", "Media"), ("alta", "Alta")], default="media", max_length=10)),
                ("fecha_vencimiento", models.DateField(blank=True, null=True)), ("fecha_creacion", models.DateTimeField(auto_now_add=True)), ("fecha_completada", models.DateTimeField(blank=True, null=True)),
                ("asignado_a", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="tareas_asignadas", to=settings.AUTH_USER_MODEL)),
                ("creado_por", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="tareas_creadas", to=settings.AUTH_USER_MODEL)),
                ("proyecto", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="tareas", to="dashboard.proyecto")),
            ], options={"ordering": ["fecha_vencimiento", "-fecha_creacion"]},
        ),
        migrations.CreateModel(
            name="InvitacionProyecto",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("email", models.EmailField(max_length=254)),
                ("rol", models.CharField(choices=[("lider", "Líder"), ("editor", "Colaborador"), ("lector", "Solo lectura")], default="editor", max_length=10)),
                ("token", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)), ("estado", models.CharField(choices=[("pendiente", "Pendiente"), ("aceptada", "Aceptada"), ("cancelada", "Cancelada")], default="pendiente", max_length=12)),
                ("fecha_creacion", models.DateTimeField(auto_now_add=True)), ("vence_en", models.DateTimeField()),
                ("creado_por", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="invitaciones_creadas", to=settings.AUTH_USER_MODEL)),
                ("proyecto", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="invitaciones", to="dashboard.proyecto")),
            ], options={"ordering": ["-fecha_creacion"]},
        ),
        migrations.CreateModel(
            name="Evento",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("titulo", models.CharField(max_length=160)), ("descripcion", models.TextField(blank=True)), ("inicia_en", models.DateTimeField()), ("termina_en", models.DateTimeField(blank=True, null=True)),
                ("creado_por", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="eventos_creados", to=settings.AUTH_USER_MODEL)), ("proyecto", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="eventos", to="dashboard.proyecto")),
            ], options={"ordering": ["inicia_en"]},
        ),
        migrations.CreateModel(
            name="DocumentoProyecto",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("nombre", models.CharField(max_length=160)), ("archivo", models.FileField(upload_to="proyectos/%Y/%m/")), ("fecha_subida", models.DateTimeField(auto_now_add=True)),
                ("proyecto", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="documentos", to="dashboard.proyecto")), ("subido_por", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="documentos_subidos", to=settings.AUTH_USER_MODEL)),
            ], options={"ordering": ["-fecha_subida"]},
        ),
        migrations.CreateModel(
            name="Correccion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("comentario", models.TextField()), ("sugerencia_calificacion", models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)), ("fecha_creacion", models.DateTimeField(auto_now_add=True)),
                ("autor", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="correcciones_creadas", to=settings.AUTH_USER_MODEL)), ("proyecto", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="correcciones", to="dashboard.proyecto")), ("tarea", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="correcciones", to="dashboard.tarea")),
            ], options={"ordering": ["-fecha_creacion"]},
        ),
        migrations.CreateModel(
            name="Lienzo",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("nombre", models.CharField(default="Canvas del proyecto", max_length=100)), ("contenido", models.JSONField(blank=True, default=dict)), ("version", models.PositiveIntegerField(default=1)), ("fecha_actualizacion", models.DateTimeField(auto_now=True)),
                ("actualizado_por", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="lienzos_actualizados", to=settings.AUTH_USER_MODEL)), ("proyecto", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="lienzo", to="dashboard.proyecto")),
            ],
        ),
        migrations.AddConstraint(model_name="proyecto", constraint=models.CheckConstraint(condition=models.Q(fecha_fin__isnull=True) | models.Q(fecha_inicio__isnull=True) | models.Q(fecha_fin__gte=models.F("fecha_inicio")), name="proyecto_fechas_validas")),
        migrations.AddConstraint(model_name="proyectomiembro", constraint=models.UniqueConstraint(fields=("proyecto", "usuario"), name="miembro_proyecto_unico")),
        migrations.AddIndex(model_name="tarea", index=models.Index(fields=["proyecto", "estado"], name="dashboard_t_proyect_058f0b_idx")),
    ]
