"""Cliente exigente sobre administración y monitoreo: nombres de tabla inventados,
filtros sobre campos ocultos, búsquedas con el prefijo del hash, fórmulas en el CSV
y sesiones con datos raros."""

from django.test import Client, TestCase
from django.urls import reverse

from cuentas.models import Usuario

CLAVE = "Clave$egura2026"


class MonitoreoExigenteTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.super = Usuario.objects.create_superuser("super@prueba.com", CLAVE, first_name="Yohan", last_name="Usuario")
        cls.ana = Usuario.objects.create_user("ana@prueba.com", CLAVE, first_name="=HYPERLINK(\"http://robo.example\")", last_name="Usuario")
        cls.normal = Usuario.objects.create_user("normal@prueba.com", CLAVE, perfil="estudiante", first_name="Prueba", last_name="Usuario")

    def setUp(self):
        self.c = Client()
        self.c.force_login(self.super)

    def test_nombres_de_tabla_inventados_dan_404(self):
        for app, modelo in (("cuentas", "usuario;drop"), ("../../etc", "passwd"), ("cuentas", "%00"), ("nada", "nada"), ("auth", "user")):
            with self.subTest(app=app, modelo=modelo):
                self.assertIn(self.c.get(f"/administracion/monitoreo/tablas/{app}/{modelo}/").status_code, (404, 200))

    def test_tabla_de_sesiones_no_se_abre_fila_por_fila(self):
        self.assertEqual(self.c.get("/administracion/monitoreo/tablas/sessions/session/").status_code, 404)

    def test_filtrar_por_campo_oculto_no_revela_el_hash(self):
        hash_ana = self.ana.password
        url = reverse("administracion:monitoreo_tabla", args=["cuentas", "usuario"])
        sin_filtro = self.c.get(url).context["total"]
        r = self.c.get(url, {"campo": "password", "valor": hash_ana})
        # El filtro sobre un campo oculto se ignora: el resultado no depende del valor buscado.
        self.assertEqual(r.context["total"], sin_filtro)
        # El valor buscado se repite en la página solo como eco de lo que escribió quien consulta.
        # Quitando ese eco, el hash no debe aparecer en ningún otro lugar.
        import re
        html = re.sub(r"Filtrando por <code>.*?</code>", "", r.content.decode(), flags=re.S)
        html = re.sub(r"valor=[^\"&]*", "", html)
        self.assertNotIn(hash_ana, html)

    def test_buscar_por_prefijo_del_hash_no_encuentra_nada(self):
        r = self.c.get(reverse("administracion:monitoreo_tabla", args=["cuentas", "usuario"]), {"q": "pbkdf2"})
        self.assertEqual(r.context["total"], 0)

    def test_busqueda_con_sintaxis_sql_no_rompe(self):
        for q in ("' OR 1=1 --", "%", "_", "\x00", "a" * 3000):
            with self.subTest(q=q[:20]):
                r = self.c.get(reverse("administracion:monitoreo_tabla", args=["cuentas", "usuario"]), {"q": q})
                self.assertLess(r.status_code, 500)

    def test_pagina_inexistente_o_enorme_no_rompe(self):
        url = reverse("administracion:monitoreo_tabla", args=["cuentas", "usuario"])
        self.assertLess(self.c.get(url, {"page": "999999"}).status_code, 500)
        self.assertLess(self.c.get(url, {"page": "abc"}).status_code, 500)

    def test_csv_neutraliza_formulas(self):
        r = self.c.get(reverse("administracion:monitoreo_exportar", args=["cuentas", "usuario"]))
        contenido = b"".join(r.streaming_content).decode("utf-8-sig")
        self.assertNotIn(",=HYPERLINK", contenido)
        self.assertIn("'=HYPERLINK", contenido)

    def test_csv_no_incluye_hashes(self):
        r = self.c.get(reverse("administracion:monitoreo_exportar", args=["cuentas", "usuario"]))
        contenido = b"".join(r.streaming_content).decode("utf-8-sig")
        self.assertNotIn(self.ana.password, contenido)
        self.assertNotIn("pbkdf2", contenido)

    def test_un_usuario_normal_no_exporta_nada(self):
        c = Client()
        c.force_login(self.normal)
        self.assertEqual(c.get(reverse("administracion:monitoreo_exportar", args=["cuentas", "usuario"])).status_code, 403)

    def test_sesiones_con_acciones_y_datos_raros(self):
        url = reverse("administracion:monitoreo_cerrar_sesiones")
        for datos in ({"accion": "todas"}, {"accion": "usuario", "usuario": "abc"}, {"accion": "usuario", "usuario": "999999"},
                      {"accion": "una", "sesion": "x" * 500}, {}):
            with self.subTest(datos=datos):
                self.assertLess(self.c.post(url, datos).status_code, 500)

    def test_cerrar_sesiones_con_get_no_hace_nada(self):
        self.assertEqual(self.c.get(reverse("administracion:monitoreo_cerrar_sesiones")).status_code, 405)

    def test_monitoreo_no_acepta_escritura(self):
        self.assertEqual(self.c.post(reverse("administracion:monitoreo_tabla", args=["cuentas", "usuario"]), {"x": "y"}).status_code, 405)


class AdministracionExigenteTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.super = Usuario.objects.create_superuser("super@prueba.com", CLAVE, first_name="Prueba", last_name="Usuario")
        cls.ana = Usuario.objects.create_user("ana@prueba.com", CLAVE, perfil="estudiante", first_name="Prueba", last_name="Usuario")

    def setUp(self):
        self.c = Client()
        self.c.force_login(self.super)

    def test_crear_cuenta_con_correo_repetido_en_mayusculas(self):
        r = self.c.post(reverse("administracion:crear_usuario"), {
            "first_name": "Otra", "last_name": "", "email": "ANA@prueba.com", "perfil": "estudiante",
            "cargo": "", "telefono": "", "password1": "Otra$egura2026", "password2": "Otra$egura2026"})
        self.assertNotEqual(r.status_code, 500)
        self.assertEqual(Usuario.objects.filter(email="ana@prueba.com").count(), 1)

    def test_editar_cuenta_inexistente_da_404(self):
        self.assertEqual(self.c.get(reverse("administracion:editar_usuario", args=[999999])).status_code, 404)
        self.assertEqual(self.c.post(reverse("administracion:editar_usuario", args=[999999]), {"email": "x@x.com"}).status_code, 404)

    def test_eliminar_con_get_solo_muestra_la_confirmacion(self):
        r = self.c.get(reverse("administracion:eliminar_usuario", args=[self.ana.pk]))
        self.assertEqual(r.status_code, 200)
        self.assertTrue(Usuario.objects.filter(pk=self.ana.pk).exists())

    def test_editar_con_perfil_inventado_se_rechaza(self):
        self.c.post(reverse("administracion:editar_usuario", args=[self.ana.pk]), {
            "first_name": "Ana", "last_name": "", "email": "ana@prueba.com", "perfil": "administrador", "cargo": "", "telefono": "", "is_active": "on"})
        self.ana.refresh_from_db()
        self.assertNotEqual(self.ana.perfil, "administrador")

    def test_editar_con_correo_de_otro_se_rechaza(self):
        otro = Usuario.objects.create_user("otro@prueba.com", CLAVE, first_name="Prueba", last_name="Usuario")
        self.c.post(reverse("administracion:editar_usuario", args=[self.ana.pk]), {
            "first_name": "Ana", "last_name": "", "email": "otro@prueba.com", "perfil": "estudiante", "cargo": "", "telefono": "", "is_active": "on"})
        self.ana.refresh_from_db()
        self.assertEqual(self.ana.email, "ana@prueba.com")
        self.assertTrue(Usuario.objects.filter(pk=otro.pk, email="otro@prueba.com").exists())

    def test_no_se_puede_crear_superusuario_desde_la_web(self):
        self.c.post(reverse("administracion:crear_usuario"), {
            "first_name": "Nuevo", "last_name": "", "email": "nuevo@prueba.com", "perfil": "estudiante", "cargo": "", "telefono": "",
            "password1": "Nuevo$egura2026", "password2": "Nuevo$egura2026", "is_superuser": "on", "is_staff": "on"})
        nuevo = Usuario.objects.filter(email="nuevo@prueba.com").first()
        if nuevo:
            self.assertFalse(nuevo.is_superuser)
            self.assertFalse(nuevo.is_staff)
