"""
Modelos del espacio de trabajo: proyectos, tareas y actividad.

Esquema normalizado:
- Nada que se pueda calcular se guarda (el % de avance de un proyecto, el
  número de miembros o de tareas se obtienen con consultas).
- Los estados y prioridades son opciones fijas (choices), no texto libre,
  para que "Completada" y "completada" no terminen siendo cosas distintas.
- La única copia intencional es Actividad.detalle: es un registro histórico
  y debe seguir diciendo "completó la tarea X" aunque X se borre después.
"""

from django.conf import settings
from django.db import models
from django.db.models import Count, Q
from django.utils import timezone


class Prioridad(models.IntegerChoices):
    """Compartida por proyectos y tareas. Entero para poder ordenar."""

    BAJA = 1, "Baja"
    MEDIA = 2, "Media"
    ALTA = 3, "Alta"


# ---------------------------------------------------------------------------
# Proyecto
# ---------------------------------------------------------------------------

class ProyectoQuerySet(models.QuerySet):
    def visibles_para(self, usuario):
        """Proyectos de los que el usuario es dueño o miembro.

        Se usa una subconsulta (y no un JOIN con miembros) para no repetir
        filas, así luego se pueden contar tareas sin resultados inflados.
        """
        como_miembro = Proyecto.miembros.through.objects.filter(usuario=usuario).values("proyecto")
        return self.filter(Q(propietario=usuario) | Q(pk__in=como_miembro))

    def con_progreso(self):
        """Agrega total_tareas y tareas_completadas a cada proyecto."""
        return self.annotate(
            total_tareas=Count("tareas"),
            tareas_completadas=Count("tareas", filter=Q(tareas__estado=Tarea.Estado.COMPLETADA)),
        )


class Proyecto(models.Model):
    class Estado(models.TextChoices):
        ACTIVO = "activo", "Activo"
        PAUSADO = "pausado", "En pausa"
        COMPLETADO = "completado", "Completado"
        ARCHIVADO = "archivado", "Archivado"

    nombre = models.CharField("nombre", max_length=150)
    descripcion = models.TextField("descripción", blank=True)
    estado = models.CharField("estado", max_length=20, choices=Estado.choices, default=Estado.ACTIVO)
    prioridad = models.PositiveSmallIntegerField("prioridad", choices=Prioridad.choices, default=Prioridad.MEDIA)
    fecha_inicio = models.DateField("fecha de inicio", null=True, blank=True)
    fecha_fin = models.DateField("fecha de entrega", null=True, blank=True)

    propietario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="proyectos_propios",
        verbose_name="propietario",
    )
    miembros = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="MiembroProyecto",
        related_name="proyectos",
        blank=True,
        verbose_name="miembros",
    )

    creado = models.DateTimeField("creado", auto_now_add=True)
    actualizado = models.DateTimeField("actualizado", auto_now=True)

    objects = ProyectoQuerySet.as_manager()

    class Meta:
        verbose_name = "proyecto"
        verbose_name_plural = "proyectos"
        ordering = ["-prioridad", "nombre"]
        indexes = [models.Index(fields=["propietario", "estado"])]
        constraints = [
            models.CheckConstraint(
                condition=Q(fecha_fin__isnull=True) | Q(fecha_inicio__isnull=True) | Q(fecha_fin__gte=models.F("fecha_inicio")),
                name="proyecto_fin_despues_de_inicio",
            ),
        ]

    def __str__(self):
        return self.nombre

    @property
    def progreso(self):
        """Porcentaje de tareas completadas (0-100).

        Usa los valores de con_progreso() si ya vienen calculados; si no,
        hace la consulta.
        """
        total = getattr(self, "total_tareas", None)
        hechas = getattr(self, "tareas_completadas", None)
        if total is None or hechas is None:
            total = self.tareas.count()
            hechas = self.tareas.filter(estado=Tarea.Estado.COMPLETADA).count()
        return round(hechas * 100 / total) if total else 0


