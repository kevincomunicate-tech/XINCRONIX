"""Seguridad de cuentas: sesiones, cambios de perfil, cierre de sesión y cuentas inactivas."""

from django.test import Client, TestCase
from django.urls import reverse

from cuentas.models import Usuario

CLAVE = "Clave$egura2026"


class SeguridadExtraTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.super = Usuario.objects.create_superuser("super@prueba.com", CLAVE, first_name="Super", last_name="Uno")
        cls.ana = Usuario.objects.create_user("ana@prueba.com", CLAVE, first_name="Ana", last_name="Ruiz", perfil="estudiante")

    def test_mi_cuenta_no_deja_el_nombre_vacio(self):
        c = Client()
        c.force_login(self.ana)
        c.post(reverse("mi_cuenta"), {"first_name": "", "last_name": "Ruiz", "email": "ana@prueba.com", "perfil": "estudiante", "cargo": "", "telefono": ""})
        self.ana.refresh_from_db()
        self.assertEqual(self.ana.first_name, "Ana")

    def test_mi_cuenta_no_deja_el_apellido_vacio(self):
        c = Client()
        c.force_login(self.ana)
        c.post(reverse("mi_cuenta"), {"first_name": "Ana", "last_name": "", "email": "ana@prueba.com", "perfil": "estudiante", "cargo": "", "telefono": ""})
        self.ana.refresh_from_db()
        self.assertEqual(self.ana.last_name, "Ruiz")

    def test_el_formulario_de_administracion_no_permite_quitarse_el_permiso(self):
        c = Client()
        c.force_login(self.super)
        c.post(reverse("administracion:editar_usuario", args=[self.super.pk]), {
            "first_name": "Super", "last_name": "Uno", "email": "super@prueba.com", "perfil": "profesional",
            "cargo": "", "telefono": "", "is_active": "on", "is_superuser": ""})
        self.super.refresh_from_db()
        self.assertTrue(self.super.is_superuser)

    def test_crear_cuenta_desde_administracion_sin_nombre_no_guarda(self):
        c = Client()
        c.force_login(self.super)
        c.post(reverse("administracion:crear_usuario"), {"first_name": "", "last_name": "", "email": "nuevo@prueba.com",
                                                         "perfil": "estudiante", "cargo": "", "telefono": "",
                                                         "password1": CLAVE, "password2": CLAVE})
        self.assertFalse(Usuario.objects.filter(email="nuevo@prueba.com").exists())

    def test_cerrar_sesion_solo_con_post(self):
        c = Client()
        c.force_login(self.ana)
        self.assertEqual(c.get(reverse("logout")).status_code, 405)
        self.assertEqual(c.get(reverse("panel")).status_code, 200)

    def test_cambiar_la_contrasena_no_cierra_la_sesion_actual(self):
        c = Client()
        c.force_login(self.ana)
        c.post(reverse("cambiar_contrasena"), {"old_password": CLAVE, "new_password1": "Nueva$egura2027", "new_password2": "Nueva$egura2027"})
        self.assertEqual(c.get(reverse("panel")).status_code, 200)

    def test_cuenta_inactiva_no_inicia_sesion(self):
        Usuario.objects.filter(pk=self.ana.pk).update(is_active=False)
        r = Client().post(reverse("login"), {"username": "ana@prueba.com", "password": CLAVE})
        self.assertEqual(r.status_code, 200)

    def test_superusuario_inactivo_no_entra_a_administracion(self):
        Usuario.objects.create_superuser("otro@prueba.com", CLAVE, first_name="Otro", last_name="Root", is_active=False)
        c = Client()
        c.post(reverse("login"), {"username": "otro@prueba.com", "password": CLAVE})
        self.assertEqual(c.get(reverse("administracion:inicio")).status_code, 302)

    def test_el_correo_no_se_puede_cambiar_por_el_de_un_superusuario(self):
        c = Client()
        c.force_login(self.ana)
        c.post(reverse("mi_cuenta"), {"first_name": "Ana", "last_name": "Ruiz", "email": "super@prueba.com", "perfil": "estudiante", "cargo": "", "telefono": ""})
        self.ana.refresh_from_db()
        self.assertEqual(self.ana.email, "ana@prueba.com")

    def test_la_contrasena_no_queda_en_texto_plano(self):
        self.assertNotIn(CLAVE, self.ana.password)
        self.assertTrue(self.ana.password.startswith("pbkdf2_"))
