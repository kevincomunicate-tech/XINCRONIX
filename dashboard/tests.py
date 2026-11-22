from datetime import date, timedelta

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from cuentas.models import Empresa, Equipo, MiembroEquipo, Rol, Usuario

from .models import Idea, Lienzo, LienzoColaborador, Proyecto, ProyectoMiembro, Tarea, VotoIdea


def crear_usuario(email, empresa, rol=Rol.USUARIO):
    return Usuario.objects.create_user(email, "Clave$egura2026", empresa=empresa, rol=Rol.objects.get(codigo=rol))


class Base(TestCase):
    """Dos empresas. En Acme: una admin, un supervisor y cuatro usuarios normales."""

    def setUp(self):
        self.acme = Empresa.objects.create(nombre="Acme")
        self.otra = Empresa.objects.create(nombre="Otra")
        self.admin = crear_usuario("admin@acme.com", self.acme, Rol.ADMIN)
        self.supervisor = crear_usuario("super@acme.com", self.acme, Rol.SUPERVISOR)
        self.ana = crear_usuario("ana@acme.com", self.acme)      # crea el proyecto
        self.beto = crear_usuario("beto@acme.com", self.acme)    # miembro directo
        self.caro = crear_usuario("caro@acme.com", self.acme)    # miembro del equipo
        self.dani = crear_usuario("dani@acme.com", self.acme)    # sin relación
        self.externo = crear_usuario("x@otra.com", self.otra, Rol.ADMIN)

        self.equipo = Equipo.objects.create(nombre="Backend", empresa=self.acme)
        MiembroEquipo.objects.create(equipo=self.equipo, usuario=self.caro)

        self.proyecto = Proyecto.objects.create(nombre="API", empresa=self.acme, equipo=self.equipo, creado_por=self.ana)
        ProyectoMiembro.objects.create(proyecto=self.proyecto, usuario=self.beto)


