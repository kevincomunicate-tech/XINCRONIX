from datetime import timedelta
from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from cuentas.models import Empresa, Rol, Usuario

from .models import Actividad, Equipo, MiembroEquipo, MiembroProyecto, Proyecto, Tarea


def crear_usuario(email, empresa, rol=Rol.COLABORADOR, **extra):
    return Usuario.objects.create_user(email, "Clave$egura2026", empresa=empresa, rol=rol, **extra)


class ModelosTests(TestCase):
    def setUp(self):
        self.empresa = Empresa.objects.create(nombre="Acme", email="info@acme.com")
        self.ana = crear_usuario("ana@acme.com", self.empresa, Rol.ADMIN, nombres="Ana")
        self.proyecto = Proyecto.objects.create(nombre="Web", empresa=self.empresa, creador=self.ana)

    def test_tablas_y_columnas_del_esquema(self):
        esperado = {
            Equipo: ("equipos", "id_equipo"),
            MiembroEquipo: ("miembros_equipo", "id"),
            Proyecto: ("proyecto", "id_proyecto"),
            MiembroProyecto: ("proyecto_miembros", "id"),
            Tarea: ("tareas", "id_tarea"),
            Actividad: ("actividad", "id_actividad"),
        }
        for modelo, (tabla, pk) in esperado.items():
            self.assertEqual(modelo._meta.db_table, tabla)
            self.assertEqual(modelo._meta.pk.column, pk)
        self.assertEqual(Tarea._meta.get_field("asignada_a").column, "id_usuario")
        self.assertEqual(Tarea._meta.get_field("creador").column, "id_creador")

    def test_fecha_completada_se_llena_y_se_limpia(self):
        t = Tarea.objects.create(proyecto=self.proyecto, titulo="Login")
        self.assertIsNone(t.fecha_completada)
        t.estado = Tarea.Estado.COMPLETADA
        t.save()
        self.assertIsNotNone(t.fecha_completada)
        t.estado = Tarea.Estado.EN_PROGRESO
        t.save()
        self.assertIsNone(t.fecha_completada)

    def test_progreso(self):
        self.assertEqual(self.proyecto.progreso, 0)  # sin tareas no divide por cero
        Tarea.objects.create(proyecto=self.proyecto, titulo="A", estado=Tarea.Estado.COMPLETADA)
        Tarea.objects.create(proyecto=self.proyecto, titulo="B")
        Tarea.objects.create(proyecto=self.proyecto, titulo="C")
        self.assertEqual(self.proyecto.progreso, 33)
        anotado = Proyecto.objects.con_progreso().get(pk=self.proyecto.pk)
        self.assertEqual((anotado.total_tareas, anotado.tareas_completadas, anotado.progreso), (3, 1, 33))

    def test_conteo_de_tareas_no_se_infla_con_miembros(self):
        luis = crear_usuario("luis@acme.com", self.empresa)
        for u in (self.ana, luis):
            MiembroProyecto.objects.create(proyecto=self.proyecto, usuario=u)
        Tarea.objects.create(proyecto=self.proyecto, titulo="A")
        p = Proyecto.objects.visibles_para(luis).con_progreso().get()
        self.assertEqual(p.total_tareas, 1)

    def test_restricciones_unicas(self):
        luis = crear_usuario("luis@acme.com", self.empresa)
        MiembroProyecto.objects.create(proyecto=self.proyecto, usuario=luis)
        with self.assertRaises(IntegrityError):
            MiembroProyecto.objects.create(proyecto=self.proyecto, usuario=luis)

    def test_equipo_unico_por_empresa(self):
        Equipo.objects.create(nombre="Diseño", empresa=self.empresa)
        otra = Empresa.objects.create(nombre="Otra", email="o@o.com")
        Equipo.objects.create(nombre="Diseño", empresa=otra)  # en otra empresa sí se puede
        with self.assertRaises(IntegrityError):
            Equipo.objects.create(nombre="Diseño", empresa=self.empresa)

    def test_fecha_fin_no_antes_de_inicio(self):
        hoy = timezone.localdate()
        with self.assertRaises(IntegrityError):
            Proyecto.objects.create(
                nombre="Mal", empresa=self.empresa, fecha_inicio=hoy, fecha_fin=hoy - timedelta(days=1)
            )

    def test_importancia_entre_1_y_4(self):
        with self.assertRaises(IntegrityError):
            Proyecto.objects.create(nombre="Mal", empresa=self.empresa, nivel_importancia=5)

    def test_actividad_conserva_texto_si_se_borra_la_tarea(self):
        t = Tarea.objects.create(proyecto=self.proyecto, titulo="Diseñar login", estado=Tarea.Estado.COMPLETADA)
        a = Actividad.registrar_tarea(self.ana, t)
        t.delete()
        a.refresh_from_db()
        self.assertEqual(a.empresa, self.empresa)
        self.assertEqual(a.tipo, Actividad.Tipo.TAREA)
        self.assertEqual(str(a), "Ana completó la tarea Diseñar login")

    def test_texto_de_actividad(self):
        t = Tarea.objects.create(proyecto=self.proyecto, titulo="Login", estado=Tarea.Estado.EN_REVISION)
        self.assertEqual(Actividad.registrar_tarea(self.ana, t, creada=True).descripcion, "creó la tarea Login")
        self.assertEqual(Actividad.registrar_tarea(self.ana, t).descripcion, "movió la tarea Login a En revisión")

    def test_vencida(self):
        ayer = timezone.localdate() - timedelta(days=1)
        t = Tarea(proyecto=self.proyecto, titulo="X", fecha_vencimiento=ayer)
        self.assertTrue(t.vencida)
        t.estado = Tarea.Estado.COMPLETADA
        self.assertFalse(t.vencida)


