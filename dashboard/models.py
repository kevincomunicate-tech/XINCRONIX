"""
Trabajo del día a día: proyectos, tareas, ideas, canvas, actividad,
notificaciones y métricas.

Trabajo en equipo
-----------------
* Un proyecto puede asignarse a un EQUIPO y/o tener MIEMBROS directos.
* Un lienzo (canvas) puede compartirse con PERSONAS, con un EQUIPO, con los
  miembros de un PROYECTO o con toda la EMPRESA.
* Quién ve qué se decide en un solo lugar: los métodos visibles_para() y
  puede_editar(). Las vistas solo los llaman.
* En los PROYECTOS los permisos salen de config/politica_accesos.json
  (sección "proyectos"); aquí solo se calcula la RELACIÓN de cada persona
  con el proyecto (creador, responsable, editor, observador, equipo).
"""

from functools import reduce
from operator import or_


from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q
from django.utils import timezone

from cuentas.models import Empresa, Equipo, Rol
from cuentas.politica import obtener_politica

Usuario = settings.AUTH_USER_MODEL

# Roles que pueden ver y editar todo dentro de su empresa
ROLES_GESTION = (Rol.ADMIN, Rol.MANAGER)
ROLES_VEN_TODO = (Rol.ADMIN, Rol.MANAGER, Rol.SUPERVISOR)


# ---------------------------------------------------------------------------
# Proyectos
# ---------------------------------------------------------------------------

# Cómo se traduce cada relación / alcance de la política a un filtro SQL
Q_RELACION = {
    "creador": lambda u: Q(creado_por=u),
    "responsable": lambda u: Q(proyectomiembro__usuario=u, proyectomiembro__rol="responsable"),
    "editor": lambda u: Q(proyectomiembro__usuario=u, proyectomiembro__rol="editor"),
    "observador": lambda u: Q(proyectomiembro__usuario=u, proyectomiembro__rol="observador"),
    "equipo": lambda u: Q(equipo__miembros=u),
}
Q_ALCANCE = {
    "todas": lambda u: Q(pk__isnull=False),
    "empresa": lambda u: Q(empresa_id=u.empresa_id) if u.empresa_id else Q(pk__in=[]),
}


class ProyectoQuerySet(models.QuerySet):
    def visibles_para(self, usuario):
        """Proyectos que puede ver un usuario, según la política (permiso "ver")."""
        if not usuario.is_authenticated:
            return self.none()
        relaciones, alcance = obtener_politica().criterios_para_ver("proyectos", usuario)
        filtros = [Q_RELACION[r](usuario) for r in relaciones]
        filtros += [Q_ALCANCE[alcance](usuario)] if alcance else []
        return self.filter(reduce(or_, filtros, Q(pk__in=[]))).distinct()


