"""Cliente exigente sobre cuentas: registro, inicio de sesión, correo, contraseña y
enlaces. Cada prueba intenta romper algo y dice qué debe pasar."""

from django.core import mail
from django.test import Client, TestCase
from django.urls import reverse

from cuentas.models import Usuario

CLAVE = "Clave$egura2026"


class RegistroExigenteTests(TestCase):
    def registrar(self, **datos):
        base = {"nombre": "Ana Ruiz", "email": "ana@prueba.com", "perfil": "estudiante", "password": CLAVE}
        base.update(datos)
        return Client().post(reverse("registro"), base)

    def test_no_se_puede_registrar_con_perfil_de_administrador(self):
        self.registrar(perfil="administrador")
        self.assertFalse(Usuario.objects.filter(email="ana@prueba.com").exists())

    def test_contrasena_muy_comun_o_solo_numeros_se_rechaza(self):
        for clave in ("12345678", "password", "11111111"):
            with self.subTest(clave=clave):
                self.registrar(email=f"{clave}@prueba.com", password=clave)
                self.assertFalse(Usuario.objects.filter(email=f"{clave}@prueba.com").exists())

    def test_contrasena_igual_al_correo_se_rechaza(self):
        self.registrar(email="ana.ruiz@prueba.com", password="ana.ruiz@prueba.com")
        self.assertFalse(Usuario.objects.filter(email="ana.ruiz@prueba.com").exists())

    def test_correo_repetido_con_mayusculas_no_rompe_el_servidor(self):
        Usuario.objects.create_user("ana@prueba.com", CLAVE, first_name="Prueba", last_name="Usuario")
        r = self.registrar(email="ANA@Prueba.COM")
        self.assertNotEqual(r.status_code, 500)
        self.assertEqual(Usuario.objects.filter(email="ana@prueba.com").count(), 1)

    def test_nombre_con_codigo_html_se_muestra_escapado(self):
        self.registrar(nombre="<script>alert('x')</script> Ana")
        cliente = Client()
        cliente.login(username="ana@prueba.com", password=CLAVE)
        html = cliente.get(reverse("mi_cuenta")).content.decode()
        self.assertNotIn("<script>alert('x')</script>", html)
        self.assertIn("&lt;script&gt;", html)

    def test_nombre_con_caracter_nulo_se_rechaza_sin_error_500(self):
        r = self.registrar(nombre="Ana\x00Ruiz")
        self.assertNotEqual(r.status_code, 500)
        self.assertFalse(Usuario.objects.filter(email="ana@prueba.com").exists())

    def test_nombre_demasiado_largo_se_rechaza(self):
        self.registrar(nombre="A" * 5000)
        self.assertFalse(Usuario.objects.filter(email="ana@prueba.com").exists())

    def test_correo_invalido_se_rechaza(self):
        for correo in ("no-es-correo", "a@", "@b.com", "a b@c.com", "x" * 300 + "@b.com"):
            with self.subTest(correo=correo):
                self.registrar(email=correo)
                self.assertFalse(Usuario.objects.filter(email=correo).exists())

    def test_campos_extra_de_privilegio_se_ignoran(self):
        self.registrar(is_superuser="on", is_staff="on", is_active="on")
        u = Usuario.objects.get(email="ana@prueba.com")
        self.assertFalse(u.is_superuser)
        self.assertFalse(u.is_staff)


class InicioDeSesionExigenteTests(TestCase):
    def setUp(self):
        self.ana = Usuario.objects.create_user("ana@prueba.com", CLAVE, perfil="estudiante", first_name="Prueba", last_name="Usuario")

    def test_redireccion_abierta_no_lleva_a_otro_sitio(self):
        r = Client().post(reverse("login") + "?next=https://evil.example/robar", {"username": "ana@prueba.com", "password": CLAVE})
        self.assertNotIn("evil.example", r.get("Location", ""))

    def test_next_relativo_sigue_funcionando(self):
        r = Client().post(reverse("login") + "?next=/app/tareas/", {"username": "ana@prueba.com", "password": CLAVE})
        self.assertEqual(r["Location"], "/app/tareas/")

    def test_clave_incorrecta_repetida_no_tumba_el_servidor(self):
        c = Client()
        for _ in range(30):
            r = c.post(reverse("login"), {"username": "ana@prueba.com", "password": "mala-clave"})
            self.assertEqual(r.status_code, 200)

    def test_cuenta_desactivada_no_puede_entrar(self):
        self.ana.is_active = False
        self.ana.save()
        c = Client()
        c.post(reverse("login"), {"username": "ana@prueba.com", "password": CLAVE})
        self.assertEqual(c.get(reverse("panel")).status_code, 302)

    def test_sesion_se_invalida_al_cerrarla(self):
        c = Client()
        c.force_login(self.ana)
        c.post(reverse("logout"))
        self.assertEqual(c.get(reverse("panel")).status_code, 302)

    def test_cookie_de_sesion_inventada_no_da_acceso(self):
        c = Client()
        c.cookies["sessionid"] = "inventada-123"
        self.assertEqual(c.get(reverse("panel")).status_code, 302)

    def test_el_correo_no_distingue_mayusculas_al_entrar(self):
        r = Client().post(reverse("login"), {"username": "ANA@PRUEBA.COM", "password": CLAVE})
        self.assertEqual(r.status_code, 302, "con el correo en mayúsculas debe poder entrar")


