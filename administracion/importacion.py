"""Carga masiva de usuarios y proyectos desde un archivo CSV.

Reglas:
- Todo o nada: si una sola fila tiene un error, no se guarda ninguna.
- Cada fila se valida con las mismas reglas del sistema (campos obligatorios, formatos,
  opciones válidas, duplicados en la base y en el archivo, y relaciones como el creador de un proyecto).
- Los usuarios importados no reciben contraseña: entran con «Recuperar contraseña».
- Se acepta UTF-8 (con o sin BOM), coma o punto y coma como separador, y máximo 2 MB y 2 000 filas.
"""

import csv
import datetime as dt
import io
from dataclasses import dataclass, field

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction

from cuentas.models import Usuario
from dashboard.models import Proyecto, ProyectoMiembro

MAX_BYTES = 2 * 1024 * 1024
MAX_FILAS = 2000

COLUMNAS = {
    "usuarios": ["email", "nombre", "apellido", "perfil", "cargo", "telefono"],
    "proyectos": ["nombre", "descripcion", "creado_por_email", "finalidad", "metodologia", "modalidad",
                  "visibilidad", "estado", "fecha_inicio", "fecha_fin", "tecnologia", "repositorio_url"],
}
OBLIGATORIAS = {
    "usuarios": ["email", "nombre", "apellido", "perfil"],
    "proyectos": ["nombre", "descripcion", "creado_por_email", "finalidad", "metodologia", "modalidad",
                  "visibilidad", "estado"],
}
PLANTILLA_EJEMPLO = {
    "usuarios": [["ana@ejemplo.com", "Ana", "Ruiz", "estudiante", "", ""]],
    "proyectos": [["App de notas", "Registro de notas de clase", "profesor@ejemplo.com", "educativo", "kanban",
                   "individual", "privado", "planificacion", "2026-03-01", "2026-06-30", "Django", ""]],
}


class ErrorImportacion(Exception):
    pass


@dataclass
class Resultado:
    tipo: str
    total: int = 0
    errores: list = field(default_factory=list)   # (linea, mensaje)
    creados: int = 0

    @property
    def valido(self):
        return not self.errores and self.total > 0


def leer_csv(contenido: bytes, tipo: str):
    """Convierte el archivo en filas (diccionarios). Lanza ErrorImportacion si no sirve."""
    if tipo not in COLUMNAS:
        raise ErrorImportacion("Tipo de carga no válido.")
    if len(contenido) > MAX_BYTES:
        raise ErrorImportacion("El archivo supera el máximo de 2 MB.")
    try:
        texto = contenido.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise ErrorImportacion("El archivo debe estar en UTF-8 (guárdalo como «CSV UTF-8» en Excel).")
    muestra = texto[:2048]
    separador = ";" if muestra.count(";") > muestra.count(",") else ","
    lector = csv.reader(io.StringIO(texto), delimiter=separador)
    try:
        encabezado = [c.strip().lower() for c in next(lector)]
    except StopIteration:
        raise ErrorImportacion("El archivo está vacío.")
    faltan = [c for c in COLUMNAS[tipo] if c not in encabezado]
    if faltan:
        raise ErrorImportacion(f"Faltan columnas: {', '.join(faltan)}. Descarga la plantilla y úsala.")
    filas = []
    for numero, fila in enumerate(lector, start=2):
        if not any(celda.strip() for celda in fila):
            continue  # línea en blanco
        if len(filas) >= MAX_FILAS:
            raise ErrorImportacion(f"El archivo supera el máximo de {MAX_FILAS} filas.")
        datos = {c: (fila[encabezado.index(c)].strip() if encabezado.index(c) < len(fila) else "") for c in encabezado}
        filas.append((numero, datos))
    if not filas:
        raise ErrorImportacion("El archivo no tiene filas para importar.")
    return filas


def _fecha(texto, campo):
    if not texto:
        return None
    try:
        return dt.date.fromisoformat(texto)
    except ValueError:
        raise ValidationError(f"{campo}: «{texto}» no es una fecha válida (usa AAAA-MM-DD).")


