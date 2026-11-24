"""
Monitoreo de la base de datos para el superadministrador.

Igual que la política de roles, las REGLAS viven en un JSON
(config/monitoreo.json, settings.MONITOREO). Este módulo solo lo lee, lo
valida y calcula lo que se muestra:

    monitoreo = obtener_monitoreo()
    catalogo()                      -> todas las tablas con su número de filas
    tablas_sin_modelo()             -> tablas de la base que ningún modelo usa
    info_sistema()                  -> motor, versión, tamaño, Django, Python...
    monitoreo.tarjetas()            -> tarjetas del resumen (del JSON)
    monitoreo.alertas()             -> alertas con su conteo (del JSON)
    monitoreo.distribuciones()      -> "usuarios por rol", "tareas por estado"...
    monitoreo.graficas()            -> registros por día de los últimos N días
    monitoreo.recientes()           -> últimos registros, inicios de sesión...
    monitoreo.filas(modelo, ...)    -> filas de una tabla, con campos sensibles ocultos
    sesiones_activas() / migraciones() / revisiones()

Todo es de SOLO LECTURA: este módulo no edita ningún registro (las únicas
escrituras son cerrar sesiones, en views_monitoreo.py).

Si una tabla no existe en la base (por ejemplo, falta correr migrate), la
consulta no rompe la página: esa tabla aparece marcada como "falta la tabla".
"""

import hashlib
import json
import platform
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from functools import lru_cache
from pathlib import Path

import django
from django.apps import apps
from django.conf import settings
from django.core import checks as django_checks
from django.core.exceptions import FieldDoesNotExist, FieldError, ValidationError
from django.db import DatabaseError, connection, models, transaction
from django.db.migrations.loader import MigrationLoader
from django.db.migrations.recorder import MigrationRecorder
from django.db.models import Count, Q
from django.urls import reverse
from django.utils import timezone
from django.utils.formats import date_format

OCULTO = "••••••"
NIVELES = {"danger", "warning", "info", "secondary", "success", "primary"}
CLAVES_OBLIGATORIAS = (
    "filas_por_pagina", "dias_grafica", "actividad_reciente", "campos_ocultos", "tablas_solo_conteo",
    "grupos", "tarjetas", "alertas", "distribuciones", "graficas", "recientes",
)

# Valores especiales que se pueden escribir en los filtros del JSON.
VALORES_ESPECIALES = {
    "@hoy": timezone.localdate,
    "@ahora": timezone.now,
}

# Consultas que dependen del motor de base de datos (connection.vendor).
SQL_VERSION = {
    "sqlite": "SELECT sqlite_version()",
    "mysql": "SELECT VERSION()",
    "postgresql": "SHOW server_version",
}
SQL_TAMANO = {
    "sqlite": "SELECT page_count * page_size FROM pragma_page_count(), pragma_page_size()",
    "mysql": "SELECT COALESCE(SUM(data_length + index_length), 0) FROM information_schema.TABLES WHERE table_schema = DATABASE()",
    "postgresql": "SELECT pg_database_size(current_database())",
}
NOMBRE_MOTOR = {"sqlite": "SQLite", "mysql": "MySQL / MariaDB", "postgresql": "PostgreSQL"}

# Campos de texto donde busca el buscador de cada tabla.
CAMPOS_BUSCABLES = (models.CharField, models.TextField)


class MonitoreoInvalido(Exception):
    """El JSON del monitoreo tiene errores. Trae la lista de problemas."""

    def __init__(self, errores):
        self.errores = errores
        super().__init__("Configuración de monitoreo inválida:\n- " + "\n- ".join(errores))


# ---------------------------------------------------------------------------
# Ayudantes
# ---------------------------------------------------------------------------

def consultar(funcion, por_defecto=None):
    """Ejecuta una consulta; si la tabla no existe (u otro error de la base) devuelve por_defecto.

    El savepoint (transaction.atomic) evita que un error deje la conexión
    inservible en PostgreSQL.
    """
    try:
        with transaction.atomic():
            return funcion()
    except DatabaseError:
        return por_defecto


