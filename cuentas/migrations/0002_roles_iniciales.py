"""Migración de datos: crea los 4 roles de Xincronix.

Así existen en cualquier base (SQLite, MariaDB, MySQL) apenas se corre
'migrate', sin tener que insertarlos a mano en phpMyAdmin.
"""

from django.db import migrations

ROLES = [
    ("admin", "Administrador", "Acceso completo a la empresa: usuarios, equipos y todos los proyectos."),
    ("manager", "Manager", "Gestiona equipos y proyectos de la empresa."),
    ("supervisor", "Supervisor", "Ve todos los proyectos y tareas de la empresa para hacer seguimiento."),
    ("colaborador", "Colaborador", "Trabaja en los proyectos, equipos y lienzos donde lo agregan."),
]


def crear_roles(apps, schema_editor):
    Rol = apps.get_model("cuentas", "Rol")
    for codigo, nombre, descripcion in ROLES:
        Rol.objects.update_or_create(codigo=codigo, defaults={"nombre": nombre, "descripcion": descripcion})


def borrar_roles(apps, schema_editor):
    apps.get_model("cuentas", "Rol").objects.filter(codigo__in=[r[0] for r in ROLES]).delete()


class Migration(migrations.Migration):
    dependencies = [("cuentas", "0001_initial")]
    operations = [migrations.RunPython(crear_roles, borrar_roles)]