class ProyectoEnEquipoTests(Base):
    def test_quien_ve_el_proyecto(self):
        ve = lambda u: Proyecto.objects.visibles_para(u).filter(pk=self.proyecto.pk).exists()
        self.assertTrue(ve(self.ana))         # lo creó
        self.assertTrue(ve(self.beto))        # miembro directo
        self.assertTrue(ve(self.caro))        # miembro del equipo asignado
        self.assertTrue(ve(self.admin))       # gestiona la empresa
        self.assertTrue(ve(self.supervisor))  # ve todo para hacer seguimiento
        self.assertFalse(ve(self.dani))       # misma empresa, sin relación
        self.assertFalse(ve(self.externo))    # otra empresa: nunca

    def test_no_se_repite_si_hay_varias_relaciones(self):
        MiembroEquipo.objects.create(equipo=self.equipo, usuario=self.beto)  # beto: directo y por equipo
        self.assertEqual(Proyecto.objects.visibles_para(self.beto).count(), 1)

    def test_quien_edita(self):
        self.assertTrue(self.proyecto.puede_editar(self.beto))
        self.assertTrue(self.proyecto.puede_editar(self.caro))
        self.assertTrue(self.proyecto.puede_editar(self.admin))
        self.assertFalse(self.proyecto.puede_editar(self.supervisor))  # ve, pero no edita
        self.assertFalse(self.proyecto.puede_editar(self.externo))
        ProyectoMiembro.objects.filter(usuario=self.beto).update(rol=ProyectoMiembro.RolProyecto.OBSERVADOR)
        self.assertFalse(self.proyecto.puede_editar(self.beto))  # observador: solo lectura

    def test_progreso_se_calcula(self):
        self.assertEqual(self.proyecto.progreso, 0)
        Tarea.objects.create(titulo="Uno", proyecto=self.proyecto, estado=Tarea.Estado.COMPLETADA)
        Tarea.objects.create(titulo="Dos", proyecto=self.proyecto)
        self.assertEqual(self.proyecto.progreso, 50)

    def test_equipo_de_otra_empresa(self):
        ajeno = Equipo.objects.create(nombre="Ajeno", empresa=self.otra)
        self.proyecto.equipo = ajeno
        with self.assertRaises(ValidationError):
            self.proyecto.full_clean()

    def test_fechas_invalidas_las_rechaza_la_base_de_datos(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Proyecto.objects.create(nombre="Mal", empresa=self.acme,
                                    fecha_inicio=date(2026, 5, 10), fecha_fin=date(2026, 5, 1))


class LienzoEnEquipoTests(Base):
    def setUp(self):
        super().setUp()
        self.lienzo = Lienzo.objects.create(nombre="Diseño", empresa=self.acme, creado_por=self.ana)

    def visible(self, u):
        return Lienzo.objects.visibles_para(u).filter(pk=self.lienzo.pk).exists()

    def test_privado_solo_creador_y_gestores(self):
        self.assertTrue(self.visible(self.ana))
        self.assertTrue(self.visible(self.admin))
        self.assertFalse(self.visible(self.beto))
        self.assertFalse(self.visible(self.externo))

    def test_colaborador_editor_y_lector(self):
        LienzoColaborador.objects.create(lienzo=self.lienzo, usuario=self.beto, permiso="editor")
        LienzoColaborador.objects.create(lienzo=self.lienzo, usuario=self.dani, permiso="lector")
        self.assertTrue(self.visible(self.beto) and self.lienzo.puede_editar(self.beto))
        self.assertTrue(self.visible(self.dani))
        self.assertFalse(self.lienzo.puede_editar(self.dani))  # lector

    def test_compartido_con_un_equipo(self):
        self.lienzo.equipo = self.equipo
        self.lienzo.save()
        self.assertTrue(self.visible(self.caro) and self.lienzo.puede_editar(self.caro))
        self.assertFalse(self.visible(self.dani))

    def test_lienzo_del_proyecto(self):
        self.lienzo.proyecto = self.proyecto
        self.lienzo.save()
        self.assertTrue(self.visible(self.beto) and self.lienzo.puede_editar(self.beto))  # miembro directo
        self.assertTrue(self.visible(self.caro) and self.lienzo.puede_editar(self.caro))  # por el equipo del proyecto
        self.assertFalse(self.visible(self.dani))

    def test_compartido_con_toda_la_empresa(self):
        self.lienzo.compartido_con_empresa = True
        self.lienzo.save()
        self.assertTrue(self.visible(self.dani))
        self.assertFalse(self.visible(self.externo))

    def test_guarda_el_dibujo_en_json(self):
        self.lienzo.contenido = {"objetos": [{"tipo": "nota", "texto": "Hola", "x": 10, "y": 20}]}
        self.lienzo.save()
        self.lienzo.refresh_from_db()
        self.assertEqual(self.lienzo.contenido["objetos"][0]["texto"], "Hola")


class TareaTests(Base):
    def test_fecha_completada_automatica(self):
        t = Tarea.objects.create(titulo="T", proyecto=self.proyecto)
        self.assertIsNone(t.fecha_completada)
        t.estado = Tarea.Estado.COMPLETADA
        t.save()
        self.assertIsNotNone(t.fecha_completada)
        t.estado = Tarea.Estado.EN_PROGRESO
        t.save()
        self.assertIsNone(t.fecha_completada)

    def test_vencida(self):
        ayer = date.today() - timedelta(days=2)
        self.assertTrue(Tarea(titulo="T", proyecto=self.proyecto, fecha_vencimiento=ayer).vencida)
        self.assertFalse(Tarea(titulo="T", proyecto=self.proyecto, fecha_vencimiento=ayer, estado="completada").vencida)

    def test_el_equipo_sale_del_proyecto(self):
        t = Tarea.objects.create(titulo="T", proyecto=self.proyecto)
        self.assertEqual(t.proyecto.equipo, self.equipo)  # no se guarda en la tarea (3FN)


class IdeaTests(Base):
    def test_un_voto_por_persona(self):
        idea = Idea.objects.create(titulo="Plantillas", empresa=self.acme, autor=self.ana)
        VotoIdea.objects.create(idea=idea, usuario=self.beto)
        with self.assertRaises(IntegrityError), transaction.atomic():
            VotoIdea.objects.create(idea=idea, usuario=self.beto)
        self.assertEqual(idea.votantes.count(), 1)

    def test_la_idea_sigue_si_se_borra_el_autor(self):
        idea = Idea.objects.create(titulo="Plantillas", empresa=self.acme, autor=self.dani)
        self.dani.delete()
        idea.refresh_from_db()
        self.assertIsNone(idea.autor)
        self.assertEqual(idea.empresa, self.acme)


class EquipoTests(Base):
    def test_miembro_de_otra_empresa(self):
        with self.assertRaises(ValidationError):
            MiembroEquipo(equipo=self.equipo, usuario=self.externo).full_clean()

    def test_miembro_repetido(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            MiembroEquipo.objects.create(equipo=self.equipo, usuario=self.caro)

    def test_cantidad_de_miembros_se_cuenta(self):
        MiembroEquipo.objects.create(equipo=self.equipo, usuario=self.beto)
        self.assertEqual(self.equipo.miembros.count(), 2)
