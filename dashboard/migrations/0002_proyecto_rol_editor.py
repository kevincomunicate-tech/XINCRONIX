"""El rol "colaborador" dentro de un proyecto pasa a llamarse "editor"."""

from django.db import migrations, models


def adelante(apps, schema_editor):
    apps.get_model("dashboard", "ProyectoMiembro").objects.filter(rol="colaborador").update(rol="editor")


def atras(apps, schema_editor):
    apps.get_model("dashboard", "ProyectoMiembro").objects.filter(rol="editor").update(rol="colaborador")


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="proyectomiembro",
            name="rol",
            field=models.CharField(
                choices=[
                    ("responsable", "Responsable"),
                    ("editor", "Editor"),
                    ("observador", "Observador (solo lectura)"),
                ],
                default="editor",
                max_length=15,
            ),
        ),
        migrations.RunPython(adelante, atras),
    ]
