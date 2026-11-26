"""Reportes del superusuario: consultas con filtros de varios criterios y exportación a Excel y PDF.

Seguridad por diseño:
- Solo se puede consultar lo que está en CATALOGO (tablas, columnas y filtros permitidos).
  Un campo que no esté en la lista no se puede pedir, aunque se manipule la URL.
- Los valores se convierten al tipo del campo antes de consultar; los inválidos se rechazan con mensaje.
- Nunca se incluyen contraseñas, tokens ni claves de sesión.
- Las celdas que empiezan por = + - @ se neutralizan en Excel y en CSV.
"""

import datetime as dt
from dataclasses import dataclass, field
from io import BytesIO
from xml.sax.saxutils import escape

from django.db import models
from django.db.models import Count
from django.utils import timezone

from cuentas.models import Usuario
from dashboard.models import InvitacionProyecto, Proyecto, ProyectoMiembro, Tarea

MAX_FILAS_EXPORTACION = 20000
MAX_CRITERIOS = 4
OPERADORES = {
    "igual": "es igual a",
    "distinto": "es distinto de",
    "contiene": "contiene",
    "mayor_que": "es posterior a (o igual)",
    "menor_que": "es anterior a (o igual)",
    "entre": "está entre",
    "vacio": "está vacío",
    "no_vacio": "no está vacío",
}
PREFIJOS_PELIGROSOS = ("=", "+", "-", "@", "\t", "\r")


@dataclass(frozen=True)
class Columna:
    ruta: str        # ruta de campos, por ejemplo "creado_por__email"
    titulo: str


@dataclass(frozen=True)
class Tabla:
    titulo: str
    modelo: type
    columnas: tuple
    filtros: dict    # ruta -> operadores permitidos
    orden: str
    base: callable = None
    anotaciones: dict = field(default_factory=dict)


