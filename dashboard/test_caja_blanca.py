"""Pruebas de caja blanca: lógica interna de proyectos, miembros e invitaciones."""

from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from cuentas.models import Usuario
from dashboard.models import InvitacionProyecto, Proyecto, ProyectoMiembro, Tarea

CLAVE = "Clave$egura2026"


class VisibilidadCajaBlancaTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.super = Usuario.objects.create_superuser("super@prueba.com", CLAVE, first_name="Prueba", last_name="Usuario")
        cls.lider = Usuario.objects.create_user("lider@prueba.com", CLAVE, first_name="Prueba", last_name="Usuario")
        cls.editor = Usuario.objects.create_user("editor@prueba.com", CLAVE, first_name="Prueba", last_name="Usuario")
        cls.lector = Usuario.objects.create_user("lector@prueba.com", CLAVE, first_name="Prueba", last_name="Usuario")
        cls.supervisor = Usuario.objects.create_user("prof@prueba.com", CLAVE, perfil="profesor", first_name="Prueba", last_name="Usuario")
        cls.ajeno = Usuario.objects.create_user("ajeno@prueba.com", CLAVE, first_name="Prueba", last_name="Usuario")
        cls.proyecto = Proyecto.objects.create(nombre="App", creado_por=cls.lider, supervisor=cls.supervisor,
                                               modalidad=Proyecto.Modalidad.GRUPAL, descripcion="Descripción de prueba")
        ProyectoMiembro.objects.create(proyecto=cls.proyecto, usuario=cls.lider, rol=ProyectoMiembro.Rol.LIDER)
        ProyectoMiembro.objects.create(proyecto=cls.proyecto, usuario=cls.editor, rol=ProyectoMiembro.Rol.EDITOR)
        ProyectoMiembro.objects.create(proyecto=cls.proyecto, usuario=cls.lector, rol=ProyectoMiembro.Rol.LECTOR)

    def test_visibles_para_anonimo_es_vacio(self):
        from django.contrib.auth.models import AnonymousUser
        self.assertFalse(Proyecto.objects.visibles_para(AnonymousUser()).exists())

    def test_superusuario_ve_todos(self):
        self.assertIn(self.proyecto, Proyecto.objects.visibles_para(self.super))

    def test_cada_relacion_ve_el_proyecto(self):
        for u in (self.lider, self.editor, self.lector, self.supervisor):
            with self.subTest(usuario=u.email):
                self.assertIn(self.proyecto, Proyecto.objects.visibles_para(u))

    def test_usuario_sin_relacion_no_lo_ve(self):
        self.assertNotIn(self.proyecto, Proyecto.objects.visibles_para(self.ajeno))

    def test_visibles_no_duplica_proyectos(self):
        # Un miembro que también es líder aparece una sola vez (por el join con miembros).
        self.assertEqual(Proyecto.objects.visibles_para(self.lider).filter(pk=self.proyecto.pk).count(), 1)


class RelacionYPermisosCajaBlancaTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.super = Usuario.objects.create_superuser("super@prueba.com", CLAVE, first_name="Prueba", last_name="Usuario")
        cls.lider = Usuario.objects.create_user("lider@prueba.com", CLAVE, first_name="Prueba", last_name="Usuario")
        cls.editor = Usuario.objects.create_user("editor@prueba.com", CLAVE, first_name="Prueba", last_name="Usuario")
        cls.lector = Usuario.objects.create_user("lector@prueba.com", CLAVE, first_name="Prueba", last_name="Usuario")
        cls.supervisor = Usuario.objects.create_user("prof@prueba.com", CLAVE, perfil="profesor", first_name="Prueba", last_name="Usuario")
        cls.ajeno = Usuario.objects.create_user("ajeno@prueba.com", CLAVE, first_name="Prueba", last_name="Usuario")
        cls.p = Proyecto.objects.create(nombre="App", creado_por=cls.lider, supervisor=cls.supervisor,
                                        modalidad=Proyecto.Modalidad.GRUPAL, descripcion="Descripción de prueba")
        ProyectoMiembro.objects.create(proyecto=cls.p, usuario=cls.editor, rol=ProyectoMiembro.Rol.EDITOR)
        ProyectoMiembro.objects.create(proyecto=cls.p, usuario=cls.lector, rol=ProyectoMiembro.Rol.LECTOR)

    def test_relacion_con(self):
        self.assertEqual(self.p.relacion_con(self.super), "administrador")
        self.assertEqual(self.p.relacion_con(self.lider), "lider")
        self.assertEqual(self.p.relacion_con(self.supervisor), "supervisor")
        self.assertEqual(self.p.relacion_con(self.editor), ProyectoMiembro.Rol.EDITOR)
        self.assertIsNone(self.p.relacion_con(self.ajeno))

    def test_permisos_del_lider(self):
        self.assertTrue({"ver", "editar", "eliminar", "miembros", "invitaciones", "tareas"} <= self.p.permisos(self.lider))

    def test_permisos_del_editor_no_incluyen_eliminar_ni_miembros(self):
        permisos = self.p.permisos(self.editor)
        self.assertIn("tareas", permisos)
        self.assertNotIn("eliminar", permisos)
        self.assertNotIn("miembros", permisos)
        self.assertNotIn("invitaciones", permisos)

    def test_permisos_del_lector_solo_ver(self):
        self.assertEqual(self.p.permisos(self.lector), {"ver"})

    def test_permisos_del_supervisor_solo_correcciones_y_ver(self):
        self.assertEqual(self.p.permisos(self.supervisor), {"ver", "correcciones"})

    def test_sin_relacion_no_hay_permisos(self):
        self.assertEqual(self.p.permisos(self.ajeno), set())

    def test_superusuario_tiene_todos_los_permisos_de_lider(self):
        self.assertEqual(self.p.permisos(self.super), self.p.permisos(self.lider))