def resolver(filtro):
    """Cambia "@hoy" / "@ahora" del JSON por la fecha real."""
    return {
        campo: VALORES_ESPECIALES[valor]() if isinstance(valor, str) and valor in VALORES_ESPECIALES else valor
        for campo, valor in (filtro or {}).items()
    }


def obtener_modelo(etiqueta):
    """'cuentas.usuario' -> clase Usuario. Lanza LookupError si no existe."""
    return apps.get_model(etiqueta)


def etiqueta_de(modelo):
    return modelo._meta.label_lower


def url_tabla(modelo):
    return reverse("administracion:monitoreo_tabla", args=[modelo._meta.app_label, modelo._meta.model_name])


def url_registro(modelo, pk):
    return reverse("administracion:monitoreo_registro", args=[modelo._meta.app_label, modelo._meta.model_name, pk])


def campo_final(modelo, ruta):
    """El campo al que llega una ruta como 'rol__nombre' (para mostrar sus opciones)."""
    campo = None
    for parte in ruta.split("__"):
        campo = modelo._meta.get_field(parte)
        modelo = campo.related_model or modelo
    return campo


def formatear(valor):
    """Un valor de la base, listo para mostrarlo en una tabla."""
    formatos = (
        (bool, lambda v: "Sí" if v else "No"),
        (datetime, lambda v: date_format(timezone.localtime(v) if timezone.is_aware(v) else v, "SHORT_DATETIME_FORMAT")),
        (date, lambda v: date_format(v, "SHORT_DATE_FORMAT")),
    )
    if valor is None or valor == "":
        return "—"
    return next((f(valor) for tipo, f in formatos if isinstance(valor, tipo)), str(valor))


def tamano_legible(numero):
    if numero is None:
        return "—"
    unidades = ["B", "KB", "MB", "GB", "TB"]
    indice = 0
    while numero >= 1024 and indice < len(unidades) - 1:
        numero /= 1024
        indice += 1
    return f"{numero:.1f} {unidades[indice]}" if indice else f"{int(numero)} B"