class MiembroProyecto(models.Model):
    """Tabla intermedia usuario <-> proyecto (permite guardar desde cuándo)."""

    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    agregado = models.DateTimeField("agregado", auto_now_add=True)

    class Meta:
        verbose_name = "miembro del proyecto"
        verbose_name_plural = "miembros del proyecto"
        constraints = [
            models.UniqueConstraint(fields=["proyecto", "usuario"], name="miembro_unico_por_proyecto"),
        ]

    def __str__(self):
        return f"{self.usuario} en {self.proyecto}"


# ---------------------------------------------------------------------------
# Tarea
# ---------------------------------------------------------------------------

class Tarea(models.Model):
    class Estado(models.TextChoices):
        POR_HACER = "por_hacer", "Por hacer"
        EN_PROGRESO = "en_progreso", "En progreso"
        EN_REVISION = "en_revision", "En revisión"
        COMPLETADA = "completada", "Completada"

    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name="tareas", verbose_name="proyecto")
    titulo = models.CharField("título", max_length=200)
    descripcion = models.TextField("descripción", blank=True)
    estado = models.CharField("estado", max_length=20, choices=Estado.choices, default=Estado.POR_HACER)
    prioridad = models.PositiveSmallIntegerField("prioridad", choices=Prioridad.choices, default=Prioridad.MEDIA)
    fecha_vencimiento = models.DateField("fecha de vencimiento", null=True, blank=True)

    asignada_a = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tareas_asignadas",
        verbose_name="asignada a",
    )
    creada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tareas_creadas",
        verbose_name="creada por",
    )

    creada = models.DateTimeField("creada", auto_now_add=True)
    actualizada = models.DateTimeField("actualizada", auto_now=True)
    # Cuándo pasó a "Completada" (lo llena save()); sirve para "esta semana"
    completada_en = models.DateTimeField("completada el", null=True, blank=True, editable=False)

    class Meta:
        verbose_name = "tarea"
        verbose_name_plural = "tareas"
        ordering = ["fecha_vencimiento", "-prioridad"]
        indexes = [
            models.Index(fields=["proyecto", "estado"]),
            models.Index(fields=["asignada_a", "estado"]),
        ]

    def __str__(self):
        return self.titulo

    def save(self, *args, **kwargs):
        # Mantiene completada_en de acuerdo con el estado
        if self.estado == self.Estado.COMPLETADA:
            if self.completada_en is None:
                self.completada_en = timezone.now()
        else:
            self.completada_en = None
        super().save(*args, **kwargs)

    @property
    def vencida(self):
        return (
            self.fecha_vencimiento is not None
            and self.estado != self.Estado.COMPLETADA
            and self.fecha_vencimiento < timezone.localdate()
        )


# ---------------------------------------------------------------------------
# Actividad (historial: "Ana completó la tarea Diseñar login")
# ---------------------------------------------------------------------------

class Actividad(models.Model):
    class Accion(models.TextChoices):
        # La etiqueta es el verbo que se muestra en el panel
        PROYECTO_CREADO = "proyecto_creado", "creó el proyecto"
        TAREA_CREADA = "tarea_creada", "creó la tarea"
        TAREA_MOVIDA = "tarea_movida", "movió la tarea"
        TAREA_COMPLETADA = "tarea_completada", "completó la tarea"

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="actividades",
        verbose_name="usuario",
    )
    accion = models.CharField("acción", max_length=30, choices=Accion.choices)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name="actividades", verbose_name="proyecto")
    tarea = models.ForeignKey(
        Tarea, on_delete=models.SET_NULL, null=True, blank=True, related_name="actividades", verbose_name="tarea"
    )
    # Nombre del proyecto/tarea en ese momento (ver nota al inicio del archivo)
    detalle = models.CharField("detalle", max_length=200)
    fecha = models.DateTimeField("fecha", default=timezone.now, db_index=True)

    class Meta:
        verbose_name = "actividad"
        verbose_name_plural = "actividades"
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.usuario or 'Alguien'} {self.get_accion_display()} {self.detalle}"

    @classmethod
    def registrar(cls, usuario, accion, proyecto, tarea=None):
        """Atajo para guardar una actividad desde vistas, admin o comandos."""
        detalle = tarea.titulo if tarea is not None else proyecto.nombre
        return cls.objects.create(usuario=usuario, accion=accion, proyecto=proyecto, tarea=tarea, detalle=detalle)
