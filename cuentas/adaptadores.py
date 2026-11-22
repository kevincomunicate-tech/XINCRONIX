"""
Conexión entre django-allauth (inicio de sesión con Google) y Xincronix.

allauth se encarga del protocolo OAuth con Google. Estos adaptadores solo
aplican NUESTRAS reglas, que salen de config/politica_accesos.json:

* Quien entra por primera vez con Google queda con el rol de "registro.rol"
  (usuario normal), igual que quien se registra con el formulario.
* Después de entrar, cada perfil va a su "inicio".
* El registro con correo y contraseña se hace en /cuentas/registro/ (nuestro
  formulario), no en las páginas de allauth.
"""

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

from .models import Rol
from .politica import obtener_politica


class CuentaAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        # El registro con contraseña es el nuestro (cuentas/views.py: registro)
        return False

    def get_login_redirect_url(self, request):
        return obtener_politica().url_inicio(request.user)


class GoogleAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request, sociallogin):
        # Sí se permite crear la cuenta la primera vez que alguien entra con Google
        return True

    def populate_user(self, request, sociallogin, data):
        usuario = super().populate_user(request, sociallogin, data)
        usuario.email = (usuario.email or "").strip().lower()
        return usuario

    def save_user(self, request, sociallogin, form=None):
        # Cuenta nueva creada con Google: usuario normal, sin empresa (la crea él)
        usuario = sociallogin.user
        politica = obtener_politica()
        usuario.rol = Rol.objects.get(codigo=politica.rol_registro)
        usuario.is_staff = False
        usuario.is_superuser = False
        return super().save_user(request, sociallogin, form)
