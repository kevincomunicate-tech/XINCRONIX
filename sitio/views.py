from django.shortcuts import redirect


def inicio(request):
    # Fase 4: aquí irá la página pública (index.html).
    # Por ahora manda al panel si hay sesión, o al login si no.
    return redirect("panel" if request.user.is_authenticated else "login")
