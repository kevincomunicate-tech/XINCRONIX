"""Pruebas de caja blanca: revisan la lógica interna de cuentas.

Se llaman directamente funciones y métodos (sin pasar por HTTP) para cubrir
cada rama: superusuario, staff sin ser superusuario, anónimo y perfiles.
"""

from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from django.urls import reverse

from cuentas.models import Usuario
from cuentas.politica import Politica, obtener_politica

CLAVE = "Clave$egura2026"


class PoliticaCajaBlancaTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.politica = Politica()
        cls.super = Usuario.objects.create_superuser("super@prueba.com", CLAVE, first_name="Prueba", last_name="Usuario")
        cls.staff = Usuario.objects.create_user("staff@prueba.com", CLAVE, is_staff=True, perfil="profesor", first_name="Prueba", last_name="Usuario")
        cls.estudiante = Usuario.objects.create_user("est@prueba.com", CLAVE, perfil="estudiante", first_name="Prueba", last_name="Usuario")

    def test_obtener_politica_devuelve_siempre_la_misma_instancia(self):
        self.assertIs(obtener_politica(), obtener_politica())

    def test_perfil_de_anonimo(self):
        self.assertEqual(self.politica.perfil_de(AnonymousUser()), "anonimo")

    def test_perfil_de_superusuario_es_administrador(self):
        self.assertEqual(self.politica.perfil_de(self.super), Usuario.Rol.ADMIN)

    def test_staff_sin_ser_superusuario_NO_es_administrador(self):
        # Regresión del hueco de seguridad: antes "is_staff" daba perfil administrador.
        self.assertEqual(self.politica.perfil_de(self.staff), Usuario.Rol.USUARIO)

    def test_perfil_de_usuario_normal_sale_de_su_rol_global(self):
        self.assertEqual(self.politica.perfil_de(self.estudiante), Usuario.Rol.USUARIO)

    def test_es_superadministrador_solo_con_superusuario(self):
        self.assertTrue(self.politica.es_superadministrador(self.super))
        self.assertFalse(self.politica.es_superadministrador(self.staff))
        self.assertFalse(self.politica.es_superadministrador(self.estudiante))
        self.assertFalse(self.politica.es_superadministrador(AnonymousUser()))

    def test_admin_global_abre_administracion_sin_ser_superusuario(self):
        admin = Usuario.objects.create_user(
            "admin-global@prueba.com", CLAVE, first_name="Admin", last_name="Global", rol=Usuario.Rol.ADMIN,
        )
        self.assertFalse(admin.is_superuser)
        self.assertEqual(self.politica.url_inicio(admin), "/administracion/")
        self.client.force_login(admin)
        self.assertEqual(self.client.get("/administracion/").status_code, 200)
        self.assertEqual(self.client.post(reverse("administracion:editar_usuario", args=[self.super.pk])).status_code, 403)

    def test_url_inicio_segun_superusuario(self):
        self.assertEqual(self.politica.url_inicio(self.super), "/administracion/")
        self.assertEqual(self.politica.url_inicio(self.staff), "/app/")
        self.assertEqual(self.politica.url_inicio(self.estudiante), "/app/")

    def test_menu_solo_para_superusuario(self):
        self.assertEqual(self.politica.menu(self.super), [
            {"texto": "Administración", "href": "/administracion/", "icono": "bi-shield-lock", "activo": False},
        ])
        self.assertEqual(self.politica.menu(self.staff), [])
        self.assertEqual(self.politica.menu(self.estudiante), [])
        self.assertEqual(self.politica.menu(AnonymousUser()), [])

    def test_menu_marca_activo_si_la_ruta_es_administracion(self):
        self.assertTrue(self.politica.menu(self.super, "/administracion/usuarios/")[0]["activo"])

    def test_perfiles_permitidos_por_ruta(self):
        self.assertEqual(self.politica.perfiles_permitidos("/administracion/"), frozenset({Usuario.Rol.ADMIN}))
        self.assertEqual(self.politica.perfiles_permitidos("/administracion/monitoreo/"), frozenset({Usuario.Rol.ADMIN}))
        self.assertEqual(
            self.politica.perfiles_permitidos("/app/proyectos/"),
            frozenset(Usuario.Rol.values),
        )
        self.assertIsNone(self.politica.perfiles_permitidos("/cuentas/login/"))


class UsuarioManagerCajaBlancaTests(TestCase):
    def test_create_user_no_da_privilegios(self):
        u = Usuario.objects.create_user("normal@prueba.com", CLAVE, first_name="Prueba", last_name="Usuario")
        self.assertFalse(u.is_staff)
        self.assertFalse(u.is_superuser)
        self.assertTrue(u.check_password(CLAVE))

    def test_create_superuser_da_ambos_privilegios(self):
        u = Usuario.objects.create_superuser("root@prueba.com", CLAVE, first_name="Prueba", last_name="Usuario")
        self.assertTrue(u.is_staff)
        self.assertTrue(u.is_superuser)

    def test_create_superuser_rechaza_privilegios_incompletos(self):
        with self.assertRaises(ValueError):
            Usuario.objects.create_superuser("root2@prueba.com", CLAVE, is_superuser=False, first_name="Prueba", last_name="Usuario")

    def test_correo_obligatorio(self):
        with self.assertRaises(ValueError):
            Usuario.objects.create_user("", CLAVE, first_name="Prueba", last_name="Usuario")

    def test_correo_se_guarda_en_minusculas(self):
        u = Usuario.objects.create_user("Ana.Lopez@Prueba.COM", CLAVE, first_name="Prueba", last_name="Usuario")
        self.assertEqual(u.email, "ana.lopez@prueba.com")
