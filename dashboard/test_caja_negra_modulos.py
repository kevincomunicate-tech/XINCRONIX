"""Pruebas de caja negra de los módulos del proyecto: calendario, documentos,
correcciones, tareas y edición. Cada prueba entra como un usuario real."""

import shutil
import tempfile
from datetime import timedelta

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from cuentas.models import Usuario
from dashboard.models import Correccion, DocumentoProyecto, Evento, Proyecto, ProyectoMiembro, Tarea

CLAVE = "Clave$egura2026"
MEDIA_TEMPORAL = tempfile.mkdtemp(prefix="xincronix_media_")


def cliente_de(usuario):
    c = Client()
    c.force_login(usuario)
    return c


@override_settings(MEDIA_ROOT=MEDIA_TEMPORAL)
class ModulosTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.lider = Usuario.objects.create_user("lider@prueba.com", CLAVE, perfil="estudiante", first_name="Prueba", last_name="Usuario")
        cls.editor = Usuario.objects.create_user("editor@prueba.com", CLAVE, perfil="profesional", first_name="Prueba", last_name="Usuario")
        cls.lector = Usuario.objects.create_user("lector@prueba.com", CLAVE, perfil="profesor", first_name="Prueba", last_name="Usuario")
        cls.supervisor = Usuario.objects.create_user("prof@prueba.com", CLAVE, rol=Usuario.Rol.SUPERVISOR, perfil="profesor", first_name="Prueba", last_name="Usuario")
        cls.p = Proyecto.objects.create(nombre="Módulos", creado_por=cls.lider, supervisor=cls.supervisor,
                                        modalidad=Proyecto.Modalidad.GRUPAL, descripcion="Descripción de prueba")
        ProyectoMiembro.objects.create(proyecto=cls.p, usuario=cls.lider, rol=ProyectoMiembro.Rol.LIDER)
        ProyectoMiembro.objects.create(proyecto=cls.p, usuario=cls.editor, rol=ProyectoMiembro.Rol.EDITOR)
        ProyectoMiembro.objects.create(proyecto=cls.p, usuario=cls.lector, rol=ProyectoMiembro.Rol.LECTOR)
        cls.tarea = Tarea.objects.create(titulo="Original", proyecto=cls.p, creado_por=cls.lider)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_TEMPORAL, ignore_errors=True)

    # --- Páginas del proyecto -------------------------------------------------
    def test_todas_las_paginas_del_proyecto_cargan_para_el_lider(self):
        c = cliente_de(self.lider)
        for nombre in ("proyecto_detalle", "proyecto_tablero", "proyecto_calendario", "proyecto_roadmap",
                       "proyecto_analytics", "proyecto_canvas", "tareas", "proyectos", "panel"):
            with self.subTest(pagina=nombre):
                args = [] if nombre in ("tareas", "proyectos", "panel") else [self.p.pk]
                self.assertEqual(c.get(reverse(nombre, args=args)).status_code, 200)

    def test_el_lector_ve_las_paginas_de_solo_lectura(self):
        c = cliente_de(self.lector)
        self.assertEqual(c.get(reverse("proyecto_detalle", args=[self.p.pk])).status_code, 200)
        self.assertEqual(c.get(reverse("proyecto_roadmap", args=[self.p.pk])).status_code, 200)

    # --- Editar proyecto ------------------------------------------------------
    def test_el_editor_puede_editar_el_proyecto(self):
        r = cliente_de(self.editor).post(reverse("proyecto_editar", args=[self.p.pk]), {
            "nombre": "Módulos v2", "descripcion": "Proyecto de prueba", "tecnologia": "Django", "repositorio_url": "",
            "estado": "en_progreso", "fecha_inicio": "", "fecha_fin": "", "supervisor": "",
        })
        self.assertEqual(r.status_code, 302)
        self.p.refresh_from_db()
        self.assertEqual(self.p.nombre, "Módulos v2")

    def test_el_lector_no_puede_editar_el_proyecto(self):
        r = cliente_de(self.lector).post(reverse("proyecto_editar", args=[self.p.pk]), {
            "nombre": "Hackeado", "estado": "planificacion"})
        self.assertEqual(r.status_code, 403)
        self.p.refresh_from_db()
        self.assertNotEqual(self.p.nombre, "Hackeado")

    def test_fechas_al_reves_se_rechazan_al_editar(self):
        r = cliente_de(self.lider).post(reverse("proyecto_editar", args=[self.p.pk]), {
            "nombre": "Módulos", "estado": "planificacion",
            "fecha_inicio": "2026-12-10", "fecha_fin": "2026-12-01",
        })
        self.assertEqual(r.status_code, 200)  # vuelve al formulario con el error

    # --- Tareas: editar y eliminar -------------------------------------------
    def test_el_editor_edita_una_tarea(self):
        r = cliente_de(self.editor).post(reverse("tarea_editar", args=[self.tarea.pk]), {
            "titulo": "Editada", "descripcion": "", "estado": "en_progreso", "prioridad": "alta",
            "fecha_vencimiento": "", "asignado_a": "",
        })
        self.assertEqual(r.status_code, 302)
        self.tarea.refresh_from_db()
        self.assertEqual((self.tarea.titulo, self.tarea.estado), ("Editada", "en_progreso"))

    def test_el_lector_no_elimina_tareas(self):
        self.assertEqual(cliente_de(self.lector).post(reverse("tarea_eliminar", args=[self.tarea.pk])).status_code, 403)
        self.assertTrue(Tarea.objects.filter(pk=self.tarea.pk).exists())

    def test_eliminar_tarea_con_confirmacion(self):
        otra = Tarea.objects.create(titulo="Para borrar", proyecto=self.p, creado_por=self.lider)
        self.assertEqual(cliente_de(self.lider).get(reverse("tarea_eliminar", args=[otra.pk])).status_code, 200)
        cliente_de(self.lider).post(reverse("tarea_eliminar", args=[otra.pk]))
        self.assertFalse(Tarea.objects.filter(pk=otra.pk).exists())

    # --- Calendario -----------------------------------------------------------
    def test_crear_evento_en_el_calendario(self):
        inicio = timezone.now() + timedelta(days=2)
        r = cliente_de(self.editor).post(reverse("evento_crear", args=[self.p.pk]), {
            "titulo": "Entrega", "descripcion": "", "inicia_en": inicio.strftime("%Y-%m-%dT%H:%M"), "termina_en": "",
        })
        self.assertEqual(r.status_code, 302)
        self.assertTrue(Evento.objects.filter(proyecto=self.p, titulo="Entrega").exists())

    def test_evento_con_fin_antes_del_inicio_no_se_guarda(self):
        inicio = timezone.now() + timedelta(days=2)
        fin = inicio - timedelta(hours=1)
        cliente_de(self.editor).post(reverse("evento_crear", args=[self.p.pk]), {
            "titulo": "Al revés", "descripcion": "",
            "inicia_en": inicio.strftime("%Y-%m-%dT%H:%M"), "termina_en": fin.strftime("%Y-%m-%dT%H:%M"),
        })
        self.assertFalse(Evento.objects.filter(titulo="Al revés").exists())

    def test_el_lector_no_crea_eventos(self):
        r = cliente_de(self.lector).post(reverse("evento_crear", args=[self.p.pk]), {"titulo": "X"})
        self.assertEqual(r.status_code, 403)

    # --- Documentos -----------------------------------------------------------
    def test_subir_documento_permitido(self):
        archivo = SimpleUploadedFile("informe.pdf", b"%PDF-1.4 contenido", content_type="application/pdf")
        r = cliente_de(self.editor).post(reverse("documento_subir", args=[self.p.pk]), {"nombre": "Informe", "archivo": archivo})
        self.assertEqual(r.status_code, 302)
        doc = DocumentoProyecto.objects.get(proyecto=self.p, nombre="Informe")
        self.assertEqual(doc.subido_por, self.editor)

    def test_subir_archivo_ejecutable_o_html_se_rechaza(self):
        for nombre in ("virus.exe", "pagina.html", "script.js"):
            with self.subTest(archivo=nombre):
                archivo = SimpleUploadedFile(nombre, b"contenido", content_type="application/octet-stream")
                cliente_de(self.editor).post(reverse("documento_subir", args=[self.p.pk]), {"nombre": nombre, "archivo": archivo})
                self.assertFalse(DocumentoProyecto.objects.filter(nombre=nombre).exists())

    def test_archivo_demasiado_grande_se_rechaza(self):
        grande = SimpleUploadedFile("grande.pdf", b"0" * (10 * 1024 * 1024 + 1), content_type="application/pdf")
        cliente_de(self.editor).post(reverse("documento_subir", args=[self.p.pk]), {"nombre": "Grande", "archivo": grande})
        self.assertFalse(DocumentoProyecto.objects.filter(nombre="Grande").exists())

    def test_el_lector_no_sube_documentos(self):
        archivo = SimpleUploadedFile("nota.txt", b"hola", content_type="text/plain")
        r = cliente_de(self.lector).post(reverse("documento_subir", args=[self.p.pk]), {"nombre": "Nota", "archivo": archivo})
        self.assertEqual(r.status_code, 403)

    def test_eliminar_documento(self):
        archivo = SimpleUploadedFile("borrar.txt", b"hola", content_type="text/plain")
        cliente_de(self.editor).post(reverse("documento_subir", args=[self.p.pk]), {"nombre": "Borrar", "archivo": archivo})
        doc = DocumentoProyecto.objects.get(nombre="Borrar")
        cliente_de(self.editor).post(reverse("documento_eliminar", args=[self.p.pk, doc.pk]))
        self.assertFalse(DocumentoProyecto.objects.filter(pk=doc.pk).exists())

    # --- Correcciones del supervisor ------------------------------------------
    def test_el_supervisor_registra_una_correccion(self):
        r = cliente_de(self.supervisor).post(reverse("correccion_crear", args=[self.p.pk]), {
            "tarea": self.tarea.pk, "comentario": "Falta una prueba", "sugerencia_calificacion": "",
        })
        self.assertEqual(r.status_code, 302)
        self.assertTrue(Correccion.objects.filter(proyecto=self.p, comentario="Falta una prueba").exists())

    def test_el_editor_no_registra_correcciones(self):
        r = cliente_de(self.editor).post(reverse("correccion_crear", args=[self.p.pk]), {"comentario": "Yo mismo"})
        self.assertEqual(r.status_code, 403)
        self.assertFalse(Correccion.objects.filter(comentario="Yo mismo").exists())

    def test_correccion_no_puede_apuntar_a_tarea_de_otro_proyecto(self):
        otro = Proyecto.objects.create(nombre="Ajeno", creado_por=self.lider, descripcion="Descripción de prueba")
        tarea_ajena = Tarea.objects.create(titulo="De otro", proyecto=otro, creado_por=self.lider)
        cliente_de(self.supervisor).post(reverse("correccion_crear", args=[self.p.pk]), {
            "tarea": tarea_ajena.pk, "comentario": "Cruzada", "sugerencia_calificacion": "",
        })
        self.assertFalse(Correccion.objects.filter(comentario="Cruzada").exists())
