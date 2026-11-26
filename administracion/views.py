from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from cuentas.models import Usuario
from cuentas.models import SuperusuarioProtegido
from cuentas.servicios import consecuencias_de_eliminar_cuenta, eliminar_cuenta

from .forms import UsuarioAdminForm, UsuarioCrearForm


def administrador(vista):
    # Solo el superusuario administra: "is_staff" no basta (puede tener permisos parciales).
    return user_passes_test(lambda usuario: usuario.is_active and usuario.is_superuser)(vista)


@administrador
def inicio(request):
    busqueda = request.GET.get("q", "").strip()
    usuarios = Usuario.objects.order_by("first_name", "email")
    if busqueda:
        usuarios = usuarios.filter(Q(email__icontains=busqueda) | Q(first_name__icontains=busqueda) | Q(last_name__icontains=busqueda))
    resumen = Usuario.objects.values("perfil").annotate(total=Count("pk"))
    return render(request, "administracion/inicio.html", {"usuarios": usuarios, "busqueda": busqueda, "resumen": resumen})


@administrador
def crear_usuario(request):
    form = UsuarioCrearForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        usuario = form.save()
        messages.success(request, f"Cuenta creada para {usuario.email}.")
        return redirect("administracion:inicio")
    return render(request, "administracion/usuario_form.html", {"form": form})


@administrador
def editar_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    form = UsuarioAdminForm(request.POST or None, instance=usuario)
    if request.method == "POST" and form.is_valid():
        try:
            form.save()
        except SuperusuarioProtegido as error:
            messages.error(request, str(error))
            return redirect("administracion:inicio")
        messages.success(request, "Cuenta actualizada.")
        return redirect("administracion:inicio")
    return render(request, "administracion/usuario_form.html", {"form": form, "usuario": usuario})


@administrador
def eliminar_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == "POST":
        propia = usuario.pk == request.user.pk
        try:
            eliminar_cuenta(usuario)
        except SuperusuarioProtegido as error:
            messages.error(request, str(error))
            return redirect("administracion:inicio")
        if propia:
            logout(request)  # la sesión de esa cuenta ya no existe
            return redirect("login")
        messages.success(request, "Cuenta eliminada.")
        return redirect("administracion:inicio")
    return render(request, "confirmar_eliminar.html", {"titulo": "Eliminar usuario", "objeto": usuario.email, "consecuencias": consecuencias_de_eliminar_cuenta(usuario, propia=False), "url_cancelar": "/administracion/"})
