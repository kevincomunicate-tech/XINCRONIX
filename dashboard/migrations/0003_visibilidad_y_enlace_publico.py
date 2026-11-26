import uuid

from django.db import migrations, models


def llenar_enlaces(apps, schema_editor):
    # Cada proyecto existente recibe su propio enlace (un default único no serviría para filas viejas).
    Proyecto = apps.get_model("dashboard", "Proyecto")
    for proyecto in Proyecto.objects.all():
        proyecto.enlace_publico = uuid.uuid4()
        proyecto.save(update_fields=["enlace_publico"])


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0002_ajustes_del_modelo"),
    ]

    operations = [
        migrations.AddField(
            model_name="proyecto",
            name="visibilidad",
            field=models.CharField(choices=[("privado", "Privado: solo el equipo"), ("publico", "Público: cualquiera con el enlace puede verlo")], default="privado", max_length=10),
        ),
        migrations.AddField(
            model_name="proyecto",
            name="enlace_publico",
            field=models.UUIDField(editable=False, null=True),
        ),
        migrations.RunPython(llenar_enlaces, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="proyecto",
            name="enlace_publico",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