class Proyecto(models.Model):
    class Estado(models.TextChoices):
        ACTIVO = "activo", "Activo"
        PENDIENTE = "pendiente", "Pendiente"
        EN_PROGRESO = "en_progreso", "En progreso"
        EN_ESPERA = "en_espera", "En espera"
        COMPLETADO = "completado", "Completado"
        CANCELADO = "cancelado", "Cancelado"

    class Tipo(models.TextChoices):
        FRONTEND = "frontend", "Frontend"
        BACKEND = "backend", "Backend"
        FULL_STACK = "full_stack", "Full Stack"
        IA_ML = "ia_ml", "IA / ML"
        MOBILE = "mobile", "Mobile / App"
        DEVOPS = "devops", "DevOps / Infra"
        DATA = "data", "Datos / Analytics"
        QA = "qa", "QA / Testing"
        OTRO = "otro", "Otro"

    class Proposito(models.TextChoices):
        """Para qué se crea el proyecto (cuestionario inicial)."""
        ESCOLAR = "escolar", "Proyecto escolar / académico"
        PERSONAL = "personal", "Proyecto personal / aprendizaje"
        COMERCIAL = "comercial", "Para vender / producto comercial"
        DESPLIEGUE = "despliegue", "Para desplegar en producción"
        OPEN_SOURCE = "open_source", "Open source / comunidad"
        INTERNO = "interno", "Interno de equipo / startup"
        OTRO = "otro", "Otro"

    class Metodologia(models.TextChoices):
        SCRUM = "scrum", "Scrum"
        KANBAN = "kanban", "Kanban"
        GAES = "gaes", "GAES (Grupos de Aprendizaje)"
        WATERFALL = "waterfall", "Cascada / Waterfall"
        POMODORO = "pomodoro", "Pomodoro + sprints cortos"
        HYBRID = "hybrid", "Híbrida"
        NINGUNA = "ninguna", "Sin metodología formal"

    class Importancia(models.IntegerChoices):
        BAJA = 1, "Baja"
        MEDIA = 2, "Media"
        ALTA = 3, "Alta"
        CRITICA = 4, "Crítica"

    id = models.BigAutoField(primary_key=True, db_column="id_proyecto")
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField("descripción", blank=True)
    estado = models.CharField(max_length=15, choices=Estado.choices, default=Estado.ACTIVO)
    nivel_importancia = models.PositiveSmallIntegerField(choices=Importancia.choices, default=Importancia.MEDIA)
    tipo_proyecto = models.CharField("tipo técnico", max_length=15, choices=Tipo.choices, blank=True)
    proposito = models.CharField(
        "propósito", max_length=20, choices=Proposito.choices, blank=True, default="",
        help_text="Respuesta del cuestionario: ¿para qué es este proyecto?",
    )
    metodologia = models.CharField(
        "metodología", max_length=15, choices=Metodologia.choices, blank=True, default="",
        help_text="Metodología de trabajo elegida en el cuestionario.",
    )
    es_educativo = models.BooleanField(
        "proyecto educativo", default=False,
        help_text="Si es escolar/universitario: el supervisor (profesor) puede ver y comentar todo.",
    )
    es_grupal = models.BooleanField("es grupal", default=False)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    # Empresa queda opcional: la plataforma ya no gira en torno a empresas.
    empresa = models.ForeignKey(
        Empresa, on_delete=models.SET_NULL, related_name="proyectos",
        db_column="id_empresa", null=True, blank=True,
    )
    equipo = models.ForeignKey(
        Equipo, on_delete=models.SET_NULL, related_name="proyectos",
        db_column="id_equipo", null=True, blank=True,
        help_text="Equipo asignado (opcional).",
    )
    creado_por = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, related_name="proyectos_creados",
        db_column="id_creador", null=True, blank=True,
    )
    # Supervisor típico de proyectos educativos (profesor / mentor)
    supervisor = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, related_name="proyectos_supervisados",
        db_column="id_supervisor", null=True, blank=True,
        help_text="En proyectos educativos: el profesor o mentor que supervisa.",
    )
    miembros = models.ManyToManyField(
        Usuario, through="ProyectoMiembro", related_name="proyectos", blank=True,
    )

    objects = ProyectoQuerySet.as_manager()

    class Meta:
        db_table = "proyecto"
        verbose_name = "proyecto"
        verbose_name_plural = "proyectos"
        ordering = ["-fecha_creacion"]
        constraints = [
            models.CheckConstraint(
                condition=Q(fecha_fin__isnull=True) | Q(fecha_inicio__isnull=True) | Q(fecha_fin__gte=F("fecha_inicio")),
                name="ck_proyecto_fechas",
                violation_error_message="La fecha de fin no puede ser anterior a la de inicio.",
            ),
            models.CheckConstraint(
                condition=Q(nivel_importancia__gte=1, nivel_importancia__lte=4),
                name="ck_proyecto_importancia",
            ),
        ]
        indexes = [models.Index(fields=["empresa", "estado"], name="idx_proyecto_empresa_estado")]

    def __str__(self):
        return self.nombre

    def clean(self):
        if self.equipo_id and self.empresa_id and getattr(self.equipo, "empresa_id", None) and self.equipo.empresa_id != self.empresa_id:
            raise ValidationError({"equipo": "El equipo debe ser de la misma empresa del proyecto."})
        if self.es_educativo and not self.supervisor_id and self.proposito == self.Proposito.ESCOLAR:
            # Solo aviso suave; se puede asignar después
            pass

    def relaciones_con(self, usuario):
        """Relaciones de una persona con el proyecto, ej. {"creador"} o {"editor", "equipo"}."""
        if not usuario.is_authenticated:
            return set()
        # Rol como miembro directo ("responsable", "editor", "observador"), si lo es
        roles_miembro = set(self.proyectomiembro_set.filter(usuario_id=usuario.pk).values_list("rol", flat=True))
        otras = {
            "creador": self.creado_por_id == usuario.pk,
            "equipo": bool(self.equipo_id) and self.equipo.miembros.filter(pk=usuario.pk).exists(),
        }
        return roles_miembro | {nombre for nombre, cumple in otras.items() if cumple}

    def permisos(self, usuario):
        """{"ver", "editar", "eliminar", "miembros", "tareas"} según la política."""
        return obtener_politica().permisos_proyecto(usuario, self)

    def puede_editar(self, usuario):
        return "editar" in self.permisos(usuario)

    def personas(self):
        """Quienes trabajan en el proyecto: creador, miembros directos y del equipo."""
        from cuentas.models import Usuario as ModeloUsuario

        filtro = Q(proyectos=self) | Q(proyectos_creados=self)
        filtro |= Q(equipos=self.equipo_id) if self.equipo_id else Q(pk__in=[])
        return ModeloUsuario.objects.filter(filtro, is_active=True).distinct()

    @property
    def progreso(self):
        """Porcentaje de tareas completadas (se calcula, no se guarda)."""
        total = self.tareas.count()
        if not total:
            return 0
        hechas = self.tareas.filter(estado=Tarea.Estado.COMPLETADA).count()
        return round(hechas * 100 / total)


