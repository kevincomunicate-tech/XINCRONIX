"""
Administración (solo superadministrador): CRUD de usuarios y de empresas.

No hay comprobaciones de "¿es el superadministrador?" aquí: la ruta
/administracion/ la protege PoliticaAccesoMiddleware según
"rutas_restringidas" de config/politica_accesos.json. Además, las cuentas
de superadministradores nunca aparecen para editar ni eliminar.
"""

from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from cuentas.models import Empresa, Usuario
from cuentas.politica import obtener_politica
from cuentas.servicios import consecuencias_de_eliminar_cuenta, eliminar_cuenta
from dashboard.metricas import metricas_empresa
from dashboard.views import consecuencias_de_eliminar_empresa

from .forms import AsignacionForm, EmpresaAdminForm, UsuarioCrearForm, VincularForm, usuarios_gestionables


# ---------------------------------------------------------------------------
# Usuarios
# ---------------------------------------------------------------------------

def inicio(request):
    """Lista de usuarios con búsqueda y conteo por rol."""
    politica = obtener_politica()
    busqueda = request.GET.get("q", "").strip()

    usuarios = usuarios_gestionables().select_related("empresa", "rol").order_by("empresa__nombre", "first_name", "email")
    if busqueda:
        usuarios = usuarios.filter(
            Q(email__icontains=busqueda) | Q(first_name__icontains=busqueda)
            | Q(last_name__icontains=busqueda) | Q(empresa__nombre__icontains=busqueda)
        )

    conteo = dict(Usuario.objects.values_list("rol__codigo").annotate(total=Count("pk")))
    resumen = [
        {"codigo": codigo, "nombre": rol["nombre"], "total": conteo.get(codigo, 0)}
        for codigo, rol in politica.roles.items()
    ]

    return render(request, "administracion/inicio.html", {
        "usuarios": usuarios,
        "busqueda": busqueda,
        "resumen": resumen,
        "superadministradores": sorted(politica.superadministradores),
    })


def crear_usuario(request):
    form = UsuarioCrearForm(request.POST or None, asignador=request.user)
    if request.method == "POST" and form.is_valid():
        usuario = form.save()
        messages.success(request, f"Se creó la cuenta de {usuario} ({usuario.rol}).")
        return redirect("administracion:inicio")
    return render(request, "administracion/usuario_form.html", {"form": form})


def editar_usuario(request, pk):
    usuario = get_object_or_404(usuarios_gestionables(), pk=pk)
    form = AsignacionForm(request.POST or None, instance=usuario, asignador=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Se actualizó a {usuario}: {usuario.rol}.")
        return redirect("administracion:inicio")
    return render(request, "administracion/usuario_form.html", {"form": form, "usuario": usuario})


def eliminar_usuario(request, pk):
    usuario = get_object_or_404(usuarios_gestionables(), pk=pk)
    if request.method == "POST":
        eliminar_cuenta(usuario)
        messages.success(request, f"Se eliminó la cuenta {usuario.email}.")
        return redirect("administracion:inicio")
    return render(request, "confirmar_eliminar.html", {
        "titulo": "Eliminar usuario",
        "objeto": usuario.email,
        "consecuencias": consecuencias_de_eliminar_cuenta(usuario, propia=False),
        "url_cancelar": reverse("administracion:inicio"),
    })


# ---------------------------------------------------------------------------
# Empresas
# ---------------------------------------------------------------------------

def empresas(request):
    busqueda = request.GET.get("q", "").strip()
    lista = Empresa.objects.select_related("propietario").annotate(
        total_usuarios=Count("usuarios", distinct=True), total_proyectos=Count("proyectos", distinct=True)
    ).order_by("nombre")
    if busqueda:
        lista = lista.filter(Q(nombre__icontains=busqueda) | Q(nit__icontains=busqueda) | Q(propietario__email__icontains=busqueda))
    return render(request, "administracion/empresas.html", {"empresas": lista, "busqueda": busqueda})


def crear_empresa(request):
    form = EmpresaAdminForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        empresa = form.save()
        messages.success(request, f"Se creó la empresa «{empresa}».")
        return redirect("administracion:empresa_detalle", pk=empresa.pk)
    return render(request, "administracion/empresa_form.html", {"form": form})


def empresa_detalle(request, pk, vincular_form=None):
    empresa = get_object_or_404(Empresa.objects.select_related("propietario"), pk=pk)
    return render(request, "administracion/empresa_detalle.html", {
        "empresa": empresa,
        "metricas": metricas_empresa(empresa),
        "integrantes": empresa.usuarios.select_related("rol").order_by("first_name", "email"),
        "vincular_form": vincular_form or VincularForm(empresa=empresa),
        "superadministradores": obtener_politica().superadministradores,
    })


def editar_empresa(request, pk):
    empresa = get_object_or_404(Empresa, pk=pk)
    form = EmpresaAdminForm(request.POST or None, instance=empresa)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Se actualizó la empresa «{empresa}».")
        return redirect("administracion:empresa_detalle", pk=empresa.pk)
    return render(request, "administracion/empresa_form.html", {"form": form, "empresa": empresa})


def eliminar_empresa(request, pk):
    empresa = get_object_or_404(Empresa, pk=pk)
    if request.method == "POST":
        nombre = empresa.nombre
        empresa.delete()
        messages.success(request, f"Se eliminó la empresa «{nombre}».")
        return redirect("administracion:empresas")
    return render(request, "confirmar_eliminar.html", {
        "titulo": "Eliminar empresa",
        "objeto": empresa.nombre,
        "consecuencias": consecuencias_de_eliminar_empresa(empresa),
        "url_cancelar": reverse("administracion:empresa_detalle", args=[empresa.pk]),
    })


@require_POST
def vincular_usuario(request, pk):
    empresa = get_object_or_404(Empresa, pk=pk)
    form = VincularForm(request.POST, empresa=empresa)
    if not form.is_valid():
        return empresa_detalle(request, pk, vincular_form=form)
    usuario = form.cleaned_data["usuario"]
    usuario.empresa = empresa
    usuario.save(update_fields=["empresa"])
    messages.success(request, f"{usuario} quedó vinculado a «{empresa}».")
    return redirect("administracion:empresa_detalle", pk=pk)


@require_POST
def desvincular_usuario(request, pk, usuario_pk):
    empresa = get_object_or_404(Empresa, pk=pk)
    usuario = get_object_or_404(usuarios_gestionables(), pk=usuario_pk, empresa=empresa)
    usuario.empresa = None
    usuario.save(update_fields=["empresa"])
    Empresa.objects.filter(pk=pk, propietario=usuario).update(propietario=None)
    messages.success(request, f"{usuario} ya no pertenece a «{empresa}».")
    return redirect("administracion:empresa_detalle", pk=pk)