CATALOGO = {
    "usuarios": Tabla(
        titulo="Usuarios",
        modelo=Usuario,
        columnas=(Columna("email", "Correo"), Columna("first_name", "Nombres"), Columna("last_name", "Apellidos"),
                  Columna("perfil", "Perfil"), Columna("is_active", "Activa"), Columna("is_superuser", "Superusuario"),
                  Columna("date_joined", "Fecha de registro"), Columna("last_login", "Último inicio de sesión")),
        filtros={"email": ("igual", "distinto", "contiene"), "first_name": ("igual", "contiene"), "last_name": ("contiene",),
                 "perfil": ("igual", "distinto"), "is_active": ("igual",), "is_superuser": ("igual",),
                 "date_joined": ("entre", "mayor_que", "menor_que"), "last_login": ("entre", "vacio", "no_vacio")},
        orden="email",
    ),
    "proyectos": Tabla(
        titulo="Proyectos",
        modelo=Proyecto,
        columnas=(Columna("nombre", "Proyecto"), Columna("creado_por__email", "Creado por"), Columna("estado", "Estado"),
                  Columna("finalidad", "Finalidad"), Columna("metodologia", "Metodología"), Columna("modalidad", "Modalidad"),
                  Columna("visibilidad", "Visibilidad"), Columna("fecha_inicio", "Inicio"), Columna("fecha_fin", "Fin"),
                  Columna("fecha_creacion", "Creado el"), Columna("total_miembros", "Integrantes")),
        filtros={"nombre": ("contiene", "igual"), "creado_por__email": ("contiene", "igual"), "estado": ("igual", "distinto"),
                 "finalidad": ("igual", "distinto"), "metodologia": ("igual", "distinto"), "modalidad": ("igual",),
                 "visibilidad": ("igual",), "fecha_inicio": ("entre", "vacio", "no_vacio"), "fecha_fin": ("entre", "vacio", "no_vacio"),
                 "fecha_creacion": ("entre", "mayor_que", "menor_que")},
        orden="-fecha_creacion",
        anotaciones={"total_miembros": Count("proyectomiembro")},
    ),
    "tareas": Tabla(
        titulo="Tareas",
        modelo=Tarea,
        columnas=(Columna("titulo", "Tarea"), Columna("proyecto__nombre", "Proyecto"), Columna("estado", "Estado"),
                  Columna("prioridad", "Prioridad"), Columna("asignado_a__email", "Responsable"),
                  Columna("fecha_vencimiento", "Vence"), Columna("fecha_creacion", "Creada el"), Columna("fecha_completada", "Completada el")),
        filtros={"titulo": ("contiene", "igual"), "proyecto__nombre": ("contiene", "igual"), "estado": ("igual", "distinto"),
                 "prioridad": ("igual", "distinto"), "asignado_a__email": ("contiene", "igual", "vacio"),
                 "fecha_vencimiento": ("entre", "menor_que", "mayor_que", "vacio", "no_vacio"),
                 "fecha_completada": ("entre", "vacio", "no_vacio"),
                 "fecha_creacion": ("entre", "mayor_que", "menor_que")},
        orden="fecha_vencimiento",
    ),
    "integrantes": Tabla(
        titulo="Integrantes por proyecto",
        modelo=ProyectoMiembro,
        columnas=(Columna("proyecto__nombre", "Proyecto"), Columna("usuario__email", "Integrante"), Columna("rol", "Permiso"),
                  Columna("fecha_ingreso", "Se unió el")),
        filtros={"proyecto__nombre": ("contiene", "igual"), "usuario__email": ("contiene", "igual"), "rol": ("igual", "distinto"),
                 "fecha_ingreso": ("entre", "mayor_que", "menor_que")},
        orden="proyecto__nombre",
    ),
    "invitaciones": Tabla(
        titulo="Invitaciones",
        modelo=InvitacionProyecto,
        columnas=(Columna("proyecto__nombre", "Proyecto"), Columna("email", "Correo invitado"), Columna("rol", "Permiso"),
                  Columna("estado", "Estado"), Columna("fecha_creacion", "Enviada el"), Columna("vence_en", "Vence")),
        filtros={"proyecto__nombre": ("contiene", "igual"), "email": ("contiene", "igual"), "rol": ("igual",),
                 "estado": ("igual", "distinto"), "fecha_creacion": ("entre", "mayor_que", "menor_que")},
        orden="-fecha_creacion",
    ),
}


class ErrorReporte(Exception):
    """Un criterio o una columna no son válidos. El mensaje es para la persona que consulta."""


def _campo_final(modelo, ruta):
    """El campo de modelo al que llega una ruta como 'creado_por__email' (o None si no existe)."""
    actual = modelo
    campo = None
    for parte in ruta.split("__"):
        try:
            campo = actual._meta.get_field(parte)
        except Exception:
            return None
        actual = campo.related_model or actual
    return campo


def _convertir(campo, texto):
    """Convierte el texto de un criterio al tipo del campo. Lanza ErrorReporte si no encaja."""
    if campo is None:
        raise ErrorReporte("Campo no válido.")
    texto = (texto or "").strip()
    if texto == "" and not isinstance(campo, models.BooleanField):
        return None  # sin valor: quien llama decide si eso es válido
    if isinstance(campo, models.BooleanField):
        if texto.lower() in ("sí", "si", "true", "1"):
            return True
        if texto.lower() in ("no", "false", "0"):
            return False
        raise ErrorReporte("Para 'Activa', 'Superusuario' o similares escribe Sí o No.")
    if isinstance(campo, models.DateTimeField):
        try:
            return timezone.make_aware(dt.datetime.fromisoformat(texto))
        except ValueError:
            raise ErrorReporte(f"La fecha «{texto}» no es válida. Usa el formato AAAA-MM-DD.")
    if isinstance(campo, models.DateField):
        try:
            return dt.date.fromisoformat(texto)
        except ValueError:
            raise ErrorReporte(f"La fecha «{texto}» no es válida. Usa el formato AAAA-MM-DD.")
    if campo.choices:
        validos = [v for v, _ in campo.flatchoices]
        if texto not in validos:
            raise ErrorReporte(f"«{texto}» no es una opción válida para este campo.")
        return texto
    return texto