class VisibilidadTests(TestCase):
    """Quién ve qué proyectos, según empresa y rol."""

    def setUp(self):
        self.acme = Empresa.objects.create(nombre="Acme", email="info@acme.com")
        self.otra = Empresa.objects.create(nombre="Otra", email="info@otra.com")
        self.colab = crear_usuario("colab@acme.com", self.acme)
        self.equipo = Equipo.objects.create(nombre="Producto", empresa=self.acme)

        self.p_creado = Proyecto.objects.create(nombre="Creado", empresa=self.acme, creador=self.colab)
        self.p_miembro = Proyecto.objects.create(nombre="Miembro", empresa=self.acme)
        self.p_equipo = Proyecto.objects.create(nombre="Equipo", empresa=self.acme, equipo=self.equipo)
        self.p_ajeno = Proyecto.objects.create(nombre="Ajeno", empresa=self.acme)
        self.p_otra = Proyecto.objects.create(nombre="Otra empresa", empresa=self.otra)

        MiembroProyecto.objects.create(proyecto=self.p_miembro, usuario=self.colab)
        MiembroEquipo.objects.create(equipo=self.equipo, usuario=self.colab)

    def nombres(self, usuario):
        return set(Proyecto.objects.visibles_para(usuario).values_list("nombre", flat=True))

    def test_colaborador_ve_solo_donde_lo_agregaron(self):
        self.assertEqual(self.nombres(self.colab), {"Creado", "Miembro", "Equipo"})

    def test_admin_manager_y_supervisor_ven_toda_su_empresa(self):
        for i, rol in enumerate((Rol.ADMIN, Rol.MANAGER, Rol.SUPERVISOR)):
            u = crear_usuario(f"jefe{i}@acme.com", self.acme, rol)
            self.assertEqual(self.nombres(u), {"Creado", "Miembro", "Equipo", "Ajeno"}, rol)

    def test_sin_empresa_no_ve_nada(self):
        jefe = Usuario.objects.create_superuser("root@x.com", "Clave$egura2026")
        self.assertEqual(self.nombres(jefe), set())

    def test_nunca_ve_otra_empresa_aunque_lo_agreguen(self):
        MiembroProyecto.objects.create(proyecto=self.p_otra, usuario=self.colab)
        self.assertNotIn("Otra empresa", self.nombres(self.colab))