def huella(clave_sesion):
    """Identificador corto de una sesión que NO revela su clave (la clave es la cookie)."""
    return hashlib.sha256(clave_sesion.encode()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Validación del JSON
# ---------------------------------------------------------------------------

def validar(datos):
    """Devuelve la lista de errores del JSON (vacía si está bien)."""
    faltan = [clave for clave in CLAVES_OBLIGATORIAS if clave not in datos]
    if faltan:
        return [f"Falta la clave obligatoria '{clave}' en monitoreo.json." for clave in faltan]

    errores = [
        f"'{clave}' debe ser un número entero mayor que 0."
        for clave in ("filas_por_pagina", "dias_grafica", "actividad_reciente")
        if not (isinstance(datos[clave], int) and datos[clave] > 0)
    ]
    errores += [
        f"'tablas_solo_conteo' tiene '{etiqueta}': {error}"
        for etiqueta in datos["tablas_solo_conteo"].get("modelos", [])
        for error in _errores_modelo(etiqueta)
    ]
    for seccion in ("tarjetas", "alertas", "distribuciones", "graficas", "recientes"):
        for numero, item in enumerate(datos[seccion], start=1):
            errores += [f"'{seccion}' #{numero} ({item.get('texto', 'sin texto')}): {e}" for e in _errores_item(seccion, item)]
    return errores


def _errores_modelo(etiqueta):
    try:
        obtener_modelo(etiqueta)
    except (LookupError, ValueError):
        return [f"el modelo '{etiqueta}' no existe (usa app.modelo, ej. 'cuentas.usuario')."]
    return []


def _errores_item(seccion, item):
    if not item.get("texto"):
        return ["necesita 'texto'."]
    errores = _errores_modelo(item.get("modelo", ""))
    if errores:
        return errores
    modelo = obtener_modelo(item["modelo"])

    # Filtros: se arma la consulta (sin ejecutarla) para saber si los campos existen.
    filtros = [item.get("filtro"), item.get("excluir"), (item.get("detalle") or {}).get("filtro")]
    for filtro in filtros:
        try:
            modelo._base_manager.filter(**resolver(filtro))
        except (FieldError, ValueError, TypeError, ValidationError) as error:
            errores.append(f"el filtro {filtro} no es válido: {error}")

    if seccion == "alertas" and item.get("nivel") not in NIVELES:
        errores.append(f"'nivel' debe ser uno de: {', '.join(sorted(NIVELES))}.")
    if seccion == "distribuciones":
        try:
            modelo._base_manager.values(item.get("campo", ""))
        except FieldError as error:
            errores.append(f"el campo '{item.get('campo')}' no existe: {error}")
    if seccion in ("graficas", "recientes"):
        try:
            campo = modelo._meta.get_field(item.get("campo_fecha", ""))
        except FieldDoesNotExist:
            return errores + [f"el campo_fecha '{item.get('campo_fecha')}' no existe."]
        if not isinstance(campo, models.DateField):
            errores.append(f"el campo_fecha '{campo.name}' debe ser una fecha.")
    return errores


# ---------------------------------------------------------------------------
# La configuración ya leída
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Monitoreo:
    filas_por_pagina: int
    dias_grafica: int
    actividad_reciente: int
    campos_ocultos_nombres: frozenset
    campos_ocultos_contienen: tuple
    solo_conteo: frozenset
    grupos: dict
    config_tarjetas: tuple
    config_alertas: tuple
    config_distribuciones: tuple
    config_graficas: tuple
    config_recientes: tuple

    # --- Reglas de privacidad ---

    def es_oculto(self, campo):
        """¿El valor de este campo se oculta? (contraseñas, tokens, claves de sesión...)"""
        nombres = {campo.name, getattr(campo, "attname", campo.name)}
        return bool(nombres & self.campos_ocultos_nombres) or any(
            texto in nombre for nombre in nombres for texto in self.campos_ocultos_contienen
        )

    def puede_abrir(self, modelo):
        """¿Se puede ver fila por fila? (las de 'tablas_solo_conteo' solo se cuentan)"""
        return etiqueta_de(modelo) not in self.solo_conteo

    def grupo_de(self, modelo):
        app = modelo._meta.app_config
        return self.grupos.get(app.label, str(app.verbose_name))

    # --- Resumen ---

    def tarjetas(self):
        return [self._tarjeta(item) for item in self.config_tarjetas]

    def _tarjeta(self, item):
        modelo = obtener_modelo(item["modelo"])
        detalle = item.get("detalle") or {}
        return {
            "texto": item["texto"],
            "icono": item.get("icono", "bi-table"),
            "total": consultar(lambda: modelo._base_manager.count()),
            "detalle_texto": detalle.get("texto", ""),
            "detalle_total": consultar(lambda: modelo._base_manager.filter(**resolver(detalle.get("filtro"))).count()) if detalle else None,
            "url": url_tabla(modelo) if self.puede_abrir(modelo) else "",
        }

    def alertas(self):
        """Cada alerta del JSON con su conteo. Las que dan 0 se marcan como 'en_orden'."""
        resultado = []
        for item in self.config_alertas:
            modelo = obtener_modelo(item["modelo"])
            consulta = modelo._base_manager.filter(**resolver(item.get("filtro"))).exclude(**resolver(item.get("excluir")))
            total = consultar(lambda: consulta.distinct().count())
            resultado.append({
                "texto": item["texto"],
                "nivel": item["nivel"],
                "total": total,
                "en_orden": total == 0,
                "falta_tabla": total is None,
                "url": url_tabla(modelo) if self.puede_abrir(modelo) else "",
            })
        return resultado

    def distribuciones(self):
        return [self._distribucion(item) for item in self.config_distribuciones]

    def _distribucion(self, item):
        modelo = obtener_modelo(item["modelo"])
        campo = campo_final(modelo, item["campo"])
        nombres = dict(campo.flatchoices) if campo.choices else {}
        filas = consultar(
            lambda: list(modelo._base_manager.values(item["campo"]).annotate(total=Count("pk")).order_by("-total")),
            por_defecto=[],
        )
        maximo = max((f["total"] for f in filas), default=0)
        return {
            "texto": item["texto"],
            "barras": [
                {
                    "nombre": nombres.get(f[item["campo"]], f[item["campo"]]) or "(vacío)",
                    "total": f["total"],
                    "ancho": round(f["total"] * 100 / maximo) if maximo else 0,
                }
                for f in filas
            ],
        }

    def graficas(self):
        """Conteo por día de los últimos N días (se agrupa en Python: funciona igual en todos los motores)."""
        hoy = timezone.localdate()
        dias = [hoy - timedelta(days=n) for n in range(self.dias_grafica - 1, -1, -1)]
        return [self._grafica(item, dias) for item in self.config_graficas]

    def _grafica(self, item, dias):
        modelo = obtener_modelo(item["modelo"])
        campo = item["campo_fecha"]
        inicio = timezone.make_aware(datetime.combine(dias[0], datetime.min.time()))
        valores = consultar(
            lambda: list(modelo._base_manager.filter(**{f"{campo}__gte": inicio}).values_list(campo, flat=True)),
            por_defecto=[],
        )
        por_dia = contar_por_dia(valores)
        maximo = max([por_dia.get(d, 0) for d in dias] + [1])
        return {
            "texto": item["texto"],
            "total": sum(por_dia.get(d, 0) for d in dias),
            "barras": [
                {"dia": d, "total": por_dia.get(d, 0), "alto": round(por_dia.get(d, 0) * 100 / maximo)}
                for d in dias
            ],
        }

    def recientes(self):
        return [self._recientes(item) for item in self.config_recientes]

    def _recientes(self, item):
        modelo = obtener_modelo(item["modelo"])
        campo = item["campo_fecha"]
        objetos = consultar(
            lambda: list(modelo._base_manager.exclude(**{f"{campo}__isnull": True}).order_by(f"-{campo}")[: self.actividad_reciente]),
            por_defecto=[],
        )
        abrir = self.puede_abrir(modelo)
        return {
            "texto": item["texto"],
            "icono": item.get("icono", "bi-clock-history"),
            "filas": [
                {"texto": str(o), "fecha": getattr(o, campo), "url": url_registro(modelo, o.pk) if abrir else ""}
                for o in objetos
            ],
        }

    # --- Tablas ---

    def valor(self, objeto, campo, completo=False):
        """El valor de un campo para mostrarlo: oculto, con su texto de opción o con enlace a su tabla."""
        if self.es_oculto(campo):
            return {"texto": OCULTO, "url": "", "oculto": True}
        if campo.is_relation:
            relacionado = getattr(objeto, campo.name)
            modelo = campo.related_model
            url = url_registro(modelo, relacionado.pk) if relacionado is not None and self.puede_abrir(modelo) else ""
            return {"texto": formatear(relacionado), "url": url, "oculto": False}
        valor = getattr(objeto, f"get_{campo.name}_display")() if campo.choices else getattr(objeto, campo.attname)
        texto = formatear(valor)
        return {"texto": texto if completo or len(texto) <= 60 else texto[:57] + "…", "url": "", "oculto": False}

    def filas(self, modelo, busqueda="", filtro_campo="", filtro_valor=""):
        """Consulta de una tabla con buscador y filtro por un campo (ej. ver las tareas de un proyecto)."""
        relaciones = [c.name for c in modelo._meta.concrete_fields if c.is_relation]
        consulta = modelo._base_manager.select_related(*relaciones).order_by("-pk")

        buscables = [c.name for c in modelo._meta.concrete_fields if isinstance(c, CAMPOS_BUSCABLES) and not self.es_oculto(c)]
        if busqueda:
            condicion = Q()
            for nombre in buscables:
                condicion |= Q(**{f"{nombre}__icontains": busqueda})
            if busqueda.isdigit():
                condicion |= Q(pk=busqueda)
            consulta = consulta.filter(condicion)

        campos_filtrables = {c.name: c for c in modelo._meta.concrete_fields if not self.es_oculto(c)}
        if filtro_campo in campos_filtrables:
            campo = campos_filtrables[filtro_campo]
            try:
                consulta = consulta.filter(**{campo.attname: campo.to_python(filtro_valor)})
            except ValidationError:
                consulta = consulta.none()
        return consulta, buscables

    def estructura(self, modelo):
        """Columnas de la tabla tal como están en la base."""
        filas = []
        for campo in modelo._meta.concrete_fields:
            filas.append({
                "nombre": campo.name,
                "columna": campo.column,
                "tipo": campo.get_internal_type(),
                "tipo_bd": campo.db_type(connection) or "—",
                "nulo": campo.null,
                "unico": campo.unique,
                "pk": campo.primary_key,
                "relacion": etiqueta_de(campo.related_model) if campo.is_relation else "",
                "oculto": self.es_oculto(campo),
            })
        return filas

    def relaciones_inversas(self, objeto):
        """Cuántos registros de otras tablas apuntan a este (con enlace a esas filas)."""
        resultado = []
        for relacion in objeto._meta.related_objects:
            if relacion.many_to_many or not relacion.field.concrete:
                continue
            modelo = relacion.related_model
            total = consultar(lambda: modelo._base_manager.filter(**{relacion.field.name: objeto.pk}).count())
            url = ""
            if self.puede_abrir(modelo) and total:
                url = f"{url_tabla(modelo)}?campo={relacion.field.name}&valor={objeto.pk}"
            resultado.append({
                "tabla": str(modelo._meta.verbose_name_plural),
                "campo": relacion.field.name,
                "total": total,
                "url": url,
            })
        return resultado


def contar_por_dia(valores):
    """{fecha: cuántos} a partir de fechas o de fechas con hora (estas se pasan a la hora local)."""
    conteo = {}
    for valor in valores:
        dia = timezone.localtime(valor).date() if isinstance(valor, datetime) else valor
        conteo[dia] = conteo.get(dia, 0) + 1
    return conteo


def leer_monitoreo(ruta):
    """Lee y valida el JSON. Lanza MonitoreoInvalido si tiene errores."""
    try:
        datos = json.loads(Path(ruta).read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise MonitoreoInvalido([f"No existe el archivo {ruta}."])
    except json.JSONDecodeError as error:
        raise MonitoreoInvalido([f"{Path(ruta).name} no es un JSON válido: {error}"])

    errores = validar(datos)
    if errores:
        raise MonitoreoInvalido(errores)

    ocultos = datos["campos_ocultos"]
    return Monitoreo(
        filas_por_pagina=datos["filas_por_pagina"],
        dias_grafica=datos["dias_grafica"],
        actividad_reciente=datos["actividad_reciente"],
        campos_ocultos_nombres=frozenset(ocultos.get("nombres", [])),
        campos_ocultos_contienen=tuple(ocultos.get("contienen", [])),
        solo_conteo=frozenset(e.lower() for e in datos["tablas_solo_conteo"].get("modelos", [])),
        grupos=datos["grupos"],
        config_tarjetas=tuple(datos["tarjetas"]),
        config_alertas=tuple(datos["alertas"]),
        config_distribuciones=tuple(datos["distribuciones"]),
        config_graficas=tuple(datos["graficas"]),
        config_recientes=tuple(datos["recientes"]),
    )


@lru_cache(maxsize=1)
def obtener_monitoreo():
    """La configuración del monitoreo. Se lee una sola vez (reinicia runserver si editas el JSON)."""
    return leer_monitoreo(settings.MONITOREO)


# ---------------------------------------------------------------------------
# Tablas, sistema, sesiones y migraciones
# ---------------------------------------------------------------------------

def catalogo():
    """Todas las tablas que conoce Django, agrupadas, con su número de filas.

    'total' es None cuando la tabla no existe en la base (falta migrate).
    """
    monitoreo = obtener_monitoreo()
    grupos = {}
    for modelo in apps.get_models(include_auto_created=True):
        total = consultar(lambda: modelo._base_manager.count())
        grupos.setdefault(monitoreo.grupo_de(modelo), []).append({
            "nombre": str(modelo._meta.verbose_name_plural),
            "etiqueta": etiqueta_de(modelo),
            "tabla": modelo._meta.db_table,
            "total": total,
            "falta_tabla": total is None,
            "abrir": monitoreo.puede_abrir(modelo),
            "url": url_tabla(modelo),
            "automatica": modelo._meta.auto_created is not False,
        })
    return [
        {"grupo": grupo, "tablas": sorted(tablas, key=lambda t: t["tabla"]), "filas": sum(t["total"] or 0 for t in tablas)}
        for grupo, tablas in grupos.items()
    ]


def tablas_sin_modelo():
    """Tablas que existen en la base pero que ningún modelo de Django usa (ej. tablas viejas)."""
    conocidas = {m._meta.db_table for m in apps.get_models(include_auto_created=True)} | {"django_migrations"}
    existentes = consultar(lambda: connection.introspection.table_names(), por_defecto=[])
    return sorted(set(existentes) - conocidas - {"sqlite_sequence"})


def info_sistema():
    vendor = connection.vendor
    version = consultar(lambda: _uno(SQL_VERSION.get(vendor))) if vendor in SQL_VERSION else None
    tamano = consultar(lambda: _uno(SQL_TAMANO.get(vendor))) if vendor in SQL_TAMANO else None
    return {
        "motor": NOMBRE_MOTOR.get(vendor, vendor),
        "version_bd": version or "—",
        "nombre_bd": str(connection.settings_dict.get("NAME", "")),
        "host": connection.settings_dict.get("HOST") or "local",
        "tamano": tamano_legible(int(tamano) if tamano is not None else None),
        "django": django.get_version(),
        "python": platform.python_version(),
        "sistema": f"{platform.system()} {platform.release()}",
        "debug": settings.DEBUG,
        "zona_horaria": settings.TIME_ZONE,
        "hora_servidor": timezone.localtime(),
        "google": bool(getattr(settings, "GOOGLE_CLIENT_ID", "") and getattr(settings, "GOOGLE_CLIENT_SECRET", "")),
    }


def _uno(sql):
    with connection.cursor() as cursor:
        cursor.execute(sql)
        fila = cursor.fetchone()
    return fila[0] if fila else None


def migraciones():
    """Migraciones de cada app: aplicadas (con fecha) y pendientes."""
    loader = consultar(lambda: MigrationLoader(connection, ignore_no_migrations=True))
    if loader is None:
        return {"apps": [], "pendientes": None}
    aplicadas = consultar(lambda: MigrationRecorder(connection).applied_migrations(), por_defecto={})
    por_app = {}
    for app, nombre in sorted(loader.graph.nodes):
        registro = aplicadas.get((app, nombre))
        por_app.setdefault(app, []).append({
            "nombre": nombre,
            "aplicada": registro is not None,
            "fecha": getattr(registro, "applied", None),
        })
    lista = [
        {"app": app, "migraciones": items, "pendientes": sum(not m["aplicada"] for m in items)}
        for app, items in sorted(por_app.items())
    ]
    return {"apps": lista, "pendientes": sum(a["pendientes"] for a in lista)}


def revisiones():
    """Resultado de 'python manage.py check' (incluye la revisión de los JSON)."""
    nombres = {
        django_checks.DEBUG: "debug", django_checks.INFO: "info", django_checks.WARNING: "advertencia",
        django_checks.ERROR: "error", django_checks.CRITICAL: "crítico",
    }
    mensajes = django_checks.run_checks()
    return [
        {"nivel": nombres.get(m.level, str(m.level)), "grave": m.is_serious(), "id": m.id or "", "mensaje": m.msg, "objeto": str(m.obj or "")}
        for m in mensajes
        if not m.is_silenced()
    ]


def sesiones_activas(clave_actual=""):
    """Sesiones sin vencer, con su usuario. Nunca se muestra la clave de sesión (es la cookie)."""
    from django.contrib.sessions.models import Session

    usuario_modelo = apps.get_model(settings.AUTH_USER_MODEL)
    ahora = timezone.now()
    sesiones = consultar(lambda: list(Session.objects.filter(expire_date__gt=ahora).order_by("-expire_date")), por_defecto=[])
    datos = [(s, s.get_decoded().get("_auth_user_id")) for s in sesiones]
    ids = {uid for _, uid in datos if uid}
    usuarios = {str(u.pk): u for u in usuario_modelo._base_manager.filter(pk__in=ids)}
    return [
        {
            "huella": huella(s.session_key),
            "usuario": usuarios.get(str(uid)),
            "anonima": not uid,
            "vence": s.expire_date,
            "actual": s.session_key == clave_actual,
        }
        for s, uid in datos
    ]


def total_sesiones_vencidas():
    from django.contrib.sessions.models import Session

    return consultar(lambda: Session.objects.filter(expire_date__lte=timezone.now()).count(), por_defecto=0)
