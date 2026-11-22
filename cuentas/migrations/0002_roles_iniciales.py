"""Crea las tablas empresa y roles, y los 4 roles de Xincronix."""

from django.db import migrations, models

ROLES = [
    (1, "admin", "Administrador", "Acceso completo a la empresa: usuarios, equipos y todos los proyectos."),
    (2, "manager", "Manager", "Gestiona equipos y proyectos de la empresa."),
    (3, "supervisor", "Supervisor", "Ve todos los proyectos y tareas de la empresa para hacer seguimiento."),
    (4, "colaborador", "Colaborador", "Trabaja en los proyectos, equipos y lienzos donde lo agregan."),
]


def crear_roles(apps, schema_editor):
    Rol = apps.get_model("cuentas", "Rol")
    for pk, codigo, nombre, descripcion in ROLES:
        Rol.objects.update_or_create(pk=pk, defaults={"codigo": codigo, "nombre": nombre, "descripcion": descripcion})


class Migration(migrations.Migration):

    dependencies = [
        ("cuentas", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Empresa",
            fields=[
                ("id", models.BigAutoField(db_column="id_empresa", primary_key=True, serialize=False)),
                ("nombre", models.CharField(max_length=200, verbose_name="nombre")),
                ("nit", models.CharField(blank=True, max_length=30, null=True, unique=True, verbose_name="NIT")),
                ("email", models.EmailField(max_length=150, verbose_name="correo")),
                ("telefono", models.CharField(blank=True, max_length=20, verbose_name="teléfono")),
                ("direccion", models.CharField(blank=True, max_length=300, verbose_name="dirección")),
                ("sector", models.CharField(blank=True, max_length=20, verbose_name="sector")),
                ("num_empleados", models.CharField(blank=True, max_length=10, verbose_name="número de empleados")),
                ("fecha_creacion", models.DateTimeField(auto_now_add=True, verbose_name="creada")),
                ("fecha_actualizacion", models.DateTimeField(auto_now=True, verbose_name="actualizada")),
            ],
            options={"verbose_name": "empresa", "verbose_name_plural": "empresas", "db_table": "empresa"},
        ),
        migrations.CreateModel(
            name="Rol",
            fields=[
                ("id", models.AutoField(db_column="id_roles", primary_key=True, serialize=False)),
                ("codigo", models.CharField(max_length=30, unique=True, verbose_name="código")),
                ("nombre", models.CharField(max_length=80, unique=True, verbose_name="nombre")),
                ("descripcion", models.TextField(blank=True, verbose_name="descripción")),
            ],
            options={"verbose_name": "rol", "verbose_name_plural": "roles", "db_table": "roles"},
        ),
        migrations.RunPython(crear_roles, migrations.RunPython.noop),
    ]