def _validar_usuarios(filas, resultado):
    correos_archivo = set()
    existentes = set(Usuario.objects.values_list("email", flat=True))
    validos = []
    for numero, d in filas:
        for campo in OBLIGATORIAS["usuarios"]:
            if not d.get(campo):
                resultado.errores.append((numero, f"«{campo}» es obligatorio."))
        correo = d.get("email", "").lower()
        if correo:
            try:
                validate_email(correo)
            except ValidationError:
                resultado.errores.append((numero, f"«{d['email']}» no es un correo válido."))
            if correo in correos_archivo:
                resultado.errores.append((numero, f"«{correo}» aparece más de una vez en el archivo."))
            if correo in existentes:
                resultado.errores.append((numero, f"«{correo}» ya existe en la plataforma."))
            correos_archivo.add(correo)
        if d.get("perfil") and d["perfil"] not in Usuario.Perfil.values:
            resultado.errores.append((numero, f"Perfil «{d['perfil']}» no existe. Usa: {', '.join(Usuario.Perfil.values)}."))
        validos.append((numero, d))
    return validos


def _validar_proyectos(filas, resultado):
    validos = []
    for numero, d in filas:
        for campo in OBLIGATORIAS["proyectos"]:
            if not d.get(campo):
                resultado.errores.append((numero, f"«{campo}» es obligatorio."))
        creador = Usuario.objects.filter(email__iexact=d.get("creado_por_email", "")).first() if d.get("creado_por_email") else None
        if d.get("creado_por_email") and creador is None:
            resultado.errores.append((numero, f"El creador «{d['creado_por_email']}» no existe en la plataforma."))
        try:
            fi = _fecha(d.get("fecha_inicio", ""), "fecha_inicio")
            ff = _fecha(d.get("fecha_fin", ""), "fecha_fin")
            proyecto = Proyecto(
                nombre=d.get("nombre", ""), descripcion=d.get("descripcion", ""), tecnologia=d.get("tecnologia", ""),
                repositorio_url=d.get("repositorio_url", ""), creado_por=creador,
                finalidad=d.get("finalidad", ""), metodologia=d.get("metodologia", ""), modalidad=d.get("modalidad", ""),
                visibilidad=d.get("visibilidad", ""), estado=d.get("estado", ""), fecha_inicio=fi, fecha_fin=ff,
            )
            if creador is not None:
                proyecto.full_clean()
        except ValidationError as error:
            for mensaje in error.messages:
                resultado.errores.append((numero, mensaje))
            continue
        validos.append((numero, d))
    return validos


def validar(tipo, contenido):
    """Revisa el archivo sin guardar nada. Devuelve un Resultado."""
    filas = leer_csv(contenido, tipo)
    resultado = Resultado(tipo=tipo, total=len(filas))
    if tipo == "usuarios":
        _validar_usuarios(filas, resultado)
    else:
        _validar_proyectos(filas, resultado)
    return resultado


@transaction.atomic
def importar(tipo, contenido):
    """Valida y guarda. Si hay cualquier error, no guarda nada y lo devuelve."""
    resultado = validar(tipo, contenido)
    if resultado.errores:
        return resultado
    filas = leer_csv(contenido, tipo)
    if tipo == "usuarios":
        for _, d in filas:
            Usuario.objects.create_user(
                d["email"].lower(), None,  # sin contraseña: se usa «Recuperar contraseña»
                first_name=d["nombre"], last_name=d["apellido"], perfil=d["perfil"],
                cargo=d.get("cargo", ""), telefono=d.get("telefono", ""),
            )
            resultado.creados += 1
    else:
        for _, d in filas:
            creador = Usuario.objects.get(email__iexact=d["creado_por_email"])
            proyecto = Proyecto(
                nombre=d["nombre"], descripcion=d["descripcion"], tecnologia=d.get("tecnologia", ""),
                repositorio_url=d.get("repositorio_url", ""), creado_por=creador, finalidad=d["finalidad"],
                metodologia=d["metodologia"], modalidad=d["modalidad"], visibilidad=d["visibilidad"], estado=d["estado"],
                fecha_inicio=_fecha(d.get("fecha_inicio", ""), "fecha_inicio"), fecha_fin=_fecha(d.get("fecha_fin", ""), "fecha_fin"),
            )
            proyecto.save()
            ProyectoMiembro.objects.create(proyecto=proyecto, usuario=creador, rol=ProyectoMiembro.Rol.LIDER)
            resultado.creados += 1
    return resultado


def plantilla(tipo):
    """El CSV de ejemplo que se descarga desde la pantalla de carga."""
    salida = io.StringIO()
    escritor = csv.writer(salida)
    escritor.writerow(COLUMNAS[tipo])
    for fila in PLANTILLA_EJEMPLO[tipo]:
        escritor.writerow(fila)
    return ("﻿" + salida.getvalue()).encode("utf-8")
