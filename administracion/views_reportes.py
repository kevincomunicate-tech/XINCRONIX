"""Reportes del superusuario: página con filtros de varios criterios y exportación a Excel o PDF."""

import logging

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_GET

from . import reportes as r

log = logging.getLogger("administracion.reportes")

TIPOS = {
    "xlsx": ("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "xlsx"),
    "pdf": ("application/pdf", "pdf"),
}


def solo_cargo_mas_alto(vista):
    def dentro(request, *args, **kwargs):
        if not r.puede_ver_reportes(request.user):
            raise PermissionDenied("Los reportes son solo para el superusuario.")
        return vista(request, *args, **kwargs)
    return user_passes_test(lambda u: u.is_authenticated)(dentro)


def _parametros(GET):
    criterios = []
    for i in range(1, r.MAX_CRITERIOS + 1):
        campo = GET.get(f"c{i}_campo", "").strip()
        if not campo:
            continue
        criterios.append({
            "campo": campo,
            "operador": GET.get(f"c{i}_op", "igual"),
            "valor": GET.get(f"c{i}_valor", ""),
            "valor2": GET.get(f"c{i}_valor2", ""),
        })
    return GET.get("tabla", "usuarios"), criterios, GET.get("logica", "y"), GET.getlist("columnas")


@solo_cargo_mas_alto
@require_GET
def reportes(request):
    clave, criterios, logica, columnas = _parametros(request.GET)
    if clave not in r.CATALOGO:
        clave = "usuarios"
    tabla = r.CATALOGO[clave]
    contexto = {
        "tablas": r.CATALOGO,
        "tabla": tabla,
        "clave": clave,
        "operadores": r.OPERADORES,
        "logica": logica,
        "columnas_sel": columnas or [c.ruta for c in tabla.columnas],
        "criterios": criterios,
        "filas_criterio": [criterios[i] if i < len(criterios) else {} for i in range(r.MAX_CRITERIOS)],
        "campos_filtro": [(c.ruta, c.titulo) for c in tabla.columnas if c.ruta in tabla.filtros],
        "columnas_catalogo": tabla.columnas,
        "query": request.GET.urlencode(),
        "max_filas": r.MAX_FILAS_EXPORTACION,
        "max_criterios": r.MAX_CRITERIOS,
    }
    if request.GET.get("ver"):
        try:
            cols, datos, total = r.filas(clave, criterios, logica, columnas, limite=200)
            contexto.update(cols=cols, datos=datos, total=total, resumen=r.descripcion_criterios(clave, criterios, logica))
        except r.ErrorReporte as error:
            messages.error(request, str(error))
    return render(request, "administracion/reportes.html", contexto)


@solo_cargo_mas_alto
@require_GET
def reportes_exportar(request, formato):
    if formato not in TIPOS:
        return HttpResponseBadRequest("Formato no válido.")
    clave, criterios, logica, columnas = _parametros(request.GET)
    generador = request.user.get_full_name() or "Superusuario"
    try:
        if formato == "xlsx":
            contenido = r.exportar_excel(clave, criterios, logica, columnas, generador)
        else:
            contenido = r.exportar_pdf(clave, criterios, logica, columnas, generador)
    except r.ErrorReporte as error:
        messages.error(request, str(error))
        return redirect(f"{reverse('administracion:reportes')}?{request.GET.urlencode()}")
    tipo, extension = TIPOS[formato]
    nombre = f"reporte_{clave}_{timezone.localdate():%Y%m%d}.{extension}"
    log.info("Reporte %s exportado en %s por el usuario %s", clave, formato, request.user.pk)
    respuesta = HttpResponse(contenido, content_type=tipo)
    respuesta["Content-Disposition"] = f'attachment; filename="{nombre}"'
    return respuesta
