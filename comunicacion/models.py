"""
Comunicación: chat, reuniones, calendario, asistente de IA y soporte.

Son tablas de la base original que todavía no tienen pantalla en la
aplicación, corregidas y normalizadas.
"""

from django.conf import settings
from django.db import models
from django.db.models import Q

from cuentas.models import Empresa, Equipo

Usuario = settings.AUTH_USER_MODEL


class Mensaje(models.Model):
    """Chat: un mensaje va a UNA persona o a UN equipo, nunca a ambos.

    La base original tenía 'estado' y 'leido' para lo mismo: queda 'leido'.
    """

    id = models.BigAutoField(primary_key=True, db_column="id_mensajes")
    contenido = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)
    remitente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="mensajes_enviados", db_column="id_usuario")
    destinatario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, related_name="mensajes_recibidos",
        db_column="id_destinatario", null=True, blank=True,
    )
    equipo = models.ForeignKey(
        Equipo, on_delete=models.CASCADE, related_name="mensajes",
        db_column="id_equipo", null=True, blank=True,
    )

    class Meta:
        db_table = "mensajes"
        verbose_name = "mensaje"
        verbose_name_plural = "mensajes"
        ordering = ["fecha_envio"]
        constraints = [
            # Exactamente uno de los dos: destinatario o equipo
            models.CheckConstraint(
                condition=(Q(destinatario__isnull=False) & Q(equipo__isnull=True))
                | (Q(destinatario__isnull=True) & Q(equipo__isnull=False)),
                name="ck_mensaje_un_destino",
                violation_error_message="El mensaje debe ir a una persona o a un equipo.",
            ),
        ]
        indexes = [
            models.Index(fields=["remitente", "destinatario", "fecha_envio"], name="idx_mensajes_conversacion"),
        ]

    def __str__(self):
        return self.contenido[:50]


class Reunion(models.Model):
    """La columna 'fecha' original tenía ON UPDATE current_timestamp():
    al editar la reunión, ¡su fecha cambiaba a "ahora"! Aquí ya no."""

    class Estado(models.TextChoices):
        PROGRAMADA = "programada", "Programada"
        EN_CURSO = "en_curso", "En curso"
        FINALIZADA = "finalizada", "Finalizada"
        CANCELADA = "cancelada", "Cancelada"

    id = models.BigAutoField(primary_key=True, db_column="id_reunion")
    nombre = models.CharField(max_length=150)
    enlace = models.URLField(max_length=300, blank=True)
    fecha = models.DateTimeField()
    estado = models.CharField(max_length=12, choices=Estado.choices, default=Estado.PROGRAMADA)
    grabacion_url = models.URLField("grabación", max_length=500, blank=True)
    equipo = models.ForeignKey(
        Equipo, on_delete=models.SET_NULL, related_name="reuniones",
        db_column="id_equipo", null=True, blank=True,
    )
    organizador = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, related_name="reuniones_organizadas",
        db_column="id_usuario", null=True, blank=True,
    )

    class Meta:
        db_table = "reuniones"
        verbose_name = "reunión"
        verbose_name_plural = "reuniones"
        ordering = ["fecha"]

    def __str__(self):
        return self.nombre


class EventoCalendario(models.Model):
    """Nota personal en el calendario (mismo arreglo de la fecha que Reunion)."""

    id = models.BigAutoField(primary_key=True, db_column="id_calendario")
    fecha_evento = models.DateTimeField()
    nota = models.TextField(blank=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="eventos", db_column="id_usuario")

    class Meta:
        db_table = "calendario"
        verbose_name = "evento del calendario"
        verbose_name_plural = "calendario"
        ordering = ["fecha_evento"]

    def __str__(self):
        return f"{self.fecha_evento:%Y-%m-%d} — {self.nota[:40]}"


class ConversacionIA(models.Model):
    """Chat con el asistente virtual.

    Sin id_empresa (la base original lo tenía): la empresa se obtiene del
    usuario. Guardarla dos veces viola la 3FN y puede contradecirse.
    """

    id = models.BigAutoField(primary_key=True, db_column="id_conversacion")
    titulo = models.CharField("título", max_length=200, default="Nueva conversación")
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_ultima = models.DateTimeField("último mensaje", auto_now=True)
    activa = models.BooleanField(default=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="conversaciones_ia", db_column="id_usuario")

    class Meta:
        db_table = "ia_conversaciones"
        verbose_name = "conversación con IA"
        verbose_name_plural = "conversaciones con IA"
        ordering = ["-fecha_ultima"]

    def __str__(self):
        return self.titulo


class MensajeIA(models.Model):
    class Rol(models.TextChoices):
        USUARIO = "user", "Usuario"
        ASISTENTE = "assistant", "Asistente"

    id = models.BigAutoField(primary_key=True, db_column="id_ia_mensaje")
    conversacion = models.ForeignKey(ConversacionIA, on_delete=models.CASCADE, related_name="mensajes", db_column="id_conversacion")
    rol = models.CharField(max_length=10, choices=Rol.choices, default=Rol.USUARIO)
    contenido = models.TextField()
    tokens_usados = models.PositiveIntegerField(null=True, blank=True)
    modelo = models.CharField(max_length=60, blank=True)
    fecha_envio = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ia_mensajes"
        verbose_name = "mensaje de IA"
        verbose_name_plural = "mensajes de IA"
        ordering = ["fecha_envio"]


class TicketSoporte(models.Model):
    class Prioridad(models.TextChoices):
        BAJA = "baja", "Baja"
        MEDIA = "media", "Media"
        ALTA = "alta", "Alta"

    class Estado(models.TextChoices):
        ABIERTO = "abierto", "Abierto"
        EN_PROCESO = "en_proceso", "En proceso"
        CERRADO = "cerrado", "Cerrado"

    id = models.BigAutoField(primary_key=True, db_column="id_ticket")
    asunto = models.CharField(max_length=200)
    descripcion = models.TextField("descripción", blank=True)
    prioridad = models.CharField(max_length=10, choices=Prioridad.choices, default=Prioridad.MEDIA)
    estado = models.CharField(max_length=12, choices=Estado.choices, default=Estado.ABIERTO)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)
    empresa = models.ForeignKey(
        Empresa, on_delete=models.SET_NULL, related_name="tickets",
        db_column="id_empresa", null=True, blank=True,
    )
    creado_por = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, related_name="tickets",
        db_column="id_usuario", null=True, blank=True,
    )

    class Meta:
        db_table = "tickets_soporte"
        verbose_name = "ticket de soporte"
        verbose_name_plural = "tickets de soporte"
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return self.asunto
