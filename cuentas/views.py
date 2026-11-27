from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .decoradores import requiere_accion
from .forms import (
    CambiarContrasenaForm, EliminarCuentaForm, LoginForm, NuevaContrasenaForm,
    PerfilForm, RecuperarForm, RegistroForm,
)
from .politica import obtener_politica
from .models import SuperusuarioProtegido
from .servicios import consecuencias_de_eliminar_cuenta, eliminar_cuenta as eliminar_cuenta_y_datos


class LoginView(auth_views.LoginView):
    template_name = "cuentas/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True  # si ya inició sesión, va directo a su inicio

    def get_default_redirect_url(self):
        # Cada perfil entra a su "inicio" (config/politica_accesos.json),
        # salvo que venga de una página protegida (?next=...).
        return obtener_politica().url_inicio(self.request.user)

    def form_valid(self, form):
        # Sin "recordar sesión", la sesión termina al cerrar el navegador
        if not form.cleaned_data.get("recordar"):
            self.request.session.set_expiry(0)
        return super().form_valid(form)


def registro(request):
    if request.user.is_authenticated:
        return redirect(obtener_politica().url_inicio(request.user))

    form = RegistroForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        usuario = form.save()
        login(request, usuario, backend="django.contrib.auth.backends.ModelBackend")
        messages.success(request, f"¡Bienvenido, {usuario.first_name}! Tu cuenta quedó creada.")
        return redirect(obtener_politica().url_inicio(usuario))

    return render(request, "cuentas/registro.html", {"form": form})


# ---- Recuperar contraseña (vistas de Django con nuestras plantillas) ----

class RecuperarView(auth_views.PasswordResetView):
    template_name = "cuentas/recuperar.html"
    form_class = RecuperarForm
    email_template_name = "cuentas/correo_recuperar.txt"
    html_email_template_name = "cuentas/correo_recuperar.html"
    subject_template_name = "cuentas/correo_recuperar_asunto.txt"
    success_url = reverse_lazy("recuperar_enviado")


class RecuperarEnviadoView(auth_views.PasswordResetDoneView):
    template_name = "cuentas/recuperar_enviado.html"


class NuevaContrasenaView(auth_views.PasswordResetConfirmView):
    template_name = "cuentas/nueva_contrasena.html"
    form_class = NuevaContrasenaForm
    success_url = reverse_lazy("recuperar_listo")


class RecuperarListoView(auth_views.PasswordResetCompleteView):
    template_name = "cuentas/recuperar_listo.html"


# ---- Mi cuenta: CRUD de la propia información ----

@requiere_accion("editar_cuenta")
def mi_cuenta(request):
    form = PerfilForm(request.POST or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Tus datos quedaron actualizados.")
        return redirect("mi_cuenta")
    return render(request, "cuentas/mi_cuenta.html", {
        "form": form,
        "puede_eliminar": obtener_politica().puede(request.user, "eliminar_cuenta"),
        "cuentas_google": request.user.socialaccount_set.filter(provider="google"),
    })


@requiere_accion("editar_cuenta")
def cambiar_contrasena(request):
    form = CambiarContrasenaForm(request.user, request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        update_session_auth_hash(request, form.user)  # no cierra la sesión actual
        messages.success(request, "Tu contraseña quedó guardada.")
        return redirect("mi_cuenta")
    return render(request, "cuentas/cambiar_contrasena.html", {"form": form})


@requiere_accion("eliminar_cuenta")
def eliminar_cuenta(request):
    form = EliminarCuentaForm(request.POST or None, usuario=request.user)
    if request.method == "POST" and form.is_valid():
        usuario = request.user
        try:
            eliminar_cuenta_y_datos(usuario)
        except SuperusuarioProtegido as error:
            messages.error(request, str(error))
            return redirect("mi_cuenta")
        logout(request)
        messages.success(request, "Tu cuenta fue eliminada. ¡Gracias por usar Xincronix!")
        return redirect("login")
    return render(request, "confirmar_eliminar.html", {
        "titulo": "Eliminar mi cuenta",
        "objeto": request.user.email,
        "consecuencias": consecuencias_de_eliminar_cuenta(request.user),
        "url_cancelar": reverse_lazy("mi_cuenta"),
        "form": form,
    })


def cuenta_inactiva(request):
    """Alguien con la cuenta desactivada intentó entrar (por ejemplo, con Google)."""
    return render(request, "cuentas/cuenta_inactiva.html", status=403)
