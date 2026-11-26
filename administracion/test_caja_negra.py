"""Pruebas de caja negra de administración: reglas de seguridad vistas desde HTTP."""

from django.test import Client, TestCase
from django.urls import reverse

from cuentas.models import Usuario

CLAVE = "Clave$egura2026"


class SeguridadAdministracionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.super = Usuario.objects.create_superuser("super@prueba.com", CLAVE, first_name="Prueba", last_name="Usuario")
        cls.otro_super = Usuario.objects.create_superuser("super2@prueba.com", CLAVE, first_name="Prueba", last_name="Usuario")
        cls.staff = Usuario.objects.create_user("staff@prueba.com", CLAVE, is_staff=True, perfil="profesional", first_name="Prueba", last_name="Usuario")
        cls.normal = Usuario.objects.create_user("normal@prueba.com", CLAVE, perfil="estudiante", first_name="Prueba", last_name="Usuario")

    def cliente(self, usuario):
        c = Client()
        c.force_login(usuario)
        return c

    def test_staff_no_puede_borrar_al_superusuario(self):
        r = self.cliente(self.staff).post(reverse("administracion:eliminar_usuario", args=[self.super.pk]))
        self.assertEqual(r.status_code, 403)
        self.assertTrue(Usuario.objects.filter(pk=self.super.pk).exists())

    def test_staff_no_puede_crear_cuentas(self):
        self.assertEqual(self.cliente(self.staff).get(reverse("administracion:crear_usuario")).status_code, 403)

    def test_superusuario_puede_borrar_a_otro_si_queda_otro_activo(self):
        # Con dos superusuarios activos, uno puede borrar al otro: queda uno activo.
        r = self.cliente(self.super).post(reverse("administracion:eliminar_usuario", args=[self.otro_super.pk]))
        self.assertEqual(r.status_code, 302)
        self.assertFalse(Usuario.objects.filter(pk=self.otro_super.pk).exists())
        self.assertTrue(Usuario.objects.filter(pk=self.super.pk, is_superuser=True, is_active=True).exists())

    def test_nadie_puede_dejar_el_sistema_sin_superusuario_activo(self):
        # Primero se desactiva al otro; después el que queda no puede desactivarse ni borrarse.
        cliente = self.cliente(self.super)
        cliente.post(reverse("administracion:editar_usuario", args=[self.otro_super.pk]), self._datos(self.otro_super, activo=""))
        self.otro_super.refresh_from_db()
        self.assertFalse(self.otro_super.is_active)

        cliente.post(reverse("administracion:editar_usuario", args=[self.super.pk]), self._datos(self.super, activo=""))
        self.super.refresh_from_db()
        self.assertTrue(self.super.is_active, "el último superusuario activo no se puede desactivar")

        r = cliente.post(reverse("administracion:eliminar_usuario", args=[self.super.pk]), follow=True)
        self.assertContains(r, "quedaría el sistema sin ningún superusuario activo")
        self.assertTrue(Usuario.objects.filter(pk=self.super.pk).exists())

    def test_superusuario_puede_borrarse_si_queda_otro_activo(self):
        cliente = self.cliente(self.super)
        r = cliente.post(reverse("administracion:eliminar_usuario", args=[self.super.pk]))
        self.assertEqual(r.status_code, 302)
        self.assertFalse(Usuario.objects.filter(pk=self.super.pk).exists())
        self.assertTrue(Usuario.objects.filter(pk=self.otro_super.pk, is_active=True).exists())

    def test_superusuario_unico_no_puede_borrarse_desde_administracion(self):
        solo = Usuario.objects.create_superuser("solo@prueba.com", CLAVE, first_name="Prueba", last_name="Usuario")
        # Se borran los otros dos en un solo lote: también debe respetarse la regla.
        Usuario.objects.filter(pk__in=[self.super.pk, self.otro_super.pk]).delete()
        r = self.cliente(solo).post(reverse("administracion:eliminar_usuario", args=[solo.pk]), follow=True)
        self.assertContains(r, "quedaría el sistema sin ningún superusuario activo")
        self.assertTrue(Usuario.objects.filter(pk=solo.pk).exists())

    def _datos(self, usuario, activo="on"):
        datos = {"first_name": usuario.first_name, "last_name": usuario.last_name, "email": usuario.email,
                 "perfil": usuario.perfil, "cargo": "", "telefono": ""}
        if activo:
            datos["is_active"] = activo
        return datos

    def test_superusuario_si_puede_borrar_a_una_cuenta_normal(self):
        r = self.cliente(self.super).post(reverse("administracion:eliminar_usuario", args=[self.normal.pk]))
        self.assertEqual(r.status_code, 302)
        self.assertFalse(Usuario.objects.filter(pk=self.normal.pk).exists())

    def test_superusuario_si_puede_desactivar_una_cuenta_normal(self):
        self.cliente(self.super).post(reverse("administracion:editar_usuario", args=[self.normal.pk]), {
            "first_name": "Normal", "last_name": "Prueba", "email": "normal@prueba.com", "perfil": "estudiante",
            "cargo": "", "telefono": "", "is_active": "",
        })
        self.normal.refresh_from_db()
        self.assertFalse(self.normal.is_active)

    def test_lista_de_usuarios_solo_para_superusuario(self):
        self.assertEqual(self.cliente(self.super).get(reverse("administracion:inicio")).status_code, 200)
        self.assertEqual(self.cliente(self.staff).get(reverse("administracion:inicio")).status_code, 403)
        self.assertEqual(Client().get(reverse("administracion:inicio")).status_code, 302)
