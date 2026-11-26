"""Flujos de proyecto más largos: salir, retirar, vencimientos, borrados y enlaces."""

import datetime as dt
import json

from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from cuentas.models import Usuario
from dashboard.models import Correccion, DocumentoProyecto, Evento, InvitacionProyecto, Proyecto, ProyectoMiembro, Tarea

CLAVE = "Clave$egura2026"


def cliente_de(usuario):
    c = Client()
    c.force_login(usuario)
    return c


class FlujosExtraTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.lider = Usuario.objects.create_user("lider@prueba.com", CLAVE, first_name="Lía", last_name="Paz", perfil="estudiante")
        cls.editor = Usuario.objects.create_user("editor@prueba.com", CLAVE, first_name="Edu", last_name="Sol", perfil="profesional")
        cls.lector = Usuario.objects.create_user("lector@prueba.com", CLAVE, first_name="Luz", last_name="Mar", perfil="profesor")
        cls.p = Proyecto.objects.create(nombre="Equipo", descripcion="Descripción", creado_por=cls.lider, modalidad="grupal")
        cls.m_lider = ProyectoMiembro.objects.create(proyecto=cls.p, usuario=cls.lider, rol="lider")
        cls.m_editor = ProyectoMiembro.objects.create(proyecto=cls.p, usuario=cls.editor, rol="editor")
        cls.m_lector = ProyectoMiembro.objects.create(proyecto=cls.p, usuario=cls.lector, rol="lector")

    def test_un_integrante_puede_salir_y_el_proyecto_sigue(self):
        r = cliente_de(self.lector).post(reverse("miembro_quitar", args=[self.p.pk, self.m_lector.pk]))
        self.assertEqual(r.status_code, 302)
        self.assertFalse(ProyectoMiembro.objects.filter(pk=self.m_lector.pk).exists())
        self.assertTrue(Proyecto.objects.filter(pk=self.p.pk).exists())

    def test_el_lider_no_puede_salir_de_su_proyecto(self):
        cliente_de(self.lider).post(reverse("miembro_quitar", args=[self.p.pk, self.m_lider.pk]))
        self.assertTrue(ProyectoMiembro.objects.filter(pk=self.m_lider.pk).exists())

    def test_editor_no_retira_a_otros(self):
        self.assertEqual(cliente_de(self.editor).post(reverse("miembro_quitar", args=[self.p.pk, self.m_lector.pk])).status_code, 403)

    def test_al_salir_el_integrante_queda_sin_sus_tareas(self):
        tarea = Tarea.objects.create(titulo="De Luz", proyecto=self.p, asignado_a=self.lector, creado_por=self.lider)
        cliente_de(self.lector).post(reverse("miembro_quitar", args=[self.p.pk, self.m_lector.pk]))
        tarea.refresh_from_db()
        self.assertIsNone(tarea.asignado_a)
        self.assertTrue(Tarea.objects.filter(pk=tarea.pk).exists())

    def test_al_retirar_a_un_integrante_su_tarea_queda_sin_responsable(self):
        tarea = Tarea.objects.create(titulo="De Edu", proyecto=self.p, asignado_a=self.editor, creado_por=self.lider)
        cliente_de(self.lider).post(reverse("miembro_quitar", args=[self.p.pk, self.m_editor.pk]))
        tarea.refresh_from_db()
        self.assertIsNone(tarea.asignado_a)

    def test_invitacion_vencida_no_bloquea_una_nueva(self):
        InvitacionProyecto.objects.create(proyecto=self.p, email="nuevo@prueba.com", rol="editor", creado_por=self.lider,
                                          vence_en=timezone.now() - dt.timedelta(days=1))
        cliente_de(self.lider).post(reverse("invitacion_crear", args=[self.p.pk]), {"email": "nuevo@prueba.com", "rol": "editor"})
        self.assertEqual(InvitacionProyecto.objects.filter(proyecto=self.p, email="nuevo@prueba.com").count(), 2)

    def test_invitacion_vigente_si_bloquea_otra(self):
        InvitacionProyecto.objects.create(proyecto=self.p, email="vigente@prueba.com", rol="editor", creado_por=self.lider,
                                          vence_en=timezone.now() + dt.timedelta(days=3))
        cliente_de(self.lider).post(reverse("invitacion_crear", args=[self.p.pk]), {"email": "vigente@prueba.com", "rol": "editor"})
        self.assertEqual(InvitacionProyecto.objects.filter(proyecto=self.p, email="vigente@prueba.com").count(), 1)

    def test_borrar_el_proyecto_borra_su_contenido(self):
        otro = Proyecto.objects.create(nombre="Borrable", descripcion="d", creado_por=self.lider)
        ProyectoMiembro.objects.create(proyecto=otro, usuario=self.lider, rol="lider")
        Tarea.objects.create(titulo="T", proyecto=otro, creado_por=self.lider)
        Evento.objects.create(proyecto=otro, titulo="E", inicia_en=timezone.now(), creado_por=self.lider)
        InvitacionProyecto.objects.create(proyecto=otro, email="z@prueba.com", rol="editor", creado_por=self.lider,
                                          vence_en=timezone.now() + dt.timedelta(days=2))
        cliente_de(self.lider).post(reverse("proyecto_eliminar", args=[otro.pk]))
        self.assertFalse(Tarea.objects.filter(proyecto_id=otro.pk).exists())
        self.assertFalse(Evento.objects.filter(proyecto_id=otro.pk).exists())
        self.assertFalse(InvitacionProyecto.objects.filter(proyecto_id=otro.pk).exists())

    def test_enlace_publico_de_un_proyecto_borrado_da_404(self):
        otro = Proyecto.objects.create(nombre="Publico", descripcion="d", creado_por=self.lider, visibilidad="publico")
        ProyectoMiembro.objects.create(proyecto=otro, usuario=self.lider, rol="lider")
        enlace = otro.enlace_publico
        otro.delete()
        self.assertEqual(Client().get(f"/publico/{enlace}/").status_code, 404)

    def test_la_pagina_publica_muestra_las_tareas_del_proyecto(self):
        Proyecto.objects.filter(pk=self.p.pk).update(visibilidad="publico")
        Tarea.objects.create(titulo="Visible", proyecto=self.p, creado_por=self.lider)
        self.assertContains(Client().get(f"/publico/{self.p.enlace_publico}/"), "Visible")

    def test_tarea_de_quien_se_borro_sigue_en_el_tablero(self):
        autor = Usuario.objects.create_user("autor@prueba.com", CLAVE, first_name="Autor", last_name="X", perfil="estudiante")
        ProyectoMiembro.objects.create(proyecto=self.p, usuario=autor, rol="editor")
        tarea = Tarea.objects.create(titulo="Historia", proyecto=self.p, creado_por=autor)
        autor.delete()
        tarea.refresh_from_db()
        self.assertIsNone(tarea.creado_por)
        self.assertEqual(cliente_de(self.lider).get(reverse("proyecto_tablero", args=[self.p.pk])).status_code, 200)

    def test_correccion_sin_tarea_es_valida(self):
        c = Correccion.objects.create(proyecto=self.p, tarea=None, comentario="Revisar la estructura", autor=self.lider)
        self.assertIsNone(c.tarea)

    def test_documento_se_guarda_con_su_autor(self):
        doc = DocumentoProyecto.objects.create(proyecto=self.p, nombre="Acta", archivo="actas/acta.pdf", subido_por=self.editor)
        self.assertEqual(doc.subido_por, self.editor)

    def test_cambiar_rol_no_quita_las_tareas(self):
        tarea = Tarea.objects.create(titulo="Se queda", proyecto=self.p, asignado_a=self.editor, creado_por=self.lider)
        cliente_de(self.lider).post(reverse("miembro_cambiar_rol", args=[self.p.pk, self.m_editor.pk]), {"rol": "lector"})
        tarea.refresh_from_db()
        self.assertEqual(tarea.asignado_a, self.editor)

    def test_el_tablero_responde_a_un_movimiento_valido(self):
        tarea = Tarea.objects.create(titulo="Mover", proyecto=self.p, creado_por=self.lider)
        r = cliente_de(self.editor).post(reverse("tarea_mover", args=[self.p.pk, tarea.pk]),
                                         data=json.dumps({"estado": "revision"}), content_type="application/json")
        self.assertEqual(r.json()["estado"], "revision")
