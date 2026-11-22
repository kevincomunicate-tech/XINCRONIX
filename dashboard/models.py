"""
Equipos, proyectos, tareas y actividad.

Las tablas y columnas siguen el esquema de xincronix_bd.sql. Reglas:
- Todo pertenece a una empresa; nadie ve datos de otra empresa.
- Admin, manager y supervisor ven todos los proyectos de su empresa;
  un colaborador solo los proyectos donde lo agregaron (directamente o
  por su equipo) o que él creó.
- Nada que se pueda calcular se guarda (el % de avance se obtiene
  contando tareas). Estados y prioridades son opciones fijas.
"""

from django.conf import settings
from django.db import models
from django.db.models import Case, Count, IntegerField, Q, Value, When
from django.utils import timezone

from cuentas.models import Empresa


# ---------------------------------------------------------------------------
# Equipos
# ---------------------------------------------------------------------------

class Equipo(models.Model):
    id = models.BigAutoField(primary_key=True, db_column="id_equipo")
    nombre = models.CharField("nombre", max_length=150)
    descripcion = models.TextField("descripción", blank=True)
    fecha_creacion = models.DateTimeField("creado", auto_now_add=True)
    empresa = models.ForeignKey(
        Empresa, on_delete=models.CASCADE, db_column="id_empresa", related_name="equipos", verbose_name="empresa"
    )
    miembros = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through="MiembroEquipo", related_name="equipos", blank=True, verbose_name="miembros"
    )

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
    class Rol(models.TextChoices):
        LIDER = "lider", "Líder"
        MIEMBRO = "miembro", "Miembro"

    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, db_column="id_equipo")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column="id_usuario")
    rol_en_equipo = models.CharField("rol en el equipo", max_length=10, choices=Rol.choices, default=Rol.MIEMBRO)
    fecha_ingreso = models.DateTimeField("ingresó", auto_now_add=True)

    class Meta:
        db_table = "miembros_equipo"
        verbose_name = "miembro del equipo"
        verbose_name_plural = "miembros del equipo"
        constraints = [models.UniqueConstraint(fields=["equipo", "usuario"], name="uq_miembro")]

    def __str__(self):
        return f"{self.usuario} en {self.equipo}"


# ---------------------------------------------------------------------------
# Proyectos
# ---------------------------------------------------------------------------

class ProyectoQuerySet(models.QuerySet):
    def visibles_para(self, usuario):
        """Proyectos que el usuario puede ver (ver reglas al inicio del archivo).

        Se usan subconsultas (no JOIN con miembros) para no repetir filas;
        así luego se pueden contar tareas sin resultados inflados.
        """
        if usuario.empresa_id is None:
            return self.none()
        de_la_empresa = self.filter(empresa_id=usuario.empresa_id)
        if usuario.ve_toda_la_empresa:
            return de_la_empresa
        como_miembro = MiembroProyecto.objects.filter(usuario=usuario).values("proyecto")
        mis_equipos = MiembroEquipo.objects.filter(usuario=usuario).values("equipo")
        return de_la_empresa.filter(Q(creador=usuario) | Q(pk__in=como_miembro) | Q(equipo__in=mis_equipos))

    def con_progreso(self):
        """Agrega total_tareas y tareas_completadas a cada proyecto."""
        return self.annotate(
            total_tareas=Count("tareas"),
            tareas_completadas=Count("tareas", filter=Q(tareas__estado=Tarea.Estado.COMPLETADA)),
        )


