"""Auditoría de integridad: revisa los datos guardados contra las reglas del sistema.

Revisa dos cosas:
1. Campos obligatorios: ningún campo importante vacío (texto en blanco o relación faltante).
2. Relaciones entre tablas: cada referencia existe y cumple la regla de negocio
   (p. ej., el responsable de una tarea debe ser integrante del proyecto).

Se usa así:  python manage.py auditar_datos
"""

from django.db import connection
from django.db.models import Exists, F, OuterRef, Q

from comunicacion.models import ConversacionIA, EventoCalendario, Mensaje, MensajeIA, Reunion, TicketSoporte
from cuentas.models import Usuario
from dashboard.models import Correccion, DocumentoProyecto, Evento, InvitacionProyecto, Lienzo, Proyecto, ProyectoMiembro, Tarea

# Campos que no pueden quedar vacíos, por modelo.
OBLIGATORIOS = {
    Usuario: ["email", "first_name", "last_name", "perfil"],
    Proyecto: ["nombre", "descripcion", "estado", "finalidad", "metodologia", "modalidad", "visibilidad", "creado_por"],
    ProyectoMiembro: ["proyecto", "usuario", "rol"],
    InvitacionProyecto: ["proyecto", "email", "rol", "estado", "creado_por", "vence_en"],
    Tarea: ["proyecto", "titulo", "estado", "prioridad"],
    Evento: ["proyecto", "titulo", "inicia_en"],
    DocumentoProyecto: ["proyecto", "nombre", "archivo"],
    Correccion: ["proyecto", "comentario", "autor"],
    Lienzo: ["proyecto", "nombre"],
    Mensaje: ["contenido", "remitente", "destinatario"],
    Reunion: ["nombre", "fecha"],
    EventoCalendario: ["fecha_evento", "usuario"],
    ConversacionIA: ["titulo", "usuario"],
    MensajeIA: ["conversacion", "rol", "contenido"],
    TicketSoporte: ["asunto", "descripcion", "prioridad", "estado"],
}


def _vacio(modelo, nombre):
    """Filas donde el campo está vacío (texto en blanco, o relación/fecha que falta)."""
    campo = modelo._meta.get_field(nombre)
    if campo.is_relation:
        return modelo._base_manager.filter(**{f"{nombre}__isnull": True})
    if campo.get_internal_type() in ("CharField", "TextField", "EmailField", "URLField", "FileField", "SlugField"):
        return modelo._base_manager.filter(Q(**{nombre: ""}) | Q(**{f"{nombre}__regex": r"^\s*$"}))
    return modelo._base_manager.filter(**{f"{nombre}__isnull": True})


def problemas():
    """Lista de problemas encontrados. Lista vacía = los datos cumplen las reglas."""
    hallazgos = []

    # 1) Campos obligatorios vacíos
    for modelo, campos in OBLIGATORIOS.items():
        for nombre in campos:
            for fila in _vacio(modelo, nombre).only("pk")[:50]:
                hallazgos.append(f"{modelo.__name__} #{fila.pk}: el campo «{nombre}» está vacío.")

    # 2) Relaciones: referencias rotas (la base lo sabe) y reglas de negocio
    try:
        connection.check_constraints()
    except Exception as error:  # SQLite/MariaDB devuelven la lista de referencias rotas
        hallazgos.append(f"Referencias rotas entre tablas: {error}")

    es_miembro = ProyectoMiembro.objects.filter(proyecto_id=OuterRef("proyecto_id"), usuario_id=OuterRef("asignado_a_id"))
    for t in Tarea.objects.filter(asignado_a__isnull=False).annotate(miembro=Exists(es_miembro)).filter(miembro=False):
        hallazgos.append(f"Tarea #{t.pk} «{t.titulo}»: el responsable no es integrante del proyecto.")

    for c in Correccion.objects.filter(tarea__isnull=False).exclude(tarea__proyecto_id=F("proyecto_id")):
        hallazgos.append(f"Corrección #{c.pk}: apunta a una tarea de otro proyecto.")

    lider = ProyectoMiembro.objects.filter(proyecto_id=OuterRef("pk"), usuario_id=OuterRef("creado_por_id"), rol=ProyectoMiembro.Rol.LIDER)
    for p in Proyecto.objects.annotate(es_lider=Exists(lider)).filter(es_lider=False):
        hallazgos.append(f"Proyecto #{p.pk} «{p.nombre}»: su creador no aparece como líder del equipo.")

    for p in Proyecto.objects.filter(supervisor__isnull=False).exclude(supervisor__rol=Usuario.Rol.SUPERVISOR, supervisor__is_active=True):
        hallazgos.append(f"Proyecto #{p.pk} «{p.nombre}»: la cuenta asignada no tiene un rol de supervisor activo.")

    integrante = ProyectoMiembro.objects.filter(proyecto_id=OuterRef("proyecto_id"), usuario__email__iexact=OuterRef("email"))
    for i in InvitacionProyecto.objects.filter(estado=InvitacionProyecto.Estado.ACEPTADA).annotate(ok=Exists(integrante)).filter(ok=False):
        hallazgos.append(f"Invitación #{i.pk}: aceptada, pero la persona no está en el proyecto.")

    for p in Proyecto.objects.filter(modalidad=Proyecto.Modalidad.INDIVIDUAL):
        if ProyectoMiembro.objects.filter(proyecto=p).exclude(usuario_id=p.creado_por_id).exists():
            hallazgos.append(f"Proyecto #{p.pk} «{p.nombre}»: es individual pero tiene integrantes adicionales.")

    return hallazgos
