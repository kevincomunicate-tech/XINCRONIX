"""
Organización: empresas, roles, usuarios y equipos.

Las tablas y columnas conservan los nombres de la base original
(xincronix_bd) gracias a db_table y db_column.
"""

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


# ---------------------------------------------------------------------------
# Empresa
# ---------------------------------------------------------------------------

class Empresa(models.Model):
    """Cada empresa es un espacio de trabajo separado de los demás."""

    class Sector(models.TextChoices):
        TECNOLOGIA = "tecnologia", "Tecnología"
        CONSULTORIA = "consultoria", "Consultoría"
        MANUFACTURA = "manufactura", "Manufactura"
        SALUD = "salud", "Salud"
        LOGISTICA = "logistica", "Logística"
        RETAIL = "retail", "Retail"
        EDUCACION = "educacion", "Educación"
        FINANZAS = "finanzas", "Finanzas"
        OTRO = "otro", "Otro"

    class RangoEmpleados(models.TextChoices):
        R1_10 = "1-10", "1 – 10"
        R11_50 = "11-50", "11 – 50"
        R51_100 = "51-100", "51 – 100"
        R101_500 = "101-500", "101 – 500"
        R500 = "500+", "Más de 500"

    id = models.BigAutoField(primary_key=True, db_column="id_empresa")
    nombre = models.CharField(max_length=200)
    # null=True + unique: varias empresas pueden no tener NIT todavía,
    # pero si lo tienen no se puede repetir (NULL no choca con NULL).
    nit = models.CharField("NIT", max_length=30, unique=True, null=True, blank=True)
    email = models.EmailField("correo de contacto", max_length=150, blank=True)
    telefono = models.CharField("teléfono", max_length=20, blank=True)
    direccion = models.CharField("dirección", max_length=300, blank=True)
    sector = models.CharField(max_length=20, choices=Sector.choices, blank=True)
    num_empleados = models.CharField("número de empleados", max_length=10, choices=RangoEmpleados.choices, blank=True)
    # Quien la creó (o a quien el superadministrador se la asignó).
    # Sus permisos sobre la empresa salen de config/politica_accesos.json.
    propietario = models.ForeignKey(
        "Usuario", on_delete=models.SET_NULL, related_name="empresas_propias",
        db_column="id_propietario", null=True, blank=True,
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "empresa"
        verbose_name = "empresa"
        verbose_name_plural = "empresas"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

    def relaciones_con(self, usuario):
        """Cómo se relaciona alguien con esta empresa: {"propietario", "integrante"}.

        Qué puede hacer cada relación lo dice el JSON (empresas.por_relacion).
        """
        relaciones = {
            "propietario": self.propietario_id is not None and self.propietario_id == usuario.pk,
            "integrante": usuario.empresa_id == self.pk,
        }
        return {nombre for nombre, cumple in relaciones.items() if cumple}


# ---------------------------------------------------------------------------
# Rol (catálogo)
# ---------------------------------------------------------------------------

class Rol(models.Model):
    """Rol dentro de la empresa. Los roles se crean en las migraciones 0002/0004
    y su nombre y descripción se sincronizan desde config/politica_accesos.json.

    El "SUPERADMIN" de la base original no es un rol: es is_superuser
    (acceso global a /admin), así que no está en esta tabla.
    """

    ADMIN = "admin"
    MANAGER = "manager"
    SUPERVISOR = "supervisor"
    USUARIO = "usuario"  # usuario normal (antes "colaborador")

    id = models.AutoField(primary_key=True, db_column="id_roles")
    codigo = models.SlugField("código", max_length=30, unique=True)
    nombre = models.CharField(max_length=80, unique=True)
    descripcion = models.TextField("descripción", blank=True)

    class Meta:
        db_table = "roles"
        verbose_name = "rol"
        verbose_name_plural = "roles"
        ordering = ["id"]

    def __str__(self):
        return self.nombre


# ---------------------------------------------------------------------------
# Usuario
# ---------------------------------------------------------------------------

class UsuarioManager(BaseUserManager):
    """Crea usuarios usando el correo como identificador (sin username)."""

    use_in_migrations = True

    def _crear(self, email, password, **extra):
        if not email:
            raise ValueError("El correo es obligatorio")
        email = self.normalize_email(email).lower()
        if "rol" not in extra and "rol_id" not in extra:
            extra["rol"] = Rol.objects.filter(codigo=Rol.USUARIO).first()
        usuario = self.model(email=email, **extra)
        usuario.set_password(password)  # guarda la contraseña cifrada
        usuario.save(using=self._db)
        return usuario

    def create_user(self, email, password=None, **extra):
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        return self._crear(email, password, **extra)

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        extra.setdefault("rol", Rol.objects.filter(codigo=Rol.ADMIN).first())
        return self._crear(email, password, **extra)


class Usuario(AbstractUser):
    """Usuario de Xincronix: inicia sesión con su correo.

    Se redefinen algunos campos de AbstractUser solo para que la columna
    se llame como en la base original (nombres, apellidos, estado...).
    """

    id = models.BigAutoField(primary_key=True, db_column="id_usuario")
    username = None  # sin "nombre de usuario": se entra con el correo

    first_name = models.CharField("nombres", max_length=100, blank=True, db_column="nombres")
    last_name = models.CharField("apellidos", max_length=100, blank=True, db_column="apellidos")
    email = models.EmailField("correo electrónico", max_length=150, unique=True)
    is_active = models.BooleanField("activo", default=True, db_column="estado")
    date_joined = models.DateTimeField("fecha de registro", default=timezone.now, db_column="fecha_creacion")

    cargo = models.CharField(max_length=80, blank=True, help_text="Cargo laboral, ej. Desarrollador. No define permisos.")
    telefono = models.CharField("teléfono", max_length=20, blank=True)
    avatar = models.ImageField("foto de perfil", upload_to="avatares/", blank=True)

    empresa = models.ForeignKey(
        # SET_NULL: si se elimina la empresa, la persona conserva su cuenta (queda sin empresa)
        Empresa, on_delete=models.SET_NULL, related_name="usuarios",
        db_column="id_empresa", null=True, blank=True,  # vacía hasta que cree o le asignen una
    )
    rol = models.ForeignKey(
        Rol, on_delete=models.PROTECT, related_name="usuarios",
        db_column="id_roles", null=True, blank=True,
    )

    USERNAME_FIELD = "email"   # campo con el que se inicia sesión
    REQUIRED_FIELDS = []       # createsuperuser solo pide correo y contraseña

    objects = UsuarioManager()

    class Meta:
        db_table = "usuarios"
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"
        ordering = ["first_name", "last_name"]

    def __str__(self):
        return self.get_full_name() or self.email

    @property
    def iniciales(self):
        """Dos letras para el avatar redondo (ej. 'Yohan Cuellar' -> 'YC')."""
        partes = [p for p in (self.first_name, self.last_name) if p]
        if not partes:
            return self.email[:2].upper()
        return "".join(p[0] for p in partes)[:2].upper()

    def tiene_rol(self, *codigos):
        return bool(self.rol_id) and self.rol.codigo in codigos


# ---------------------------------------------------------------------------
# Equipos
# ---------------------------------------------------------------------------

class Equipo(models.Model):
    """Grupo de personas de una misma empresa.

    La cantidad de miembros NO se guarda (la base original tenía la columna
    'miembros'): se cuenta con equipo.miembros.count() y así nunca queda
    desactualizada.
    """

    id = models.BigAutoField(primary_key=True, db_column="id_equipo")
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField("descripción", blank=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="equipos", db_column="id_empresa")
    miembros = models.ManyToManyField(
        Usuario, through="MiembroEquipo", related_name="equipos", blank=True,
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "equipos"
        verbose_name = "equipo"
        verbose_name_plural = "equipos"
        ordering = ["nombre"]
        constraints = [
            models.UniqueConstraint(fields=["empresa", "nombre"], name="uq_equipo_nombre_por_empresa"),
        ]

    def __str__(self):
        return self.nombre


class MiembroEquipo(models.Model):
    """Tabla intermedia usuario <-> equipo, con el rol dentro del equipo."""

    class RolEquipo(models.TextChoices):
        LIDER = "lider", "Líder"
        MIEMBRO = "miembro", "Miembro"

    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, db_column="id_equipo")
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column="id_usuario")
    rol_en_equipo = models.CharField(max_length=10, choices=RolEquipo.choices, default=RolEquipo.MIEMBRO)
    fecha_ingreso = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "miembros_equipo"
        verbose_name = "miembro de equipo"
        verbose_name_plural = "miembros de equipo"
        constraints = [
            models.UniqueConstraint(fields=["equipo", "usuario"], name="uq_miembro"),
        ]

    def __str__(self):
        return f"{self.usuario} en {self.equipo}"

    def clean(self):
        # Un equipo solo puede tener personas de su misma empresa
        if self.usuario_id and self.equipo_id and self.usuario.empresa_id != self.equipo.empresa_id:
            raise ValidationError("El usuario y el equipo deben ser de la misma empresa.")