class Proyecto(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        ACTIVO = "activo", "Activo"
        EN_ESPERA = "en_espera", "En espera"
        COMPLETADO = "completado", "Completado"
        CANCELADO = "cancelado", "Cancelado"

    class Importancia(models.IntegerChoices):
        BAJA = 1, "Baja"
        MEDIA = 2, "Media"
        ALTA = 3, "Alta"
        CRITICA = 4, "Crítica"

    class Tipo(models.TextChoices):
        DESARROLLO = "desarrollo", "Desarrollo"
        DISENO = "diseno", "Diseño"
        MARKETING = "marketing", "Marketing"
        INVESTIGACION = "investigacion", "Investigación"
        OPERACIONES = "operaciones", "Operaciones"
        OTRO = "otro", "Otro"

    id = models.BigAutoField(primary_key=True, db_column="id_proyecto")
    nombre = models.CharField("nombre", max_length=150)
    descripcion = models.TextField("descripción", blank=True)
    estado = models.CharField("estado", max_length=15, choices=Estado.choices, default=Estado.ACTIVO)
    nivel_importancia = models.PositiveSmallIntegerField(
        "importancia", choices=Importancia.choices, default=Importancia.MEDIA
    )
    tipo_proyecto = models.CharField("tipo", max_length=15, choices=Tipo.choices, default=Tipo.OTRO)
    fecha_inicio = models.DateField("fecha de inicio", null=True, blank=True)
    fecha_fin = models.DateField("fecha de entrega", null=True, blank=True)
    fecha_creacion = models.DateTimeField("creado", auto_now_add=True)
    creador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="id_creador",
        related_name="proyectos_creados",
        verbose_name="creador",
    )
    empresa = models.ForeignKey(
        Empresa, on_delete=models.CASCADE, db_column="id_empresa", related_name="proyectos", verbose_name="empresa"
    )
    equipo = models.ForeignKey(
        Equipo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="id_equipo",
        related_name="proyectos",
        verbose_name="equipo",
    )
    miembros = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through="MiembroProyecto", related_name="proyectos", blank=True, verbose_name="miembros"
    )

    objects = ProyectoQuerySet.as_manager()

    class Meta:
        db_table = "proyecto"
        verbose_name = "proyecto"
        verbose_name_plural = "proyectos"
        ordering = ["-nivel_importancia", "nombre"]
        indexes = [models.Index(fields=["empresa", "estado"], name="idx_proyecto_empresa_estado")]
        constraints = [
            models.CheckConstraint(
                condition=Q(fecha_fin__isnull=True) | Q(fecha_inicio__isnull=True) | Q(fecha_fin__gte=models.F("fecha_inicio")),
                name="ck_proyecto_fechas",
            ),
            models.CheckConstraint(
                condition=Q(nivel_importancia__gte=1, nivel_importancia__lte=4),
                name="ck_proyecto_importancia",
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
    class Rol(models.TextChoices):
        RESPONSABLE = "responsable", "Responsable"
        COLABORADOR = "colaborador", "Colaborador"
        OBSERVADOR = "observador", "Observador"

    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, db_column="id_proyecto")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column="id_usuario")
    rol = models.CharField("rol", max_length=15, choices=Rol.choices, default=Rol.COLABORADOR)
    fecha_ingreso = models.DateTimeField("ingresó", auto_now_add=True)

    class Meta:
        db_table = "proyecto_miembros"
        verbose_name = "miembro del proyecto"
        verbose_name_plural = "miembros del proyecto"
        constraints = [models.UniqueConstraint(fields=["proyecto", "usuario"], name="uq_proyecto_miembro")]

    def __str__(self):
        return f"{self.usuario} en {self.proyecto}"


# ---------------------------------------------------------------------------
# Tareas
# ---------------------------------------------------------------------------

class Tarea(models.Model):
    class Estado(models.TextChoices):
        POR_HACER = "por_hacer", "Por hacer"
        EN_PROGRESO = "en_progreso", "En progreso"
        EN_REVISION = "en_revision", "En revisión"
        COMPLETADA = "completada", "Completada"

    class Prioridad(models.TextChoices):
        BAJA = "baja", "Baja"
        MEDIA = "media", "Media"
        ALTA = "alta", "Alta"
        URGENTE = "urgente", "Urgente"

    id = models.BigAutoField(primary_key=True, db_column="id_tarea")
    titulo = models.CharField("título", max_length=200)
    descripcion = models.TextField("descripción", blank=True)
    estado = models.CharField("estado", max_length=15, choices=Estado.choices, default=Estado.POR_HACER)
    prioridad = models.CharField("prioridad", max_length=10, choices=Prioridad.choices, default=Prioridad.MEDIA)
    fecha_creacion = models.DateTimeField("creada", auto_now_add=True)
    fecha_vencimiento = models.DateField("fecha de vencimiento", null=True, blank=True)
    # Cuándo pasó a "Completada" (lo llena save()); sirve para "esta semana"
    fecha_completada = models.DateTimeField("completada el", null=True, blank=True, editable=False)
    asignada_a = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="id_usuario",
        related_name="tareas_asignadas",
        verbose_name="asignada a",
    )
    creador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="id_creador",
        related_name="tareas_creadas",
        verbose_name="creada por",
    )
    proyecto = models.ForeignKey(
        Proyecto, on_delete=models.CASCADE, db_column="id_proyecto", related_name="tareas", verbose_name="proyecto"
    )

    class Meta:
        db_table = "tareas"
        verbose_name = "tarea"
        verbose_name_plural = "tareas"
        ordering = ["fecha_vencimiento", "titulo"]
        indexes = [models.Index(fields=["proyecto", "estado"], name="idx_tareas_proyecto_estado")]

    def __str__(self):
        return self.titulo

    def save(self, *args, **kwargs):
        # Mantiene fecha_completada de acuerdo con el estado
        if self.estado == self.Estado.COMPLETADA:
            if self.fecha_completada is None:
                self.fecha_completada = timezone.now()
        else:
            self.fecha_completada = None
        super().save(*args, **kwargs)

    @property
    def vencida(self):
        return (
            self.fecha_vencimiento is not None
            and self.estado != self.Estado.COMPLETADA
            and self.fecha_vencimiento < timezone.localdate()
        )

    @staticmethod
    def orden_prioridad():
        """Expresión para ordenar por prioridad (urgente primero).

        La prioridad se guarda como texto, así que se traduce a número.
        """
        P = Tarea.Prioridad
        return Case(
            When(prioridad=P.URGENTE, then=Value(4)),
            When(prioridad=P.ALTA, then=Value(3)),
            When(prioridad=P.MEDIA, then=Value(2)),
            default=Value(1),
            output_field=IntegerField(),
        )