class PanelTests(TestCase):
    def setUp(self):
        self.empresa = Empresa.objects.create(nombre="Acme", email="info@acme.com")
        self.ana = crear_usuario("ana@acme.com", self.empresa, Rol.ADMIN, nombres="Ana")
        self.client.force_login(self.ana)

    def test_requiere_sesion(self):
        self.client.logout()
        r = self.client.get(reverse("panel"))
        self.assertRedirects(r, f"{reverse('login')}?next={reverse('panel')}")

    def test_panel_vacio(self):
        r = self.client.get(reverse("panel"))
        self.assertContains(r, "Hola, Ana")
        self.assertContains(r, "Administrador")  # rol en la barra lateral
        self.assertContains(r, "Todavía no hay actividad")
        self.assertContains(r, "No tienes proyectos activos.")
        self.assertNotContains(r, "no pertenece a ninguna empresa")
        self.assertEqual(r.context["estadisticas"]["proyectos_activos"], 0)

    def test_aviso_sin_empresa(self):
        self.client.force_login(Usuario.objects.create_superuser("root@x.com", "Clave$egura2026"))
        self.assertContains(self.client.get(reverse("panel")), "no pertenece a ninguna empresa")

    def test_estadisticas_y_datos_reales(self):
        ayer = timezone.localdate() - timedelta(days=1)
        p = Proyecto.objects.create(nombre="Web", empresa=self.empresa)
        Proyecto.objects.create(nombre="Viejo", empresa=self.empresa, estado=Proyecto.Estado.CANCELADO)
        hecha = Tarea.objects.create(proyecto=p, titulo="Hecha", estado=Tarea.Estado.COMPLETADA)
        Tarea.objects.create(proyecto=p, titulo="Atrasada", asignada_a=self.ana, fecha_vencimiento=ayer)
        Tarea.objects.create(proyecto=p, titulo="De otro")  # sin asignar
        Actividad.registrar_tarea(self.ana, hecha)

        r = self.client.get(reverse("panel"))
        e = r.context["estadisticas"]
        self.assertEqual(e["proyectos_activos"], 1)
        self.assertEqual(e["proyectos_este_mes"], 2)
        self.assertEqual(e["tareas_completadas"], 1)
        self.assertEqual(e["completadas_semana"], 1)
        self.assertEqual(e["mis_pendientes"], 1)
        self.assertEqual(e["mis_vencidas"], 1)
        self.assertEqual([x.progreso for x in r.context["progreso"]], [33])
        self.assertContains(r, "completó la tarea Hecha")
        self.assertContains(r, "Atrasada")

    def test_progreso_ordenado_por_importancia(self):
        I = Proyecto.Importancia
        for nombre, importancia in [("Media", I.MEDIA), ("Crítica", I.CRITICA), ("Alta", I.ALTA)]:
            p = Proyecto.objects.create(nombre=nombre, empresa=self.empresa, nivel_importancia=importancia)
            Tarea.objects.create(proyecto=p, titulo="t")
        r = self.client.get(reverse("panel"))
        self.assertEqual([p.nombre for p in r.context["progreso"]], ["Crítica", "Alta", "Media"])

    def test_proximas_ordenadas_por_fecha_y_prioridad(self):
        p = Proyecto.objects.create(nombre="Web", empresa=self.empresa)
        manana = timezone.localdate() + timedelta(days=1)
        for titulo, prioridad, fecha in [
            ("Sin fecha", Tarea.Prioridad.URGENTE, None),
            ("Mañana baja", Tarea.Prioridad.BAJA, manana),
            ("Mañana urgente", Tarea.Prioridad.URGENTE, manana),
        ]:
            Tarea.objects.create(proyecto=p, titulo=titulo, prioridad=prioridad, fecha_vencimiento=fecha, asignada_a=self.ana)
        r = self.client.get(reverse("panel"))
        self.assertEqual([t.titulo for t in r.context["proximas"]], ["Mañana urgente", "Mañana baja", "Sin fecha"])

    def test_no_ve_datos_de_otra_empresa(self):
        otra = Empresa.objects.create(nombre="Otra", email="o@o.com")
        luis = crear_usuario("luis@otra.com", otra, Rol.ADMIN)
        p = Proyecto.objects.create(nombre="Secreto de Otra", empresa=otra)
        t = Tarea.objects.create(proyecto=p, titulo="Tarea privada", estado=Tarea.Estado.COMPLETADA)
        Actividad.registrar_tarea(luis, t)

        r = self.client.get(reverse("panel"))
        self.assertNotContains(r, "Secreto de Otra")
        self.assertNotContains(r, "Tarea privada")
        self.assertEqual(r.context["estadisticas"]["tareas_completadas"], 0)


