"""Pruebas de caja negra de cuentas: solo se usa HTTP, como lo haría una persona.

No se revisan modelos ni funciones internas: se entra, se envían formularios y
se comprueba lo que ve el usuario (códigos de respuesta, redirecciones, datos).
"""

from django.test import Client, TestCase
from django.urls import reverse

from cuentas.models import Usuario

CLAVE = "Clave$egura2026"


class PaginasPublicasTests(TestCase):
    def test_portada_y_formularios_publicos_responden(self):
        cliente = Client()
        for ruta in ("/", "/cuentas/login/", "/cuentas/registro/", "/cuentas/recuperar/"):
            with self.subTest(ruta=ruta):
                self.assertEqual(cliente.get(ruta).status_code, 200)

    def test_login_muestra_el_boton_de_google(self):
        self.assertContains(Client().get(reverse("login")), "Google")


class LoginTests(TestCase):
    def setUp(self):
        Usuario.objects.create_user("ana@prueba.com", CLAVE, first_name="Ana", perfil="estudiante", last_name="Usuario")

    def test_inicia_sesion_con_correo_y_clave(self):
        r = Client().post(reverse("login"), {"username": "ana@prueba.com", "password": CLAVE})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r["Location"], "/app/")

    def test_clave_incorrecta_no_entra(self):
        cliente = Client()
        r = cliente.post(reverse("login"), {"username": "ana@prueba.com", "password": "otra-clave"})
        self.assertEqual(r.status_code, 200)  # vuelve a mostrar el formulario
        self.assertNotIn("_auth_user_id", cliente.session)
        self.assertEqual(cliente.get(reverse("panel")).status_code, 302)

    def test_superusuario_entra_a_administracion(self):
        Usuario.objects.create_superuser("super@prueba.com", CLAVE, first_name="Prueba", last_name="Usuario")
        r = Client().post(reverse("login"), {"username": "super@prueba.com", "password": CLAVE})
        self.assertEqual(r["Location"], "/administracion/")


class RegistroTests(TestCase):
    def test_registro_crea_cuenta_normal_e_inicia_sesion(self):
        cliente = Client()
        r = cliente.post(reverse("registro"), {
            "nombre": "Luis Pérez", "email": "luis@prueba.com", "perfil": "profesional", "password": CLAVE,
        })
        self.assertEqual(r.status_code, 302)
        usuario = Usuario.objects.get(email="luis@prueba.com")
        self.assertFalse(usuario.is_staff)
        self.assertFalse(usuario.is_superuser)
        self.assertEqual(usuario.perfil, "profesional")
        self.assertEqual(cliente.get(reverse("panel")).status_code, 200)

    def test_registro_no_permite_pedirse_privilegios(self):
        # Aunque se envíen campos extra, el registro no crea administradores.
        Client().post(reverse("registro"), {
            "nombre": "Intruso Prueba", "email": "intruso@prueba.com", "perfil": "estudiante", "password": CLAVE,
            "is_superuser": "on", "is_staff": "on",
        })
        self.assertFalse(Usuario.objects.get(email="intruso@prueba.com").is_superuser)

    def test_con_sesion_no_muestra_el_registro(self):
        u = Usuario.objects.create_user("ya@prueba.com", CLAVE, first_name="Prueba", last_name="Usuario")
        cliente = Client()
        cliente.force_login(u)
        self.assertEqual(cliente.get(reverse("registro")).status_code, 302)


class MiCuentaTests(TestCase):
    def setUp(self):
        self.u = Usuario.objects.create_user("eli@prueba.com", CLAVE, first_name="Eli", perfil="estudiante", last_name="Usuario")
        self.cliente = Client()
        self.cliente.force_login(self.u)

    def test_ve_su_cuenta(self):
        self.assertEqual(self.cliente.get(reverse("mi_cuenta")).status_code, 200)

    def test_eliminar_cuenta_pide_confirmar_con_el_correo(self):
        r = self.cliente.post(reverse("eliminar_cuenta"), {"confirmacion": "otro@prueba.com"})
        self.assertEqual(r.status_code, 200)
        self.assertTrue(Usuario.objects.filter(pk=self.u.pk).exists())

    def test_eliminar_cuenta_con_correo_correcto(self):
        self.cliente.post(reverse("eliminar_cuenta"), {"confirmacion": "eli@prueba.com"})
        self.assertFalse(Usuario.objects.filter(pk=self.u.pk).exists())


class MatrizDeAccesoTests(TestCase):
    """Qué ve cada tipo de persona. Esta es la tabla de acceso del proyecto."""

    RUTAS_APP = ["/app/", "/app/proyectos/", "/app/tareas/"]
    RUTAS_ADMIN = ["/administracion/", "/administracion/monitoreo/", "/administracion/monitoreo/sistema/"]

    @classmethod
    def setUpTestData(cls):
        cls.super = Usuario.objects.create_superuser("super@prueba.com", CLAVE, first_name="Prueba", last_name="Usuario")
        cls.staff = Usuario.objects.create_user("staff@prueba.com", CLAVE, is_staff=True, perfil="profesional", first_name="Prueba", last_name="Usuario")
        cls.estudiante = Usuario.objects.create_user("est@prueba.com", CLAVE, perfil="estudiante", first_name="Prueba", last_name="Usuario")
        cls.profesional = Usuario.objects.create_user("prof@prueba.com", CLAVE, perfil="profesional", first_name="Prueba", last_name="Usuario")
        cls.profesor = Usuario.objects.create_user("profesor@prueba.com", CLAVE, perfil="profesor", first_name="Prueba", last_name="Usuario")

    def _cliente(self, usuario):
        c = Client()
        if usuario is not None:
            c.force_login(usuario)
        return c

    def test_anonimo_va_al_login_en_todas_las_rutas(self):
        c = self._cliente(None)
        for ruta in self.RUTAS_APP + self.RUTAS_ADMIN:
            with self.subTest(ruta=ruta):
                r = c.get(ruta)
                self.assertEqual(r.status_code, 302)
                self.assertIn("/cuentas/login/", r["Location"])

    def test_perfiles_normales_usan_app_y_no_administracion(self):
        for usuario in (self.estudiante, self.profesional, self.profesor):
            c = self._cliente(usuario)
            for ruta in self.RUTAS_APP:
                with self.subTest(usuario=usuario.email, ruta=ruta):
                    self.assertEqual(c.get(ruta).status_code, 200)
            for ruta in self.RUTAS_ADMIN:
                with self.subTest(usuario=usuario.email, ruta=ruta):
                    self.assertEqual(c.get(ruta).status_code, 403)

    def test_staff_sin_superusuario_no_entra_a_administracion(self):
        c = self._cliente(self.staff)
        for ruta in self.RUTAS_APP:
            self.assertEqual(c.get(ruta).status_code, 200)
        for ruta in self.RUTAS_ADMIN:
            with self.subTest(ruta=ruta):
                self.assertEqual(c.get(ruta).status_code, 403)

    def test_superusuario_entra_a_todo(self):
        c = self._cliente(self.super)
        for ruta in self.RUTAS_APP + self.RUTAS_ADMIN:
            with self.subTest(ruta=ruta):
                self.assertEqual(c.get(ruta).status_code, 200)

    def test_menu_muestra_administracion_solo_al_superusuario(self):
        self.assertContains(self._cliente(self.super).get("/app/"), "Administración")
        self.assertNotContains(self._cliente(self.staff).get("/app/"), "bi-shield-lock")
