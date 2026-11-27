"""Modelo de la plataforma: proyectos de tecnología, sin organizaciones."""

import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone

from cuentas.restricciones import fin_no_antes_que_inicio, no_vacio

Usuario = settings.AUTH_USER_MODEL


class ProyectoQuerySet(models.QuerySet):
    def visibles_para(self, usuario):
        if not getattr(usuario, "is_authenticated", False) or not usuario.is_active:
            return self.none()
        if usuario.es_admin:
            return self
        acceso = Q(creado_por=usuario) | Q(miembros=usuario)
        if usuario.es_supervisor:
            acceso |= Q(supervisor=usuario)
        return self.filter(acceso).distinct()


class Proyecto(models.Model):
    class Estado(models.TextChoices):
        PLANIFICACION = "planificacion", "Planificación"
        EN_PROGRESO = "en_progreso", "En progreso"
        EN_PAUSA = "en_pausa", "En pausa"
        COMPLETADO = "completado", "Completado"
        CANCELADO = "cancelado", "Cancelado"

    class Finalidad(models.TextChoices):
        EDUCATIVO = "educativo", "Educativo"
        COMERCIAL = "comercial", "Producto comercial"
        DESPLIEGUE = "despliegue", "Despliegue / producción"
        PERSONAL = "personal", "Portafolio o personal"
        OTRO = "otro", "Otro"

    class Metodologia(models.TextChoices):
        SCRUM = "scrum", "Scrum"
        GAES = "gaes", "GAES"
        POMODORO = "pomodoro", "Pomodoro"
        KANBAN = "kanban", "Kanban"
        PROPIA = "propia", "Propia"

    class Modalidad(models.TextChoices):
        INDIVIDUAL = "individual", "Individual"
        GRUPAL = "grupal", "Grupal"

    class Visibilidad(models.TextChoices):
        PRIVADO = "privado", "Privado: solo el equipo"
        PUBLICO = "publico", "Público: cualquiera con el enlace puede verlo"

    nombre = models.CharField(max_length=150)
    descripcion = models.TextField("descripción")
    tecnologia = models.CharField("tecnologías", max_length=180, blank=True, help_text="Ej.: Django, React, PostgreSQL")
    repositorio_url = models.URLField("repositorio", blank=True)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PLANIFICACION)
    finalidad = models.CharField(max_length=15, choices=Finalidad.choices, default=Finalidad.OTRO)
    metodologia = models.CharField(max_length=15, choices=Metodologia.choices, default=Metodologia.KANBAN)
    modalidad = models.CharField(max_length=12, choices=Modalidad.choices, default=Modalidad.INDIVIDUAL)
    visibilidad = models.CharField(max_length=10, choices=Visibilidad.choices, default=Visibilidad.PRIVADO)
    # Enlace de solo lectura para la vista pública. Si se regenera, el enlace anterior deja de servir.
    enlace_publico = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    contexto_educativo = models.CharField("curso o contexto educativo", max_length=180, blank=True)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    creado_por = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="proyectos_creados")
    supervisor = models.ForeignKey(Usuario, on_delete=models.SET_NULL, related_name="proyectos_supervisados", null=True, blank=True)
    miembros = models.ManyToManyField(Usuario, through="ProyectoMiembro", related_name="proyectos", blank=True)

    objects = ProyectoQuerySet.as_manager()

    class Meta:
        ordering = ["-fecha_creacion"]
        constraints = [
            models.CheckConstraint(condition=Q(fecha_fin__isnull=True) | Q(fecha_inicio__isnull=True) | Q(fecha_fin__gte=models.F("fecha_inicio")), name="proyecto_fechas_validas"),
            no_vacio("proyecto", "nombre"),
            no_vacio("proyecto", "descripcion"),
        ]

    def __str__(self):
        return self.nombre

    def clean(self):
        if self.modalidad == self.Modalidad.INDIVIDUAL and self.pk and self.miembros.exclude(pk=self.creado_por_id).exists():
            raise ValidationError("Un proyecto individual no puede tener integrantes adicionales.")
        if self.supervisor_id and not self.supervisor.es_supervisor:
            raise ValidationError({"supervisor": "Selecciona una cuenta activa con el rol global de supervisor."})

    def relacion_con(self, usuario):
        if not getattr(usuario, "is_authenticated", False) or not usuario.is_active:
            return None
        if usuario.es_admin:
            return "administrador"
        if self.creado_por_id == usuario.pk:
            return "lider"
        if self.supervisor_id == usuario.pk and usuario.es_supervisor:
            return "supervisor"
        return self.proyectomiembro_set.filter(usuario=usuario).values_list("rol", flat=True).first()

    def permisos(self, usuario):
        relacion = self.relacion_con(usuario)
        permisos = {"ver"} if relacion else set()
        if relacion in {"administrador", "lider"}:
            permisos |= {"editar", "eliminar", "miembros", "invitaciones", "tareas", "calendario", "canvas", "documentos", "correcciones"}
        elif relacion == ProyectoMiembro.Rol.EDITOR:
            permisos |= {"editar", "tareas", "calendario", "canvas", "documentos"}
        elif relacion == "supervisor":
            permisos |= {"correcciones"}
        return permisos

    def puede_editar(self, usuario):
        return "editar" in self.permisos(usuario)

    def personas(self):
        from cuentas.models import Usuario as ModeloUsuario
        return ModeloUsuario.objects.filter(Q(pk=self.creado_por_id) | Q(proyectos=self), is_active=True).distinct()

    @property
    def progreso(self):
        total = self.tareas.count()
        return round(self.tareas.filter(estado=Tarea.Estado.HECHA).count() * 100 / total) if total else 0


