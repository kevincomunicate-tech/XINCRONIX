from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .forms import LoginForm, NuevaContrasenaForm, RecuperarForm, RegistroForm


class LoginView(auth_views.LoginView):
    template_name = "cuentas/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True  # si ya inició sesión, va directo al panel

    def form_valid(self, form):
        # Sin "recordar sesión", la sesión termina al cerrar el navegador
        if not form.cleaned_data.get("recordar"):
            self.request.session.set_expiry(0)
        return super().form_valid(form)


def registro(request):
    if request.user.is_authenticated:
        return redirect("panel")

    form = RegistroForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        usuario = form.save()
        login(request, usuario)
        messages.success(request, f"¡Bienvenido, {usuario.nombres}! Tu cuenta quedó creada.")
        return redirect("panel")

    return render(request, "cuentas/registro.html", {"form": form})


# ---- Recuperar contraseña (vistas de Django con nuestras plantillas) ----

class RecuperarView(auth_views.PasswordResetView):
    template_name = "cuentas/recuperar.html"
    form_class = RecuperarForm
    email_template_name = "cuentas/correo_recuperar.txt"
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
