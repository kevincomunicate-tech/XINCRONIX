from django.test import TestCase
from django.urls import reverse

from cuentas.models import Usuario


class InicioTests(TestCase):
    def test_sin_sesion_muestra_la_portada(self):
        r = self.client.get(reverse("inicio"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, reverse("login"))
        self.assertContains(r, reverse("registro"))

    def test_con_sesion_va_a_su_inicio(self):
        self.client.force_login(Usuario.objects.create_user("ana@x.com", "Clave$egura2026"))
        self.assertRedirects(self.client.get(reverse("inicio")), reverse("panel"))
