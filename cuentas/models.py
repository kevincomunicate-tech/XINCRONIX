"""
Empresas, roles y usuarios.

Las tablas y columnas siguen el esquema de xincronix_bd.sql
(empresa, roles, usuarios). Todo en Xincronix pertenece a una empresa.
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class Empresa(models.Model):
    id = models.BigAutoField(primary_key=True, db_column="id_empresa")
    nombre = models.CharField("nombre", max_length=200)
    nit = models.CharField("NIT", max_length=30, unique=True, null=True, blank=True)
    email = models.EmailField("correo", max_length=150)
    telefono = models.CharField("teléfono", max_length=20, blank=True)
    direccion = models.CharField("dirección", max_length=300, blank=True)
    sector = models.CharField("sector", max_length=20, blank=True)
    num_empleados = models.CharField("número de empleados", max_length=10, blank=True)
    fecha_creacion = models.DateTimeField("creada", auto_now_add=True)
    fecha_actualizacion = models.DateTimeField("actualizada", auto_now=True)

    class Meta:
        db_table = "empresa"
        verbose_name = "empresa"
        verbose_name_plural = "empresas"

    def __str__(self):
        return self.nombre


class Rol(models.Model):
    """Los 4 roles se crean en la migración 0002_roles_iniciales."""

    ADMIN = "admin"
    MANAGER = "manager"
    SUPERVISOR = "supervisor"
    COLABORADOR = "colaborador"

    # Roles que ven todos los proyectos de su empresa
    VEN_TODO = (ADMIN, MANAGER, SUPERVISOR)

    id = models.AutoField(primary_key=True, db_column="id_roles")
    codigo = models.CharField("código", max_length=30, unique=True)
    nombre = models.CharField("nombre", max_length=80, unique=True)
    descripcion = models.TextField("descripción", blank=True)

    class Meta:
        db_table = "roles"
        verbose_name = "rol"
        verbose_name_plural = "roles"

    def __str__(self):
        return self.nombre


class UsuarioManager(BaseUserManager):
    """Crea usuarios usando el correo como identificador (sin username)."""

    use_in_migrations = True

    def _crear(self, email, password, **extra):
        if not email:
            raise ValueError("El correo es obligatorio")
        email = self.normalize_email(email).lower()
        if isinstance(extra.get("rol"), str):  # permite pasar rol="admin"
            extra["rol"] = Rol.objects.get(codigo=extra["rol"])
        usuario = self.model(email=email, **extra)
        usuario.set_password(password)  # guarda la contraseña cifrada
        usuario.save(using=self._db)
        return usuario

    def create_user(self, email, password=None, **extra):
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        extra.setdefault("rol", Rol.COLABORADOR)
        return self._crear(email, password, **extra)

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        extra.setdefault("rol", Rol.ADMIN)
        return self._crear(email, password, **extra)


class Usuario(AbstractBaseUser, PermissionsMixin):
    """Usuario de Xincronix: inicia sesión con su correo."""

    id = models.BigAutoField(primary_key=True, db_column="id_usuario")
    nombres = models.CharField("nombres", max_length=100, blank=True)
    apellidos = models.CharField("apellidos", max_length=100, blank=True)
    email = models.EmailField("correo electrónico", max_length=150, unique=True)
    # Django espera el nombre is_active; en la tabla la columna se llama "estado"
    is_active = models.BooleanField("activo", default=True, db_column="estado")
    is_staff = models.BooleanField("acceso al admin", default=False)
    fecha_creacion = models.DateTimeField("fecha de registro", default=timezone.now)
    cargo = models.CharField("cargo", max_length=80, blank=True)
    telefono = models.CharField("teléfono", max_length=20, blank=True)
    avatar = models.FileField("avatar", upload_to="avatares/", blank=True)
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_column="id_empresa",
        related_name="usuarios",
        verbose_name="empresa",
    )
    rol = models.ForeignKey(
        Rol,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_column="id_roles",
        related_name="usuarios",
        verbose_name="rol",
    )

    USERNAME_FIELD = "email"   # campo con el que se inicia sesión
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = []       # createsuperuser solo pedirá correo y contraseña

    objects = UsuarioManager()

    class Meta:
        db_table = "usuarios"
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"

    def __str__(self):
        return self.get_full_name() or self.email

    def get_full_name(self):
        return f"{self.nombres} {self.apellidos}".strip()

    def get_short_name(self):
        return self.nombres

    @property
    def iniciales(self):
        """Dos letras para el avatar redondo (ej. 'Yohan Cuellar' -> 'YC')."""
        partes = [p for p in (self.nombres, self.apellidos) if p]
        if not partes:
            return self.email[:2].upper()
        return "".join(p[0] for p in partes)[:2].upper()

    @property
    def ve_toda_la_empresa(self):
        """Admin, manager y supervisor ven todos los proyectos de su empresa."""
        return self.rol is not None and self.rol.codigo in Rol.VEN_TODO
