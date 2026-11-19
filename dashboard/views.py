from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def panel(request):
    # Fase 2: aquí se calcularán las estadísticas reales desde la base de datos
    return render(request, "dashboard/panel.html")


@login_required
def proximamente(request, seccion):
    return render(request, "dashboard/proximamente.html", {"seccion": seccion})
