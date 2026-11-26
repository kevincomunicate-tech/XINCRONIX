"""Integridad: las restricciones también bloquean actualizaciones, no solo inserciones."""

import datetime as dt

from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from comunicacion.models import Mensaje
from cuentas.models import Usuario
from dashboard.auditoria import problemas
from dashboard.models import Evento, Lienzo, Proyecto, ProyectoMiembro, Tarea

CLAVE = "Clave$egura2026"


class IntegridadExtraTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ana = Usuario.objects.create_user("ana@prueba.com", CLAVE, first_name="Ana", last_name="Ruiz", perfil="estudiante")
        cls.beto = Usuario.objects.create_user("beto@prueba.com", CLAVE, first_name="Beto", last_name="Luna", perfil="profesional")
        cls.p = Proyecto.objects.create(nombre="Base", descripcion="Descripción", creado_por=cls.ana, modalidad="grupal")
        ProyectoMiembro.objects.create(proyecto=cls.p, usuario=cls.ana, rol="lider")
        ProyectoMiembro.objects.create(proyecto=cls.p, usuario=cls.beto, rol="editor")

    def rechaza(self, operacion):
        with self.assertRaises(IntegrityError), transaction.atomic():
            operacion()

    def test_actualizar_el_nombre_a_vacio_se_bloquea(self):
        self.rechaza(lambda: Proyecto.objects.filter(pk=self.p.pk).update(nombre=""))

    def test_actualizar_el_contenido_de_un_mensaje_a_vacio_se_bloquea(self):
        m = Mensaje.objects.create(contenido="Hola", remitente=self.ana, destinatario=self.beto)
        self.rechaza(lambda: Mensaje.objects.filter(pk=m.pk).update(contenido=""))

    def test_un_mensaje_no_puede_quedar_dirigido_a_quien_lo_envia(self):
        m = Mensaje.objects.create(contenido="Hola", remitente=self.ana, destinatario=self.beto)
        self.rechaza(lambda: Mensaje.objects.filter(pk=m.pk).update(destinatario=self.ana))

    def test_un_evento_no_puede_quedar_terminando_antes_de_empezar(self):
        ahora = timezone.now()
        e = Evento.objects.create(proyecto=self.p, titulo="Ok", inicia_en=ahora, termina_en=ahora + dt.timedelta(hours=1), creado_por=self.ana)
        self.rechaza(lambda: Evento.objects.filter(pk=e.pk).update(termina_en=ahora - dt.timedelta(hours=2)))

    def test_solo_puede_haber_un_lienzo_por_proyecto(self):
        Lienzo.objects.create(proyecto=self.p, nombre="Primero")
        self.rechaza(lambda: Lienzo.objects.create(proyecto=self.p, nombre="Segundo"))

    def test_borrar_un_proyecto_no_deja_tareas_huerfanas(self):
        otro = Proyecto.objects.create(nombre="Temporal", descripcion="d", creado_por=self.ana)
        ProyectoMiembro.objects.create(proyecto=otro, usuario=self.ana, rol="lider")
        Tarea.objects.create(titulo="Huérfana?", proyecto=otro, creado_por=self.ana)
        otro.delete()
        self.assertEqual(problemas(), [])

    def test_un_flujo_completo_no_deja_problemas_en_la_auditoria(self):
        Tarea.objects.create(titulo="Asignada", proyecto=self.p, asignado_a=self.beto, creado_por=self.ana)
        Mensaje.objects.create(contenido="Listo", remitente=self.ana, destinatario=self.beto)
        self.assertEqual(problemas(), [])
