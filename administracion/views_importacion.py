"""Pantalla de carga masiva (solo superusuario): validar primero y luego importar."""

from django.contrib import messages
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_http_methods

from . import importacion as imp
from .views import administrador


@administrador
@require_http_methods(["GET", "POST"])
def importar(request):
    contexto = {"tipos": imp.COLUMNAS, "columnas": imp.COLUMNAS, "tipo_sel": request.POST.get("tipo", "usuarios"), "resultado": None}
    if request.method == "POST":
        archivo = request.FILES.get("archivo")
        accion = request.POST.get("accion", "validar")
        if not archivo:
            messages.error(request, "Elige un archivo CSV.")
            return render(request, "administracion/importar.html", contexto)
        contenido = archivo.read()
        try:
            if accion == "importar":
                resultado = imp.importar(contexto["tipo_sel"], contenido)
                if not resultado.errores:
                    messages.success(request, f"Listo: se crearon {resultado.creados} registro(s).")
            else:
                resultado = imp.validar(contexto["tipo_sel"], contenido)
        except imp.ErrorImportacion as error:
            messages.error(request, str(error))
            return render(request, "administracion/importar.html", contexto)
        contexto["resultado"] = resultado
        if resultado.errores and accion == "importar":
            messages.error(request, "No se guardó nada: corrige los errores y vuelve a intentarlo.")
    return render(request, "administracion/importar.html", contexto)


@administrador
@require_GET
def plantilla(request, tipo):
    if tipo not in imp.COLUMNAS:
        return HttpResponseBadRequest("Tipo no válido.")
    respuesta = HttpResponse(imp.plantilla(tipo), content_type="text/csv; charset=utf-8")
    respuesta["Content-Disposition"] = f'attachment; filename="plantilla_{tipo}.csv"'
    return respuesta
