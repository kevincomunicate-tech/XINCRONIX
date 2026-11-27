"""
Filtro {{ texto|markdown_simple }} para mostrar las respuestas del asistente IA.

Primero escapa TODO el HTML (la respuesta viene de fuera y podría traer etiquetas)
y después convierte solo lo básico del Markdown: **negrita**, *cursiva*, `código`,
listas con viñetas o números y títulos con #.
"""

import re

from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()

VINETA = re.compile(r"^[-*•]\s+(.*)")
NUMERO = re.compile(r"^\d+[.)]\s+(.*)")
TITULO = re.compile(r"^#{1,6}\s+(.*)")


def _en_linea(texto):
    texto = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", texto)
    texto = re.sub(r"(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?![*\w])", r"<em>\1</em>", texto)
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", texto)


@register.filter
def markdown_simple(texto):
    partes, lista = [], None
    for linea in escape(texto or "").split("\n"):
        linea = linea.strip()
        vineta, numero, titulo = VINETA.match(linea), NUMERO.match(linea), TITULO.match(linea)
        if vineta or numero:
            tipo = "ul" if vineta else "ol"
            if lista != tipo:
                if lista:
                    partes.append(f"</{lista}>")
                partes.append(f"<{tipo}>")
                lista = tipo
            partes.append(f"<li>{_en_linea((vineta or numero).group(1))}</li>")
            continue
        if lista:
            partes.append(f"</{lista}>")
            lista = None
        if titulo:
            partes.append(f'<p class="ia-titulo">{_en_linea(titulo.group(1))}</p>')
        elif linea:
            partes.append(f"<p>{_en_linea(linea)}</p>")
    if lista:
        partes.append(f"</{lista}>")
    return mark_safe("".join(partes))