class ProyectoMiembro(models.Model):
    class Rol(models.TextChoices):
        LIDER = "lider", "Líder"
        EDITOR = "editor", "Colaborador"
        LECTOR = "lector", "Solo lectura"

    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    rol = models.CharField(max_length=10, choices=Rol.choices, default=Rol.EDITOR)
    fecha_ingreso = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["proyecto", "usuario"], name="miembro_proyecto_unico")]
        ordering = ["rol", "usuario__first_name"]

    def __str__(self):
        return f"{self.usuario} — {self.proyecto}"


class InvitacionProyecto(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        ACEPTADA = "aceptada", "Aceptada"
        RECHAZADA = "rechazada", "Rechazada"
        CANCELADA = "cancelada", "Cancelada"

    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name="invitaciones")
    email = models.EmailField()
    rol = models.CharField(max_length=10, choices=ProyectoMiembro.Rol.choices, default=ProyectoMiembro.Rol.EDITOR)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    estado = models.CharField(max_length=12, choices=Estado.choices, default=Estado.PENDIENTE)
    creado_por = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="invitaciones_creadas")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    vence_en = models.DateTimeField()

    class Meta:
        ordering = ["-fecha_creacion"]

    @property
    def vencida(self):
        return timezone.now() > self.vence_en

    @property
    def descripcion_rol(self):
        """Qué podrá hacer la persona si acepta (se muestra en el correo y en la notificación)."""
        if self.rol == ProyectoMiembro.Rol.LECTOR:
            return "Solo lectura: podrás mirar el proyecto sin cambiar nada."
        return "Colaborador: podrás editar tareas, calendario, canvas y documentos."

    @classmethod
    def pendientes_para(cls, usuario):
        """Invitaciones vigentes dirigidas al correo de esta cuenta."""
        if not getattr(usuario, "is_authenticated", False) or not usuario.email:
            return cls.objects.none()
        return (cls.objects.filter(email__iexact=usuario.email, estado=cls.Estado.PENDIENTE, vence_en__gt=timezone.now())
                .select_related("proyecto", "creado_por"))

    def __str__(self):
        return f"{self.email} → {self.proyecto}"


