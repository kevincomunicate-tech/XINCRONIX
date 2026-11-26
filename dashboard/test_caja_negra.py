"""Pruebas de caja negra de proyectos: flujo completo por HTTP, como un usuario.

Cada prueba cuenta una historia: crear, invitar, trabajar en el tablero,
guardar el canvas, y comprobar qué puede hacer cada rol y qué no.
"""

import json

from django.core import mail
from django.test import Client, TestCase
from django.urls import reverse

from cuentas.models import Usuario
from dashboard.models import InvitacionProyecto, Proyecto, ProyectoMiembro, Tarea

CLAVE = "Clave$egura2026"


def cliente_de(usuario, forzar_csrf=False):
    c = Client(enforce_csrf_checks=forzar_csrf)
    c.force_login(usuario)
    return c


class FlujoProyectoTests(TestCase):
    """Historia principal: Ana crea un proyecto grupal y trabaja con Beto."""

    @classmethod
    def setUpTestData(cls):
        cls.ana = Usuario.objects.create_user("ana@prueba.com", CLAVE, first_name="Ana", perfil="estudiante", last_name="Usuario")
        cls.beto = Usuario.objects.create_user("beto@prueba.com", CLAVE, first_name="Beto", perfil="profesional", last_name="Usuario")
        cls.ajeno = Usuario.objects.create_user("ajeno@prueba.com", CLAVE, first_name="Ajeno", last_name="Usuario")

    def crear_proyecto_grupal(self, cliente, nombre="App de notas"):
        # Paso 1: orientación (modalidad). Paso 2: datos del proyecto.
        cliente.post(reverse("proyecto_orientacion"), {"finalidad": "educativo", "metodologia": "kanban",
                                                        "modalidad": "grupal", "contexto_educativo": "",
                                                        "supervisor_email": ""})
        r = cliente.post(reverse("proyecto_crear"), {"nombre": nombre, "descripcion": "Notas de clase",
                                                     "tecnologia": "Django", "repositorio_url": "",
                                                     "estado": "planificacion", "fecha_inicio": "",
                                                     "fecha_fin": "", "supervisor": ""})
        self.assertEqual(r.status_code, 302)
        return Proyecto.objects.get(nombre=nombre)

    def test_crear_proyecto_y_quedar_como_lider(self):
        p = self.crear_proyecto_grupal(cliente_de(self.ana))
        self.assertEqual(p.creado_por, self.ana)
        self.assertEqual(p.modalidad, Proyecto.Modalidad.GRUPAL)
        self.assertEqual(p.proyectomiembro_set.get(usuario=self.ana).rol, ProyectoMiembro.Rol.LIDER)

    def test_crear_tarea_y_moverla_hasta_hecha(self):
        ana = cliente_de(self.ana)
        p = self.crear_proyecto_grupal(ana)
        r = ana.post(reverse("tarea_crear", args=[p.pk]), {"titulo": "Diseñar pantallas", "descripcion": "",
                                                           "estado": "por_hacer", "prioridad": "media",
                                                           "fecha_vencimiento": "", "asignado_a": ""})
        self.assertEqual(r.status_code, 302)
        tarea = Tarea.objects.get(titulo="Diseñar pantallas")
        r = ana.post(reverse("tarea_mover", args=[p.pk, tarea.pk]), data=json.dumps({"estado": "hecha"}),
                     content_type="application/json")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {"ok": True, "estado": "hecha", "progreso": 100})

    def test_mover_a_un_estado_inventado_se_rechaza(self):
        ana = cliente_de(self.ana)
        p = self.crear_proyecto_grupal(ana)
        tarea = Tarea.objects.create(titulo="X", proyecto=p, creado_por=self.ana)
        r = ana.post(reverse("tarea_mover", args=[p.pk, tarea.pk]), data=json.dumps({"estado": "volando"}),
                     content_type="application/json")
        self.assertEqual(r.status_code, 400)
        tarea.refresh_from_db()
        self.assertEqual(tarea.estado, Tarea.Estado.POR_HACER)

    def test_mover_con_json_roto_se_rechaza(self):
        ana = cliente_de(self.ana)
        p = self.crear_proyecto_grupal(ana)
        tarea = Tarea.objects.create(titulo="X", proyecto=p, creado_por=self.ana)
        r = ana.post(reverse("tarea_mover", args=[p.pk, tarea.pk]), data="{no-es-json",
                     content_type="application/json")
        self.assertEqual(r.status_code, 400)

    def test_invitar_por_correo_envia_el_enlace(self):
        ana = cliente_de(self.ana)
        p = self.crear_proyecto_grupal(ana)
        r = ana.post(reverse("invitacion_crear", args=[p.pk]), {"email": "beto@prueba.com", "rol": "editor"})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("App de notas", mail.outbox[0].subject)
        self.assertIn("beto@prueba.com", mail.outbox[0].body)
        self.assertTrue(InvitacionProyecto.objects.filter(proyecto=p, email="beto@prueba.com").exists())

    def test_invitado_acepta_el_enlace_y_trabaja_como_editor(self):
        ana = cliente_de(self.ana)
        p = self.crear_proyecto_grupal(ana)
        ana.post(reverse("invitacion_crear", args=[p.pk]), {"email": "beto@prueba.com", "rol": "editor"})
        invitacion = InvitacionProyecto.objects.get(email="beto@prueba.com")

        beto = cliente_de(self.beto)
        self.assertEqual(beto.get(reverse("proyecto_detalle", args=[p.pk])).status_code, 404)  # aún no es miembro
        r = beto.get(reverse("invitacion_aceptar", args=[invitacion.token]))
        self.assertEqual(r.status_code, 302)
        invitacion.refresh_from_db()
        self.assertEqual(invitacion.estado, InvitacionProyecto.Estado.ACEPTADA)

        self.assertEqual(beto.get(reverse("proyecto_tablero", args=[p.pk])).status_code, 200)
        self.assertEqual(p.proyectomiembro_set.get(usuario=self.beto).rol, ProyectoMiembro.Rol.EDITOR)

    def test_invitacion_no_se_acepta_con_otra_cuenta(self):
        ana = cliente_de(self.ana)
        p = self.crear_proyecto_grupal(ana)
        ana.post(reverse("invitacion_crear", args=[p.pk]), {"email": "beto@prueba.com", "rol": "editor"})
        invitacion = InvitacionProyecto.objects.get(email="beto@prueba.com")
        r = cliente_de(self.ajeno).get(reverse("invitacion_aceptar", args=[invitacion.token]))
        self.assertEqual(r.status_code, 403)
        self.assertFalse(p.proyectomiembro_set.filter(usuario=self.ajeno).exists())

    def test_correo_invalido_no_crea_invitacion(self):
        ana = cliente_de(self.ana)
        p = self.crear_proyecto_grupal(ana)
        ana.post(reverse("invitacion_crear", args=[p.pk]), {"email": "no-es-correo", "rol": "editor"})
        self.assertFalse(InvitacionProyecto.objects.filter(proyecto=p).exists())
        self.assertEqual(len(mail.outbox), 0)

    def test_invitar_desde_un_proyecto_individual_lo_vuelve_grupal(self):
        ana = cliente_de(self.ana)
        ana.post(reverse("proyecto_orientacion"), {"modalidad": "individual"})
        ana.post(reverse("proyecto_crear"), {"nombre": "Solo", "descripcion": "Proyecto de prueba", "tecnologia": "", "repositorio_url": "",
                                             "estado": "planificacion", "fecha_inicio": "", "fecha_fin": "", "supervisor": ""})
        p = Proyecto.objects.get(nombre="Solo")
        self.assertEqual(p.modalidad, Proyecto.Modalidad.INDIVIDUAL)
        ana.post(reverse("invitacion_crear", args=[p.pk]), {"email": "beto@prueba.com", "rol": "editor"})
        p.refresh_from_db()
        self.assertEqual(p.modalidad, Proyecto.Modalidad.GRUPAL)
        self.assertTrue(InvitacionProyecto.objects.filter(proyecto=p, email="beto@prueba.com").exists())

    def test_invitacion_invalida_no_cambia_la_modalidad(self):
        ana = cliente_de(self.ana)
        ana.post(reverse("proyecto_orientacion"), {"modalidad": "individual"})
        ana.post(reverse("proyecto_crear"), {"nombre": "Quieto", "descripcion": "Proyecto de prueba", "tecnologia": "", "repositorio_url": "",
                                             "estado": "planificacion", "fecha_inicio": "", "fecha_fin": "", "supervisor": ""})
        p = Proyecto.objects.get(nombre="Quieto")
        ana.post(reverse("invitacion_crear", args=[p.pk]), {"email": "no-es-correo", "rol": "editor"})
        p.refresh_from_db()
        self.assertEqual(p.modalidad, Proyecto.Modalidad.INDIVIDUAL)


