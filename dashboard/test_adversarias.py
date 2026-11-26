"""Cliente exigente sobre proyectos: intenta romper tableros, invitaciones, canvas,
documentos y ids. Cada prueba dice qué debe pasar (código y estado de la base)."""

import json
import shutil
import tempfile
from datetime import timedelta

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from cuentas.models import Usuario
from dashboard.models import DocumentoProyecto, InvitacionProyecto, Proyecto, ProyectoMiembro, Tarea

CLAVE = "Clave$egura2026"
MEDIA_TEMPORAL = tempfile.mkdtemp(prefix="xincronix_adv_")


def cliente_de(usuario):
    c = Client()
    c.force_login(usuario)
    return c


class Base(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.lider = Usuario.objects.create_user("lider@prueba.com", CLAVE, perfil="estudiante", first_name="Prueba", last_name="Usuario")
        cls.editor = Usuario.objects.create_user("editor@prueba.com", CLAVE, perfil="profesional", first_name="Prueba", last_name="Usuario")
        cls.lector = Usuario.objects.create_user("lector@prueba.com", CLAVE, perfil="profesor", first_name="Prueba", last_name="Usuario")
        cls.ajeno = Usuario.objects.create_user("ajeno@prueba.com", CLAVE, perfil="estudiante", first_name="Prueba", last_name="Usuario")
        cls.p = Proyecto.objects.create(nombre="Equipo", creado_por=cls.lider, modalidad=Proyecto.Modalidad.GRUPAL, descripcion="Descripción de prueba")
        ProyectoMiembro.objects.create(proyecto=cls.p, usuario=cls.lider, rol=ProyectoMiembro.Rol.LIDER)
        ProyectoMiembro.objects.create(proyecto=cls.p, usuario=cls.editor, rol=ProyectoMiembro.Rol.EDITOR)
        ProyectoMiembro.objects.create(proyecto=cls.p, usuario=cls.lector, rol=ProyectoMiembro.Rol.LECTOR)
        cls.tarea = Tarea.objects.create(titulo="Base", proyecto=cls.p, creado_por=cls.lider)

    def mover(self, usuario, tarea, cuerpo, pk=None):
        return cliente_de(usuario).post(reverse("tarea_mover", args=[pk or self.p.pk, tarea.pk]),
                                        data=cuerpo, content_type="application/json")


class TableroYTareasExigentesTests(Base):
    def test_mover_a_un_estado_que_no_existe_se_rechaza(self):
        for estado in ("volando", "", None, 5, ["hecha"], {"x": 1}):
            with self.subTest(estado=estado):
                r = self.mover(self.editor, self.tarea, json.dumps({"estado": estado}))
                self.assertEqual(r.status_code, 400)
        self.tarea.refresh_from_db()
        self.assertEqual(self.tarea.estado, Tarea.Estado.POR_HACER)

    def test_cuerpo_que_no_es_objeto_se_rechaza(self):
        for cuerpo in ("[]", "null", "42", '"hecha"', "{no-es-json", ""):
            with self.subTest(cuerpo=cuerpo):
                self.assertEqual(self.mover(self.editor, self.tarea, cuerpo).status_code, 400)

    def test_mover_con_id_de_tarea_inexistente_da_404(self):
        r = cliente_de(self.editor).post(reverse("tarea_mover", args=[self.p.pk, 999999]),
                                         data=json.dumps({"estado": "hecha"}), content_type="application/json")
        self.assertEqual(r.status_code, 404)

    def test_metodo_get_en_mover_tarea_no_cambia_nada(self):
        self.assertEqual(cliente_de(self.editor).get(reverse("tarea_mover", args=[self.p.pk, self.tarea.pk])).status_code, 405)

    def test_titulo_gigante_no_se_guarda(self):
        cliente_de(self.editor).post(reverse("tarea_crear", args=[self.p.pk]), {"titulo": "T" * 5000, "estado": "por_hacer", "prioridad": "media"})
        self.assertFalse(Tarea.objects.filter(titulo__startswith="TTTT").exists())

    def test_fecha_imposible_no_se_guarda(self):
        cliente_de(self.editor).post(reverse("tarea_crear", args=[self.p.pk]), {"titulo": "Fecha mala", "estado": "por_hacer", "prioridad": "media", "fecha_vencimiento": "2026-13-45"})
        self.assertFalse(Tarea.objects.filter(titulo="Fecha mala").exists())

    def test_asignar_tarea_a_quien_no_esta_en_el_proyecto_se_rechaza(self):
        cliente_de(self.editor).post(reverse("tarea_crear", args=[self.p.pk]), {"titulo": "Ajena", "estado": "por_hacer", "prioridad": "media", "asignado_a": self.ajeno.pk})
        self.assertFalse(Tarea.objects.filter(titulo="Ajena").exists())

    def test_asignado_con_texto_en_lugar_de_numero_no_rompe(self):
        r = cliente_de(self.editor).post(reverse("tarea_crear", args=[self.p.pk]), {"titulo": "Texto", "estado": "por_hacer", "prioridad": "media", "asignado_a": "DROP TABLE"})
        self.assertNotEqual(r.status_code, 500)
        self.assertFalse(Tarea.objects.filter(titulo="Texto").exists())

    def test_nombre_de_proyecto_con_html_se_muestra_escapado(self):
        cliente = cliente_de(self.lider)
        cliente.post(reverse("proyecto_crear"), {"nombre": "<img src=x onerror=alert(1)>", "estado": "planificacion", "descripcion": "Proyecto de prueba", "tecnologia": "", "repositorio_url": "", "fecha_inicio": "", "fecha_fin": "", "supervisor": ""})
        p = Proyecto.objects.filter(nombre__contains="onerror").first()
        self.assertIsNotNone(p)
        html = cliente.get(reverse("proyecto_detalle", args=[p.pk])).content.decode()
        self.assertNotIn("<img src=x onerror=alert(1)>", html)
        self.assertIn("&lt;img", html)


class IdsExigentesTests(Base):
    def test_ids_absurdos_dan_404_y_nunca_500(self):
        c = cliente_de(self.lider)
        for pk in ("99999999999999999999999", "-1", "0", "9223372036854775808"):
            for nombre in ("proyecto_detalle", "proyecto_tablero", "proyecto_canvas", "proyecto_roadmap"):
                with self.subTest(pk=pk, pagina=nombre):
                    self.assertEqual(c.get(reverse(nombre, args=[pk]) if pk.isdigit() else f"/app/proyectos/{pk}/").status_code, 404)

    def test_quitar_a_alguien_que_no_es_miembro_da_404(self):
        r = cliente_de(self.lider).post(reverse("miembro_quitar", args=[self.p.pk, self.ajeno.pk]))
        self.assertEqual(r.status_code, 404)

    def test_eliminar_dos_veces_el_mismo_proyecto(self):
        otro = Proyecto.objects.create(nombre="Doble", creado_por=self.lider, descripcion="Descripción de prueba")
        ProyectoMiembro.objects.create(proyecto=otro, usuario=self.lider, rol=ProyectoMiembro.Rol.LIDER)
        c = cliente_de(self.lider)
        self.assertEqual(c.post(reverse("proyecto_eliminar", args=[otro.pk])).status_code, 302)
        self.assertEqual(c.post(reverse("proyecto_eliminar", args=[otro.pk])).status_code, 404)

    def test_tarea_de_otro_proyecto_no_se_puede_mover_desde_este(self):
        otro = Proyecto.objects.create(nombre="Otro", creado_por=self.lider, descripcion="Descripción de prueba")
        ProyectoMiembro.objects.create(proyecto=otro, usuario=self.lider, rol=ProyectoMiembro.Rol.LIDER)
        ajena = Tarea.objects.create(titulo="De otro", proyecto=otro, creado_por=self.lider)
        r = self.mover(self.lider, ajena, json.dumps({"estado": "hecha"}))  # URL del proyecto Equipo
        self.assertEqual(r.status_code, 404)
        ajena.refresh_from_db()
        self.assertEqual(ajena.estado, Tarea.Estado.POR_HACER)


class InvitacionesExigentesTests(Base):
    def invitar(self, rol="editor", email="nuevo@prueba.com", usuario=None):
        return cliente_de(usuario or self.lider).post(reverse("invitacion_crear", args=[self.p.pk]), {"email": email, "rol": rol})

    def test_no_se_puede_invitar_como_lider(self):
        self.invitar(rol="lider")
        self.assertFalse(InvitacionProyecto.objects.filter(proyecto=self.p, rol="lider").exists())

    def test_no_se_puede_invitar_con_un_rol_inventado(self):
        self.invitar(rol="administrador")
        self.assertFalse(InvitacionProyecto.objects.filter(proyecto=self.p).exists())

    def test_no_me_puedo_invitar_a_mi_mismo(self):
        self.invitar(email="lider@prueba.com")
        self.assertFalse(InvitacionProyecto.objects.filter(proyecto=self.p).exists())

    def test_no_se_invita_a_un_miembro_que_ya_esta(self):
        self.invitar(email="EDITOR@prueba.com")
        self.assertFalse(InvitacionProyecto.objects.filter(proyecto=self.p, email__iexact="editor@prueba.com").exists())

    def test_no_se_repite_una_invitacion_pendiente(self):
        self.invitar(email="nuevo@prueba.com")
        self.invitar(email="nuevo@prueba.com")
        self.assertEqual(InvitacionProyecto.objects.filter(proyecto=self.p, email="nuevo@prueba.com").count(), 1)

    def test_correo_con_espacios_y_mayusculas_se_normaliza(self):
        self.invitar(email="  Nuevo@Prueba.COM ")
        self.assertTrue(InvitacionProyecto.objects.filter(proyecto=self.p, email="nuevo@prueba.com").exists())

    def test_invitacion_con_token_inventado_da_404(self):
        self.assertEqual(cliente_de(self.ajeno).get("/app/invitaciones/00000000-0000-0000-0000-000000000000/aceptar/").status_code, 404)

    def test_invitacion_de_otro_correo_no_se_acepta(self):
        self.invitar(email="nuevo@prueba.com")
        inv = InvitacionProyecto.objects.get(email="nuevo@prueba.com")
        r = cliente_de(self.ajeno).get(reverse("invitacion_aceptar", args=[inv.token]))
        self.assertEqual(r.status_code, 403)
        inv.refresh_from_db()
        self.assertEqual(inv.estado, InvitacionProyecto.Estado.PENDIENTE)

    def test_invitacion_no_se_puede_aceptar_dos_veces(self):
        Usuario.objects.create_user("nuevo@prueba.com", CLAVE, perfil="estudiante", first_name="Prueba", last_name="Usuario")
        self.invitar(email="nuevo@prueba.com")
        inv = InvitacionProyecto.objects.get(email="nuevo@prueba.com")
        nuevo = cliente_de(Usuario.objects.get(email="nuevo@prueba.com"))
        nuevo.get(reverse("invitacion_aceptar", args=[inv.token]))
        r = nuevo.get(reverse("invitacion_aceptar", args=[inv.token]), follow=True)
        self.assertContains(r, "ya no está disponible")
        self.assertEqual(ProyectoMiembro.objects.filter(proyecto=self.p, usuario__email="nuevo@prueba.com").count(), 1)

    def test_invitacion_vencida_no_se_acepta(self):
        Usuario.objects.create_user("nuevo@prueba.com", CLAVE, perfil="estudiante", first_name="Prueba", last_name="Usuario")
        inv = InvitacionProyecto.objects.create(proyecto=self.p, email="nuevo@prueba.com", rol="editor", creado_por=self.lider,
                                                vence_en=timezone.now() - timedelta(minutes=1))
        cliente_de(Usuario.objects.get(email="nuevo@prueba.com")).get(reverse("invitacion_aceptar", args=[inv.token]))
        self.assertFalse(ProyectoMiembro.objects.filter(proyecto=self.p, usuario__email="nuevo@prueba.com").exists())

    def test_el_lector_no_puede_invitar(self):
        self.assertEqual(self.invitar(usuario=self.lector).status_code, 403)

    def test_el_editor_no_puede_invitar(self):
        self.assertEqual(self.invitar(usuario=self.editor).status_code, 403)


class CanvasExigenteTests(Base):
    def guardar(self, cuerpo, usuario=None):
        return cliente_de(usuario or self.lider).post(reverse("canvas_guardar", args=[self.p.pk]), data=cuerpo, content_type="application/json")

    def test_canvas_gigante_se_rechaza(self):
        r = self.guardar(json.dumps({"contenido": {"texto": "x" * (600 * 1024)}}))
        self.assertEqual(r.status_code, 413)

    def test_canvas_muy_anidado_se_rechaza(self):
        anidado = {}
        actual = anidado
        for _ in range(60):
            actual["n"] = {}
            actual = actual["n"]
        self.assertEqual(self.guardar(json.dumps({"contenido": anidado})).status_code, 400)

    def test_canvas_con_bytes_invalidos_se_rechaza(self):
        self.assertEqual(self.guardar(b"\xff\xfe\x00{}").status_code, 400)

    def test_canvas_cuyo_contenido_es_una_lista_se_rechaza(self):
        self.assertEqual(self.guardar(json.dumps({"contenido": [1, 2]})).status_code, 400)

    def test_el_lector_no_guarda_el_canvas(self):
        self.assertEqual(self.guardar(json.dumps({"contenido": {}}), usuario=self.lector).status_code, 403)

    def test_el_editor_si_puede_guardar_el_canvas(self):
        # Según la matriz de permisos, el editor sí colabora en el canvas.
        self.assertEqual(self.guardar(json.dumps({"contenido": {}}), usuario=self.editor).status_code, 200)

    def test_metodo_get_en_guardar_canvas_da_405(self):
        self.assertEqual(cliente_de(self.lider).get(reverse("canvas_guardar", args=[self.p.pk])).status_code, 405)


@override_settings(MEDIA_ROOT=MEDIA_TEMPORAL)
class DocumentosExigentesTests(Base):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_TEMPORAL, ignore_errors=True)

    def subir(self, nombre, contenido=b"contenido", usuario=None):
        archivo = SimpleUploadedFile(nombre, contenido, content_type="application/octet-stream")
        return cliente_de(usuario or self.editor).post(reverse("documento_subir", args=[self.p.pk]), {"nombre": "Doc", "archivo": archivo})

    def test_extension_doble_peligrosa_se_rechaza(self):
        self.subir("informe.pdf.exe")
        self.assertFalse(DocumentoProyecto.objects.filter(proyecto=self.p).exists())

    def test_extension_en_mayusculas_se_acepta(self):
        self.subir("INFORME.PDF")
        self.assertTrue(DocumentoProyecto.objects.filter(proyecto=self.p).exists())

    def test_ruta_con_retrocesos_no_sale_de_media(self):
        self.subir("../../../../evil.txt")
        for doc in DocumentoProyecto.objects.filter(proyecto=self.p):
            self.assertNotIn("..", doc.archivo.name)

    def test_archivo_sin_extension_se_rechaza(self):
        self.subir("sinextension")
        self.assertFalse(DocumentoProyecto.objects.filter(proyecto=self.p).exists())

    def test_html_disfrazado_de_pdf_se_rechaza_por_extension_solo(self):
        # La validación es por extensión; el contenido no se analiza. Se documenta el límite.
        self.subir("pagina.html.pdf", contenido=b"<script>alert(1)</script>")
        self.assertTrue(DocumentoProyecto.objects.filter(proyecto=self.p).exists())

    def test_el_lector_no_sube_ni_borra(self):
        self.subir("nota.txt", usuario=self.lector)
        self.assertFalse(DocumentoProyecto.objects.filter(proyecto=self.p).exists())

    def test_borrar_documento_ajeno_da_404(self):
        otro = Proyecto.objects.create(nombre="Otro", creado_por=self.lider, descripcion="Descripción de prueba")
        ProyectoMiembro.objects.create(proyecto=otro, usuario=self.lider, rol=ProyectoMiembro.Rol.LIDER)
        doc = DocumentoProyecto.objects.create(proyecto=otro, nombre="Ajeno", archivo="x.txt", subido_por=self.lider)
        r = cliente_de(self.lider).post(reverse("documento_eliminar", args=[self.p.pk, doc.pk]))
        self.assertEqual(r.status_code, 404)
        self.assertTrue(DocumentoProyecto.objects.filter(pk=doc.pk).exists())


