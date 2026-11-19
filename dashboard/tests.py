from datetime import timedelta
from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from cuentas.models import Usuario

from .models import Actividad, MiembroProyecto, Proyecto, Tarea


class ModelosTests(TestCase):
    def setUp(self):
        self.ana = Usuario.objects.create_user("ana@empresa.com", "Clave$egura2026", first_name="Ana")
        self.luis = Usuario.objects.create_user("luis@empresa.com", "Clave$egura2026")
        self.proyecto = Proyecto.objects.create(nombre="Web", propietario=self.ana)

    def test_completada_en_se_llena_y_se_limpia(self):
        t = Tarea.objects.create(proyecto=self.proyecto, titulo="Login")
        self.assertIsNone(t.completada_en)
        t.estado = Tarea.Estado.COMPLETADA
        t.save()
        self.assertIsNotNone(t.completada_en)
        t.estado = Tarea.Estado.EN_PROGRESO
        t.save()
        self.assertIsNone(t.completada_en)

    def test_progreso(self):
        self.assertEqual(self.proyecto.progreso, 0)  # sin tareas no divide por cero
        Tarea.objects.create(proyecto=self.proyecto, titulo="A", estado=Tarea.Estado.COMPLETADA)
        Tarea.objects.create(proyecto=self.proyecto, titulo="B")
        Tarea.objects.create(proyecto=self.proyecto, titulo="C")
        self.assertEqual(self.proyecto.progreso, 33)
        anotado = Proyecto.objects.con_progreso().get(pk=self.proyecto.pk)
        self.assertEqual((anotado.total_tareas, anotado.tareas_completadas, anotado.progreso), (3, 1, 33))

    def test_visibles_para_dueno_y_miembro_sin_duplicados(self):
        MiembroProyecto.objects.create(proyecto=self.proyecto, usuario=self.ana)  # dueña y miembro
        Proyecto.objects.create(nombre="Ajeno", propietario=self.luis)
        self.assertEqual(list(Proyecto.objects.visibles_para(self.ana)), [self.proyecto])
        self.assertEqual(Proyecto.objects.visibles_para(self.luis).count(), 1)
        MiembroProyecto.objects.create(proyecto=self.proyecto, usuario=self.luis)
        self.assertEqual(Proyecto.objects.visibles_para(self.luis).count(), 2)

    def test_conteo_de_tareas_no_se_infla_con_miembros(self):
        for u in (self.ana, self.luis):
            MiembroProyecto.objects.create(proyecto=self.proyecto, usuario=u)
        Tarea.objects.create(proyecto=self.proyecto, titulo="A")
        p = Proyecto.objects.visibles_para(self.ana).con_progreso().get()
        self.assertEqual(p.total_tareas, 1)

    def test_miembro_unico(self):
        MiembroProyecto.objects.create(proyecto=self.proyecto, usuario=self.luis)
        with self.assertRaises(IntegrityError):
            MiembroProyecto.objects.create(proyecto=self.proyecto, usuario=self.luis)

    def test_fecha_fin_no_antes_de_inicio(self):
        hoy = timezone.localdate()
        with self.assertRaises(IntegrityError):
            Proyecto.objects.create(nombre="Mal", propietario=self.ana, fecha_inicio=hoy, fecha_fin=hoy - timedelta(days=1))

    def test_actividad_conserva_detalle_si_se_borra_la_tarea(self):
        t = Tarea.objects.create(proyecto=self.proyecto, titulo="Diseñar login")
        a = Actividad.registrar(self.ana, Actividad.Accion.TAREA_COMPLETADA, self.proyecto, t)
        t.delete()
        a.refresh_from_db()
        self.assertIsNone(a.tarea)
        self.assertEqual(str(a), "Ana completó la tarea Diseñar login")

    def test_vencida(self):
        ayer = timezone.localdate() - timedelta(days=1)
        t = Tarea(proyecto=self.proyecto, titulo="X", fecha_vencimiento=ayer)
        self.assertTrue(t.vencida)
        t.estado = Tarea.Estado.COMPLETADA
        self.assertFalse(t.vencida)