class PermisosPorRolTests(TestCase):
    """Lo que puede y no puede hacer cada rol dentro de un proyecto."""

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

    def test_lector_ve_el_tablero_pero_no_crea_tareas(self):
        c = cliente_de(self.lector)
        self.assertEqual(c.get(reverse("proyecto_tablero", args=[self.p.pk])).status_code, 200)
        r = c.post(reverse("tarea_crear", args=[self.p.pk]), {"titulo": "Intento", "estado": "por_hacer", "prioridad": "media"})
        self.assertEqual(r.status_code, 403)
        self.assertFalse(Tarea.objects.filter(titulo="Intento").exists())

    def test_lector_no_mueve_tareas(self):
        r = cliente_de(self.lector).post(reverse("tarea_mover", args=[self.p.pk, self.tarea.pk]),
                                         data=json.dumps({"estado": "hecha"}), content_type="application/json")
        self.assertEqual(r.status_code, 403)

    def test_editor_mueve_tareas_pero_no_elimina_el_proyecto(self):
        c = cliente_de(self.editor)
        r = c.post(reverse("tarea_mover", args=[self.p.pk, self.tarea.pk]),
                   data=json.dumps({"estado": "en_progreso"}), content_type="application/json")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(c.post(reverse("proyecto_eliminar", args=[self.p.pk])).status_code, 403)
        self.assertTrue(Proyecto.objects.filter(pk=self.p.pk).exists())

    def test_editor_no_invita_ni_quita_miembros(self):
        c = cliente_de(self.editor)
        self.assertEqual(c.post(reverse("invitacion_crear", args=[self.p.pk]), {"email": "x@prueba.com", "rol": "lector"}).status_code, 403)
        self.assertEqual(c.post(reverse("miembro_quitar", args=[self.p.pk, self.lector.pk])).status_code, 403)
        self.assertTrue(ProyectoMiembro.objects.filter(proyecto=self.p, usuario=self.lector).exists())

    def test_lider_quita_a_un_miembro(self):
        r = cliente_de(self.lider).post(reverse("miembro_quitar", args=[self.p.pk, self.lector.pk]))
        self.assertEqual(r.status_code, 302)
        self.assertFalse(ProyectoMiembro.objects.filter(proyecto=self.p, usuario=self.lector).exists())

    def test_el_lider_no_puede_salirse_de_su_propio_proyecto(self):
        cliente_de(self.lider).post(reverse("miembro_quitar", args=[self.p.pk, self.lider.pk]))
        self.assertTrue(ProyectoMiembro.objects.filter(proyecto=self.p, usuario=self.lider).exists())

    def test_lider_elimina_el_proyecto(self):
        r = cliente_de(self.lider).post(reverse("proyecto_eliminar", args=[self.p.pk]))
        self.assertEqual(r.status_code, 302)
        self.assertFalse(Proyecto.objects.filter(pk=self.p.pk).exists())


