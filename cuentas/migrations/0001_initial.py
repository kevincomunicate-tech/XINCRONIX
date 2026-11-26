# Generated manually for the standalone project model.
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True
    dependencies = [("auth", "0012_alter_user_first_name_max_length")]

    operations = [
        migrations.CreateModel(
            name="Usuario",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                ("last_login", models.DateTimeField(blank=True, null=True, verbose_name="last login")),
                ("is_superuser", models.BooleanField(default=False, help_text="Designates that this user has all permissions without explicitly assigning them.", verbose_name="superuser status")),
                ("first_name", models.CharField(blank=True, max_length=100, verbose_name="nombres")),
                ("last_name", models.CharField(blank=True, max_length=100, verbose_name="apellidos")),
                ("is_staff", models.BooleanField(default=False, help_text="Designates whether the user can log into this admin site.", verbose_name="staff status")),
                ("is_active", models.BooleanField(default=True, help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.", verbose_name="active")),
                ("date_joined", models.DateTimeField(default=django.utils.timezone.now, verbose_name="fecha de registro")),
                ("email", models.EmailField(max_length=254, unique=True, verbose_name="correo electrónico")),
                ("perfil", models.CharField(choices=[("profesional", "Profesional"), ("estudiante", "Estudiante"), ("profesor", "Profesor / supervisor")], default="profesional", max_length=15)),
                ("cargo", models.CharField(blank=True, max_length=80, verbose_name="especialidad o rol")),
                ("telefono", models.CharField(blank=True, max_length=20, verbose_name="teléfono")),
                ("avatar", models.ImageField(blank=True, upload_to="avatares/", verbose_name="foto de perfil")),
                ("groups", models.ManyToManyField(blank=True, help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.", related_name="user_set", related_query_name="user", to="auth.group", verbose_name="groups")),
                ("user_permissions", models.ManyToManyField(blank=True, help_text="Specific permissions for this user.", related_name="user_set", related_query_name="user", to="auth.permission", verbose_name="user permissions")),
            ],
            options={"verbose_name": "usuario", "verbose_name_plural": "usuarios", "ordering": ["first_name", "last_name", "email"]},
        ),
    ]