class CorreoYContrasenaExigenteTests(TestCase):
    def setUp(self):
        self.ana = Usuario.objects.create_user("ana@prueba.com", CLAVE, perfil="estudiante", first_name="Prueba", last_name="Usuario")
        self.beto = Usuario.objects.create_user("beto@prueba.com", CLAVE, perfil="estudiante", first_name="Prueba", last_name="Usuario")
        self.c = Client()
        self.c.force_login(self.ana)

    def test_no_se_puede_cambiar_el_correo_a_uno_ya_usado(self):
        self.c.post(reverse("mi_cuenta"), {"first_name": "Ana", "last_name": "", "email": "beto@prueba.com", "perfil": "estudiante", "cargo": "", "telefono": ""})
        self.ana.refresh_from_db()
        self.assertEqual(self.ana.email, "ana@prueba.com")

    def test_no_se_puede_cambiar_el_correo_a_uno_ya_usado_con_mayusculas(self):
        self.c.post(reverse("mi_cuenta"), {"first_name": "Ana", "last_name": "", "email": "BETO@prueba.com", "perfil": "estudiante", "cargo": "", "telefono": ""})
        self.ana.refresh_from_db()
        self.assertEqual(self.ana.email, "ana@prueba.com")

    def test_no_se_puede_elegir_perfil_de_administrador_en_mi_cuenta(self):
        self.c.post(reverse("mi_cuenta"), {"first_name": "Ana", "last_name": "", "email": "ana@prueba.com", "perfil": "administrador", "cargo": "", "telefono": ""})
        self.ana.refresh_from_db()
        self.assertNotEqual(self.ana.perfil, "administrador")

    def test_cambiar_contrasena_exige_la_actual(self):
        self.c.post(reverse("cambiar_contrasena"), {"old_password": "otra-cosa", "new_password1": "Nueva$egura2027", "new_password2": "Nueva$egura2027"})
        self.ana.refresh_from_db()
        self.assertTrue(self.ana.check_password(CLAVE))

    def test_recuperar_no_revela_si_el_correo_existe(self):
        existe = Client().post(reverse("recuperar"), {"email": "ana@prueba.com"})
        no_existe = Client().post(reverse("recuperar"), {"email": "nadie@prueba.com"})
        self.assertEqual(existe.status_code, no_existe.status_code)
        self.assertEqual(existe["Location"], no_existe["Location"])

    def test_recuperar_con_correo_real_envia_un_solo_mensaje(self):
        Client().post(reverse("recuperar"), {"email": "ana@prueba.com"})
        self.assertEqual(len(mail.outbox), 1)


class HttpExigenteTests(TestCase):
    """Métodos, cabeceras y rutas raras que no deben tumbar nada."""

    def setUp(self):
        self.ana = Usuario.objects.create_user("ana@prueba.com", CLAVE, perfil="estudiante", first_name="Prueba", last_name="Usuario")
        self.c = Client()
        self.c.force_login(self.ana)

    def test_metodos_raros_no_dan_error_del_servidor(self):
        for metodo in ("put", "patch", "delete", "options", "head"):
            with self.subTest(metodo=metodo):
                r = getattr(self.c, metodo)(reverse("mi_cuenta"))
                self.assertLess(r.status_code, 500)

    def test_host_no_permitido_se_rechaza(self):
        r = Client(HTTP_HOST="evil.example").get("/")
        self.assertEqual(r.status_code, 400)

    def test_la_pagina_no_se_puede_meter_en_un_marco_ajeno(self):
        r = self.c.get(reverse("panel"))
        self.assertEqual(r.get("X-Frame-Options"), "DENY")

    def test_rutas_inexistentes_dan_404_no_500(self):
        for ruta in ("/no-existe/", "/app/proyectos/abc/", "/app/proyectos/-1/", "/app/proyectos/99999999999999999999999/", "/..%2f..%2fetc/passwd"):
            with self.subTest(ruta=ruta):
                self.assertLess(self.c.get(ruta).status_code, 500)

    def test_ruta_con_barra_final_faltante_redirige_o_responde(self):
        self.assertLess(self.c.get("/app/proyectos").status_code, 500)