def _q_criterio(tabla, criterio):
    ruta, operador = criterio["campo"], criterio["operador"]
    if ruta not in tabla.filtros:
        raise ErrorReporte("Ese campo no se puede filtrar.")
    if operador not in tabla.filtros[ruta]:
        raise ErrorReporte(f"El operador «{OPERADORES[operador]}» no aplica a ese campo.")
    campo = _campo_final(tabla.modelo, ruta)
    if operador == "vacio":
        return models.Q(**{f"{ruta}__isnull": True}) | models.Q(**{ruta: ""}) if _admite_vacio_texto(campo) else models.Q(**{f"{ruta}__isnull": True})
    if operador == "no_vacio":
        return ~(models.Q(**{f"{ruta}__isnull": True}) | models.Q(**{ruta: ""})) if _admite_vacio_texto(campo) else models.Q(**{f"{ruta}__isnull": False})
    if operador == "contiene":
        if not isinstance(campo, (models.CharField, models.TextField)) and not (campo and campo.is_relation):
            raise ErrorReporte("«Contiene» solo sirve para texto.")
        return models.Q(**{f"{ruta}__icontains": criterio["valor"]})
    if operador == "entre":
        inicio = _convertir(campo, criterio["valor"])
        fin = _convertir(campo, criterio["valor2"])
        if inicio is None or fin is None:
            raise ErrorReporte("«Está entre» necesita dos fechas.")
        if isinstance(campo, (models.DateTimeField, models.DateField)):
            if fin < inicio:
                raise ErrorReporte("En «está entre», la segunda fecha no puede ser anterior a la primera.")
            # Si se escribió solo la fecha, el criterio incluye ese día completo.
            if isinstance(campo, models.DateField) or _solo_fecha(criterio["valor2"]):
                fin = fin + dt.timedelta(days=1)
            return models.Q(**{f"{ruta}__gte": inicio, f"{ruta}__lt": fin})
        raise ErrorReporte("«Está entre» solo sirve para fechas.")
    valor = _convertir(campo, criterio["valor"])
    if valor is None and operador in ("igual", "distinto", "mayor_que", "menor_que"):
        raise ErrorReporte(f"Escribe un valor para «{OPERADORES[operador]}».")
    if operador == "mayor_que":
        return models.Q(**{f"{ruta}__gte": valor})
    if operador == "menor_que":
        # "anterior a o igual": incluye todo el día indicado.
        if isinstance(campo, models.DateTimeField) and _solo_fecha(criterio["valor"]):
            return models.Q(**{f"{ruta}__lt": valor + dt.timedelta(days=1)})
        return models.Q(**{f"{ruta}__lte": valor})
    if operador == "igual":
        return models.Q(**{ruta: valor})
    if operador == "distinto":
        return ~models.Q(**{ruta: valor})
    raise ErrorReporte("Operador no válido.")


def _solo_fecha(texto):
    return len((texto or "").strip()) == 10


def _admite_vacio_texto(campo):
    return isinstance(campo, (models.CharField, models.TextField))


def construir(clave, criterios, logica="y", columnas=None):
    """Arma la consulta. Devuelve (queryset, columnas usadas). Lanza ErrorReporte si algo no es válido."""
    if clave not in CATALOGO:
        raise ErrorReporte("Tabla de reporte no válida.")
    tabla = CATALOGO[clave]
    if logica not in ("y", "o"):
        raise ErrorReporte("La combinación de criterios debe ser «todos» o «alguno».")
    if len(criterios) > MAX_CRITERIOS:
        raise ErrorReporte(f"Puedes usar hasta {MAX_CRITERIOS} criterios.")

    disponibles = {c.ruta: c for c in tabla.columnas}
    elegidas = [disponibles[c] for c in (columnas or []) if c in disponibles] or list(tabla.columnas)

    qs = tabla.modelo._base_manager.all()
    if tabla.anotaciones:
        qs = qs.annotate(**tabla.anotaciones)
    condicion = None
    for criterio in criterios:
        q = _q_criterio(tabla, criterio)
        if condicion is None:
            condicion = q
        else:
            condicion = (condicion & q) if logica == "y" else (condicion | q)
    if condicion is not None:
        qs = qs.filter(condicion)
    return qs.order_by(tabla.orden), elegidas