class ProyectoMiembro(models.Model):
    """Persona que trabaja en un proyecto y con qué rol.

    Puede ser de OTRA empresa: el creador invita a quien necesite por su
    correo. Lo que puede hacer cada rol lo dice la política (proyectos.por_relacion).
    """

    class RolProyecto(models.TextChoices):
        RESPONSABLE = "responsable", "Responsable"
        EDITOR = "editor", "Editor"
        OBSERVADOR = "observador", "Observador (solo lectura)"

    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, db_column="id_proyecto")
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column="id_usuario")
    rol = models.CharField(max_length=15, choices=RolProyecto.choices, default=RolProyecto.EDITOR)
    fecha_ingreso = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "proyecto_miembros"
        verbose_name = "miembro del proyecto"
        verbose_name_plural = "miembros del proyecto"
        constraints = [models.UniqueConstraint(fields=["proyecto", "usuario"], name="uq_proyecto_miembro")]

    def __str__(self):
        return f"{self.usuario} en {self.proyecto}"

    def clean(self):
        if self.usuario_id and self.proyecto_id and self.usuario_id == self.proyecto.creado_por_id:
            raise ValidationError("El creador ya tiene todos los permisos: no hace falta agregarlo.")


# ---------------------------------------------------------------------------
# Roadmap / Milestones (estilo GitHub Projects)
# ---------------------------------------------------------------------------

class Hito(models.Model):
    """Hito o milestone del roadmap de un proyecto."""

    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        EN_PROGRESO = "en_progreso", "En progreso"
        COMPLETADO = "completado", "Completado"
        CANCELADO = "cancelado", "Cancelado"

    id = models.BigAutoField(primary_key=True, db_column="id_hito")
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name="hitos", db_column="id_proyecto")
    titulo = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    fecha_objetivo = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=15, choices=Estado.choices, default=Estado.PENDIENTE)
    orden = models.PositiveSmallIntegerField(default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "hito"
        verbose_name = "hito"
        verbose_name_plural = "hitos"
        ordering = ["orden", "fecha_objetivo", "id"]

    def __str__(self):
        return f"{self.titulo} ({self.proyecto})"


class InvitacionProyecto(models.Model):
    """Invitación por correo (enlace único) para unirse a un proyecto grupal."""

    id = models.BigAutoField(primary_key=True)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name="invitaciones")
    email = models.EmailField()
    token = models.CharField(max_length=64, unique=True)
    rol = models.CharField(max_length=15, choices=ProyectoMiembro.RolProyecto.choices, default=ProyectoMiembro.RolProyecto.EDITOR)
    creada_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    aceptada = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_expiracion = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "invitacion_proyecto"
        verbose_name = "invitación a proyecto"
        verbose_name_plural = "invitaciones a proyectos"
        unique_together = [("proyecto", "email")]

    def __str__(self):
        return f"Invitación a {self.email} → {self.proyecto}"


# ---------------------------------------------------------------------------
# Tareas
# ---------------------------------------------------------------------------

