"""Mi cuenta: cada persona ve, edita y elimina su propia información."""

from django.test import TestCase
from django.urls import reverse

from .models import Empresa, Usuario

CLAVE = "Clave$egura2026"


class MiCuentaTests(TestCase):
    def setUp(self):
        self.ana = Usuario.objects.create_user("ana@x.com", CLAVE, first_name="Ana")
        self.client.force_login(self.ana)

    def test_editar_mis_datos(self):
        r = self.client.post(reverse("mi_cuenta"), {
            "first_name": "Ana María", "last_name": "Ruiz", "email": "ANA.RUIZ@x.com", "cargo": "Diseñadora", "telefono": "300",
        })
        self.assertRedirects(r, reverse("mi_cuenta"))
        self.ana.refresh_from_db()
        self.assertEqual((self.ana.get_full_name(), self.ana.email, self.ana.cargo), ("Ana María Ruiz", "ana.ruiz@x.com", "Diseñadora"))

    def test_no_puede_tomar_el_correo_de_otro(self):
        Usuario.objects.create_user("beto@x.com", CLAVE)
        r = self.client.post(reverse("mi_cuenta"), {"first_name": "Ana", "email": "beto@x.com"})
        self.assertContains(r, "Ya existe otra cuenta con este correo.")

    def test_cambiar_contrasena_pide_la_actual(self):
        url = reverse("cambiar_contrasena")
        r = self.client.post(url, {"actual": "mala", "new_password1": "Nueva$Clave2026", "new_password2": "Nueva$Clave2026"})
        self.assertContains(r, "La contraseña actual no es correcta.")
        r = self.client.post(url, {"actual": CLAVE, "new_password1": "Nueva$Clave2026", "new_password2": "Nueva$Clave2026"})
        self.assertRedirects(r, reverse("mi_cuenta"))
        self.ana.refresh_from_db()
        self.assertTrue(self.ana.check_password("Nueva$Clave2026"))
        self.assertEqual(self.client.get(reverse("mi_cuenta")).status_code, 200)  # sigue con la sesión

    def test_cuenta_de_google_crea_contrasena_sin_pedir_la_actual(self):
        self.ana.set_unusable_password()
        self.ana.save()
        self.client.force_login(self.ana)  # cambiar la contraseña invalida la sesión anterior
        r = self.client.post(reverse("cambiar_contrasena"), {"new_password1": "Nueva$Clave2026", "new_password2": "Nueva$Clave2026"})
        self.assertRedirects(r, reverse("mi_cuenta"))

    def test_eliminar_cuenta_pide_confirmar_con_el_correo(self):
        url = reverse("eliminar_cuenta")
        r = self.client.post(url, {"confirmacion": "otro@x.com"})
        self.assertContains(r, "El correo no coincide")
        self.assertTrue(Usuario.objects.filter(pk=self.ana.pk).exists())

    def test_eliminar_cuenta_borra_su_empresa_si_esta_sola(self):
        sola = Empresa.objects.create(nombre="Solo Ana", propietario=self.ana)
        compartida = Empresa.objects.create(nombre="Con Beto", propietario=self.ana)
        self.ana.empresa = sola
        self.ana.save()
        Usuario.objects.create_user("beto@x.com", CLAVE, empresa=compartida)

        r = self.client.get(reverse("eliminar_cuenta"))
        self.assertContains(r, "Se elimina tu empresa «Solo Ana»")
        self.assertContains(r, "«Con Beto» sigue existiendo")

        r = self.client.post(reverse("eliminar_cuenta"), {"confirmacion": "ana@x.com"})
        self.assertRedirects(r, reverse("login"))
        self.assertFalse(Usuario.objects.filter(email="ana@x.com").exists())
        self.assertFalse(Empresa.objects.filter(pk=sola.pk).exists())
        compartida.refresh_from_db()
        self.assertIsNone(compartida.propietario)
        self.assertEqual(Usuario.objects.get(email="beto@x.com").empresa, compartida)
        self.assertNotIn("_auth_user_id", self.client.session)  # se cerró la sesión

    def test_el_superadministrador_no_elimina_su_cuenta(self):
        super_ = Usuario.objects.create_superuser("cuellaryohan100@gmail.com", CLAVE)
        self.client.force_login(super_)
        self.assertEqual(self.client.get(reverse("eliminar_cuenta")).status_code, 403)
        self.assertNotContains(self.client.get(reverse("mi_cuenta")), reverse("eliminar_cuenta"))

    def test_mi_cuenta_pide_sesion(self):
        self.client.logout()
        self.assertRedirects(self.client.get(reverse("mi_cuenta")), f"{reverse('login')}?next={reverse('mi_cuenta')}")
