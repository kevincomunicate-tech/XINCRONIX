"""Integridad de datos: campos obligatorios, relaciones entre tablas y auditoría.

La base rechaza textos vacíos y referencias imposibles; los modelos validan las reglas de negocio;
la auditoría (python manage.py auditar_datos) revisa todo lo guardado."""

from datetime import timedelta
from io import StringIO

from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from comunicacion.models import ConversacionIA, MensajeIA, Mensaje, Reunion, TicketSoporte
from cuentas.forms import RegistroForm
from cuentas.models import Usuario
from dashboard.auditoria import OBLIGATORIOS, problemas
from dashboard.forms import ProyectoForm
from dashboard.models import Correccion, DocumentoProyecto, Evento, InvitacionProyecto, Lienzo, Proyecto, ProyectoMiembro, Tarea

CLAVE = "Clave$egura2026"


def usuario(correo, nombre="Ana", apellido="Ruiz", perfil="estudiante"):
    return Usuario.objects.create_user(correo, CLAVE, first_name=nombre, last_name=apellido, perfil=perfil)


class CamposObligatoriosEnLaBaseTests(TestCase):
    """Un texto vacío no entra aunque se salte la web: lo rechaza la base de datos."""

    def setUp(self):
        self.ana = usuario("ana@prueba.com")
        self.p = Proyecto.objects.create(nombre="Base", descripcion="Descripción", creado_por=self.ana)

    def rechaza(self, crear):
        with self.assertRaises(IntegrityError), transaction.atomic():
            crear()

    def test_usuario_sin_nombres_o_apellidos(self):
        # El gestor lo rechaza con un mensaje claro...
        with self.assertRaises(ValueError):
            usuario("sin-nombre@prueba.com", nombre="")
        # ...y si alguien salta el gestor, la base también lo rechaza.
        self.rechaza(lambda: Usuario(email="crudo@prueba.com", first_name="", last_name="Ruiz").save())

    def test_proyecto_sin_nombre_o_descripcion(self):
        self.rechaza(lambda: Proyecto.objects.create(nombre="", descripcion="x", creado_por=self.ana))
        self.rechaza(lambda: Proyecto.objects.create(nombre="x", descripcion="", creado_por=self.ana))

    def test_tarea_evento_documento_lienzo_sin_nombre(self):
        self.rechaza(lambda: Tarea.objects.create(titulo="", proyecto=self.p, creado_por=self.ana))
        self.rechaza(lambda: Evento.objects.create(titulo="", proyecto=self.p, inicia_en=timezone.now(), creado_por=self.ana))
        self.rechaza(lambda: DocumentoProyecto.objects.create(nombre="", proyecto=self.p, archivo="a.pdf", subido_por=self.ana))
        Lienzo.objects.filter(proyecto=self.p).delete()
        self.rechaza(lambda: Lienzo.objects.create(proyecto=self.p, nombre=""))

    def test_correccion_sin_comentario(self):
        self.rechaza(lambda: Correccion.objects.create(proyecto=self.p, comentario="", autor=self.ana))

    def test_mensaje_sin_contenido_o_a_si_mismo(self):
        otro = usuario("otro@prueba.com")
        self.rechaza(lambda: Mensaje.objects.create(contenido="", remitente=self.ana, destinatario=otro))
        self.rechaza(lambda: Mensaje.objects.create(contenido="Hola", remitente=self.ana, destinatario=self.ana))

    def test_reunion_conversacion_ticket_sin_texto_obligatorio(self):
        self.rechaza(lambda: Reunion.objects.create(nombre="", fecha=timezone.now()))
        self.rechaza(lambda: ConversacionIA.objects.create(titulo="", usuario=self.ana))
        conv = ConversacionIA.objects.create(titulo="Charla", usuario=self.ana)
        self.rechaza(lambda: MensajeIA.objects.create(conversacion=conv, contenido="", rol="user"))
        self.rechaza(lambda: TicketSoporte.objects.create(asunto="", descripcion="x", creado_por=self.ana))
        self.rechaza(lambda: TicketSoporte.objects.create(asunto="x", descripcion="", creado_por=self.ana))

    def test_evento_que_termina_antes_de_empezar(self):
        ahora = timezone.now()
        self.rechaza(lambda: Evento.objects.create(titulo="Al revés", proyecto=self.p, inicia_en=ahora, termina_en=ahora - timedelta(hours=1), creado_por=self.ana))

    def test_proyecto_sin_creador(self):
        self.rechaza(lambda: Proyecto.objects.create(nombre="Huérfano", descripcion="x", creado_por=None))


