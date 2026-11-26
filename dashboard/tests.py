import json

from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from cuentas.models import Usuario

from .models import InvitacionProyecto, Proyecto, ProyectoMiembro, Tarea


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class ProyectoFlujoTests(TestCase):
    def setUp(self):
        self.autor = Usuario.objects.create_user("autor@example.com", "ClaveSegura123", first_name="Ana", last_name="Usuario")
        self.profesor = Usuario.objects.create_user("profe@example.com", "ClaveSegura123", perfil=Usuario.Perfil.PROFESOR, first_name="Prueba", last_name="Usuario")
        self.colaborador = Usuario.objects.create_user("colab@example.com", "ClaveSegura123", first_name="Prueba", last_name="Usuario")
        self.client.force_login(self.autor)

    def test_crear_proyecto_desde_orientacion(self):
        self.client.post(reverse("proyecto_orientacion"), {"finalidad": "educativo", "metodologia": "scrum", "modalidad": "grupal", "supervisor_email": self.profesor.email})
        respuesta = self.client.post(reverse("proyecto_crear"), {"nombre": "API escolar", "descripcion": "Proyecto de prueba", "estado": "planificacion"})
        proyecto = Proyecto.objects.get(nombre="API escolar")
        self.assertRedirects(respuesta, reverse("proyecto_detalle", args=[proyecto.pk]))
        self.assertEqual((proyecto.finalidad, proyecto.metodologia, proyecto.modalidad, proyecto.supervisor), ("educativo", "scrum", "grupal", self.profesor))
        self.assertTrue(ProyectoMiembro.objects.filter(proyecto=proyecto, usuario=self.autor, rol="lider").exists())

    def test_invitacion_y_aceptacion_por_mismo_correo(self):
        proyecto = Proyecto.objects.create(nombre="Motor", creado_por=self.autor, modalidad="grupal", descripcion="Descripción de prueba")
        ProyectoMiembro.objects.create(proyecto=proyecto, usuario=self.autor, rol="lider")
        respuesta = self.client.post(reverse("invitacion_crear", args=[proyecto.pk]), {"email": self.colaborador.email, "rol": "editor"})
        invitacion = InvitacionProyecto.objects.get(proyecto=proyecto)
        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.client.force_login(self.colaborador)
        self.client.get(reverse("invitacion_aceptar", args=[invitacion.token]))
        self.assertTrue(ProyectoMiembro.objects.filter(proyecto=proyecto, usuario=self.colaborador).exists())

    def test_mover_tarea_actualiza_el_tablero(self):
        proyecto = Proyecto.objects.create(nombre="Motor", creado_por=self.autor, descripcion="Descripción de prueba")
        tarea = Tarea.objects.create(proyecto=proyecto, titulo="Implementar", creado_por=self.autor)
        respuesta = self.client.post(reverse("tarea_mover", args=[proyecto.pk, tarea.pk]), data=json.dumps({"estado": "hecha"}), content_type="application/json")
        tarea.refresh_from_db()
        self.assertEqual((respuesta.status_code, tarea.estado), (200, "hecha"))

    def test_tablero_ofrece_control_de_estado_y_token_csrf(self):
        proyecto = Proyecto.objects.create(nombre="App", creado_por=self.autor, descripcion="Descripción de prueba")
        Tarea.objects.create(proyecto=proyecto, titulo="Diseñar", creado_por=self.autor)
        respuesta = self.client.get(reverse("proyecto_tablero", args=[proyecto.pk]))
        self.assertContains(respuesta, 'class="form-select form-select-sm task-status-select"')
        self.assertContains(respuesta, "Cambiar estado")
        self.assertIn("csrftoken", respuesta.cookies)

    def test_canvas_da_altura_y_token_para_guardar(self):
        proyecto = Proyecto.objects.create(nombre="App", creado_por=self.autor, descripcion="Descripción de prueba")
        respuesta = self.client.get(reverse("proyecto_canvas", args=[proyecto.pk]))
        self.assertContains(respuesta, 'class="canvas-editor"')
        self.assertIn("csrftoken", respuesta.cookies)
