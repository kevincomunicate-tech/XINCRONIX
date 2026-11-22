"""Operaciones de cuentas que tocan varias tablas a la vez."""

from django.db import transaction

from .models import Empresa, Usuario


def empresas_que_se_eliminan(usuario):
    """Empresas de las que es propietario y en las que no hay nadie más."""
    propias = Empresa.objects.filter(propietario=usuario)
    con_otros = Usuario.objects.filter(empresa__in=propias).exclude(pk=usuario.pk).values("empresa")
    return propias.exclude(pk__in=con_otros)


# Textos en primera persona (Mi cuenta) o tercera (administración)
TEXTOS = {
    True: {
        "datos": "Se borran tus datos personales y ya no podrás iniciar sesión con esta cuenta.",
        "sola": "Se elimina tu empresa «{}» con sus proyectos, tareas e ideas (no tiene más integrantes).",
        "compartida": "La empresa «{}» sigue existiendo para sus integrantes, pero quedará sin propietario.",
        "proyectos": "Los proyectos que creaste en empresas que siguen existiendo se conservan para su equipo.",
    },
    False: {
        "datos": "Se borran sus datos personales y ya no podrá iniciar sesión.",
        "sola": "Se elimina su empresa «{}» con sus proyectos, tareas e ideas (no tiene más integrantes).",
        "compartida": "La empresa «{}» sigue existiendo para sus integrantes, pero quedará sin propietario.",
        "proyectos": "Los proyectos que creó en empresas que siguen existiendo se conservan para su equipo.",
    },
}


def consecuencias_de_eliminar_cuenta(usuario, propia=True):
    """Textos para la página de confirmación."""
    textos = TEXTOS[propia]
    solas = list(empresas_que_se_eliminan(usuario))
    compartidas = Empresa.objects.filter(propietario=usuario).exclude(pk__in=[e.pk for e in solas])
    return (
        [textos["datos"]]
        + [textos["sola"].format(e.nombre) for e in solas]
        + [textos["compartida"].format(e.nombre) for e in compartidas]
        + [textos["proyectos"]]
    )


@transaction.atomic  # todo o nada
def eliminar_cuenta(usuario):
    empresas_que_se_eliminan(usuario).delete()
    usuario.delete()
