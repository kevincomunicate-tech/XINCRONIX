"""Mi empresa, proyectos (CRUD), miembros de otras empresas y tareas."""

from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse

from cuentas.models import Empresa, Rol, Usuario

from .models import Proyecto, ProyectoMiembro, Tarea

CLAVE = "Clave$egura2026"


def usuario(email, empresa=None, rol=Rol.USUARIO):
    return Usuario.objects.create_user(email, CLAVE, first_name=email.split("@")[0].title(), empresa=empresa,
                                       rol=Rol.objects.get(codigo=rol))


class MiEmpresaTests(TestCase):
    def setUp(self):
        self.ana = usuario("ana@x.com")
        self.client.force_login(self.ana)

    def test_crear_mi_empresa(self):
        self.assertContains(self.client.get(reverse("mi_empresa")), "Crear mi empresa")
        r = self.client.post(reverse("mi_empresa"), {"nombre": "Acme"})
        self.assertRedirects(r, reverse("mi_empresa"))
        self.ana.refresh_from_db()
        self.assertEqual(self.ana.empresa.nombre, "Acme")
        self.assertEqual(self.ana.empresa.propietario, self.ana)
        self.assertEqual(self.ana.rol.codigo, Rol.USUARIO)  # crear empresa NO lo vuelve administrador

    def test_ve_sus_metricas(self):
        empresa = Empresa.objects.create(nombre="Acme", propietario=self.ana)
        self.ana.empresa = empresa
        self.ana.save()
        p = Proyecto.objects.create(nombre="Web", empresa=empresa, creado_por=self.ana)
        Tarea.objects.create(titulo="Uno", proyecto=p, estado=Tarea.Estado.COMPLETADA)
        Tarea.objects.create(titulo="Dos", proyecto=p, fecha_vencimiento=date.today() - timedelta(days=3))
        r = self.client.get(reverse("mi_empresa"))
        self.assertEqual(r.context["metricas"]["avance"], 50)
        self.assertEqual(r.context["metricas"]["tareas_vencidas"], 1)
        self.assertContains(r, "Avance por proyecto")
        self.assertEqual(self.client.get(reverse("panel")).context["metricas"]["proyectos"], 1)

    def test_integrante_ve_pero_no_edita_ni_elimina(self):
        empresa = Empresa.objects.create(nombre="Acme", propietario=usuario("dueno@x.com"))
        self.ana.empresa = empresa
        self.ana.save()
        self.assertEqual(self.client.get(reverse("mi_empresa")).status_code, 200)
        self.assertEqual(self.client.get(reverse("mi_empresa_editar")).status_code, 403)
        self.assertEqual(self.client.post(reverse("mi_empresa_eliminar")).status_code, 403)

    def test_propietario_elimina_y_los_integrantes_conservan_su_cuenta(self):
        empresa = Empresa.objects.create(nombre="Acme", propietario=self.ana)
        self.ana.empresa = empresa
        self.ana.save()
        beto = usuario("beto@x.com", empresa)
        r = self.client.post(reverse("mi_empresa_eliminar"))
        self.assertRedirects(r, reverse("panel"))
        self.assertFalse(Empresa.objects.exists())
        beto.refresh_from_db()
        self.assertIsNone(beto.empresa)


class ProyectoBase(TestCase):
    def setUp(self):
        self.acme = Empresa.objects.create(nombre="Acme")
        self.ana = usuario("ana@acme.com", self.acme)           # crea el proyecto
        self.acme.propietario = self.ana
        self.acme.save()
        self.externo = usuario("leo@otra.com", Empresa.objects.create(nombre="Otra"))  # de otra empresa
        self.colega = usuario("dani@acme.com", self.acme)       # misma empresa, sin relación
        self.client.force_login(self.ana)
        r = self.client.post(reverse("proyecto_crear"), {
            "nombre": "App móvil", "estado": "activo", "nivel_importancia": 2,
            "fecha_inicio": "2026-11-01", "fecha_fin": "2026-12-15",
        })
        self.proyecto = Proyecto.objects.get(nombre="App móvil")
        self.assertRedirects(r, reverse("proyecto_detalle", args=[self.proyecto.pk]))

    def agregar(self, correo, rol="editor"):
        return self.client.post(reverse("miembro_agregar", args=[self.proyecto.pk]), {"email": correo, "rol": rol})