class ReglasDeRelacionTests(TestCase):
    """Reglas entre tablas que las columnas no pueden expresar: se validan en el modelo."""

    def setUp(self):
        self.ana = usuario("ana@prueba.com")
        self.beto = usuario("beto@prueba.com", nombre="Beto")
        self.ajeno = usuario("ajeno@prueba.com", nombre="Ajeno")
        self.p = Proyecto.objects.create(nombre="Equipo", descripcion="Descripción", creado_por=self.ana, modalidad="grupal")
        ProyectoMiembro.objects.create(proyecto=self.p, usuario=self.ana, rol="lider")
        ProyectoMiembro.objects.create(proyecto=self.p, usuario=self.beto, rol="editor")

    def test_responsable_debe_ser_integrante(self):
        t = Tarea(titulo="Mía", proyecto=self.p, asignado_a=self.ajeno, creado_por=self.ana)
        with self.assertRaises(ValidationError):
            t.full_clean()
        t.asignado_a = self.beto
        t.full_clean()  # ahora sí

    def test_correccion_solo_sobre_tareas_de_su_proyecto(self):
        otro = Proyecto.objects.create(nombre="Otro", descripcion="Descripción", creado_por=self.ana)
        tarea_ajena = Tarea.objects.create(titulo="Ajena", proyecto=otro, creado_por=self.ana)
        c = Correccion(proyecto=self.p, tarea=tarea_ajena, comentario="Cruzada", autor=self.ana)
        with self.assertRaises(ValidationError):
            c.full_clean()

    def test_el_supervisor_debe_ser_profesor(self):
        p = Proyecto(nombre="Con supervisor", descripcion="x", creado_por=self.ana, supervisor=self.beto)
        with self.assertRaises(ValidationError):
            p.full_clean()

    def test_un_profesor_si_puede_ser_supervisor(self):
        prof = usuario("prof@prueba.com", nombre="Carla", perfil="profesor")
        Proyecto(nombre="Educativo", descripcion="x", creado_por=self.ana, supervisor=prof).full_clean()

    def test_individual_no_admite_integrantes(self):
        self.p.modalidad = "individual"
        with self.assertRaises(ValidationError):
            self.p.clean()

    def test_no_se_repite_la_misma_persona_en_el_proyecto(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            ProyectoMiembro.objects.create(proyecto=self.p, usuario=self.beto, rol="lector")


class FormulariosObligatoriosTests(TestCase):
    def test_proyecto_no_se_guarda_sin_descripcion(self):
        datos = {"nombre": "Sin desc", "descripcion": "", "estado": "planificacion"}
        self.assertFalse(ProyectoForm(datos).is_valid())
        self.assertIn("descripcion", ProyectoForm(datos).errors)

    def test_registro_pide_nombres_y_apellidos(self):
        base = {"email": "nuevo@prueba.com", "perfil": "estudiante", "password": CLAVE}
        self.assertFalse(RegistroForm({**base, "nombre": "Solo"}).is_valid())
        self.assertTrue(RegistroForm({**base, "nombre": "Ana Ruiz"}).is_valid())

    def test_createsuperuser_exige_nombre_y_apellido(self):
        self.assertEqual(Usuario.REQUIRED_FIELDS, ["first_name", "last_name"])
        with self.assertRaises(ValueError):
            Usuario.objects.create_superuser("root@prueba.com", CLAVE)


class HistorialTests(TestCase):
    """Si se borra una cuenta, su trabajo no desaparece: solo queda sin autor."""

    def test_borrar_una_cuenta_conserva_sus_tareas(self):
        dueno = usuario("dueno@prueba.com")
        autor = usuario("autor@prueba.com", nombre="Autor")
        p = Proyecto.objects.create(nombre="Trabajo", descripcion="Descripción", creado_por=dueno)
        ProyectoMiembro.objects.create(proyecto=p, usuario=dueno, rol="lider")
        ProyectoMiembro.objects.create(proyecto=p, usuario=autor, rol="editor")
        tarea = Tarea.objects.create(titulo="Quedará", proyecto=p, creado_por=autor)
        autor.delete()  # el proyecto es de otra persona: no se borra
        tarea.refresh_from_db()
        self.assertIsNone(tarea.creado_por)
        self.assertTrue(Tarea.objects.filter(pk=tarea.pk).exists())


class AuditoriaTests(TestCase):
    def setUp(self):
        self.ana = usuario("ana@prueba.com")
        self.beto = usuario("beto@prueba.com", nombre="Beto")
        self.p = Proyecto.objects.create(nombre="Equipo", descripcion="Descripción", creado_por=self.ana, modalidad="grupal")
        ProyectoMiembro.objects.create(proyecto=self.p, usuario=self.ana, rol="lider")
        ProyectoMiembro.objects.create(proyecto=self.p, usuario=self.beto, rol="editor")

    def test_datos_correctos_no_tienen_problemas(self):
        Tarea.objects.create(titulo="Bien", proyecto=self.p, asignado_a=self.beto, creado_por=self.ana)
        self.assertEqual(problemas(), [])

    def test_detecta_responsable_que_no_es_integrante(self):
        ajeno = usuario("ajeno@prueba.com", nombre="Ajeno")
        Tarea.objects.create(titulo="Mal asignada", proyecto=self.p, asignado_a=ajeno, creado_por=self.ana)
        self.assertTrue(any("no es integrante" in linea for linea in problemas()))

    def test_detecta_correccion_de_otro_proyecto(self):
        otro = Proyecto.objects.create(nombre="Otro", descripcion="x", creado_por=self.ana)
        tarea = Tarea.objects.create(titulo="De otro", proyecto=otro, creado_por=self.ana)
        Correccion.objects.create(proyecto=self.p, tarea=tarea, comentario="Cruzada", autor=self.ana)
        self.assertTrue(any("otro proyecto" in linea for linea in problemas()))

    def test_detecta_proyecto_sin_lider(self):
        Proyecto.objects.create(nombre="Sin líder", descripcion="x", creado_por=self.beto)
        self.assertTrue(any("no aparece como líder" in linea for linea in problemas()))

    def test_detecta_invitacion_aceptada_sin_membresia(self):
        InvitacionProyecto.objects.create(proyecto=self.p, email="fantasma@prueba.com", rol="editor", estado="aceptada",
                                          creado_por=self.ana, vence_en=timezone.now() + timedelta(days=3))
        self.assertTrue(any("aceptada, pero" in linea for linea in problemas()))

    def test_detecta_supervisor_que_no_es_profesor(self):
        Proyecto.objects.filter(pk=self.p.pk).update(supervisor=self.beto)
        self.assertTrue(any("supervisor no tiene perfil" in linea for linea in problemas()))

    def test_comando_termina_bien_sin_problemas(self):
        salida = StringIO()
        call_command("auditar_datos", stdout=salida)
        self.assertIn("ningún problema", salida.getvalue())

    def test_comando_falla_si_hay_problemas(self):
        Tarea.objects.create(titulo="Mal", proyecto=self.p, asignado_a=usuario("x@prueba.com", nombre="X"), creado_por=self.ana)
        with self.assertRaises(CommandError):
            call_command("auditar_datos", stdout=StringIO())

    def test_todas_las_tablas_obligatorias_estan_cubiertas(self):
        for modelo, campos in OBLIGATORIOS.items():
            for campo in campos:
                with self.subTest(modelo=modelo.__name__, campo=campo):
                    modelo._meta.get_field(campo)  # existe en el modelo