class Tarea(models.Model):
    """Tarea de un proyecto.

    No guarda empresa ni equipo (la base original tenía id_equipo): los
    obtiene de su proyecto. Así no pueden contradecirse (3FN).
    """

    class Estado(models.TextChoices):
        POR_HACER = "por_hacer", "Por hacer"
        EN_PROGRESO = "en_progreso", "En progreso"
        EN_REVISION = "en_revision", "En revisión"
        COMPLETADA = "completada", "Completada"

    class Prioridad(models.TextChoices):
        BAJA = "baja", "Baja"
        MEDIA = "media", "Media"
        ALTA = "alta", "Alta"

    id = models.BigAutoField(primary_key=True, db_column="id_tarea")
    titulo = models.CharField("título", max_length=200)
    descripcion = models.TextField("descripción", blank=True)
    estado = models.CharField(max_length=15, choices=Estado.choices, default=Estado.POR_HACER)
    prioridad = models.CharField(max_length=10, choices=Prioridad.choices, default=Prioridad.MEDIA)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    fecha_completada = models.DateTimeField(null=True, blank=True, editable=False)

    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name="tareas", db_column="id_proyecto")
    asignado_a = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, related_name="tareas_asignadas",
        db_column="id_usuario", null=True, blank=True,
    )
    creado_por = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, related_name="tareas_creadas",
        db_column="id_creador", null=True, blank=True,
    )

    class Meta:
        db_table = "tareas"
        verbose_name = "tarea"
        verbose_name_plural = "tareas"
        ordering = ["fecha_vencimiento", "-fecha_creacion"]
        indexes = [models.Index(fields=["proyecto", "estado"], name="idx_tareas_proyecto_estado")]

    def __str__(self):
        return self.titulo

    def save(self, *args, **kwargs):
        # Registra cuándo se completó (lo usa Analytics)
        if self.estado == self.Estado.COMPLETADA and not self.fecha_completada:
            self.fecha_completada = timezone.now()
        elif self.estado != self.Estado.COMPLETADA:
            self.fecha_completada = None
        super().save(*args, **kwargs)

    @property
    def vencida(self):
        return (
            self.fecha_vencimiento is not None
            and self.estado != self.Estado.COMPLETADA
            and self.fecha_vencimiento < timezone.localdate()
        )


# ---------------------------------------------------------------------------
# Tablero de ideas
# ---------------------------------------------------------------------------

class Idea(models.Model):
    class Categoria(models.TextChoices):
        PRODUCTO = "producto", "Producto"
        PROCESOS = "procesos", "Procesos"
        TECNOLOGIA = "tecnologia", "Tecnología"
        CLIENTES = "clientes", "Clientes"
        EQUIPO = "equipo", "Equipo"

    class Estado(models.TextChoices):
        NUEVA = "nueva", "Nueva"
        EVALUACION = "evaluacion", "En evaluación"
        APROBADA = "aprobada", "Aprobada"
        ARCHIVADA = "archivada", "Archivada"

    class Color(models.TextChoices):
        AZUL = "azul", "Azul"
        AMARILLO = "amarillo", "Amarillo"
        VERDE = "verde", "Verde"
        ROSA = "rosa", "Rosa"
        MORADO = "morado", "Morado"

    id = models.BigAutoField(primary_key=True, db_column="id_idea")
    titulo = models.CharField("título", max_length=120)
    descripcion = models.TextField("descripción", max_length=600, blank=True)
    categoria = models.CharField("categoría", max_length=15, choices=Categoria.choices, default=Categoria.PRODUCTO)
    estado = models.CharField(max_length=15, choices=Estado.choices, default=Estado.NUEVA)
    color = models.CharField(max_length=10, choices=Color.choices, default=Color.AZUL)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    # La empresa no se saca del autor porque el autor puede borrarse
    # (SET_NULL) y la idea debe seguir en su empresa.
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="ideas", db_column="id_empresa")
    autor = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, related_name="ideas",
        db_column="id_usuario", null=True, blank=True,
    )
    votantes = models.ManyToManyField(Usuario, through="VotoIdea", related_name="ideas_votadas", blank=True)

    class Meta:
        db_table = "ideas"
        verbose_name = "idea"
        verbose_name_plural = "ideas"
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return self.titulo


class VotoIdea(models.Model):
    """Un voto por persona y por idea. El total se cuenta, no se guarda."""

    idea = models.ForeignKey(Idea, on_delete=models.CASCADE, db_column="id_idea")
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column="id_usuario")
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ideas_votos"
        verbose_name = "voto"
        verbose_name_plural = "votos"
        constraints = [models.UniqueConstraint(fields=["idea", "usuario"], name="uq_voto_idea")]