class ProyectoTests(ProyectoBase):
    def test_creado_con_su_empresa_y_creador(self):
        self.assertEqual((self.proyecto.empresa, self.proyecto.creado_por), (self.acme, self.ana))

    def test_sin_empresa_primero_debe_crearla(self):
        self.client.force_login(usuario("sin@x.com"))
        self.assertRedirects(self.client.get(reverse("proyecto_crear")), reverse("mi_empresa"))

    def test_fechas_al_reves_se_rechazan(self):
        r = self.client.post(reverse("proyecto_editar", args=[self.proyecto.pk]), {
            "nombre": "App", "estado": "activo", "nivel_importancia": 2, "fecha_inicio": "2026-12-10", "fecha_fin": "2026-12-01",
        })
        self.assertContains(r, "La fecha de fin no puede ser anterior a la de inicio.")

    def test_invitar_a_alguien_de_otra_empresa(self):
        self.assertRedirects(self.agregar("LEO@otra.com"), reverse("proyecto_detalle", args=[self.proyecto.pk]))
        self.client.force_login(self.externo)
        self.assertContains(self.client.get(reverse("proyectos")), "App móvil")
        # El editor ajusta las fechas del proyecto...
        r = self.client.post(reverse("proyecto_editar", args=[self.proyecto.pk]), {
            "nombre": "App móvil", "estado": "en_progreso", "nivel_importancia": 3,
            "fecha_inicio": "2026-11-01", "fecha_fin": "2027-01-31",
        })
        self.assertRedirects(r, reverse("proyecto_detalle", args=[self.proyecto.pk]))
        self.proyecto.refresh_from_db()
        self.assertEqual(self.proyecto.fecha_fin, date(2027, 1, 31))
        # ...y crea y edita tareas
        r = self.client.post(reverse("tarea_crear", args=[self.proyecto.pk]), {
            "titulo": "Login", "estado": "por_hacer", "prioridad": "alta", "fecha_vencimiento": "2026-12-01", "asignado_a": self.ana.pk,
        })
        tarea = Tarea.objects.get(titulo="Login")
        self.assertEqual((tarea.creado_por, tarea.asignado_a), (self.externo, self.ana))
        self.client.post(reverse("tarea_editar", args=[tarea.pk]), {
            "titulo": "Login", "estado": "completada", "prioridad": "alta", "fecha_vencimiento": "2026-12-05",
        })
        tarea.refresh_from_db()
        self.assertEqual((tarea.estado, tarea.fecha_vencimiento), ("completada", date(2026, 12, 5)))
        # pero no lo elimina ni gestiona miembros
        self.assertEqual(self.client.post(reverse("proyecto_eliminar", args=[self.proyecto.pk])).status_code, 403)
        self.assertEqual(self.agregar("dani@acme.com").status_code, 403)

    def test_observador_solo_ve(self):
        self.agregar("leo@otra.com", rol="observador")
        self.client.force_login(self.externo)
        self.assertEqual(self.client.get(reverse("proyecto_detalle", args=[self.proyecto.pk])).status_code, 200)
        self.assertEqual(self.client.get(reverse("proyecto_editar", args=[self.proyecto.pk])).status_code, 403)
        self.assertEqual(self.client.get(reverse("tarea_crear", args=[self.proyecto.pk])).status_code, 403)

    def test_sin_relacion_no_lo_ve(self):
        self.client.force_login(self.colega)
        self.assertEqual(self.client.get(reverse("proyecto_detalle", args=[self.proyecto.pk])).status_code, 404)
        self.assertNotContains(self.client.get(reverse("proyectos")), "App móvil")

    def test_responsable_gestiona_miembros(self):
        self.agregar("leo@otra.com", rol="responsable")
        self.client.force_login(self.externo)
        self.assertRedirects(self.agregar("dani@acme.com", rol="observador"), reverse("proyecto_detalle", args=[self.proyecto.pk]))

    def test_validaciones_al_invitar(self):
        self.assertContains(self.agregar("nadie@x.com"), "No hay ninguna cuenta activa con ese correo.")
        self.assertContains(self.agregar("ana@acme.com"), "Es quien creó el proyecto")
        self.agregar("leo@otra.com")
        self.assertContains(self.agregar("leo@otra.com"), "Esa persona ya está en el proyecto.")

    def test_un_miembro_puede_salirse(self):
        self.agregar("leo@otra.com")
        miembro = ProyectoMiembro.objects.get(usuario=self.externo)
        self.client.force_login(self.externo)
        r = self.client.post(reverse("miembro_quitar", args=[self.proyecto.pk, miembro.pk]))
        self.assertRedirects(r, reverse("proyectos"))
        self.assertFalse(ProyectoMiembro.objects.exists())

    def test_creador_elimina_el_proyecto(self):
        Tarea.objects.create(titulo="T", proyecto=self.proyecto)
        self.assertContains(self.client.get(reverse("proyecto_eliminar", args=[self.proyecto.pk])), "Se eliminan sus 1 tarea(s).")
        self.assertRedirects(self.client.post(reverse("proyecto_eliminar", args=[self.proyecto.pk])), reverse("proyectos"))
        self.assertFalse(Proyecto.objects.exists() or Tarea.objects.exists())

    def test_tarea_solo_se_asigna_a_quien_trabaja_en_el_proyecto(self):
        r = self.client.post(reverse("tarea_crear", args=[self.proyecto.pk]), {
            "titulo": "X", "estado": "por_hacer", "prioridad": "media", "asignado_a": self.colega.pk,
        })
        self.assertEqual(r.status_code, 200)
        self.assertIn("asignado_a", r.context["form"].errors)

    def test_lista_de_mis_tareas(self):
        Tarea.objects.create(titulo="Mía", proyecto=self.proyecto, asignado_a=self.ana)
        Tarea.objects.create(titulo="De nadie", proyecto=self.proyecto)
        r = self.client.get(reverse("tareas"))
        self.assertContains(r, "Mía")
        self.assertNotContains(r, "De nadie")
        self.assertContains(self.client.get(reverse("tareas"), {"ver": "todas"}), "De nadie")