class AislamientoTests(TestCase):
    """Un usuario sin relación con el proyecto no ve ni toca nada de él."""

    @classmethod
    def setUpTestData(cls):
        cls.lider = Usuario.objects.create_user("lider@prueba.com", CLAVE, perfil="estudiante", first_name="Prueba", last_name="Usuario")
        cls.ajeno = Usuario.objects.create_user("ajeno@prueba.com", CLAVE, perfil="estudiante", first_name="Prueba", last_name="Usuario")
        cls.p = Proyecto.objects.create(nombre="Secreto", creado_por=cls.lider, descripcion="Descripción de prueba")
        cls.tarea = Tarea.objects.create(titulo="Privada", proyecto=cls.p, creado_por=cls.lider)

    def test_ajeno_recibe_404_en_las_paginas_del_proyecto(self):
        c = cliente_de(self.ajeno)
        for nombre in ("proyecto_detalle", "proyecto_tablero", "proyecto_calendario", "proyecto_roadmap",
                       "proyecto_analytics", "proyecto_canvas"):
            with self.subTest(pagina=nombre):
                self.assertEqual(c.get(reverse(nombre, args=[self.p.pk])).status_code, 404)

    def test_ajeno_no_mueve_ni_guarda_nada(self):
        c = cliente_de(self.ajeno)
        r = c.post(reverse("tarea_mover", args=[self.p.pk, self.tarea.pk]), data=json.dumps({"estado": "hecha"}),
                   content_type="application/json")
        self.assertEqual(r.status_code, 404)
        r = c.post(reverse("canvas_guardar", args=[self.p.pk]), data=json.dumps({"contenido": {}}),
                   content_type="application/json")
        self.assertEqual(r.status_code, 404)
        self.tarea.refresh_from_db()
        self.assertEqual(self.tarea.estado, Tarea.Estado.POR_HACER)

    def test_la_lista_de_proyectos_no_muestra_los_ajenos(self):
        self.assertNotContains(cliente_de(self.ajeno).get(reverse("proyectos")), "Secreto")

    def test_ajeno_no_ve_la_tarea_en_la_lista_de_tareas(self):
        self.assertNotContains(cliente_de(self.ajeno).get(reverse("tareas")), "Privada")


class CanvasTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.lider = Usuario.objects.create_user("lider@prueba.com", CLAVE, perfil="estudiante", first_name="Prueba", last_name="Usuario")
        cls.p = Proyecto.objects.create(nombre="Mapa", creado_por=cls.lider, descripcion="Descripción de prueba")
        ProyectoMiembro.objects.create(proyecto=cls.p, usuario=cls.lider, rol=ProyectoMiembro.Rol.LIDER)

    def test_guardar_canvas_sube_la_version(self):
        c = cliente_de(self.lider)
        url = reverse("canvas_guardar", args=[self.p.pk])
        r1 = c.post(url, data=json.dumps({"nombre": "Mapa 1", "contenido": {"notas": ["a"]}}), content_type="application/json")
        r2 = c.post(url, data=json.dumps({"nombre": "Mapa 1", "contenido": {"notas": ["a", "b"]}}), content_type="application/json")
        # Cada guardado suma una versión: la segunda es exactamente la primera + 1.
        self.assertEqual(r2.json()["version"], r1.json()["version"] + 1)

    def test_canvas_con_contenido_que_no_es_objeto_se_rechaza(self):
        r = cliente_de(self.lider).post(reverse("canvas_guardar", args=[self.p.pk]),
                                        data=json.dumps({"contenido": ["no", "es", "dict"]}), content_type="application/json")
        self.assertEqual(r.status_code, 400)

    def test_la_pagina_del_canvas_carga(self):
        self.assertEqual(cliente_de(self.lider).get(reverse("proyecto_canvas", args=[self.p.pk])).status_code, 200)


class SeguridadWebTests(TestCase):
    """Protecciones básicas: CSRF y acceso sin sesión."""

    @classmethod
    def setUpTestData(cls):
        cls.lider = Usuario.objects.create_user("lider@prueba.com", CLAVE, perfil="estudiante", first_name="Prueba", last_name="Usuario")
        cls.p = Proyecto.objects.create(nombre="Seguro", creado_por=cls.lider, descripcion="Descripción de prueba")
        cls.tarea = Tarea.objects.create(titulo="T", proyecto=cls.p, creado_por=cls.lider)

    def test_post_sin_token_csrf_es_rechazado(self):
        c = cliente_de(self.lider, forzar_csrf=True)
        r = c.post(reverse("tarea_mover", args=[self.p.pk, self.tarea.pk]), data=json.dumps({"estado": "hecha"}),
                   content_type="application/json")
        self.assertEqual(r.status_code, 403)
        self.tarea.refresh_from_db()
        self.assertEqual(self.tarea.estado, Tarea.Estado.POR_HACER)

    def test_sin_sesion_no_se_puede_ver_el_proyecto(self):
        r = Client().get(reverse("proyecto_detalle", args=[self.p.pk]))
        self.assertEqual(r.status_code, 302)
        self.assertIn("/cuentas/login/", r["Location"])

    def test_sin_sesion_no_se_puede_borrar_el_proyecto(self):
        Client().post(reverse("proyecto_eliminar", args=[self.p.pk]))
        self.assertTrue(Proyecto.objects.filter(pk=self.p.pk).exists())

    def test_superusuario_ve_proyectos_ajenos(self):
        super_ = Usuario.objects.create_superuser("super@prueba.com", CLAVE, first_name="Prueba", last_name="Usuario")
        self.assertEqual(cliente_de(super_).get(reverse("proyecto_detalle", args=[self.p.pk])).status_code, 200)
