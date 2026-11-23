from django.conf import settings
from django.db import models
from django.utils import timezone

from cuentas.models import Empresa, Equipo


class Proyecto(models.Model):
    class Estado(models.TextChoices):
        ACTIVO = "activo", "Activo"
        EN_PAUSA = "pausa", "En pausa"
        COMPLETADO = "completado", "Completado"

    class Prioridad(models.TextChoices):
        BAJA = "baja", "Baja"
        NORMAL = "normal", "Normal"
        ALTA = "alta", "Alta"
        URGENTE = "urgente", "Urgente"

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="proyectos")
    nombre = models.CharField("nombre", max_length=180)
    descripcion = models.TextField("descripción", blank=True)
    estado = models.CharField(max_length=16, choices=Estado.choices, default=Estado.ACTIVO)
    prioridad = models.CharField(max_length=12, choices=Prioridad.choices, default=Prioridad.NORMAL)
    repositorio_url = models.URLField("repositorio público de GitHub", blank=True)
    fecha_inicio = models.DateField("fecha de inicio", null=True, blank=True)
    fecha_fin = models.DateField("fecha límite", null=True, blank=True)
    equipo = models.ForeignKey(
        Equipo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="proyectos",
    )
    miembros = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="proyectos", blank=True)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="proyectos_creados",
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-actualizado_en", "nombre")
        verbose_name = "proyecto"
        verbose_name_plural = "proyectos"

    def __str__(self):
        return self.nombre


class ReferenciaGitHub(models.Model):
    class Tipo(models.TextChoices):
        ISSUE = "issue", "Issue"
        PULL_REQUEST = "pull_request", "Pull request"

    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name="referencias_github",
    )
    tipo = models.CharField(max_length=16, choices=Tipo.choices)
    titulo = models.CharField("título", max_length=200)
    url = models.URLField("enlace de GitHub")
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="referencias_github_creadas",
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("tipo", "titulo")
        constraints = [
            models.UniqueConstraint(fields=("proyecto", "url"), name="unique_github_reference_per_project")
        ]
        verbose_name = "referencia de GitHub"
        verbose_name_plural = "referencias de GitHub"

    def __str__(self):
        return self.titulo


class Tarea(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Por hacer"
        EN_PROGRESO = "progreso", "En progreso"
        REVISION = "revision", "En revisión"
        COMPLETADA = "completada", "Completada"

    class Prioridad(models.TextChoices):
        BAJA = "baja", "Baja"
        NORMAL = "normal", "Normal"
        ALTA = "alta", "Alta"
        URGENTE = "urgente", "Urgente"

    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name="tareas")
    titulo = models.CharField("título", max_length=180)
    descripcion = models.TextField("descripción", blank=True)
    estado = models.CharField(max_length=16, choices=Estado.choices, default=Estado.PENDIENTE)
    prioridad = models.CharField(max_length=12, choices=Prioridad.choices, default=Prioridad.NORMAL)
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tareas_asignadas",
    )
    fecha_limite = models.DateField("fecha límite", null=True, blank=True)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="tareas_creadas",
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("estado", "fecha_limite", "titulo")
        verbose_name = "tarea"
        verbose_name_plural = "tareas"

    def __str__(self):
        return self.titulo

    @property
    def vencida(self):
        return bool(
            self.fecha_limite
            and self.fecha_limite < timezone.localdate()
            and self.estado != self.Estado.COMPLETADA
        )
