"""Pruebas del comando cargar_demo (caja negra: se ejecuta como lo haría el equipo)."""

from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from cuentas.models import Usuario
from dashboard.models import Proyecto, Tarea

CLAVE = "Clave$egura2026"


class CargarDemoTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user("demo@prueba.com", CLAVE, perfil="estudiante", first_name="Prueba", last_name="Usuario")

    def test_crea_proyectos_y_tareas_del_usuario(self):
        call_command("cargar_demo", "demo@prueba.com", stdout=StringIO())
        self.assertEqual(Proyecto.objects.filter(creado_por=self.usuario).count(), 3)
        self.assertGreater(Tarea.objects.filter(proyecto__creado_por=self.usuario).count(), 0)

    def test_no_duplica_si_se_ejecuta_dos_veces(self):
        call_command("cargar_demo", "demo@prueba.com", stdout=StringIO())
        call_command("cargar_demo", "demo@prueba.com", stdout=StringIO())
        self.assertEqual(Proyecto.objects.filter(creado_por=self.usuario).count(), 3)

    def test_correo_inexistente_da_error_claro(self):
        with self.assertRaisesMessage(CommandError, "No existe un usuario"):
            call_command("cargar_demo", "nadie@prueba.com", stdout=StringIO())

    def test_el_usuario_queda_como_lider_de_cada_proyecto(self):
        call_command("cargar_demo", "demo@prueba.com", stdout=StringIO())
        for p in Proyecto.objects.filter(creado_por=self.usuario):
            self.assertEqual(p.relacion_con(self.usuario), "lider")
