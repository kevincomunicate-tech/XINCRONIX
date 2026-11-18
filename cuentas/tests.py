import re

from django.core import mail
from django.test import TestCase
from django.urls import reverse

from .models import Usuario


class RegistroTests(TestCase):
    def test_registro_crea_usuario_e_inicia_sesion(self):
        r = self.client.post(reverse("registro"), {
            "nombre": "Yohan Cuellar",
            "email": "Yohan@Empresa.com",
            "password": "Clave$egura2026",
        })
        self.assertRedirects(r, reverse("panel"))
        usuario = Usuario.objects.get(email="yohan@empresa.com")  # se guarda en minúsculas
        self.assertEqual(usuario.first_name, "Yohan")
        self.assertEqual(usuario.last_name, "Cuellar")
        self.assertEqual(usuario.iniciales, "YC")
        self.assertTrue(usuario.check_password("Clave$egura2026"))  # cifrada, no en texto plano
        # quedó con la sesión iniciada
        self.assertEqual(self.client.get(reverse("panel")).status_code, 200)

    def test_correo_repetido(self):
        Usuario.objects.create_user("ana@empresa.com", "Clave$egura2026")
        r = self.client.post(reverse("registro"), {
            "nombre": "Ana Ruiz", "email": "ana@empresa.com", "password": "OtraClave#2026",
        })
        self.assertContains(r, "Ya existe una cuenta con este correo.")
        self.assertEqual(Usuario.objects.count(), 1)

    def test_validaciones(self):
        r = self.client.post(reverse("registro"), {"nombre": "Ana", "email": "no-es-correo", "password": "123"})
        self.assertContains(r, "Escribe tu nombre y tu apellido.")
        self.assertContains(r, "has-error")
        self.assertEqual(Usuario.objects.count(), 0)

    def test_contrasena_comun_rechazada(self):
        r = self.client.post(reverse("registro"), {"nombre": "Ana Ruiz", "email": "ana@empresa.com", "password": "password123"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Usuario.objects.count(), 0)


class LoginTests(TestCase):
    def setUp(self):
        Usuario.objects.create_user("ana@empresa.com", "Clave$egura2026", first_name="Ana")

    def test_login_con_correo(self):
        r = self.client.post(reverse("login"), {"username": "ANA@empresa.com", "password": "Clave$egura2026"})
        self.assertRedirects(r, reverse("panel"))

    def test_login_incorrecto(self):
        r = self.client.post(reverse("login"), {"username": "ana@empresa.com", "password": "mala"})
        self.assertContains(r, "Correo o contraseña incorrectos.")

    def test_recordar_sesion(self):
        self.client.post(reverse("login"), {"username": "ana@empresa.com", "password": "Clave$egura2026"})
        self.assertTrue(self.client.session.get_expire_at_browser_close())
        self.client.post(reverse("logout"))
        self.client.post(reverse("login"), {"username": "ana@empresa.com", "password": "Clave$egura2026", "recordar": "on"})
        self.assertFalse(self.client.session.get_expire_at_browser_close())

    def test_panel_pide_login(self):
        r = self.client.get(reverse("panel"))
        self.assertRedirects(r, reverse("login") + "?next=" + reverse("panel"))

    def test_cerrar_sesion(self):
        self.client.login(email="ana@empresa.com", password="Clave$egura2026")
        r = self.client.post(reverse("logout"))
        self.assertRedirects(r, reverse("login"))
        self.assertEqual(self.client.get(reverse("panel")).status_code, 302)


class RecuperarTests(TestCase):
    def test_flujo_completo(self):
        Usuario.objects.create_user("ana@empresa.com", "Vieja$Clave2026")

        # 1. Pide el enlace
        r = self.client.post(reverse("recuperar"), {"email": "ana@empresa.com"})
        self.assertRedirects(r, reverse("recuperar_enviado"))
        self.assertEqual(len(mail.outbox), 1)

        # 2. Abre el enlace del correo (Django lo redirige a una URL segura)
        enlace = re.search(r"https?://[^/]+(/\S+)", mail.outbox[0].body).group(1)
        r = self.client.get(enlace, follow=True)
        self.assertContains(r, "Restablecer contraseña")

        # 3. Guarda la contraseña nueva
        r = self.client.post(r.redirect_chain[-1][0], {
            "new_password1": "Nueva$Clave2026", "new_password2": "Nueva$Clave2026",
        })
        self.assertRedirects(r, reverse("recuperar_listo"))
        self.assertTrue(self.client.login(email="ana@empresa.com", password="Nueva$Clave2026"))

    def test_correo_inexistente_no_revela_nada(self):
        r = self.client.post(reverse("recuperar"), {"email": "nadie@empresa.com"})
        self.assertRedirects(r, reverse("recuperar_enviado"))  # misma respuesta
        self.assertEqual(len(mail.outbox), 0)

    def test_enlace_invalido(self):
        r = self.client.get(reverse("password_reset_confirm", args=["MQ", "token-falso"]))
        self.assertContains(r, "Enlace no válido")