class AdminTests(TestCase):
    def setUp(self):
        self.empresa = Empresa.objects.create(nombre="Acme", email="info@acme.com")
        self.admin = Usuario.objects.create_superuser("admin@acme.com", "Clave$egura2026", empresa=self.empresa)
        self.client.force_login(self.admin)
        self.proyecto = Proyecto.objects.create(nombre="Web", empresa=self.empresa)

    def _datos_tarea(self, **extra):
        return {"proyecto": self.proyecto.pk, "titulo": "Login", "estado": "por_hacer", "prioridad": "media", **extra}

    def test_crear_y_completar_tarea_registra_actividad(self):
        self.client.post(reverse("admin:dashboard_tarea_add"), self._datos_tarea())
        tarea = Tarea.objects.get()
        self.assertEqual(tarea.creador, self.admin)

        url = reverse("admin:dashboard_tarea_change", args=[tarea.pk])
        self.client.post(url, self._datos_tarea(estado="completada"))
        textos = list(Actividad.objects.order_by("fecha", "pk").values_list("descripcion", flat=True))
        self.assertEqual(textos, ["creó la tarea Login", "completó la tarea Login"])

        # Guardar sin cambiar el estado no agrega actividad
        self.client.post(url, self._datos_tarea(estado="completada", titulo="Login v2"))
        self.assertEqual(Actividad.objects.count(), 2)

    def test_listados_cargan(self):
        for app, nombre in [
            ("dashboard", "proyecto"), ("dashboard", "tarea"), ("dashboard", "actividad"), ("dashboard", "equipo"),
            ("cuentas", "usuario"), ("cuentas", "empresa"), ("cuentas", "rol"),
        ]:
            self.assertEqual(self.client.get(reverse(f"admin:{app}_{nombre}_changelist")).status_code, 200, nombre)

    def test_formularios_de_alta_cargan(self):
        for app, nombre in [("dashboard", "proyecto"), ("cuentas", "usuario")]:
            self.assertEqual(self.client.get(reverse(f"admin:{app}_{nombre}_add")).status_code, 200, nombre)


class CargarDemoTests(TestCase):
    def test_crea_datos_en_la_empresa_sin_duplicar(self):
        empresa = Empresa.objects.create(nombre="Acme", email="info@acme.com")
        crear_usuario("ana@acme.com", empresa, Rol.ADMIN)
        call_command("cargar_demo", "ANA@acme.com", stdout=StringIO())
        self.assertEqual(Proyecto.objects.filter(empresa=empresa).count(), 3)
        self.assertEqual(Equipo.objects.filter(empresa=empresa).count(), 1)
        tareas = Tarea.objects.count()
        self.assertGreater(Actividad.objects.filter(empresa=empresa).count(), 0)

        call_command("cargar_demo", "ana@acme.com", stdout=StringIO())
        self.assertEqual(Proyecto.objects.count(), 3)
        self.assertEqual(Tarea.objects.count(), tareas)

    def test_usuario_sin_empresa_recibe_una(self):
        root = Usuario.objects.create_superuser("root@x.com", "Clave$egura2026")
        call_command("cargar_demo", "root@x.com", stdout=StringIO())
        root.refresh_from_db()
        self.assertEqual(root.empresa.nombre, "Empresa demo")
        self.assertEqual(Proyecto.objects.filter(empresa=root.empresa).count(), 3)

    def test_usuario_inexistente(self):
        with self.assertRaises(CommandError):
            call_command("cargar_demo", "nadie@empresa.com", stdout=StringIO())
