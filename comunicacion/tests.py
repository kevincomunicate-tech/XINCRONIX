from django.db import IntegrityError
from django.test import TestCase

from cuentas.models import Usuario
from dashboard.models import Proyecto

from .models import Mensaje, Reunion, TicketSoporte


class ComunicacionTests(TestCase):
    def setUp(self):
        self.ana = Usuario.objects.create_user("ana@ejemplo.com", "Clave$egura2026", first_name="Prueba", last_name="Usuario")
        self.beto = Usuario.objects.create_user("beto@ejemplo.com", "Clave$egura2026", first_name="Prueba", last_name="Usuario")

    def test_mensaje_directo_entre_dos_personas(self):
        m = Mensaje.objects.create(contenido="Hola Beto", remitente=self.ana, destinatario=self.beto)
        self.assertFalse(m.leido)
        self.assertEqual(str(m), "Hola Beto")

    def test_mensaje_sin_destinatario_no_se_guarda(self):
        with self.assertRaises(IntegrityError):
            Mensaje.objects.create(contenido="Sin destino", remitente=self.ana, destinatario=None)

    def test_reunion_pertenece_a_un_proyecto(self):
        proyecto = Proyecto.objects.create(nombre="Web", creado_por=self.ana, descripcion="Descripción de prueba")
        r = Reunion.objects.create(nombre="Revisión", fecha="2026-12-01T10:00:00Z", proyecto=proyecto, organizador=self.ana)
        self.assertEqual(proyecto.reuniones.get(), r)

    def test_ticket_queda_a_nombre_de_quien_lo_crea(self):
        t = TicketSoporte.objects.create(asunto="No carga el tablero", creado_por=self.ana, descripcion="Descripción de prueba")
        self.assertEqual(t.estado, TicketSoporte.Estado.ABIERTO)
        self.assertEqual(self.ana.tickets.get(), t)
