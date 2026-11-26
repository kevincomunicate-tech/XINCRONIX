"""
Panel de monitoreo del superadministrador (/administracion/monitoreo/).

Igual que el resto de /administracion/, la ruta la protege
PoliticaAccesoMiddleware ("rutas_restringidas" de config/politica_accesos.json):
aquí no hay comprobaciones de rol.

Qué se ve y qué se oculta lo decide config/monitoreo.json (ver monitoreo.py).
Todo es de solo lectura, salvo cerrar sesiones.
"""

import csv

from django.contrib import messages
from django.contrib.sessions.models import Session
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.http import Http404, StreamingHttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from . import monitoreo as m


def _modelo_o_404(app_label, nombre):
    try:
        return m.obtener_modelo(f"{app_label}.{nombre}")
    except (LookupError, ValueError):
        raise Http404("Esa tabla no existe.")


def _modelo_abrible_o_404(app_label, nombre):
    """Las tablas de 'tablas_solo_conteo' no se abren fila por fila."""
    modelo = _modelo_o_404(app_label, nombre)
    if not m.obtener_monitoreo().puede_abrir(modelo):
        raise Http404("Esta tabla solo se puede contar (config/monitoreo.json → tablas_solo_conteo).")
    return modelo


# ---------------------------------------------------------------------------
# Resumen
# ---------------------------------------------------------------------------

@require_GET
def resumen(request):
    monitoreo = m.obtener_monitoreo()
    catalogo = m.catalogo()
    return render(request, "administracion/monitoreo/resumen.html", {
        "pestana": "resumen",
        "tarjetas": monitoreo.tarjetas(),
        "alertas": monitoreo.alertas(),
        "distribuciones": monitoreo.distribuciones(),
        "graficas": monitoreo.graficas(),
        "recientes": monitoreo.recientes(),
        "sistema": m.info_sistema(),
        "total_tablas": sum(len(g["tablas"]) for g in catalogo),
        "total_filas": sum(g["filas"] for g in catalogo),
        "tablas_faltantes": [t for g in catalogo for t in g["tablas"] if t["falta_tabla"]],
        "sesiones": len(m.sesiones_activas()),
        "dias": monitoreo.dias_grafica,
    })


# ---------------------------------------------------------------------------
# Tablas
# ---------------------------------------------------------------------------

@require_GET
def tablas(request):
    catalogo = m.catalogo()
    return render(request, "administracion/monitoreo/tablas.html", {
        "pestana": "tablas",
        "catalogo": catalogo,
        "sin_modelo": m.tablas_sin_modelo(),
        "total_filas": sum(g["filas"] for g in catalogo),
    })


@require_GET
def tabla(request, app_label, modelo):
    monitoreo = m.obtener_monitoreo()
    clase = _modelo_abrible_o_404(app_label, modelo)
    busqueda = request.GET.get("q", "").strip()
    filtro_campo = request.GET.get("campo", "")
    filtro_valor = request.GET.get("valor", "")

    consulta, buscables = monitoreo.filas(clase, busqueda, filtro_campo, filtro_valor)
    total = m.consultar(lambda: consulta.count())
    pagina = Paginator(consulta, monitoreo.filas_por_pagina).get_page(request.GET.get("pagina")) if total is not None else None
    campos = list(clase._meta.concrete_fields)
    filas = [
        {"pk": objeto.pk, "url": m.url_registro(clase, objeto.pk), "celdas": [monitoreo.valor(objeto, c) for c in campos]}
        for objeto in (pagina.object_list if pagina else [])
    ]
    return render(request, "administracion/monitoreo/tabla.html", {
        "pestana": "tablas",
        "modelo": clase._meta,
        "etiqueta": m.etiqueta_de(clase),
        "campos": campos,
        "filas": filas,
        "pagina": pagina,
        "total": total,
        "falta_tabla": total is None,
        "busqueda": busqueda,
        "buscables": buscables,
        "filtro_campo": filtro_campo,
        "filtro_valor": filtro_valor,
        "estructura": monitoreo.estructura(clase),
        "vista": request.GET.get("vista", "datos"),
    })