class FlechasTests(ProyectoBase):
    def test_las_paginas_internas_tienen_flecha_de_regreso(self):
        tarea = Tarea.objects.create(titulo="T", proyecto=self.proyecto)
        paginas = {
            reverse("proyectos"): reverse("panel"),
            reverse("proyecto_detalle", args=[self.proyecto.pk]): reverse("proyectos"),
            reverse("proyecto_editar", args=[self.proyecto.pk]): reverse("proyecto_detalle", args=[self.proyecto.pk]),
            reverse("tarea_editar", args=[tarea.pk]): reverse("proyecto_detalle", args=[self.proyecto.pk]),
            reverse("mi_empresa"): reverse("panel"),
            reverse("mi_cuenta"): reverse("inicio"),
            reverse("ideas"): reverse("panel"),
        }
        for pagina, destino in paginas.items():
            with self.subTest(pagina=pagina):
                self.assertContains(self.client.get(pagina), f'href="{destino}" class="xnx-volver"')

    def test_login_y_registro_tienen_flecha_a_la_portada(self):
        self.client.logout()
        for pagina in ("login", "registro"):
            self.assertContains(self.client.get(reverse(pagina)), f'href="{reverse("inicio")}" class="auth-volver"')
        self.assertContains(self.client.get(reverse("recuperar")), f'href="{reverse("login")}" class="auth-volver"')


class CargarDemoTests(TestCase):
    """El comando de datos de ejemplo (versión de Felipe, adaptada)."""

    def test_crea_empresa_proyectos_y_no_duplica(self):
        from io import StringIO

        from django.core.management import call_command

        from .models import Actividad

        ana = usuario("ana@demo.com")
        call_command("cargar_demo", "ANA@demo.com", stdout=StringIO())
        ana.refresh_from_db()
        self.assertEqual((ana.empresa.nombre, ana.empresa.propietario, ana.rol.codigo), ("Empresa demo", ana, Rol.USUARIO))
        self.assertEqual(Proyecto.objects.filter(empresa=ana.empresa).count(), 3)
        self.assertEqual(Tarea.objects.filter(proyecto__empresa=ana.empresa).count(), 9)
        self.assertEqual(Actividad.objects.filter(empresa=ana.empresa).count(), 12)
        call_command("cargar_demo", "ana@demo.com", stdout=StringIO())
        self.assertEqual(Proyecto.objects.count(), 3)  # no duplica
        self.client.force_login(ana)
        self.assertEqual(self.client.get(reverse("panel")).context["metricas"]["proyectos"], 3)
