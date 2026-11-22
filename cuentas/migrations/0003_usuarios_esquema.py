"""
Adapta la tabla de usuarios al esquema de xincronix_bd.sql sin perder
los usuarios que ya existan:

- first_name/last_name -> nombres/apellidos, date_joined -> fecha_creacion
- columnas id_usuario y estado; tabla "usuarios"
- cargo, teléfono, avatar y empresa
- el rol pasa de texto a la tabla roles ("director" queda como "manager")
"""

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models

EQUIVALENCIAS = {"admin": "admin", "director": "manager", "colaborador": "colaborador"}


def pasar_rol_a_tabla(apps, schema_editor):
    Usuario = apps.get_model("cuentas", "Usuario")
    Rol = apps.get_model("cuentas", "Rol")
    roles = {r.codigo: r for r in Rol.objects.all()}
    for usuario in Usuario.objects.all():
        codigo = EQUIVALENCIAS.get(usuario.rol_anterior, "colaborador")
        usuario.rol = roles[codigo]
        usuario.save(update_fields=["rol"])


def devolver_rol_a_texto(apps, schema_editor):
    Usuario = apps.get_model("cuentas", "Usuario")
    inversas = {v: k for k, v in EQUIVALENCIAS.items()}
    for usuario in Usuario.objects.select_related("rol"):
        codigo = usuario.rol.codigo if usuario.rol else "colaborador"
        usuario.rol_anterior = inversas.get(codigo, "colaborador")
        usuario.save(update_fields=["rol_anterior"])


class Migration(migrations.Migration):

    dependencies = [
        ("cuentas", "0002_roles_iniciales"),
    ]

    operations = [
        # --- nombres de campos ---
        migrations.RenameField("usuario", "first_name", "nombres"),
        migrations.AlterField(
            "usuario", "nombres", models.CharField(blank=True, max_length=100, verbose_name="nombres")
        ),
        migrations.RenameField("usuario", "last_name", "apellidos"),
        migrations.AlterField(
            "usuario", "apellidos", models.CharField(blank=True, max_length=100, verbose_name="apellidos")
        ),
        migrations.RenameField("usuario", "date_joined", "fecha_creacion"),
        migrations.AlterField(
            "usuario",
            "fecha_creacion",
            models.DateTimeField(default=django.utils.timezone.now, verbose_name="fecha de registro"),
        ),
        # --- columnas con el nombre del esquema ---
        migrations.AlterField(
            "usuario", "id", models.BigAutoField(db_column="id_usuario", primary_key=True, serialize=False)
        ),
        migrations.AlterField(
            "usuario", "is_active", models.BooleanField(db_column="estado", default=True, verbose_name="activo")
        ),
        migrations.AlterField(
            "usuario", "is_staff", models.BooleanField(default=False, verbose_name="acceso al admin")
        ),
        migrations.AlterField(
            "usuario",
            "email",
            models.EmailField(max_length=150, unique=True, verbose_name="correo electrónico"),
        ),
        # --- campos nuevos ---
        migrations.AddField("usuario", "cargo", models.CharField(blank=True, max_length=80, verbose_name="cargo")),
        migrations.AddField(
            "usuario", "telefono", models.CharField(blank=True, max_length=20, verbose_name="teléfono")
        ),
        migrations.AddField(
            "usuario", "avatar", models.FileField(blank=True, upload_to="avatares/", verbose_name="avatar")
        ),
        migrations.AddField(
            "usuario",
            "empresa",
            models.ForeignKey(
                blank=True,
                null=True,
                db_column="id_empresa",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="usuarios",
                to="cuentas.empresa",
                verbose_name="empresa",
            ),
        ),
        # --- rol: de texto a llave foránea hacia roles ---
        migrations.RenameField("usuario", "rol", "rol_anterior"),
        migrations.AddField(
            "usuario",
            "rol",
            models.ForeignKey(
                blank=True,
                null=True,
                db_column="id_roles",
                on_delete=django.db.models.deletion.PROTECT,
                related_name="usuarios",
                to="cuentas.rol",
                verbose_name="rol",
            ),
        ),
        migrations.RunPython(pasar_rol_a_tabla, devolver_rol_a_texto),
        migrations.RemoveField("usuario", "rol_anterior"),
        # --- nombre de la tabla ---
        migrations.AlterModelTable("usuario", "usuarios"),
    ]