# ---------------------------------------------------------------------------
# Actividad (historial: "Ana completó la tarea Diseñar login")
# ---------------------------------------------------------------------------

class Actividad(models.Model):
    class Tipo(models.TextChoices):
        PROYECTO = "proyecto", "Proyecto"
        TAREA = "tarea", "Tarea"
        EQUIPO = "equipo", "Equipo"

    id = models.BigAutoField(primary_key=True, db_column="id_actividad")
    tipo = models.CharField("tipo", max_length=10, choices=Tipo.choices)
    # Texto ya armado ("completó la tarea Diseñar login"): es un registro
    # histórico y debe seguir leyéndose aunque la tarea se borre después.
    descripcion = models.CharField("descripción", max_length=255)
    fecha = models.DateTimeField("fecha", default=timezone.now)
    empresa = models.ForeignKey(
        Empresa, on_delete=models.CASCADE, db_column="id_empresa", related_name="actividades", verbose_name="empresa"
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="id_usuario",
        related_name="actividades",
        verbose_name="usuario",
    )
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_column="id_proyecto",
        related_name="actividades",
        verbose_name="proyecto",
    )

    class Meta:
        db_table = "actividad"
        verbose_name = "actividad"
        verbose_name_plural = "actividades"
        ordering = ["-fecha"]
        indexes = [models.Index(fields=["empresa", "-fecha"], name="idx_actividad_empresa_fecha")]

    def __str__(self):
        return f"{self.usuario or 'Alguien'} {self.descripcion}"

    # Frases que se guardan en descripcion
    PROYECTO_CREADO = "creó el proyecto {}"
    TAREA_CREADA = "creó la tarea {}"
    TAREA_MOVIDA = "movió la tarea {} a {}"
    TAREA_COMPLETADA = "completó la tarea {}"

    @classmethod
    def registrar_proyecto_creado(cls, usuario, proyecto):
        return cls._crear(usuario, cls.Tipo.PROYECTO, proyecto, cls.PROYECTO_CREADO.format(proyecto.nombre))

    @classmethod
    def registrar_tarea(cls, usuario, tarea, creada=False):
        """Registra que una tarea se creó o cambió de estado."""
        if creada:
            texto = cls.TAREA_CREADA.format(tarea.titulo)
        elif tarea.estado == Tarea.Estado.COMPLETADA:
            texto = cls.TAREA_COMPLETADA.format(tarea.titulo)
        else:
            texto = cls.TAREA_MOVIDA.format(tarea.titulo, tarea.get_estado_display())
        return cls._crear(usuario, cls.Tipo.TAREA, tarea.proyecto, texto)

    @classmethod
    def _crear(cls, usuario, tipo, proyecto, texto):
        return cls.objects.create(
            usuario=usuario, tipo=tipo, proyecto=proyecto, empresa_id=proyecto.empresa_id, descripcion=texto[:255]
        )