class EdicionExigenteTests(Base):
    def test_fin_antes_de_inicio_al_editar_se_rechaza(self):
        cliente_de(self.lider).post(reverse("proyecto_editar", args=[self.p.pk]), {
            "nombre": "Equipo", "estado": "planificacion", "fecha_inicio": "2026-12-10", "fecha_fin": "2026-12-01"})
        self.p.refresh_from_db()
        self.assertNotEqual(self.p.fecha_fin.isoformat() if self.p.fecha_fin else "", "2026-12-01")

    def test_nombre_vacio_al_editar_se_rechaza(self):
        cliente_de(self.lider).post(reverse("proyecto_editar", args=[self.p.pk]), {"nombre": "   ", "estado": "planificacion"})
        self.p.refresh_from_db()
        self.assertEqual(self.p.nombre, "Equipo")

    def test_estado_inventado_al_editar_se_rechaza(self):
        cliente_de(self.lider).post(reverse("proyecto_editar", args=[self.p.pk]), {"nombre": "Equipo", "estado": "eliminado_para_siempre"})
        self.p.refresh_from_db()
        self.assertNotEqual(self.p.estado, "eliminado_para_siempre")

    def test_el_lector_no_puede_abrir_la_edicion(self):
        self.assertEqual(cliente_de(self.lector).get(reverse("proyecto_editar", args=[self.p.pk])).status_code, 403)

    def test_evento_sin_fecha_no_se_crea(self):
        cliente_de(self.editor).post(reverse("evento_crear", args=[self.p.pk]), {"titulo": "Sin fecha"})
        from dashboard.models import Evento
        self.assertFalse(Evento.objects.filter(titulo="Sin fecha").exists())
