"""Carga masiva y reportes: solo el cargo más alto (superusuario). Ni el staff ni los perfiles normales entran."""

from django.test import Client, TestCase
from django.urls import reverse

from cuentas.models import Usuario

CLAVE = "Clave$egura2026"


class CargoMasAltoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.super = Usuario.objects.create_superuser("super@prueba.com", CLAVE, first_name="Super", last_name="Uno")
        cls.staff = Usuario.objects.create_user("staff@prueba.com", CLAVE, first_name="Staff", last_name="Uno", is_staff=True, perfil="profesional")
        cls.normal = Usuario.objects.create_user("normal@prueba.com", CLAVE, first_name="Normal", last_name="Uno", perfil="profesor")

    def cliente(self, usuario):
        c = Client()
        c.force_login(usuario)
        return c

    def test_superusuario_entra_a_carga_masiva_y_reportes(self):
        c = self.cliente(self.super)
        self.assertEqual(c.get(reverse("administracion:importar")).status_code, 200)
        self.assertEqual(c.get(reverse("administracion:reportes")).status_code, 200)
        self.assertEqual(c.get(reverse("administracion:importar_plantilla", args=["usuarios"])).status_code, 200)

    def test_staff_no_entra_a_carga_masiva_ni_reportes(self):
        c = self.cliente(self.staff)
        self.assertEqual(c.get(reverse("administracion:importar")).status_code, 403)
        self.assertEqual(c.get(reverse("administracion:reportes")).status_code, 403)
        self.assertEqual(c.get(reverse("administracion:importar_plantilla", args=["usuarios"])).status_code, 403)
        self.assertEqual(c.get(reverse("administracion:reportes_exportar", args=["xlsx"])).status_code, 403)

    def test_perfil_normal_no_entra(self):
        c = self.cliente(self.normal)
        for nombre in ("administracion:importar", "administracion:reportes"):
            self.assertEqual(c.get(reverse(nombre)).status_code, 403)

    def test_anonimo_va_al_login(self):
        for nombre in ("administracion:importar", "administracion:reportes"):
            self.assertEqual(Client().get(reverse(nombre)).status_code, 302)

    def test_staff_no_puede_importar_usuarios_por_post(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        archivo = SimpleUploadedFile("u.csv", b"email,nombre,apellido,perfil,cargo,telefono\nx@prueba.com,X,Y,estudiante,,\n", content_type="text/csv")
        r = self.cliente(self.staff).post(reverse("administracion:importar"), {"tipo": "usuarios", "accion": "importar", "archivo": archivo})
        self.assertEqual(r.status_code, 403)
        self.assertFalse(Usuario.objects.filter(email="x@prueba.com").exists())
