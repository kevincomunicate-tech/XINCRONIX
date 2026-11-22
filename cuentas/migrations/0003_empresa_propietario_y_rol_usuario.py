"""Empresa con propietario, usuarios que sobreviven a su empresa y rol "usuario".

1. Agrega empresa.id_propietario y le pone como propietario a su primer
   integrante (prefiere a quien tenga rol Administrador).
2. Si se borra una empresa, sus usuarios quedan sin empresa (antes se borraban).
3. El rol "colaborador" pasa a llamarse "usuario" (usuario normal).
"""

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def renombrar_rol(apps, codigo_viejo, codigo_nuevo, nombre, descripcion):
    Rol = apps.get_model("cuentas", "Rol")
    Rol.objects.filter(codigo=codigo_viejo).update(codigo=codigo_nuevo, nombre=nombre, descripcion=descripcion)


def adelante(apps, schema_editor):
    renombrar_rol(apps, "colaborador", "usuario", "Usuario",
                  "Usuario normal: crea su empresa, sus proyectos y trabaja en los proyectos donde lo agregan.")
    # Si no existía ninguno de los dos (base nueva), se crea
    apps.get_model("cuentas", "Rol").objects.get_or_create(codigo="usuario", defaults={"nombre": "Usuario"})

    Empresa = apps.get_model("cuentas", "Empresa")
    Usuario = apps.get_model("cuentas", "Usuario")
    for empresa in Empresa.objects.filter(propietario__isnull=True):
        integrantes = Usuario.objects.filter(empresa=empresa).order_by("date_joined", "pk")
        primero = integrantes.filter(rol__codigo="admin").first() or integrantes.first()
        if primero:
            Empresa.objects.filter(pk=empresa.pk).update(propietario=primero)


def atras(apps, schema_editor):
    renombrar_rol(apps, "usuario", "colaborador", "Colaborador",
                  "Trabaja en los proyectos, equipos y lienzos donde lo agregan.")


class Migration(migrations.Migration):

    dependencies = [
        ("cuentas", "0002_roles_iniciales"),
    ]

    operations = [
        migrations.AddField(
            model_name="empresa",
            name="propietario",
            field=models.ForeignKey(
                blank=True,
                db_column="id_propietario",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="empresas_propias",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="usuario",
            name="empresa",
            field=models.ForeignKey(
                blank=True,
                db_column="id_empresa",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="usuarios",
                to="cuentas.empresa",
            ),
        ),
        migrations.RunPython(adelante, atras),
    ]