def filas(clave, criterios, logica="y", columnas=None, limite=None):
    """Devuelve (columnas, filas listas para mostrar, total encontrado)."""
    qs, cols = construir(clave, criterios, logica, columnas)
    tabla = CATALOGO[clave]
    total = qs.count()
    if limite is not None:
        qs = qs[:limite]
    rutas = [c.ruta for c in cols]
    salida = []
    for registro in qs.values(*rutas):
        fila = []
        for c in cols:
            fila.append(_formatear(tabla.modelo, c.ruta, registro.get(c.ruta)))
        salida.append(fila)
    return cols, salida, total


def _formatear(modelo, ruta, valor):
    campo = _campo_final(modelo, ruta)
    if valor is None or valor == "":
        return ""
    if campo is not None and campo.choices:
        return dict(campo.flatchoices).get(valor, valor)
    if isinstance(valor, bool):
        return "Sí" if valor else "No"
    if isinstance(valor, dt.datetime):
        if timezone.is_aware(valor):
            valor = timezone.localtime(valor)
        return valor.replace(tzinfo=None, microsecond=0)  # Excel no admite zona horaria; los segundos bastan
    return valor


def _etiqueta_valor(campo, valor):
    """Muestra la etiqueta legible de una opción ('En progreso') en vez de su código ('en_progreso')."""
    if campo is not None and campo.choices and valor in dict(campo.flatchoices):
        return dict(campo.flatchoices)[valor]
    return valor


def neutralizar(valor):
    """Un texto que empieza por = + - @ se muestra como texto, nunca como fórmula."""
    if isinstance(valor, str) and valor.startswith(PREFIJOS_PELIGROSOS):
        return "'" + valor
    return valor


def descripcion_criterios(clave, criterios, logica):
    tabla = CATALOGO[clave]
    etiquetas = {c.ruta: c.titulo for c in tabla.columnas}
    partes = []
    for c in criterios:
        campo = _campo_final(tabla.modelo, c["campo"])
        texto = f"{etiquetas.get(c['campo'], c['campo'])} {OPERADORES[c['operador']]}"
        if c["operador"] not in ("vacio", "no_vacio"):
            texto += f" {_etiqueta_valor(campo, c['valor'])}"
            if c["operador"] == "entre":
                texto += f" y {_etiqueta_valor(campo, c['valor2'])}"
        partes.append(texto)
    union = " y " if logica == "y" else " o "
    return union.join(partes) if partes else "Sin filtros: todos los registros"


# ---------------------------------------------------------------------------
# Exportación a Excel
# ---------------------------------------------------------------------------