@require_GET
def registro(request, app_label, modelo, pk):
    monitoreo = m.obtener_monitoreo()
    clase = _modelo_abrible_o_404(app_label, modelo)
    relaciones = [c.name for c in clase._meta.concrete_fields if c.is_relation]
    try:
        objeto = m.consultar(lambda: clase._base_manager.select_related(*relaciones).filter(pk=pk).first())
    except (ValueError, ValidationError):
        objeto = None
    if objeto is None:
        raise Http404("No existe ese registro.")

    campos = [
        {"nombre": c.verbose_name, "campo": c.name, "columna": c.column, **monitoreo.valor(objeto, c, completo=True)}
        for c in clase._meta.concrete_fields
    ]
    muchos = [
        {"nombre": c.verbose_name, "valores": m.consultar(lambda: [str(o) for o in getattr(objeto, c.name).all()[:50]], por_defecto=[])}
        for c in clase._meta.many_to_many
    ]
    return render(request, "administracion/monitoreo/registro.html", {
        "pestana": "tablas",
        "modelo": clase._meta,
        "objeto": objeto,
        "campos": campos,
        "muchos": muchos,
        "inversas": monitoreo.relaciones_inversas(objeto),
        "url_tabla": m.url_tabla(clase),
    })


class _Eco:
    """Objeto 'archivo' que devuelve lo que se le escribe (para generar el CSV por partes)."""

    def write(self, valor):
        return valor


# Excel y otras hojas de cálculo ejecutan una celda que empieza por estos caracteres
# (inyección de fórmulas). Se neutraliza anteponiendo una comilla simple.
_PREFIJOS_PELIGROSOS = ("=", "+", "-", "@", "\t", "\r")


def _celda_segura(texto):
    texto = str(texto)
    return "'" + texto if texto.startswith(_PREFIJOS_PELIGROSOS) else texto


@require_GET
def exportar(request, app_label, modelo):
    """Descarga la tabla en CSV. Los campos sensibles NO se exportan (ni siquiera la columna)."""
    monitoreo = m.obtener_monitoreo()
    clase = _modelo_abrible_o_404(app_label, modelo)
    campos = [c for c in clase._meta.concrete_fields if not monitoreo.es_oculto(c)]
    consulta, _ = monitoreo.filas(clase, request.GET.get("q", "").strip(), request.GET.get("campo", ""), request.GET.get("valor", ""))
    escritor = csv.writer(_Eco())

    def filas():
        yield "﻿"  # BOM: Excel abre bien las tildes
        yield escritor.writerow([_celda_segura(c.column) for c in campos])
        for objeto in consulta.iterator(chunk_size=500):
            yield escritor.writerow([_celda_segura(monitoreo.valor(objeto, c, completo=True)["texto"]) for c in campos])

    nombre = f"{clase._meta.db_table}_{timezone.localdate():%Y%m%d}.csv"
    respuesta = StreamingHttpResponse(filas(), content_type="text/csv; charset=utf-8")
    respuesta["Content-Disposition"] = f'attachment; filename="{nombre}"'
    return respuesta


# ---------------------------------------------------------------------------
# Sesiones
# ---------------------------------------------------------------------------

@require_GET
def sesiones(request):
    lista = m.sesiones_activas(request.session.session_key or "")
    return render(request, "administracion/monitoreo/sesiones.html", {
        "pestana": "sesiones",
        "sesiones": lista,
        "usuarios_conectados": len({s["usuario"].pk for s in lista if s["usuario"]}),
        "vencidas": m.total_sesiones_vencidas(),
    })


@require_POST
def cerrar_sesiones(request):
    """Cierra una sesión, todas las de un usuario o borra las vencidas. Nunca la propia."""
    actual = request.session.session_key or ""
    huella = request.POST.get("sesion", "")
    usuario_id = request.POST.get("usuario", "")
    activas = Session.objects.filter(expire_date__gt=timezone.now()).exclude(session_key=actual)

    acciones = {
        "una": lambda: [s.delete() for s in activas if m.huella(s.session_key) == huella],
        "usuario": lambda: [s.delete() for s in activas if str(s.get_decoded().get("_auth_user_id")) == usuario_id],
        "vencidas": lambda: Session.objects.filter(expire_date__lte=timezone.now()).delete(),
    }
    textos = {
        "una": "Se cerró la sesión.",
        "usuario": "Se cerraron las sesiones de ese usuario (menos la tuya).",
        "vencidas": "Se borraron las sesiones vencidas.",
    }
    accion = request.POST.get("accion", "")
    if accion not in acciones:
        messages.error(request, "Acción no válida.")
        return redirect("administracion:monitoreo_sesiones")
    acciones[accion]()
    messages.success(request, textos[accion])
    return redirect("administracion:monitoreo_sesiones")


# ---------------------------------------------------------------------------
# Sistema
# ---------------------------------------------------------------------------

@require_GET
def sistema(request):
    return render(request, "administracion/monitoreo/sistema.html", {
        "pestana": "sistema",
        "sistema": m.info_sistema(),
        "migraciones": m.migraciones(),
        "revisiones": m.revisiones(),
    })
