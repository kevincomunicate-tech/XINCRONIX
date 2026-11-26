"""Restricciones de integridad reutilizables.

Un campo marcado como obligatorio no puede quedar en blanco ni en la base de datos
(además de la validación de formularios): así un dato vacío no entra aunque se salte la web.
"""

from django.db import models
from django.db.models import F, Q


def no_vacio(tabla, campo):
    """La columna no puede guardar un texto vacío."""
    return models.CheckConstraint(condition=~Q(**{campo: ""}), name=f"ck_{tabla}_{campo}_no_vacio")


def fin_no_antes_que_inicio(tabla, inicio, fin):
    """Si hay fin, no puede ser anterior al inicio."""
    return models.CheckConstraint(
        condition=Q(**{f"{fin}__isnull": True}) | Q(**{f"{fin}__gte": F(inicio)}),
        name=f"ck_{tabla}_{fin}_no_antes",
    )


def distinto_de(tabla, campo, otro):
    """Dos relaciones no pueden apuntar a la misma persona (p. ej. remitente y destinatario)."""
    return models.CheckConstraint(condition=~Q(**{campo: F(otro)}), name=f"ck_{tabla}_{campo}_distinto_{otro}")


def agregar_restricciones(src, clase, nuevas):
    """Inserta 'constraints = [...]' en el Meta de la clase indicada, junto a las que ya tenga."""
    import re
    inicio = src.index(f"class {clase}(")
    siguiente = re.search(r"\n(class |$)", src[inicio + 1:])
    fin = inicio + 1 + siguiente.start() if siguiente else len(src)
    bloque = src[inicio:fin]
    if "constraints = [" in bloque:
        return src  # ya tiene restricciones: no se toca para evitar duplicados
    marca = "    class Meta:\n"
    assert bloque.count(marca) == 1, clase
    extra = "        constraints = [\n" + "".join(f"            {c},\n" for c in nuevas) + "        ]\n"
    nuevo = bloque.replace(marca, marca + extra, 1)
    return src[:inicio] + nuevo + src[fin:]
