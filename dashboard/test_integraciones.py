"""Integraciones: GitHub (repositorio), Gemini (asistente IA) e invitaciones con notificación.

Las APIs externas se simulan con unittest.mock: las pruebas nunca salen a internet.
"""

from datetime import timedelta
from unittest import mock

import json

import requests
from django.core import mail
from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from cuentas.models import Usuario
from dashboard import github
from dashboard.models import ChatAsistente, InvitacionProyecto, Proyecto, ProyectoMiembro, Tarea
from dashboard.templatetags.texto_ia import markdown_simple

CLAVE = "Clave$egura2026"


def cliente_de(usuario):
    c = Client()
    c.force_login(usuario)
    return c


def respuesta_falsa(codigo=200, datos=None, encabezados=None):
    r = mock.Mock()
    r.status_code = codigo
    r.json.return_value = datos if datos is not None else {}
    r.headers = encabezados or {}
    return r


class Base(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.lider = Usuario.objects.create_user("lider@prueba.com", CLAVE, first_name="Lía", last_name="Gómez")
        cls.lector = Usuario.objects.create_user("lector@prueba.com", CLAVE, first_name="Luz", last_name="Pérez")
        cls.ajeno = Usuario.objects.create_user("ajeno@prueba.com", CLAVE, first_name="Ajeno", last_name="Usuario")
        cls.p = Proyecto.objects.create(nombre="App de notas", creado_por=cls.lider, modalidad=Proyecto.Modalidad.GRUPAL,
                                        descripcion="Notas para estudiantes", repositorio_url="https://github.com/equipo/notas")
        ProyectoMiembro.objects.create(proyecto=cls.p, usuario=cls.lider, rol=ProyectoMiembro.Rol.LIDER)
        ProyectoMiembro.objects.create(proyecto=cls.p, usuario=cls.lector, rol=ProyectoMiembro.Rol.LECTOR)
        Tarea.objects.create(titulo="Login con correo", proyecto=cls.p, creado_por=cls.lider, asignado_a=cls.lector,
                             fecha_vencimiento=timezone.localdate() - timedelta(days=2))

    def setUp(self):
        cache.clear()


# ---------------------------------------------------------------------------
# GitHub
# ---------------------------------------------------------------------------

class AnalizarUrlTests(TestCase):
    def test_enlaces_validos(self):
        casos = {
            "https://github.com/equipo/notas": ("equipo", "notas"),
            "https://github.com/equipo/notas.git": ("equipo", "notas"),
            "https://www.github.com/equipo/notas/tree/main/src": ("equipo", "notas"),
            "http://github.com/equipo/": ("equipo", None),
            "https://github.com/equipo": ("equipo", None),
        }
        for url, esperado in casos.items():
            with self.subTest(url=url):
                self.assertEqual(github.analizar_url(url), esperado)

    def test_enlaces_que_no_son_de_github(self):
        for url in ["", None, "https://gitlab.com/equipo/notas", "https://github.com.evil.com/a/b", "javascript:alert(1)",
                    "https://github.com/", "https://github.com/../etc", "ftp://github.com/a/b", "https://evil.com/github.com/a"]:
            with self.subTest(url=url):
                self.assertIsNone(github.analizar_url(url))


def github_falso(url, params=None, headers=None, timeout=None):
    if url.endswith("/repos/equipo/notas"):
        return respuesta_falsa(200, {"full_name": "equipo/notas", "description": "Repo de notas", "html_url": "https://github.com/equipo/notas",
                                     "stargazers_count": 12, "forks_count": 3, "open_issues_count": 4, "default_branch": "main",
                                     "license": {"name": "MIT License"}, "pushed_at": "2026-11-20T10:00:00Z", "private": False})
    if url.endswith("/languages"):
        return respuesta_falsa(200, {"Python": 750, "HTML": 250})
    if url.endswith("/commits"):
        return respuesta_falsa(200, [{"sha": "abcdef1234567", "html_url": "https://github.com/equipo/notas/commit/abcdef1",
                                      "commit": {"message": "Agrega login\n\ndetalle", "author": {"name": "Lía", "date": "2026-11-01T10:00:00Z"},
                                                 "committer": {"name": "GitHub", "date": "2026-11-20T10:00:00Z"}}}])
    if url.endswith("/users/equipo/repos"):
        return respuesta_falsa(200, [{"name": "notas", "description": "Repo de notas", "language": "Python", "stargazers_count": 12, "pushed_at": "2026-11-20T10:00:00Z"},
                                     {"name": "web", "description": "", "language": "HTML", "stargazers_count": 0, "pushed_at": None, "fork": True}])
    return respuesta_falsa(404, {"message": "Not Found"})


@override_settings(GITHUB_TOKEN="")
@mock.patch("dashboard.github.requests.get", side_effect=github_falso)
class RepositorioVistaTests(Base):
    def url(self, **params):
        return reverse("proyecto_repositorio", args=[self.p.pk])

    def test_muestra_datos_del_repositorio(self, falso):
        r = cliente_de(self.lector).get(self.url())
        self.assertContains(r, "equipo/notas")
        self.assertContains(r, "Repo de notas")
        self.assertContains(r, "Agrega login")
        self.assertNotContains(r, "detalle")  # solo la primera línea del commit
        self.assertContains(r, "75,0%")       # lenguajes en porcentaje (formato es-co)
        self.assertContains(r, "MIT License")

    def test_fecha_del_commit_es_cuando_entro_al_repositorio(self, falso):
        datos = github.repositorio("equipo", "notas")
        self.assertEqual(datos["commits"][0]["fecha"].day, 20)
        self.assertEqual(datos["commits"][0]["autor"], "Lía")

    def test_la_cache_evita_consultas_repetidas(self, falso):
        cliente_de(self.lider).get(self.url())
        llamadas = falso.call_count
        cliente_de(self.lider).get(self.url())
        self.assertEqual(falso.call_count, llamadas)

    def test_envia_version_y_token_solo_si_existe(self, falso):
        cliente_de(self.lider).get(self.url())
        encabezados = falso.call_args.kwargs["headers"]
        self.assertEqual(encabezados["X-GitHub-Api-Version"], github.VERSION_API)
        self.assertNotIn("Authorization", encabezados)
        cache.clear()
        admin = Usuario.objects.create_user(
            "admin-github@prueba.com", CLAVE, first_name="Admin", last_name="GitHub", rol=Usuario.Rol.ADMIN,
        )
        with override_settings(GITHUB_TOKEN="tok-123"):
            cliente_de(admin).get(self.url())
            self.assertEqual(falso.call_args.kwargs["headers"]["Authorization"], "Bearer tok-123")
            falso.reset_mock()
            cliente_de(self.lider).get(self.url())
            self.assertGreater(falso.call_count, 0)
            self.assertTrue(all("Authorization" not in llamada.kwargs["headers"] for llamada in falso.call_args_list))

    def test_enlace_de_usuario_lista_sus_repositorios(self, falso):
        Proyecto.objects.filter(pk=self.p.pk).update(repositorio_url="https://github.com/equipo")
        r = cliente_de(self.lider).get(self.url())
        self.assertContains(r, "Repositorios públicos de equipo")
        self.assertContains(r, "?repo=notas")
        r = cliente_de(self.lider).get(self.url() + "?repo=notas")
        self.assertContains(r, "Agrega login")

    def test_nombre_de_repo_invalido_en_la_url_se_ignora(self, falso):
        Proyecto.objects.filter(pk=self.p.pk).update(repositorio_url="https://github.com/equipo")
        r = cliente_de(self.lider).get(self.url() + "?repo=../../orgs/x")
        self.assertContains(r, "Repositorios públicos de equipo")

    def test_repositorio_inexistente_muestra_mensaje(self, falso):
        Proyecto.objects.filter(pk=self.p.pk).update(repositorio_url="https://github.com/equipo/no-existe")
        r = cliente_de(self.lider).get(self.url())
        self.assertContains(r, "No se encontró en GitHub")

    def test_limite_de_github(self, falso):
        falso.side_effect = lambda *a, **k: respuesta_falsa(403, {}, {"X-RateLimit-Remaining": "0"})
        r = cliente_de(self.lider).get(self.url())
        self.assertContains(r, "límite de consultas a GitHub")

    def test_sin_conexion(self, falso):
        falso.side_effect = requests.ConnectionError()
        r = cliente_de(self.lider).get(self.url())
        self.assertContains(r, "No hay conexión con GitHub")

    def test_sin_enlace_o_enlace_que_no_es_de_github(self, falso):
        Proyecto.objects.filter(pk=self.p.pk).update(repositorio_url="")
        self.assertContains(cliente_de(self.lider).get(self.url()), "Este proyecto no tiene repositorio")
        Proyecto.objects.filter(pk=self.p.pk).update(repositorio_url="https://gitlab.com/a/b")
        self.assertContains(cliente_de(self.lider).get(self.url()), "no es de GitHub")
        falso.assert_not_called()

    def test_quien_no_es_del_proyecto_no_lo_ve(self, falso):
        self.assertEqual(cliente_de(self.ajeno).get(self.url()).status_code, 404)
        falso.assert_not_called()


# ---------------------------------------------------------------------------
# Gemini
# ---------------------------------------------------------------------------

def gemini_ok(texto="**Resumen:** vas bien.\n- Tarea 1\n- Tarea 2"):
    return respuesta_falsa(200, {"candidates": [{"content": {"parts": [{"text": texto}]}, "finishReason": "STOP"}]})


@override_settings(GEMINI_API_KEY="clave-secreta", GEMINI_MODEL="modelo-prueba", GEMINI_LIMITE_POR_HORA=3)
class AsistenteTests(Base):
    def url(self):
        return reverse("proyecto_asistente", args=[self.p.pk])

    @mock.patch("dashboard.gemini.requests.post", return_value=gemini_ok())
    def test_pregunta_y_respuesta(self, post):
        c = cliente_de(self.lector)
        r = c.post(self.url(), {"pregunta": "¿Cómo vamos?"}, follow=True)
        self.assertContains(r, "¿Cómo vamos?")
        self.assertContains(r, "<strong>Resumen:</strong>", html=False)
        self.assertContains(r, "<li>Tarea 1</li>", html=False)
        # La clave va en el encabezado, nunca en la URL
        url, kwargs = post.call_args.args[0], post.call_args.kwargs
        self.assertIn("modelo-prueba:generateContent", url)
        self.assertNotIn("clave-secreta", url)
        self.assertEqual(kwargs["headers"]["x-goog-api-key"], "clave-secreta")
        # Se envían los datos del proyecto, con la tarea vencida marcada
        datos = str(kwargs["json"]["contents"])
        self.assertIn("Login con correo", datos)
        self.assertIn("VENCIDA", datos)
        self.assertNotIn("lector@prueba.com", datos)  # sin correos

    @mock.patch("dashboard.gemini.requests.post", return_value=gemini_ok("Respuesta 2"))
    def test_recuerda_la_conversacion_y_permite_abrirla_despues(self, post):
        c = cliente_de(self.lider)
        c.post(self.url(), {"pregunta": "Primera"})
        c.post(self.url(), {"pregunta": "Segunda"})
        contenidos = post.call_args.kwargs["json"]["contents"]
        self.assertIn("Primera", str(contenidos))
        anterior = ChatAsistente.objects.get(usuario=self.lider, proyecto=self.p)
        r = c.post(self.url() + "?nuevo=1", {"pregunta": "Otro tema"}, follow=True)
        self.assertContains(r, "Otro tema")
        self.assertEqual(ChatAsistente.objects.filter(usuario=self.lider).count(), 2)
        self.assertNotIn("Primera", str(post.call_args.kwargs["json"]["contents"]))
        r = c.get(self.url() + f"?chat={anterior.pk}")
        self.assertContains(r, "Segunda")
        self.assertEqual(anterior.turnos.count(), 2)
        self.assertEqual(cliente_de(self.lector).get(self.url() + f"?chat={anterior.pk}").status_code, 404)

    @override_settings(GEMINI_API_KEY="")
    def test_gestion_de_chat_solo_para_su_propietario(self):
        chat = ChatAsistente.objects.create(proyecto=self.p, usuario=self.lider, titulo="Título original")
        turno = chat.turnos.create(pregunta="Pregunta guardada", respuesta="Respuesta guardada")
        renombrar = reverse("asistente_chat_renombrar", args=[self.p.pk, chat.pk])
        eliminar = reverse("asistente_chat_eliminar", args=[self.p.pk, chat.pk])
        otro_cliente = cliente_de(self.lector)
        self.assertEqual(otro_cliente.post(renombrar, {"titulo": "Intruso"}).status_code, 404)
        self.assertEqual(otro_cliente.post(eliminar).status_code, 404)

        cliente = cliente_de(self.lider)
        self.assertContains(cliente.get(self.url()), renombrar)
        self.assertContains(cliente.get(renombrar), "Título original")
        self.assertEqual(cliente.post(renombrar, {"titulo": " "}).status_code, 200)
        chat.refresh_from_db()
        self.assertEqual(chat.titulo, "Título original")

        resultado = cliente.post(renombrar, {"titulo": "  Nuevo título  "}, follow=True)
        self.assertContains(resultado, "Nuevo título")
        self.assertContains(resultado, "Respuesta guardada")

        self.assertContains(cliente.get(eliminar), "Sí, eliminar")
        self.assertTrue(ChatAsistente.objects.filter(pk=chat.pk).exists())
        self.assertRedirects(cliente.post(eliminar), self.url())
        self.assertFalse(ChatAsistente.objects.filter(pk=chat.pk).exists())
        self.assertFalse(chat.turnos.filter(pk=turno.pk).exists())

    @mock.patch("dashboard.gemini.requests.post", return_value=gemini_ok("<script>alert(1)</script> **ok**"))
    def test_la_respuesta_no_ejecuta_html(self, post):
        r = cliente_de(self.lider).post(self.url(), {"pregunta": "hola"}, follow=True)
        self.assertNotContains(r, "<script>alert(1)</script>", html=False)
        self.assertContains(r, "&lt;script&gt;", html=False)

    @mock.patch("dashboard.gemini.requests.post", return_value=gemini_ok())
    def test_limite_por_hora(self, post):
        c = cliente_de(self.lider)
        for i in range(3):
            c.post(self.url(), {"pregunta": f"P{i}"})
        r = c.post(self.url(), {"pregunta": "Una más"}, follow=True)
        self.assertContains(r, "límite de 3 preguntas por hora")
        self.assertEqual(post.call_count, 3)

    def test_errores_de_gemini_con_mensaje_claro(self):
        casos = [
            (respuesta_falsa(400, {"error": {"message": "API key not valid."}}), "no es válida"),
            (respuesta_falsa(404, {"error": {"message": "not found"}}), "modelo-prueba"),
            (respuesta_falsa(429, {}), "límite de uso"),
            (respuesta_falsa(200, {"promptFeedback": {"blockReason": "SAFETY"}}), "filtros de seguridad"),
        ]
        for respuesta, texto in casos:
            with self.subTest(texto=texto), mock.patch("dashboard.gemini.requests.post", return_value=respuesta):
                cache.clear()
                r = cliente_de(self.lider).post(self.url(), {"pregunta": "hola"}, follow=True)
                self.assertContains(r, texto)

    @mock.patch("dashboard.gemini.requests.post", return_value=gemini_ok("TÍTULO: Solución al error de acceso\nPuedes revisar la configuración."))
    def test_el_titulo_resume_la_primera_pregunta_sin_otra_solicitud(self, post):
        respuesta = cliente_de(self.lider).post(self.url(), {"pregunta": "¿Cómo soluciono el error de acceso?"}, follow=True)
        chat = ChatAsistente.objects.get(usuario=self.lider, proyecto=self.p)
        self.assertEqual(chat.titulo, "Solución al error de acceso")
        self.assertEqual(chat.turnos.get().respuesta, "Puedes revisar la configuración.")
        self.assertNotContains(respuesta, "TÍTULO:")
        post.assert_called_once()

    def test_respuesta_en_vivo_entrega_fragmentos_y_guarda_el_historial(self):
        cliente = cliente_de(self.lider)
        api = respuesta_falsa(200, {})
        api.iter_lines.return_value = iter([
            b'data: {"candidates":[{"content":{"parts":[{"text":"T\\u00cd"}]}}]}',
            b'data: {"candidates":[{"content":{"parts":[{"text":"TULO: Rutina del equipo\\nHola"}]}}]}',
            b'data: {"candidates":[{"content":{"parts":[{"text":" equipo"}]},"finishReason":"STOP"}]}',
        ])
        with mock.patch("dashboard.gemini.requests.post", return_value=api) as post:
            respuesta = cliente.post(self.url(), {"pregunta": "hola"}, HTTP_ACCEPT="application/x-ndjson")
            self.assertTrue(respuesta.streaming)
            contenido = iter(respuesta.streaming_content)
            self.assertEqual(json.loads(next(contenido)), {"texto": "Hola"})
            self.assertEqual(json.loads(next(contenido)), {"texto": " equipo"})
            cierre = json.loads(next(contenido))
            chat = ChatAsistente.objects.get(usuario=self.lider, proyecto=self.p)
            self.assertEqual(cierre, {"final": True, "url": self.url() + f"?chat={chat.pk}#ultima"})
            self.assertEqual(list(contenido), [])
        self.assertEqual(chat.turnos.get().respuesta, "Hola equipo")
        self.assertEqual(chat.titulo, "Rutina del equipo")
        self.assertTrue(post.call_args.args[0].endswith(":streamGenerateContent"))
        self.assertEqual(post.call_args.kwargs["params"], {"alt": "sse"})
        api.close.assert_called_once()

    def test_respuesta_interrumpida_no_se_guarda(self):
        cliente = cliente_de(self.lider)
        api = respuesta_falsa(200, {})
        api.iter_lines.return_value = iter([
            b'data: {"candidates":[{"content":{"parts":[{"text":"Parcial"}]}}]}',
        ])
        with mock.patch("dashboard.gemini.requests.post", return_value=api):
            respuesta = cliente.post(self.url(), {"pregunta": "hola"}, HTTP_ACCEPT="application/x-ndjson")
            eventos = [json.loads(fragmento) for fragmento in respuesta.streaming_content]
        self.assertEqual(eventos[0], {"texto": "Parcial"})
        self.assertIn("error", eventos[-1])
        self.assertFalse(ChatAsistente.objects.filter(usuario=self.lider, proyecto=self.p).exists())

    @override_settings(GEMINI_MODEL_RESPALDO="modelo-respaldo")
    def test_si_el_modelo_esta_saturado_usa_el_de_respaldo(self):
        saturado = respuesta_falsa(503, {"error": {"message": "This model is currently experiencing high demand."}})
        with mock.patch("dashboard.gemini.requests.post", side_effect=[saturado, gemini_ok("Respuesta del respaldo")]) as post, \
                self.assertLogs("dashboard.gemini", "WARNING"):
            r = cliente_de(self.lider).post(self.url(), {"pregunta": "hola"}, follow=True)
        self.assertContains(r, "Respuesta del respaldo")
        self.assertIn("modelo-prueba:generateContent", post.call_args_list[0].args[0])
        self.assertIn("modelo-respaldo:generateContent", post.call_args_list[1].args[0])

    @override_settings(GEMINI_MODEL_RESPALDO="modelo-respaldo")
    def test_tiempo_agotado_en_el_primer_modelo_usa_el_respaldo(self):
        with mock.patch("dashboard.gemini.requests.post", side_effect=[requests.Timeout(), gemini_ok()]) as post, self.assertLogs("dashboard.gemini", "WARNING"):
            respuesta = cliente_de(self.lider).post(self.url(), {"pregunta": "hola"}, follow=True)
        self.assertContains(respuesta, "Resumen")
        self.assertIn("modelo-respaldo:generateContent", post.call_args_list[1].args[0])

    @override_settings(GEMINI_MODEL_RESPALDO="respaldo-1, respaldo-2")
    def test_si_todos_estan_saturados_avisa_la_alta_demanda(self):
        saturado = respuesta_falsa(503, {"error": {"message": "high demand"}})
        with mock.patch("dashboard.gemini.requests.post", return_value=saturado) as post, self.assertLogs("dashboard.gemini", "WARNING"):
            r = cliente_de(self.lider).post(self.url(), {"pregunta": "hola"}, follow=True)
        self.assertContains(r, "mucha demanda")
        self.assertEqual([c.args[0].split("/models/")[1] for c in post.call_args_list],
                         ["modelo-prueba:generateContent", "respaldo-1:generateContent", "respaldo-2:generateContent"])

    @mock.patch("dashboard.gemini.requests.post", side_effect=requests.Timeout())
    def test_tiempo_agotado(self, post):
        r = cliente_de(self.lider).post(self.url(), {"pregunta": "hola"}, follow=True)
        self.assertContains(r, "tardó demasiado")

    @mock.patch("dashboard.gemini.requests.post")
    def test_pregunta_vacia_no_llama_a_gemini(self, post):
        r = cliente_de(self.lider).post(self.url(), {"pregunta": "   "})
        self.assertContains(r, "Escribe una pregunta")
        post.assert_not_called()

    @mock.patch("dashboard.gemini.requests.post")
    def test_quien_no_es_del_proyecto_no_lo_usa(self, post):
        self.assertEqual(cliente_de(self.ajeno).post(self.url(), {"pregunta": "datos"}).status_code, 404)
        post.assert_not_called()


class AsistenteSinClaveTests(Base):
    @override_settings(GEMINI_API_KEY="")
    @mock.patch("dashboard.gemini.requests.post")
    def test_sin_clave_explica_como_configurarlo(self, post):
        url = reverse("proyecto_asistente", args=[self.p.pk])
        self.assertContains(cliente_de(self.lider).get(url), "GEMINI_API_KEY")
        r = cliente_de(self.lider).post(url, {"pregunta": "hola"}, follow=True)
        self.assertContains(r, "no está configurado")
        post.assert_not_called()


class MarkdownSimpleTests(TestCase):
    def test_formato_basico(self):
        html = markdown_simple("# Título\n**negrita** y *cursiva*\n1. uno\n2. dos\n- a")
        self.assertIn('<p class="ia-titulo">Título</p>', html)
        self.assertIn("<strong>negrita</strong>", html)
        self.assertIn("<em>cursiva</em>", html)
        self.assertIn("<ol><li>uno</li><li>dos</li></ol><ul><li>a</li></ul>", html)

    def test_escapa_html(self):
        html = markdown_simple('<img src=x onerror="alert(1)"> **<b>x</b>**')
        self.assertNotIn("<img", html)
        self.assertNotIn("<b>", html)
        self.assertIn("&lt;img", html)


# ---------------------------------------------------------------------------
# Invitaciones: correo + notificación en la página
# ---------------------------------------------------------------------------

@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class InvitacionNotificacionTests(Base):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.invitado = Usuario.objects.create_user("invitado@prueba.com", CLAVE, first_name="Iván", last_name="Ruiz")

    def invitar(self, rol="lector", correo="invitado@prueba.com"):
        return cliente_de(self.lider).post(reverse("invitacion_crear", args=[self.p.pk]), {"email": correo, "rol": rol}, follow=True)

    def test_llega_por_correo_con_version_html_y_permiso(self):
        r = self.invitar("lector")
        self.assertContains(r, "le llega por correo y como notificación")
        self.assertEqual(len(mail.outbox), 1)
        correo = mail.outbox[0]
        self.assertIn("Solo lectura", correo.body)
        self.assertIn("invitado@prueba.com", correo.body)
        html, tipo = correo.alternatives[0]
        self.assertEqual(tipo, "text/html")
        self.assertIn("Aceptar invitación", html)

    def test_aparece_como_notificacion_en_la_campana_y_el_centro(self):
        self.invitar("editor")
        r = cliente_de(self.invitado).get(reverse("panel"))
        self.assertContains(r, 'class="xnx-notif-num">1<', html=False)
        self.assertContains(r, "Te invitaron a 1 proyecto")
        self.assertContains(r, "App de notas")
        self.assertContains(r, "Colaborador: podrás editar")
        # A quien no invitaron no le aparece
        self.assertNotContains(cliente_de(self.ajeno).get(reverse("panel")), "Te invitaron")

    def test_aceptar_desde_la_notificacion_con_el_permiso_elegido(self):
        self.invitar("lector")
        inv = InvitacionProyecto.objects.get(email="invitado@prueba.com")
        r = cliente_de(self.invitado).post(reverse("invitacion_responder", args=[inv.pk]), {"accion": "aceptar"})
        self.assertRedirects(r, reverse("proyecto_detalle", args=[self.p.pk]))
        self.assertEqual(ProyectoMiembro.objects.get(proyecto=self.p, usuario=self.invitado).rol, ProyectoMiembro.Rol.LECTOR)
        inv.refresh_from_db()
        self.assertEqual(inv.estado, InvitacionProyecto.Estado.ACEPTADA)
        self.assertNotContains(cliente_de(self.invitado).get(reverse("panel")), "Te invitaron")

    def test_rechazar(self):
        self.invitar()
        inv = InvitacionProyecto.objects.get(email="invitado@prueba.com")
        r = cliente_de(self.invitado).post(reverse("invitacion_responder", args=[inv.pk]), {"accion": "rechazar", "siguiente": "https://evil.com/"})
        self.assertRedirects(r, reverse("panel"))  # no redirige a otro sitio
        inv.refresh_from_db()
        self.assertEqual(inv.estado, InvitacionProyecto.Estado.RECHAZADA)
        self.assertFalse(ProyectoMiembro.objects.filter(proyecto=self.p, usuario=self.invitado).exists())

    def test_otra_cuenta_no_puede_responder(self):
        self.invitar()
        inv = InvitacionProyecto.objects.get(email="invitado@prueba.com")
        self.assertEqual(cliente_de(self.ajeno).post(reverse("invitacion_responder", args=[inv.pk]), {"accion": "aceptar"}).status_code, 404)
        self.assertFalse(ProyectoMiembro.objects.filter(proyecto=self.p, usuario=self.ajeno).exists())

    def test_vencida_o_respondida_ya_no_se_puede_responder(self):
        self.invitar()
        inv = InvitacionProyecto.objects.get(email="invitado@prueba.com")
        InvitacionProyecto.objects.filter(pk=inv.pk).update(vence_en=timezone.now() - timedelta(minutes=1))
        c = cliente_de(self.invitado)
        self.assertEqual(c.post(reverse("invitacion_responder", args=[inv.pk]), {"accion": "aceptar"}).status_code, 404)
        self.assertNotContains(c.get(reverse("panel")), "Te invitaron")

    def test_responder_solo_por_post_y_con_accion_valida(self):
        self.invitar()
        inv = InvitacionProyecto.objects.get(email="invitado@prueba.com")
        c = cliente_de(self.invitado)
        self.assertEqual(c.get(reverse("invitacion_responder", args=[inv.pk])).status_code, 405)
        self.assertEqual(c.post(reverse("invitacion_responder", args=[inv.pk]), {"accion": "otra"}).status_code, 400)

    def test_lider_ve_las_pendientes_y_puede_cancelarlas(self):
        self.invitar()
        inv = InvitacionProyecto.objects.get(email="invitado@prueba.com")
        detalle = cliente_de(self.lider).get(reverse("proyecto_detalle", args=[self.p.pk]))
        self.assertContains(detalle, "Invitaciones pendientes")
        self.assertContains(detalle, "invitado@prueba.com")
        url = reverse("invitacion_cancelar", args=[self.p.pk, inv.pk])
        self.assertEqual(cliente_de(self.lector).post(url).status_code, 403)  # solo el líder
        cliente_de(self.lider).post(url)
        inv.refresh_from_db()
        self.assertEqual(inv.estado, InvitacionProyecto.Estado.CANCELADA)
        self.assertNotContains(cliente_de(self.invitado).get(reverse("panel")), "Te invitaron")

    def test_si_el_correo_falla_la_invitacion_queda_como_notificacion(self):
        with mock.patch("dashboard.views.send_mail", side_effect=OSError("SMTP caído")), self.assertLogs("dashboard.views", "ERROR"):
            r = self.invitar()
        self.assertContains(r, "el correo no se pudo enviar")
        self.assertTrue(InvitacionProyecto.objects.filter(email="invitado@prueba.com", estado="pendiente").exists())
        self.assertContains(cliente_de(self.invitado).get(reverse("panel")), "Te invitaron a 1 proyecto")
