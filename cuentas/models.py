"""Cuentas personales de la plataforma de proyectos Xincronix."""

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models, router, transaction
from django.utils import timezone

from .restricciones import no_vacio

MENSAJE_ULTIMO_SUPERUSUARIO = (
    "No se puede: quedaría el sistema sin ningún superusuario activo. "
    "Primero crea o activa otro superusuario."
)


class SuperusuarioProtegido(Exception):
    """La operación dejaría el sistema sin ningún superusuario activo."""


class UsuarioQuerySet(models.QuerySet):
    """Borrados y cambios en lote también pasan por la regla del último superusuario.

    Las señales de instancia no alcanzan a QuerySet.delete() ni a QuerySet.update(),
    por eso la comprobación vive aquí.
    """

    def delete(self):
        with transaction.atomic(using=self.db):
            self._verificar_queda_un_superusuario()
            return super().delete()

    def update(self, **kwargs):
        if kwargs.get("is_active") is False or kwargs.get("is_superuser") is False:
            with transaction.atomic(using=self.db):
                self._verificar_queda_un_superusuario()
                return super().update(**kwargs)
        return super().update(**kwargs)

    def _verificar_queda_un_superusuario(self):
        with transaction.atomic(using=self.db):
            # Bloquea a todos los superusuarios activos: dos operaciones simultáneas no pueden
            # leer "quedan dos" y dejar cero.
            list(self.model._base_manager.using(self.db).select_for_update().filter(is_superuser=True, is_active=True).values_list("pk", flat=True))
            que_se_pierden = self.filter(is_superuser=True, is_active=True).count()
            if not que_se_pierden:
                return
            activos = self.model._base_manager.using(self.db).filter(is_superuser=True, is_active=True).count()
            if activos - que_se_pierden < 1:
                raise SuperusuarioProtegido(MENSAJE_ULTIMO_SUPERUSUARIO)


class UsuarioManager(BaseUserManager.from_queryset(UsuarioQuerySet)):
    """Crea cuentas identificadas exclusivamente por correo electrónico."""

    use_in_migrations = True

    def _crear(self, email, password, **extra):
        if not email:
            raise ValueError("El correo electrónico es obligatorio.")
        if not extra.get("first_name", "").strip() or not extra.get("last_name", "").strip():
            raise ValueError("Los nombres y los apellidos son obligatorios.")
        usuario = self.model(email=self.normalize_email(email).lower(), **extra)
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_user(self, email, password=None, **extra):
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        return self._crear(email, password, **extra)

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        if not extra.get("is_staff") or not extra.get("is_superuser"):
            raise ValueError("Un superusuario debe tener is_staff e is_superuser en True.")
        extra["rol"] = "admin"
        return self._crear(email, password, **extra)


class Usuario(AbstractUser):
    """Persona que usa la plataforma de proyectos de software."""

    class Perfil(models.TextChoices):
        PROFESIONAL = "profesional", "Profesional"
        ESTUDIANTE = "estudiante", "Estudiante"
        PROFESOR = "profesor", "Profesor / supervisor"

    class Rol(models.TextChoices):
        ADMIN = "admin", "Administrador"
        USUARIO = "usuario", "Usuario"
        SUPERVISOR = "supervisor", "Supervisor"

    username = None
    email = models.EmailField("correo electrónico", unique=True)
    first_name = models.CharField("nombres", max_length=100)
    last_name = models.CharField("apellidos", max_length=100)
    perfil = models.CharField(max_length=15, choices=Perfil.choices, default=Perfil.PROFESIONAL)
    rol = models.CharField("rol global", max_length=10, choices=Rol.choices, default=Rol.USUARIO, db_index=True)
    cargo = models.CharField("especialidad o rol", max_length=80, blank=True)
    telefono = models.CharField("teléfono", max_length=20, blank=True)
    avatar = models.ImageField("foto de perfil", upload_to="avatares/", blank=True)
    date_joined = models.DateTimeField("fecha de registro", default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]  # createsuperuser también pide nombre y apellido
    objects = UsuarioManager()

    class Meta:
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"
        ordering = ["first_name", "last_name", "email"]
        constraints = [
            models.CheckConstraint(condition=models.Q(rol__in=["admin", "usuario", "supervisor"]), name="usuario_rol_global_valido"),
            models.CheckConstraint(condition=models.Q(is_superuser=False) | models.Q(rol="admin"), name="usuario_superuser_rol_admin"),
            no_vacio("usuario", "first_name"),
            no_vacio("usuario", "last_name"),
        ]

    def save(self, *args, **kwargs):
        alias = kwargs.get("using") or router.db_for_write(type(self), instance=self)
        with transaction.atomic(using=alias):
            return super().save(*args, **kwargs)

    def __str__(self):
        return self.get_full_name() or self.email

    @property
    def es_admin(self):
        return self.is_active and self.rol == self.Rol.ADMIN

    @property
    def es_supervisor(self):
        return self.is_active and self.rol == self.Rol.SUPERVISOR

    @property
    def iniciales(self):
        partes = [parte[0] for parte in (self.first_name, self.last_name) if parte]
        return "".join(partes)[:2].upper() or self.email[:2].upper()