class ValidacionModeloCajaBlancaTests(TestCase):
    def setUp(self):
        self.ana = Usuario.objects.create_user("ana@prueba.com", CLAVE, first_name="Prueba", last_name="Usuario")
        self.beto = Usuario.objects.create_user("beto@prueba.com", CLAVE, first_name="Prueba", last_name="Usuario")

    def test_proyecto_individual_no_admite_integrantes_extra(self):
        p = Proyecto.objects.create(nombre="Solo", creado_por=self.ana, modalidad=Proyecto.Modalidad.INDIVIDUAL, descripcion="Descripción de prueba")
        ProyectoMiembro.objects.create(proyecto=p, usuario=self.beto, rol=ProyectoMiembro.Rol.EDITOR)
        with self.assertRaises(ValidationError):
            p.clean()

    def test_proyecto_grupal_admite_integrantes(self):
        p = Proyecto.objects.create(nombre="Equipo", creado_por=self.ana, modalidad=Proyecto.Modalidad.GRUPAL, descripcion="Descripción de prueba")
        ProyectoMiembro.objects.create(proyecto=p, usuario=self.beto, rol=ProyectoMiembro.Rol.EDITOR)
        p.clean()  # no lanza

    def test_no_se_repite_un_miembro_en_el_mismo_proyecto(self):
        p = Proyecto.objects.create(nombre="Equipo", creado_por=self.ana, modalidad=Proyecto.Modalidad.GRUPAL, descripcion="Descripción de prueba")
        ProyectoMiembro.objects.create(proyecto=p, usuario=self.beto, rol=ProyectoMiembro.Rol.EDITOR)
        with self.assertRaises(IntegrityError), transaction.atomic():
            ProyectoMiembro.objects.create(proyecto=p, usuario=self.beto, rol=ProyectoMiembro.Rol.LECTOR)

    def test_progreso_cuenta_tareas_hechas(self):
        p = Proyecto.objects.create(nombre="Avance", creado_por=self.ana, descripcion="Descripción de prueba")
        self.assertEqual(p.progreso, 0)  # sin tareas no divide por cero
        Tarea.objects.create(titulo="A", proyecto=p, estado=Tarea.Estado.HECHA)
        Tarea.objects.create(titulo="B", proyecto=p, estado=Tarea.Estado.POR_HACER)
        self.assertEqual(p.progreso, 50)


class InvitacionCajaBlancaTests(TestCase):
    def setUp(self):
        self.ana = Usuario.objects.create_user("ana@prueba.com", CLAVE, first_name="Prueba", last_name="Usuario")
        self.p = Proyecto.objects.create(nombre="Equipo", creado_por=self.ana, modalidad=Proyecto.Modalidad.GRUPAL, descripcion="Descripción de prueba")

    def _invitacion(self, vence_en):
        return InvitacionProyecto.objects.create(proyecto=self.p, email="nuevo@prueba.com",
                                                 rol=ProyectoMiembro.Rol.EDITOR, creado_por=self.ana, vence_en=vence_en)

    def test_invitacion_vigente_no_esta_vencida(self):
        self.assertFalse(self._invitacion(timezone.now() + timedelta(days=7)).vencida)

    def test_invitacion_pasada_esta_vencida(self):
        self.assertTrue(self._invitacion(timezone.now() - timedelta(minutes=1)).vencida)

    def test_cada_invitacion_tiene_token_unico(self):
        a = self._invitacion(timezone.now() + timedelta(days=1))
        b = self._invitacion(timezone.now() + timedelta(days=1))
        self.assertNotEqual(a.token, b.token)