def exportar_excel(clave, criterios, logica, columnas, nombre_generador):
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter

    cols, datos, total = filas(clave, criterios, logica, columnas, limite=MAX_FILAS_EXPORTACION)
    tabla = CATALOGO[clave]
    libro = Workbook()
    hoja = libro.active
    hoja.title = "Reporte"
    azul = PatternFill("solid", fgColor="1F3A5F")
    gris = PatternFill("solid", fgColor="F2F4F7")
    borde = Border(bottom=Side(style="thin", color="C9D1DC"))

    ancho = max(len(cols), 2)
    hoja.merge_cells(start_row=1, start_column=1, end_row=1, end_column=ancho)
    hoja.cell(1, 1, f"Xincronix · Reporte de {tabla.titulo}").font = Font(bold=True, size=14, color="1F3A5F")
    hoja.merge_cells(start_row=2, start_column=1, end_row=2, end_column=ancho)
    hoja.cell(2, 1, f"Generado el {timezone.localtime():%d/%m/%Y %H:%M} por {nombre_generador}").font = Font(italic=True, color="5B6578")
    hoja.merge_cells(start_row=3, start_column=1, end_row=3, end_column=ancho)
    hoja.cell(3, 1, f"Criterios: {descripcion_criterios(clave, criterios, logica)}").alignment = Alignment(wrap_text=True)
    hoja.row_dimensions[3].height = 30
    hoja.merge_cells(start_row=4, start_column=1, end_row=4, end_column=ancho)
    aviso = f"Registros: {total}" + (f" (se exportan los primeros {MAX_FILAS_EXPORTACION})" if total > MAX_FILAS_EXPORTACION else "")
    hoja.cell(4, 1, aviso).font = Font(color="5B6578")

    fila_encabezado = 6
    for indice, columna in enumerate(cols, 1):
        celda = hoja.cell(fila_encabezado, indice, columna.titulo)
        celda.font = Font(bold=True, color="FFFFFF")
        celda.fill = azul
        celda.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    hoja.row_dimensions[fila_encabezado].height = 28

    for numero, fila in enumerate(datos, fila_encabezado + 1):
        for indice, valor in enumerate(fila, 1):
            celda = hoja.cell(numero, indice)
            valor = neutralizar(valor)
            celda.value = valor
            if isinstance(valor, str):
                celda.data_type = "s"  # nunca interpretar texto como fórmula
            if isinstance(valor, dt.datetime):
                celda.number_format = "dd/mm/yyyy hh:mm"
            elif isinstance(valor, dt.date):
                celda.number_format = "dd/mm/yyyy"
            celda.border = borde
            if (numero - fila_encabezado) % 2 == 0:
                celda.fill = gris

    for indice, columna in enumerate(cols, 1):
        longitudes = [len(str(columna.titulo))] + [len(str(f[indice - 1])) for f in datos[:500]]
        hoja.column_dimensions[get_column_letter(indice)].width = min(max(max(longitudes) + 2, 10), 45)

    if datos:
        hoja.auto_filter.ref = f"A{fila_encabezado}:{get_column_letter(len(cols))}{fila_encabezado + len(datos)}"
    hoja.freeze_panes = hoja.cell(fila_encabezado + 1, 1)
    hoja.page_setup.orientation = "landscape"
    hoja.page_setup.fitToWidth = 1
    hoja.page_setup.fitToHeight = 0
    hoja.sheet_properties.pageSetUpPr.fitToPage = True
    hoja.print_title_rows = f"{fila_encabezado}:{fila_encabezado}"

    criterios_hoja = libro.create_sheet("Criterios")
    criterios_hoja.append(["Tabla", tabla.titulo])
    criterios_hoja.append(["Combinación", "Todos los criterios" if logica == "y" else "Alguno de los criterios"])
    criterios_hoja.append(["Resumen", descripcion_criterios(clave, criterios, logica)])
    criterios_hoja.append(["Registros", total])
    criterios_hoja.column_dimensions["A"].width = 16
    criterios_hoja.column_dimensions["B"].width = 90
    for fila in criterios_hoja.iter_rows(min_row=1, max_row=4):
        fila[0].font = Font(bold=True)

    salida = BytesIO()
    libro.save(salida)
    return salida.getvalue()


# ---------------------------------------------------------------------------
# Exportación a PDF
# ---------------------------------------------------------------------------

