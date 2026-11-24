from django.shortcuts import redirect, render

from cuentas.politica import obtener_politica


def inicio(request):
    """Página pública (/).

    Sin sesión se muestra la portada de Xincronix (index.html); con sesión,
    cada perfil va a su inicio (lo define config/politica_accesos.json).
    """
    if request.user.is_authenticated:
        return redirect(obtener_politica().url_inicio(request.user))
    return render(request, "sitio/index.html")