# ---------------------------------------------------------------------------
# Canvas (pizarra colaborativa)
# ---------------------------------------------------------------------------

class LienzoQuerySet(models.QuerySet):
    def visibles_para(self, usuario):
        if usuario.is_superuser:
            return self
        if not usuario.empresa_id:
            return self.none()
        base = self.filter(empresa_id=usuario.empresa_id)
        if usuario.tiene_rol(*ROLES_VEN_TODO):
            return base
        return base.filter(
            Q(compartido_con_empresa=True)
            | Q(creado_por=usuario)
            | Q(colaboradores=usuario)
            | Q(equipo__miembros=usuario)
            | Q(proyecto__miembros=usuario)
            | Q(proyecto__equipo__miembros=usuario)
        ).distinct()


class Lienzo(models.Model):
    """Pizarra del canvas.

    'contenido' guarda los dibujos en JSON ({"objetos": [...]}): un dibujo
    se carga y guarda siempre completo, así que no conviene una fila por
    trazo. El zoom y la posición de cada persona NO se guardan aquí (son de
    cada navegador).

    'version' sube en cada guardado: si dos personas guardan a la vez, la
    segunda se entera de que el lienzo cambió (control de concurrencia).
    """

    id = models.BigAutoField(primary_key=True, db_column="id_lienzo")
    nombre = models.CharField(max_length=60, default="Lluvia de ideas")
    contenido = models.JSONField(default=dict, blank=True)
    version = models.PositiveIntegerField(default=1)
    compartido_con_empresa = models.BooleanField(
        "visible para toda la empresa", default=False,
        help_text="Si está marcado, cualquiera de la empresa puede verlo (y editarlo).",
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="lienzos", db_column="id_empresa")
    proyecto = models.ForeignKey(
        Proyecto, on_delete=models.CASCADE, related_name="lienzos",
        db_column="id_proyecto", null=True, blank=True,
        help_text="Si pertenece a un proyecto, sus miembros pueden editarlo.",
    )
    equipo = models.ForeignKey(
        Equipo, on_delete=models.SET_NULL, related_name="lienzos",
        db_column="id_equipo", null=True, blank=True,
    )
    creado_por = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, related_name="lienzos_creados",
        db_column="id_creador", null=True, blank=True,
    )
    actualizado_por = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, related_name="+",
        db_column="id_ultimo_editor", null=True, blank=True,
    )
    colaboradores = models.ManyToManyField(
        Usuario, through="LienzoColaborador", related_name="lienzos", blank=True,
    )

    objects = LienzoQuerySet.as_manager()

    class Meta:
        db_table = "lienzos"
        verbose_name = "lienzo"
        verbose_name_plural = "lienzos"
        ordering = ["-fecha_actualizacion"]

    def __str__(self):
        return self.nombre

    def clean(self):
        for campo in ("proyecto", "equipo"):
            relacionado = getattr(self, campo)
            if relacionado and self.empresa_id and relacionado.empresa_id != self.empresa_id:
                raise ValidationError({campo: "Debe ser de la misma empresa del lienzo."})

    def puede_editar(self, usuario):
        if usuario.is_superuser:
            return True
        if usuario.empresa_id != self.empresa_id:
            return False
        if usuario.tiene_rol(*ROLES_GESTION) or self.creado_por_id == usuario.pk or self.compartido_con_empresa:
            return True
        permiso = self.lienzocolaborador_set.filter(usuario=usuario).values_list("permiso", flat=True).first()
        if permiso:
            return permiso == LienzoColaborador.Permiso.EDITOR
        if self.equipo_id and self.equipo.miembros.filter(pk=usuario.pk).exists():
            return True
        return bool(self.proyecto_id) and self.proyecto.puede_editar(usuario)


class LienzoColaborador(models.Model):
    class Permiso(models.TextChoices):
        EDITOR = "editor", "Puede editar"
        LECTOR = "lector", "Solo ver"

    lienzo = models.ForeignKey(Lienzo, on_delete=models.CASCADE, db_column="id_lienzo")
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column="id_usuario")
    permiso = models.CharField(max_length=10, choices=Permiso.choices, default=Permiso.EDITOR)
    fecha_ingreso = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "lienzo_colaboradores"
        verbose_name = "colaborador del lienzo"
        verbose_name_plural = "colaboradores del lienzo"
        constraints = [models.UniqueConstraint(fields=["lienzo", "usuario"], name="uq_lienzo_colaborador")]

    def clean(self):
        if self.usuario_id and self.lienzo_id and self.usuario.empresa_id != self.lienzo.empresa_id:
            raise ValidationError("El colaborador debe ser de la misma empresa del lienzo.")