def exportar_pdf(clave, criterios, logica, columnas, nombre_generador):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    fuente, fuente_negrita = _fuentes_pdf(pdfmetrics, TTFont)
    cols, datos, total = filas(clave, criterios, logica, columnas, limite=MAX_FILAS_EXPORTACION)
    tabla = CATALOGO[clave]
    azul = colors.HexColor("#1F3A5F")
    gris = colors.HexColor("#F2F4F7")

    base = ParagraphStyle("base", parent=getSampleStyleSheet()["Normal"], fontName=fuente, fontSize=8, leading=10)
    cabecera = ParagraphStyle("cab", parent=base, fontName=fuente_negrita, textColor=colors.white)
    titulo = ParagraphStyle("t", parent=base, fontName=fuente_negrita, fontSize=15, leading=19, textColor=azul)
    texto = ParagraphStyle("x", parent=base, fontSize=9, leading=12)

    def p(valor, estilo):
        return Paragraph(escape(str(valor)) if valor != "" else "", estilo)

    historia = [
        Paragraph(escape(f"Xincronix · Reporte de {tabla.titulo}"), titulo),
        Paragraph(escape(f"Generado el {timezone.localtime():%d/%m/%Y %H:%M} por {nombre_generador}"), texto),
        Paragraph(escape(f"Criterios: {descripcion_criterios(clave, criterios, logica)}"), texto),
        Paragraph(escape(f"Registros: {total}" + (f" (se muestran los primeros {MAX_FILAS_EXPORTACION})" if total > MAX_FILAS_EXPORTACION else "")), texto),
        Spacer(1, 10),
    ]

    ancho_util = landscape(A4)[0] - 3 * cm
    anchos = [ancho_util / len(cols)] * len(cols)
    datos_tabla = [[p(c.titulo, cabecera) for c in cols]]
    for fila in datos:
        datos_tabla.append([p(neutralizar(v) if not isinstance(v, (dt.date, dt.datetime)) else _fecha_texto(v), base) for v in fila])
    tabla_pdf = Table(datos_tabla, colWidths=anchos, repeatRows=1)
    estilo = [
        ("BACKGROUND", (0, 0), (-1, 0), azul),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#C9D1DC")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]
    for indice in range(1, len(datos_tabla)):
        if indice % 2 == 0:
            estilo.append(("BACKGROUND", (0, indice), (-1, indice), gris))
    tabla_pdf.setStyle(TableStyle(estilo))
    historia.append(tabla_pdf)

    def pie(lienzo, documento):
        lienzo.saveState()
        lienzo.setFont(fuente, 7.5)
        lienzo.setFillColor(colors.HexColor("#777777"))
        lienzo.drawString(1.5 * cm, 1 * cm, "Xincronix · Reporte confidencial para administración")
        lienzo.drawRightString(landscape(A4)[0] - 1.5 * cm, 1 * cm, f"Página {documento.page}")
        lienzo.restoreState()

    salida = BytesIO()
    doc = SimpleDocTemplate(salida, pagesize=landscape(A4), leftMargin=1.5 * cm, rightMargin=1.5 * cm,
                            topMargin=1.5 * cm, bottomMargin=1.8 * cm, title=f"Reporte de {tabla.titulo}", author="Xincronix")
    doc.build(historia, onFirstPage=pie, onLaterPages=pie)
    return salida.getvalue()


def _fecha_texto(valor):
    if isinstance(valor, dt.datetime):
        return f"{timezone.localtime(valor) if timezone.is_aware(valor) else valor:%d/%m/%Y %H:%M}"
    return f"{valor:%d/%m/%Y}"


def _fuentes_pdf(pdfmetrics, TTFont):
    """DejaVu tiene tildes y ñ; si no está instalada, se usa Helvetica (sin tildes en negrita)."""
    import os
    ruta = "/usr/share/fonts/truetype/dejavu/"
    if os.path.exists(ruta + "DejaVuSans.ttf"):
        pdfmetrics.registerFont(TTFont("XNX", ruta + "DejaVuSans.ttf"))
        pdfmetrics.registerFont(TTFont("XNX-B", ruta + "DejaVuSans-Bold.ttf"))
        return "XNX", "XNX-B"
    return "Helvetica", "Helvetica-Bold"


def puede_ver_reportes(usuario):
    """Solo el cargo más alto (superusuario). El sistema no tiene un rol 'administrador' aparte."""
    return bool(usuario.is_authenticated and usuario.is_active and usuario.is_superuser)
