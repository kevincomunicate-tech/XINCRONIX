"""Visibilidad (privado o público con enlace), modalidad, invitar siempre disponible
y permisos que da el líder a cada integrante."""

import uuid

from django.test import Client, TestCase
from django.urls import reverse

from cuentas.models import Usuario
from dashboard.forms import ProyectoForm, ProyectoLiderForm
from dashboard.models import DocumentoProyecto, InvitacionProyecto, Proyecto, ProyectoMiembro, Tarea

CLAVE = "Clave$egura2026"


def cliente_de(usuario=None):
    c = Client()
    if usuario is not None:
        c.force_login(usuario)
    return c


class Base(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.lider = Usuario.objects.create_user("lider@prueba.com", CLAVE, first_name="Lía", perfil="estudiante", last_name="Usuario")
        cls.editor = Usuario.objects.create_user("editor@prueba.com", CLAVE, first_name="Edu", perfil="profesional", last_name="Usuario")
        cls.lector = Usuario.objects.create_user("lector@prueba.com", CLAVE, first_name="Luz", perfil="profesor", last_name="Usuario")
        cls.ajeno = Usuario.objects.create_user("ajeno@prueba.com", CLAVE, first_name="Ajeno", perfil="estudiante", last_name="Usuario")
        cls.p = Proyecto.objects.create(nombre="Mi proyecto", creado_por=cls.lider, modalidad=Proyecto.Modalidad.GRUPAL,
                                        descripcion="Una app de notas")
        ProyectoMiembro.objects.create(proyecto=cls.p, usuario=cls.lider, rol=ProyectoMiembro.Rol.LIDER)
        ProyectoMiembro.objects.create(proyecto=cls.p, usuario=cls.editor, rol=ProyectoMiembro.Rol.EDITOR)
        ProyectoMiembro.objects.create(proyecto=cls.p, usuario=cls.lector, rol=ProyectoMiembro.Rol.LECTOR)
        cls.tarea = Tarea.objects.create(titulo="Diseñar pantalla", proyecto=cls.p, creado_por=cls.lider)


class CajaBlancaVisibilidadTests(TestCase):
    def test_proyecto_nuevo_es_privado_y_tiene_enlace_unico(self):
        a = Proyecto.objects.create(nombre="A", creado_por=Usuario.objects.create_user("a@prueba.com", CLAVE, first_name="Prueba", last_name="Usuario"), descripcion="Descripción de prueba")
        b = Proyecto.objects.create(nombre="B", creado_por=a.creado_por, descripcion="Descripción de prueba")
        self.assertEqual(a.visibilidad, Proyecto.Visibilidad.PRIVADO)
        self.assertIsInstance(a.enlace_publico, uuid.UUID)
        self.assertNotEqual(a.enlace_publico, b.enlace_publico)

    def test_el_formulario_del_lider_incluye_modalidad_y_visibilidad(self):
        self.assertIn("modalidad", ProyectoLiderForm().fields)
        self.assertIn("visibilidad", ProyectoLiderForm().fields)
        self.assertNotIn("visibilidad", ProyectoForm().fields)
        self.assertNotIn("modalidad", ProyectoForm().fields)

    def test_individual_con_integrantes_no_se_guarda(self):
        creador = Usuario.objects.create_user("c@prueba.com", CLAVE, first_name="Prueba", last_name="Usuario")
        p = Proyecto.objects.create(nombre="Con gente", creado_por=creador, modalidad=Proyecto.Modalidad.GRUPAL, descripcion="Descripción de prueba")
        ProyectoMiembro.objects.create(proyecto=p, usuario=Usuario.objects.create_user("d@prueba.com", CLAVE, first_name="Prueba", last_name="Usuario"), rol="editor")
        datos = {"nombre": "Con gente", "estado": "planificacion", "modalidad": "individual", "visibilidad": "privado"}
        form = ProyectoLiderForm(datos, instance=p)
        self.assertFalse(form.is_valid())


class EdicionDelLiderTests(Base):
    def editar(self, usuario, **datos):
        # Con integrantes en el equipo, el proyecto debe ser grupal (lo exige el modelo).
        base = {"nombre": "Mi proyecto", "estado": "planificacion", "descripcion": "Una app de notas",
                "modalidad": "grupal", "visibilidad": "privado"}
        base.update(datos)
        return cliente_de(usuario).post(reverse("proyecto_editar", args=[self.p.pk]), base)

    def test_el_lider_ve_los_campos_de_modalidad_y_visibilidad(self):
        r = cliente_de(self.lider).get(reverse("proyecto_editar", args=[self.p.pk]))
        self.assertContains(r, 'name="visibilidad"')
        self.assertContains(r, 'name="modalidad"')

    def test_el_editor_no_ve_ni_cambia_modalidad_ni_visibilidad(self):
        r = cliente_de(self.editor).get(reverse("proyecto_editar", args=[self.p.pk]))
        self.assertNotContains(r, 'name="visibilidad"')
        self.editar(self.editor, nombre="Cambiado por editor", visibilidad="publico", modalidad="grupal")
        self.p.refresh_from_db()
        self.assertEqual(self.p.nombre, "Cambiado por editor")  # el editor sí edita el contenido
        self.assertEqual(self.p.visibilidad, "privado")
        self.assertEqual(self.p.modalidad, "grupal")  # el editor no puede cambiarla

    def test_el_lector_no_edita_nada(self):
        self.assertEqual(cliente_de(self.lector).post(reverse("proyecto_editar", args=[self.p.pk]), {"nombre": "X", "estado": "planificacion"}).status_code, 403)

    def test_el_lider_hace_publico_el_proyecto(self):
        self.editar(self.lider, visibilidad="publico")
        self.p.refresh_from_db()
        self.assertEqual(self.p.visibilidad, Proyecto.Visibilidad.PUBLICO)

    def test_el_lider_pasa_a_grupal_y_luego_a_individual_si_no_hay_integrantes(self):
        Proyecto.objects.filter(pk=self.p.pk).update(modalidad="grupal")
        ProyectoMiembro.objects.filter(proyecto=self.p).exclude(usuario=self.lider).delete()
        self.editar(self.lider, modalidad="individual")
        self.p.refresh_from_db()
        self.assertEqual(self.p.modalidad, "individual")

    def test_no_se_puede_volver_individual_con_integrantes(self):
        self.editar(self.lider, modalidad="individual")
        self.p.refresh_from_db()
        self.assertEqual(self.p.modalidad, "grupal")  # el editor y el lector siguen ahí
        self.assertTrue(ProyectoMiembro.objects.filter(proyecto=self.p, usuario=self.editor).exists())


class InvitarSiempreTests(Base):
    def test_el_boton_de_invitar_siempre_aparece_para_el_lider(self):
        r = cliente_de(self.lider).get(reverse("proyecto_detalle", args=[self.p.pk]))
        self.assertContains(r, reverse("invitacion_crear", args=[self.p.pk]))

    def test_invitar_a_un_proyecto_individual_funciona_y_lo_vuelve_grupal(self):
        cliente_de(self.lider).post(reverse("invitacion_crear", args=[self.p.pk]), {"email": "nuevo@prueba.com", "rol": "lector"})
        self.p.refresh_from_db()
        self.assertEqual(self.p.modalidad, Proyecto.Modalidad.GRUPAL)
        inv = InvitacionProyecto.objects.get(email="nuevo@prueba.com")
        self.assertEqual(inv.rol, "lector")

    def test_un_solo_proyecto_puede_seguir_trabajando_sin_invitados(self):
        r = cliente_de(self.lider).get(reverse("tareas"))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(cliente_de(self.lider).post(reverse("tarea_crear", args=[self.p.pk]), {"titulo": "Solo", "estado": "por_hacer", "prioridad": "media"}).status_code, 302)


class EnlacePublicoTests(Base):
    def url(self, enlace=None):
        return reverse("proyecto_publico", args=[enlace or self.p.enlace_publico])

    def test_privado_el_enlace_no_existe(self):
        self.assertEqual(Client().get(self.url()).status_code, 404)

    def test_publico_se_ve_sin_iniciar_sesion(self):
        Proyecto.objects.filter(pk=self.p.pk).update(visibilidad=Proyecto.Visibilidad.PUBLICO)
        r = Client().get(self.url())
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Mi proyecto")
        self.assertContains(r, "Diseñar pantalla")
        self.assertEqual(r["X-Robots-Tag"], "noindex, nofollow")

    def test_publico_no_muestra_personas_ni_documentos(self):
        Proyecto.objects.filter(pk=self.p.pk).update(visibilidad=Proyecto.Visibilidad.PUBLICO)
        DocumentoProyecto.objects.create(proyecto=self.p, nombre="Secreto", archivo="secreto.pdf", subido_por=self.lider)
        html = Client().get(self.url()).content.decode()
        for dato in ("lider@prueba.com", "editor@prueba.com", "lector@prueba.com", "Secreto", "Lía", "Edu"):
            self.assertNotIn(dato, html)

    def test_enlace_inventado_da_404(self):
        Proyecto.objects.filter(pk=self.p.pk).update(visibilidad=Proyecto.Visibilidad.PUBLICO)
        self.assertEqual(Client().get(f"/publico/{uuid.uuid4()}/").status_code, 404)
        self.assertEqual(Client().get("/publico/no-es-uuid/").status_code, 404)

    def test_el_publico_no_puede_escribir(self):
        Proyecto.objects.filter(pk=self.p.pk).update(visibilidad=Proyecto.Visibilidad.PUBLICO)
        self.assertEqual(Client().post(self.url(), {"nombre": "Hack"}).status_code, 405)
        self.p.refresh_from_db()
        self.assertEqual(self.p.nombre, "Mi proyecto")

    def test_nombre_con_html_se_escapa_en_la_vista_publica(self):
        Proyecto.objects.filter(pk=self.p.pk).update(visibilidad=Proyecto.Visibilidad.PUBLICO, nombre="<b>x</b>")
        self.assertNotIn("<b>x</b>", Client().get(self.url()).content.decode())

    def test_si_vuelve_a_privado_el_enlace_deja_de_funcionar(self):
        Proyecto.objects.filter(pk=self.p.pk).update(visibilidad=Proyecto.Visibilidad.PUBLICO)
        Proyecto.objects.filter(pk=self.p.pk).update(visibilidad=Proyecto.Visibilidad.PRIVADO)
        self.assertEqual(Client().get(self.url()).status_code, 404)

    def test_regenerar_el_enlace_invalida_el_anterior(self):
        Proyecto.objects.filter(pk=self.p.pk).update(visibilidad=Proyecto.Visibilidad.PUBLICO)
        viejo = self.p.enlace_publico
        r = cliente_de(self.lider).post(reverse("proyecto_enlace_nuevo", args=[self.p.pk]))
        self.assertEqual(r.status_code, 302)
        self.p.refresh_from_db()
        self.assertNotEqual(self.p.enlace_publico, viejo)
        self.assertEqual(Client().get(self.url(viejo)).status_code, 404)
        self.assertEqual(Client().get(self.url()).status_code, 200)

    def test_solo_el_lider_regenera_el_enlace(self):
        for usuario in (self.editor, self.lector, self.ajeno):
            with self.subTest(usuario=usuario.email):
                r = cliente_de(usuario).post(reverse("proyecto_enlace_nuevo", args=[self.p.pk]))
                self.assertIn(r.status_code, (403, 404))

    def test_regenerar_solo_admite_post(self):
        self.assertEqual(cliente_de(self.lider).get(reverse("proyecto_enlace_nuevo", args=[self.p.pk])).status_code, 405)

    def test_la_pagina_del_lider_muestra_el_enlace_solo_si_es_publico(self):
        self.assertNotContains(cliente_de(self.lider).get(reverse("proyecto_detalle", args=[self.p.pk])), "/publico/")
        Proyecto.objects.filter(pk=self.p.pk).update(visibilidad=Proyecto.Visibilidad.PUBLICO)
        self.assertContains(cliente_de(self.lider).get(reverse("proyecto_detalle", args=[self.p.pk])), f"/publico/{self.p.enlace_publico}/")


class PermisosDeIntegrantesTests(Base):
    def cambiar(self, usuario, miembro, rol, proyecto=None):
        return cliente_de(usuario).post(reverse("miembro_cambiar_rol", args=[(proyecto or self.p).pk, miembro.pk]), {"rol": rol})

    def test_el_lider_da_solo_lectura_y_el_integrante_pierde_la_capacidad_de_escribir(self):
        miembro = ProyectoMiembro.objects.get(proyecto=self.p, usuario=self.editor)
        self.cambiar(self.lider, miembro, "lector")
        miembro.refresh_from_db()
        self.assertEqual(miembro.rol, "lector")
        r = cliente_de(self.editor).post(reverse("tarea_crear", args=[self.p.pk]), {"titulo": "Ya no", "estado": "por_hacer", "prioridad": "media"})
        self.assertEqual(r.status_code, 403)

    def test_el_lider_sube_a_lector_a_colaborador(self):
        miembro = ProyectoMiembro.objects.get(proyecto=self.p, usuario=self.lector)
        self.cambiar(self.lider, miembro, "editor")
        miembro.refresh_from_db()
        self.assertEqual(miembro.rol, "editor")

    def test_no_se_puede_asignar_el_rol_de_lider(self):
        miembro = ProyectoMiembro.objects.get(proyecto=self.p, usuario=self.editor)
        self.cambiar(self.lider, miembro, "lider")
        miembro.refresh_from_db()
        self.assertEqual(miembro.rol, "editor")

    def test_el_lider_no_cambia_su_propio_rol(self):
        mio = ProyectoMiembro.objects.get(proyecto=self.p, usuario=self.lider)
        self.cambiar(self.lider, mio, "lector")
        mio.refresh_from_db()
        self.assertEqual(mio.rol, "lider")

    def test_un_integrante_no_puede_cambiar_permisos(self):
        miembro = ProyectoMiembro.objects.get(proyecto=self.p, usuario=self.lector)
        self.assertEqual(self.cambiar(self.editor, miembro, "editor").status_code, 403)
        miembro.refresh_from_db()
        self.assertEqual(miembro.rol, "lector")

    def test_no_se_puede_cambiar_un_miembro_de_otro_proyecto(self):
        otro = Proyecto.objects.create(nombre="Otro", creado_por=self.lider, descripcion="Descripción de prueba")
        ProyectoMiembro.objects.create(proyecto=otro, usuario=self.lider, rol=ProyectoMiembro.Rol.LIDER)
        ajeno = ProyectoMiembro.objects.create(proyecto=otro, usuario=self.ajeno, rol=ProyectoMiembro.Rol.EDITOR)
        r = cliente_de(self.lider).post(reverse("miembro_cambiar_rol", args=[self.p.pk, ajeno.pk]), {"rol": "lector"})
        self.assertEqual(r.status_code, 404)

    def test_cambiar_rol_solo_admite_post(self):
        miembro = ProyectoMiembro.objects.get(proyecto=self.p, usuario=self.editor)
        self.assertEqual(cliente_de(self.lider).get(reverse("miembro_cambiar_rol", args=[self.p.pk, miembro.pk])).status_code, 405)

    def test_invitar_con_rol_lector_limita_lo_que_puede_hacer(self):
        cliente_de(self.lider).post(reverse("invitacion_crear", args=[self.p.pk]), {"email": "luis@prueba.com", "rol": "lector"})
        inv = InvitacionProyecto.objects.get(email="luis@prueba.com")
        nuevo = Usuario.objects.create_user("luis@prueba.com", CLAVE, perfil="estudiante", first_name="Prueba", last_name="Usuario")
        cliente_de(nuevo).get(reverse("invitacion_aceptar", args=[inv.token]))
        self.assertEqual(ProyectoMiembro.objects.get(proyecto=self.p, usuario=nuevo).rol, "lector")
        self.assertEqual(cliente_de(nuevo).post(reverse("tarea_crear", args=[self.p.pk]), {"titulo": "X", "estado": "por_hacer", "prioridad": "media"}).status_code, 403)