# ---------------------------------------------------------------------------
# Actividad, notificaciones y métricas
# ---------------------------------------------------------------------------

class Actividad(models.Model):
    """Lo que aparece en 'Actividad reciente' del panel."""

    class Tipo(models.TextChoices):
        PROYECTO = "proyecto", "Proyecto"
        TAREA = "tarea", "Tarea"
        IDEA = "idea", "Idea"
        LIENZO = "lienzo", "Canvas"
        EQUIPO = "equipo", "Equipo"

    id = models.BigAutoField(primary_key=True, db_column="id_actividad")
    tipo = models.CharField(max_length=10, choices=Tipo.choices)
    descripcion = models.CharField("descripción", max_length=255)
    fecha = models.DateTimeField(auto_now_add=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="actividades", db_column="id_empresa")
    usuario = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, related_name="actividades",
        db_column="id_usuario", null=True, blank=True,
    )
    proyecto = models.ForeignKey(
        Proyecto, on_delete=models.CASCADE, related_name="actividades",
        db_column="id_proyecto", null=True, blank=True,
    )

    class Meta:
        db_table = "actividad"
        verbose_name = "actividad"
        verbose_name_plural = "actividad"
        ordering = ["-fecha"]
        indexes = [models.Index(fields=["empresa", "-fecha"], name="idx_actividad_empresa_fecha")]

    def __str__(self):
        return self.descripcion


class Notificacion(models.Model):
    """La base original tenía 'estado' y 'leida' para lo mismo: queda 'leida'."""

    class Tipo(models.TextChoices):
        INFO = "info", "Información"
        TAREA = "tarea", "Tarea"
        PROYECTO = "proyecto", "Proyecto"
        MENSAJE = "mensaje", "Mensaje"
        SISTEMA = "sistema", "Sistema"

    id = models.BigAutoField(primary_key=True, db_column="id_notificaciones")
    titulo = models.CharField("título", max_length=100)
    mensaje = models.TextField()
    tipo = models.CharField(max_length=10, choices=Tipo.choices, default=Tipo.INFO)
    url = models.CharField("enlace", max_length=300, blank=True)
    leida = models.BooleanField(default=False)
    fecha_envio = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="notificaciones", db_column="id_usuario")

    class Meta:
        db_table = "notificaciones"
        verbose_name = "notificación"
        verbose_name_plural = "notificaciones"
        ordering = ["-fecha_envio"]
        indexes = [models.Index(fields=["usuario", "leida"], name="idx_notificaciones_usuario")]

    def __str__(self):
        return self.titulo


class MetricaRendimiento(models.Model):
    """Indicadores que muestra Analytics (valor vs. meta en un periodo)."""

    id = models.BigAutoField(primary_key=True, db_column="id_metrica")
    tipo_metrica = models.CharField("indicador", max_length=100)
    valor = models.DecimalField(max_digits=12, decimal_places=4)
    meta = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    unidad = models.CharField(max_length=20, blank=True)
    fecha_inicio_periodo = models.DateField()
    fecha_fin_periodo = models.DateField()
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="metricas", db_column="id_empresa")
    usuario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, related_name="metricas",
        db_column="id_usuario", null=True, blank=True,
        help_text="Vacío = métrica de toda la empresa.",
    )

    class Meta:
        db_table = "metrica_rendimiento"
        verbose_name = "métrica de rendimiento"
        verbose_name_plural = "métricas de rendimiento"
        ordering = ["-fecha_fin_periodo"]
        constraints = [
            models.CheckConstraint(
                condition=Q(fecha_fin_periodo__gte=F("fecha_inicio_periodo")),
                name="ck_metrica_periodo",
                violation_error_message="El periodo termina antes de empezar.",
            ),
        ]
        indexes = [
            models.Index(fields=["tipo_metrica", "fecha_inicio_periodo", "fecha_fin_periodo"], name="idx_metrica_tipo_periodo"),
        ]

    def __str__(self):
        return self.tipo_metrica

    @property
    def cumplida(self):
        return None if self.meta is None else self.valor >= self.meta