class Tarea(models.Model):
    class Estado(models.TextChoices):
        POR_HACER = "por_hacer", "Por hacer"
        EN_PROGRESO = "en_progreso", "En progreso"
        REVISION = "revision", "En revisión"
        HECHA = "hecha", "Hecha"

    class Prioridad(models.TextChoices):
        BAJA = "baja", "Baja"
        MEDIA = "media", "Media"
        ALTA = "alta", "Alta"

    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name="tareas")
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    estado = models.CharField(max_length=15, choices=Estado.choices, default=Estado.POR_HACER)
    prioridad = models.CharField(max_length=10, choices=Prioridad.choices, default=Prioridad.MEDIA)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_completada = models.DateTimeField(null=True, blank=True)
    asignado_a = models.ForeignKey(Usuario, on_delete=models.SET_NULL, related_name="tareas_asignadas", null=True, blank=True)
    creado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, related_name="tareas_creadas", null=True, blank=True)

    def clean(self):
        if self.asignado_a_id and self.proyecto_id and not ProyectoMiembro.objects.filter(proyecto_id=self.proyecto_id, usuario_id=self.asignado_a_id).exists():
            raise ValidationError({"asignado_a": "Solo puedes asignar la tarea a un integrante del proyecto."})

    class Meta:
        constraints = [
            no_vacio("tarea", "titulo"),
        ]
        ordering = ["fecha_vencimiento", "-fecha_creacion"]
        indexes = [models.Index(fields=["proyecto", "estado"])]

    def __str__(self):
        return self.titulo

    def save(self, *args, **kwargs):
        if self.estado == self.Estado.HECHA and not self.fecha_completada:
            self.fecha_completada = timezone.now()
        elif self.estado != self.Estado.HECHA:
            self.fecha_completada = None
        super().save(*args, **kwargs)

    @property
    def vencida(self):
        return bool(self.fecha_vencimiento and self.estado != self.Estado.HECHA and self.fecha_vencimiento < timezone.localdate())


class Evento(models.Model):
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name="eventos")
    titulo = models.CharField(max_length=160)
    descripcion = models.TextField(blank=True)
    inicia_en = models.DateTimeField()
    termina_en = models.DateTimeField(null=True, blank=True)
    creado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name="eventos_creados")

    class Meta:
        constraints = [
            no_vacio("evento", "titulo"),
            fin_no_antes_que_inicio("evento", "inicia_en", "termina_en"),
        ]
        ordering = ["inicia_en"]

    def clean(self):
        if self.termina_en and self.termina_en < self.inicia_en:
            raise ValidationError({"termina_en": "El fin no puede ser anterior al inicio."})


class DocumentoProyecto(models.Model):
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name="documentos")
    nombre = models.CharField(max_length=160)
    archivo = models.FileField(upload_to="proyectos/%Y/%m/")
    subido_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name="documentos_subidos")
    fecha_subida = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            no_vacio("documento", "nombre"),
            no_vacio("documento", "archivo"),
        ]
        ordering = ["-fecha_subida"]


class Correccion(models.Model):
    """Observación del supervisor; no calcula ni publica una evaluación."""

    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name="correcciones")
    tarea = models.ForeignKey(Tarea, on_delete=models.SET_NULL, null=True, blank=True, related_name="correcciones")
    comentario = models.TextField()
    sugerencia_calificacion = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    autor = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="correcciones_creadas")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.tarea_id and self.proyecto_id and self.tarea.proyecto_id != self.proyecto_id:
            raise ValidationError({"tarea": "La tarea debe ser de este mismo proyecto."})

    class Meta:
        constraints = [
            no_vacio("correccion", "comentario"),
        ]
        ordering = ["-fecha_creacion"]


class Lienzo(models.Model):
    """Pizarra por proyecto. El contenido JSON se guarda compartido en el servidor."""

    proyecto = models.OneToOneField(Proyecto, on_delete=models.CASCADE, related_name="lienzo")
    nombre = models.CharField(max_length=100, default="Canvas del proyecto")
    contenido = models.JSONField(default=dict, blank=True)
    version = models.PositiveIntegerField(default=1)
    actualizado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name="lienzos_actualizados")
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [no_vacio("lienzo", "nombre")]

    def __str__(self):
        return self.nombre


class ChatAsistente(models.Model):
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name="chats_asistente")
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="chats_asistente")
    titulo = models.CharField(max_length=100)
    actualizado = models.DateTimeField(auto_now=True)
    version = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-actualizado", "-pk"]
        indexes = [models.Index(fields=["usuario", "proyecto", "-actualizado"], name="chat_usuario_proyecto_fecha")]


class TurnoAsistente(models.Model):
    chat = models.ForeignKey(ChatAsistente, on_delete=models.CASCADE, related_name="turnos")
    pregunta = models.TextField()
    respuesta = models.TextField()

    class Meta:
        ordering = ["pk"]
