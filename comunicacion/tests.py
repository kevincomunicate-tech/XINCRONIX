from django.db import IntegrityError, transaction
from django.test import TestCase

from cuentas.models import Empresa, Equipo, Usuario

from .models import Mensaje


class MensajeTests(TestCase):
    def setUp(self):
        empresa = Empresa.objects.create(nombre="Acme")
        self.ana = Usuario.objects.create_user("ana@acme.com", "Clave$egura2026", empresa=empresa)
        self.beto = Usuario.objects.create_user("beto@acme.com", "Clave$egura2026", empresa=empresa)
        self.equipo = Equipo.objects.create(nombre="Backend", empresa=empresa)

    def test_mensaje_directo_o_de_equipo(self):
        Mensaje.objects.create(contenido="Hola", remitente=self.ana, destinatario=self.beto)
        Mensaje.objects.create(contenido="Hola equipo", remitente=self.ana, equipo=self.equipo)
        self.assertEqual(Mensaje.objects.count(), 2)

    def test_sin_destino_lo_rechaza_la_base_de_datos(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Mensaje.objects.create(contenido="¿A quién?", remitente=self.ana)

    def test_con_ambos_destinos_lo_rechaza(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Mensaje.objects.create(contenido="Doble", remitente=self.ana, destinatario=self.beto, equipo=self.equipo)
