from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class Empresa(models.Model):
    nombre = models.CharField("nombre", max_length=150)
    creada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("nombre",)
        verbose_name = "empresa"
        verbose_name_plural = "empresas"

    def __str__(self):
        return self.nombre


class UsuarioManager(BaseUserManager):
    """Crea usuarios usando el correo como identificador (sin username)."""

    use_in_migrations = True

    def _crear(self, email, password, **extra):
        email = str(email or "").strip().lower()
        if not email:
            raise ValueError("El correo es obligatorio")
        email = self.normalize_email(email)
        usuario = self.model(email=email, **extra)
        usuario.set_password(password)  # guarda la contraseña cifrada
        usuario.save(using=self._db)
        return usuario

    def create_user(self, email, password=None, **extra):
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        return self._crear(email, password, **extra)

    def create_superuser(self, email, password=None, **extra):
        extra["is_staff"] = True
        extra["is_superuser"] = True
        extra.setdefault("rol", Usuario.Rol.ADMIN)
        return self._crear(email, password, **extra)


class Usuario(AbstractUser):
    """Usuario de Xincronix: inicia sesión con su correo."""

    class Rol(models.TextChoices):
        ADMIN = "admin", "Administrador"
        MANAGER = "manager", "Manager"
        SUPERVISOR = "supervisor", "Supervisor"
        COLABORADOR = "colaborador", "Colaborador"

    username = None  # quitamos el "nombre de usuario" de Django
    email = models.EmailField("correo electrónico", unique=True)
    rol = models.CharField("rol", max_length=20, choices=Rol.choices, default=Rol.COLABORADOR)
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.PROTECT,
        related_name="usuarios",
        null=True,
        blank=True,
    )

    USERNAME_FIELD = "email"   # campo con el que se inicia sesión
    REQUIRED_FIELDS = []       # createsuperuser solo pedirá correo y contraseña

    objects = UsuarioManager()

    class Meta:
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"

    @property
    def puede_administrar_equipo(self):
        return self.rol in {self.Rol.ADMIN, self.Rol.MANAGER}

    def __str__(self):
        return self.get_full_name() or self.email

    @property
    def iniciales(self):
        """Dos letras para el avatar redondo (ej. 'Yohan Cuellar' -> 'YC')."""
        partes = [p for p in (self.first_name, self.last_name) if p]
        if not partes:
            return self.email[:2].upper()
        return "".join(p[0] for p in partes)[:2].upper()


class Equipo(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="equipos")
    nombre = models.CharField("nombre", max_length=120)
    descripcion = models.TextField("descripción", blank=True)
    miembros = models.ManyToManyField(Usuario, related_name="equipos", blank=True)
    creado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name="equipos_creados",
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("nombre",)
        constraints = [
            models.UniqueConstraint(fields=("empresa", "nombre"), name="unique_team_name_per_company")
        ]
        verbose_name = "equipo"
        verbose_name_plural = "equipos"

    def __str__(self):
        return self.nombre