class PanelTests(TestCase):
    def setUp(self):
        self.ana = Usuario.objects.create_user("ana@empresa.com", "Clave$egura2026", first_name="Ana")
        self.client.force_login(self.ana)

    def test_requiere_sesion(self):
        self.client.logout()
        r = self.client.get(reverse("panel"))
        self.assertRedirects(r, f"{reverse('login')}?next={reverse('panel')}")

    def test_panel_vacio(self):
        r = self.client.get(reverse("panel"))
        self.assertContains(r, "Todavía no hay actividad")
        self.assertContains(r, "No tienes proyectos activos.")
        self.assertEqual(r.context["estadisticas"]["proyectos_activos"], 0)

    def test_estadisticas_y_datos_reales(self):
        ayer = timezone.localdate() - timedelta(days=1)
        p = Proyecto.objects.create(nombre="Web", propietario=self.ana)
        Proyecto.objects.create(nombre="Viejo", propietario=self.ana, estado=Proyecto.Estado.ARCHIVADO)
        hecha = Tarea.objects.create(proyecto=p, titulo="Hecha", estado=Tarea.Estado.COMPLETADA)
        Tarea.objects.create(proyecto=p, titulo="Atrasada", asignada_a=self.ana, fecha_vencimiento=ayer)
        Tarea.objects.create(proyecto=p, titulo="De otro")  # sin asignar
        Actividad.registrar(self.ana, Actividad.Accion.TAREA_COMPLETADA, p, hecha)

        r = self.client.get(reverse("panel"))
        e = r.context["estadisticas"]
        self.assertEqual(e["proyectos_activos"], 1)
        self.assertEqual(e["proyectos_este_mes"], 2)
        self.assertEqual(e["tareas_completadas"], 1)
        self.assertEqual(e["completadas_semana"], 1)
        self.assertEqual(e["mis_pendientes"], 1)
        self.assertEqual(e["mis_vencidas"], 1)
        self.assertEqual([x.progreso for x in r.context["progreso"]], [33])
        self.assertContains(r, "completó la tarea")
        self.assertContains(r, "Atrasada")

    def test_no_ve_datos_de_otros(self):
        luis = Usuario.objects.create_user("luis@empresa.com", "Clave$egura2026")
        p = Proyecto.objects.create(nombre="Secreto de Luis", propietario=luis)
        t = Tarea.objects.create(proyecto=p, titulo="Tarea privada", estado=Tarea.Estado.COMPLETADA)
        Actividad.registrar(luis, Actividad.Accion.TAREA_COMPLETADA, p, t)

        r = self.client.get(reverse("panel"))
        self.assertNotContains(r, "Secreto de Luis")
        self.assertNotContains(r, "Tarea privada")
        self.assertEqual(r.context["estadisticas"]["tareas_completadas"], 0)

        # Al agregarla como miembro, ya lo ve
        MiembroProyecto.objects.create(proyecto=p, usuario=self.ana)
        self.assertContains(self.client.get(reverse("panel")), "Secreto de Luis")


class AdminTests(TestCase):
    def setUp(self):
        self.admin = Usuario.objects.create_superuser("admin@empresa.com", "Clave$egura2026")
        self.client.force_login(self.admin)
        self.proyecto = Proyecto.objects.create(nombre="Web", propietario=self.admin)

    def _datos_tarea(self, **extra):
        return {"proyecto": self.proyecto.pk, "titulo": "Login", "estado": "por_hacer", "prioridad": 2, **extra}

    def test_crear_y_completar_tarea_registra_actividad(self):
        self.client.post(reverse("admin:dashboard_tarea_add"), self._datos_tarea())
        tarea = Tarea.objects.get()
        self.assertEqual(tarea.creada_por, self.admin)

        url = reverse("admin:dashboard_tarea_change", args=[tarea.pk])
        self.client.post(url, self._datos_tarea(estado="completada"))
        acciones = list(Actividad.objects.order_by("fecha", "pk").values_list("accion", flat=True))
        self.assertEqual(acciones, [Actividad.Accion.TAREA_CREADA, Actividad.Accion.TAREA_COMPLETADA])

        # Guardar sin cambiar el estado no agrega actividad
        self.client.post(url, self._datos_tarea(estado="completada", titulo="Login v2"))
        self.assertEqual(Actividad.objects.count(), 2)

    def test_listados_cargan(self):
        for nombre in ("proyecto", "tarea", "actividad"):
            self.assertEqual(self.client.get(reverse(f"admin:dashboard_{nombre}_changelist")).status_code, 200)


class CargarDemoTests(TestCase):
    def test_crea_datos_sin_duplicar(self):
        ana = Usuario.objects.create_user("ana@empresa.com", "Clave$egura2026")
        call_command("cargar_demo", "ANA@empresa.com", stdout=StringIO())
        self.assertEqual(Proyecto.objects.filter(propietario=ana).count(), 3)
        tareas = Tarea.objects.count()
        self.assertGreater(Actividad.objects.count(), 0)

        call_command("cargar_demo", "ana@empresa.com", stdout=StringIO())
        self.assertEqual(Proyecto.objects.count(), 3)
        self.assertEqual(Tarea.objects.count(), tareas)

    def test_usuario_inexistente(self):
        with self.assertRaises(CommandError):
            call_command("cargar_demo", "nadie@empresa.com", stdout=StringIO())
