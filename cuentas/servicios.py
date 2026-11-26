"""Operaciones de cuenta con sus reglas de seguridad.

Regla central: después de cualquier operación debe quedar al menos un
superusuario ACTIVO. Esta función es la única fuente de esa regla; las
vistas y las señales (cuentas/signals.py) la usan.
"""

from django.db import transaction

from .models import Usuario


def bloquear_superusuarios():
    """Bloquea las filas de los superusuarios activos hasta terminar la transacción.

    Así dos operaciones simultáneas no pueden leer "quedan dos" y borrar cada una a una
    dejando cero. En SQLite el bloqueo lo hace la base completa.
    """
    list(Usuario.objects.select_for_update().filter(is_superuser=True, is_active=True).values_list("pk", flat=True))


def otros_superusuarios_activos(pk_excluido):
    return Usuario.objects.filter(is_superuser=True, is_active=True).exclude(pk=pk_excluido)


def quitaria_el_ultimo_superusuario(usuario):
    """¿Borrar o desactivar a este usuario dejaría cero superusuarios activos?"""
    return usuario.is_superuser and usuario.is_active and not otros_superusuarios_activos(usuario.pk).exists()


def consecuencias_de_eliminar_cuenta(usuario, propia=True):
    sujeto = "tus" if propia else "sus"
    return [
        f"Se borrarán {sujeto} datos personales y no se podrá iniciar sesión con esta cuenta.",
        "Los proyectos creados por esta cuenta se eliminarán junto con sus tareas, documentos, eventos y canvas.",
        "Las invitaciones y participaciones en otros proyectos dejarán de estar disponibles.",
    ]


@transaction.atomic
def eliminar_cuenta(usuario):
    # El borrado pasa por UsuarioQuerySet.delete(), que aplica la regla del último superusuario.
    Usuario.objects.filter(pk=usuario.pk).delete()
