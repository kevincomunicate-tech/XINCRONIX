from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

from .politica import obtener_politica


class CuentaAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        return False

    def get_login_redirect_url(self, request):
        return obtener_politica().url_inicio(request.user)


class GoogleAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request, sociallogin):
        return True

    def populate_user(self, request, sociallogin, data):
        usuario = super().populate_user(request, sociallogin, data)
        usuario.email = (usuario.email or "").strip().lower()
        return usuario
