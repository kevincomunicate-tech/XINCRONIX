"""Inicio de sesión con Google (django-allauth), sin salir a internet.

Se simula la respuesta de Google: el intercambio del código por el token y
el contenido del id_token. Todo lo demás (estado anti-CSRF, PKCE, creación
de la cuenta, vinculación por correo, redirección) corre de verdad.
"""

from unittest import mock
from urllib.parse import parse_qs, urlparse

from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Rol, Usuario

GOOGLE = {
    "google": {
        "APP": {"client_id": "id-de-prueba.apps.googleusercontent.com", "secret": "secreto-de-prueba"},
        "SCOPE": ["openid", "profile", "email"],
        "OAUTH_PKCE_ENABLED": True,
    }
}
CON_GOOGLE = override_settings(
    SOCIALACCOUNT_PROVIDERS=GOOGLE, GOOGLE_CLIENT_ID="id-de-prueba", GOOGLE_CLIENT_SECRET="secreto-de-prueba"
)


def datos_google(correo, nombre="Nuevo", apellido="Google"):
    return {
        "iss": "https://accounts.google.com", "aud": GOOGLE["google"]["APP"]["client_id"], "sub": "1234567890",
        "email": correo, "email_verified": True, "given_name": nombre, "family_name": apellido,
        "name": f"{nombre} {apellido}", "picture": "https://example.com/foto.png",
    }


class BotonTests(TestCase):
    @override_settings(GOOGLE_CLIENT_ID="", GOOGLE_CLIENT_SECRET="")
    def test_sin_credenciales_el_boton_sale_desactivado(self):
        r = self.client.get(reverse("login"))
        self.assertContains(r, "Continuar con Google")
        self.assertContains(r, "Inicio con Google sin configurar")
        self.assertNotContains(r, reverse("google_login"))

    @CON_GOOGLE
    def test_con_credenciales_el_boton_envia_a_google(self):
        for pagina in ("login", "registro"):
            self.assertContains(self.client.get(reverse(pagina)), f'action="{reverse("google_login")}"')


@CON_GOOGLE
class FlujoGoogleTests(TestCase):
    def iniciar(self):
        """Paso 1: el botón (POST) redirige a la pantalla de Google con state y PKCE."""
        r = self.client.post(reverse("google_login"))
        self.assertEqual(r.status_code, 302)
        destino = urlparse(r["Location"])
        self.assertEqual(destino.netloc, "accounts.google.com")
        parametros = parse_qs(destino.query)
        self.assertEqual(parametros["client_id"], [GOOGLE["google"]["APP"]["client_id"]])
        self.assertIn("code_challenge", parametros)
        return parametros["state"][0]

    def volver_de_google(self, state, datos):
        """Paso 2: Google devuelve un código; se simula su respuesta."""
        token = {"access_token": "token-de-prueba", "expires_in": 3600, "id_token": "id-token-de-prueba"}
        with mock.patch("allauth.socialaccount.providers.oauth2.client.OAuth2Client.get_access_token", return_value=token), \
             mock.patch("allauth.socialaccount.providers.google.views._verify_and_decode", return_value=datos):
            return self.client.get(reverse("google_callback"), {"code": "codigo-de-prueba", "state": state})

    def test_cuenta_nueva_queda_como_usuario_normal(self):
        r = self.volver_de_google(self.iniciar(), datos_google("Nuevo@Gmail.com"))
        self.assertRedirects(r, reverse("panel"), fetch_redirect_response=False)
        usuario = Usuario.objects.get(email="nuevo@gmail.com")
        self.assertEqual((usuario.first_name, usuario.last_name), ("Nuevo", "Google"))
        self.assertEqual(usuario.rol.codigo, Rol.USUARIO)
        self.assertIsNone(usuario.empresa)
        self.assertFalse(usuario.is_superuser or usuario.is_staff)
        self.assertFalse(usuario.has_usable_password())  # entra con Google; puede crear contraseña en Mi cuenta
        self.assertEqual(int(self.client.session["_auth_user_id"]), usuario.pk)

    def test_correo_existente_se_vincula_y_respeta_su_inicio(self):
        super_ = Usuario.objects.create_superuser("cuellaryohan100@gmail.com", "Clave$egura2026")
        r = self.volver_de_google(self.iniciar(), datos_google("cuellaryohan100@gmail.com"))
        self.assertRedirects(r, reverse("administracion:inicio"), fetch_redirect_response=False)
        self.assertEqual(Usuario.objects.count(), 1)  # no creó otra cuenta
        self.assertEqual(int(self.client.session["_auth_user_id"]), super_.pk)

    def test_state_falso_no_inicia_sesion(self):
        self.iniciar()
        r = self.volver_de_google("state-inventado", datos_google("intruso@gmail.com"))
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertFalse(Usuario.objects.filter(email="intruso@gmail.com").exists())
        self.assertContains(r, "No se pudo iniciar sesión con Google", status_code=401)  # nuestra plantilla

    def test_cuenta_desactivada_no_entra(self):
        Usuario.objects.create_user("baja@gmail.com", "Clave$egura2026", is_active=False)
        r = self.volver_de_google(self.iniciar(), datos_google("baja@gmail.com"))
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertContains(self.client.get(r["Location"]), "Cuenta desactivada", status_code=403)

    def test_solo_se_exponen_las_urls_necesarias_de_allauth(self):
        self.assertRedirects(self.client.get("/cuentas/social/login/"), reverse("login"))
        self.assertRedirects(self.client.get("/cuentas/social/signup/"), reverse("registro"))
        self.assertContains(self.client.get(reverse("socialaccount_login_cancelled")), "Inicio con Google cancelado")
        for ruta in ("/cuentas/social/password/reset/", "/cuentas/social/email/", "/cuentas/social/3rdparty/"):
            self.assertEqual(self.client.get(ruta).status_code, 404)
