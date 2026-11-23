from django.test import TestCase
from django.urls import reverse

from cuentas.models import Empresa, Equipo, Usuario
from .models import Proyecto, ReferenciaGitHub, Tarea


class DashboardCrudTests(TestCase):
    def setUp(self):
        self.empresa = Empresa.objects.create(nombre="Empresa Uno")
        self.admin = Usuario.objects.create_user(
            "admin@uno.test",
            "ClaveSegura#2026",
            first_name="Admin",
            empresa=self.empresa,
            rol=Usuario.Rol.ADMIN,
        )
        self.client.force_login(self.admin)

    def test_crea_edita_y_elimina_equipo(self):
        response = self.client.post(
            reverse("equipo_crear"),
            {"nombre": "Producto", "descripcion": "Equipo de producto"},
        )
        self.assertRedirects(response, reverse("equipo"))
        equipo = Equipo.objects.get(nombre="Producto", empresa=self.empresa)

        response = self.client.post(
            reverse("equipo_editar", args=[equipo.pk]),
            {"nombre": "Producto web", "descripcion": ""},
        )
        self.assertRedirects(response, reverse("equipo"))
        equipo.refresh_from_db()
        self.assertEqual(equipo.nombre, "Producto web")

        response = self.client.post(reverse("equipo_eliminar", args=[equipo.pk]))
        self.assertRedirects(response, reverse("equipo"))
        self.assertFalse(Equipo.objects.filter(pk=equipo.pk).exists())

    def test_agrega_integrante_y_asigna_equipo(self):
        equipo = Equipo.objects.create(empresa=self.empresa, nombre="Diseño")
        response = self.client.post(
            reverse("miembro_crear"),
            {
                "first_name": "Ana",
                "last_name": "Ruiz",
                "email": "ANA@UNO.test",
                "rol": Usuario.Rol.COLABORADOR,
                "password": "OtraClaveSegura#2026",
                "equipos": [str(equipo.pk)],
            },
        )
        self.assertRedirects(response, reverse("miembros"))
        miembro = Usuario.objects.get(email="ana@uno.test", empresa=self.empresa)
        self.assertTrue(miembro.check_password("OtraClaveSegura#2026"))
        self.assertEqual(list(miembro.equipos.all()), [equipo])
        response = self.client.post(
            reverse("miembro_editar", args=[miembro.pk]),
            {
                "first_name": "Ana María",
                "last_name": "Ruiz",
                "email": "ana@uno.test",
                "rol": Usuario.Rol.SUPERVISOR,
                "password": "",
                "equipos": [],
            },
        )
        self.assertRedirects(response, reverse("miembros"))
        miembro.refresh_from_db()
        self.assertEqual(miembro.first_name, "Ana María")
        self.assertFalse(miembro.equipos.exists())
        response = self.client.post(reverse("miembro_eliminar", args=[miembro.pk]))
        self.assertRedirects(response, reverse("miembros"))
        miembro.refresh_from_db()
        self.assertFalse(miembro.is_active)

    def test_crud_de_proyecto_y_tarea(self):
        response = self.client.post(
            reverse("proyecto_crear"),
            {
                "nombre": "Lanzamiento",
                "descripcion": "Nueva versión",
                "estado": Proyecto.Estado.ACTIVO,
                "prioridad": Proyecto.Prioridad.ALTA,
                "fecha_inicio": "",
                "fecha_fin": "",
                "equipo": "",
            },
        )
        self.assertRedirects(response, reverse("proyectos"))
        proyecto = Proyecto.objects.get(nombre="Lanzamiento", empresa=self.empresa)
        self.assertTrue(proyecto.miembros.filter(pk=self.admin.pk).exists())
        response = self.client.post(
            reverse("proyecto_editar", args=[proyecto.pk]),
            {
                "nombre": "Lanzamiento actualizado",
                "descripcion": "Nueva versión",
                "estado": Proyecto.Estado.EN_PAUSA,
                "prioridad": Proyecto.Prioridad.ALTA,
                "fecha_inicio": "",
                "fecha_fin": "",
                "equipo": "",
                "miembros": [str(self.admin.pk)],
            },
        )
        self.assertRedirects(response, reverse("proyectos"))
        proyecto.refresh_from_db()
        self.assertEqual(proyecto.estado, Proyecto.Estado.EN_PAUSA)

        response = self.client.post(
            reverse("tarea_crear"),
            {
                "proyecto": str(proyecto.pk),
                "titulo": "Preparar entrega",
                "descripcion": "",
                "estado": Tarea.Estado.PENDIENTE,
                "prioridad": Tarea.Prioridad.NORMAL,
                "responsable": "",
                "fecha_limite": "",
            },
        )
        self.assertRedirects(response, reverse("tareas"))
        tarea = Tarea.objects.get(titulo="Preparar entrega")

        response = self.client.post(
            reverse("tarea_editar", args=[tarea.pk]),
            {
                "proyecto": str(proyecto.pk),
                "titulo": "Entrega lista",
                "descripcion": "",
                "estado": Tarea.Estado.COMPLETADA,
                "prioridad": Tarea.Prioridad.NORMAL,
                "responsable": "",
                "fecha_limite": "",
            },
        )
        self.assertRedirects(response, reverse("tareas"))
        tarea.refresh_from_db()
        self.assertEqual(tarea.titulo, "Entrega lista")
        self.assertEqual(tarea.estado, Tarea.Estado.COMPLETADA)
        response = self.client.post(
            reverse("tarea_cambiar_estado", args=[tarea.pk]),
            {"estado": Tarea.Estado.EN_PROGRESO},
        )
        self.assertRedirects(
            response,
            f"{reverse('tareas')}?proyecto={proyecto.pk}",
        )
        tarea.refresh_from_db()
        self.assertEqual(tarea.estado, Tarea.Estado.EN_PROGRESO)
        self.assertContains(
            self.client.get(reverse("tareas")),
            "Entrega lista",
        )

        response = self.client.post(reverse("tarea_eliminar", args=[tarea.pk]))
        self.assertRedirects(response, reverse("tareas"))
        self.assertFalse(Tarea.objects.filter(pk=tarea.pk).exists())
        Tarea.objects.create(proyecto=proyecto, titulo="Tarea para eliminar con el proyecto")
        response = self.client.post(reverse("proyecto_eliminar", args=[proyecto.pk]))
        self.assertRedirects(response, reverse("proyectos"))
        self.assertFalse(Proyecto.objects.filter(pk=proyecto.pk).exists())

    def test_empresa_y_rol_limita_acceso_a_proyectos(self):
        proyecto = Proyecto.objects.create(
            empresa=self.empresa, nombre="Proyecto interno", creado_por=self.admin
        )
        otra_empresa = Empresa.objects.create(nombre="Empresa Dos")
        proyecto_ajeno = Proyecto.objects.create(empresa=otra_empresa, nombre="Proyecto ajeno")

        colaborador = Usuario.objects.create_user(
            "colaborador@uno.test",
            "ClaveSegura#2026",
            empresa=self.empresa,
            rol=Usuario.Rol.COLABORADOR,
        )
        self.client.force_login(colaborador)
        self.assertEqual(self.client.get(reverse("proyectos")).status_code, 200)
        self.assertNotContains(self.client.get(reverse("proyectos")), "Proyecto interno")
        self.assertEqual(
            self.client.get(reverse("proyecto_editar", args=[proyecto_ajeno.pk])).status_code,
            404,
        )

        proyecto.miembros.add(colaborador)
        self.assertContains(self.client.get(reverse("proyectos")), "Proyecto interno")
        self.assertEqual(
            self.client.get(reverse("proyecto_editar", args=[proyecto.pk])).status_code,
            200,
        )

        supervisor = Usuario.objects.create_user(
            "supervisor@uno.test",
            "ClaveSegura#2026",
            empresa=self.empresa,
            rol=Usuario.Rol.SUPERVISOR,
        )
        self.client.force_login(supervisor)
        self.assertEqual(self.client.get(reverse("proyectos")).status_code, 200)
        self.assertEqual(
            self.client.get(reverse("proyecto_editar", args=[proyecto.pk])).status_code,
            403,
        )

    def test_usuario_no_puede_administrar_equipos(self):
        colaborador = Usuario.objects.create_user(
            "colaborador2@uno.test",
            "ClaveSegura#2026",
            empresa=self.empresa,
            rol=Usuario.Rol.COLABORADOR,
        )
        self.client.force_login(colaborador)
        self.assertEqual(self.client.get(reverse("equipo_crear")).status_code, 403)

    def test_acciones_de_creacion_y_control_de_tema_se_mantienen(self):
        response = self.client.get(reverse("proyectos"))
        self.assertContains(response, "Crear proyecto")
        self.assertContains(response, "data-theme-toggle")
        self.assertContains(response, "xnx-action-create")

        response = self.client.get(reverse("equipo"))
        self.assertContains(response, "Crear equipo")
        self.assertContains(response, "data-theme-toggle")

    def test_tablero_filtra_tareas_por_proyecto(self):
        visible = Proyecto.objects.create(
            empresa=self.empresa, nombre="Proyecto visible", creado_por=self.admin
        )
        oculto = Proyecto.objects.create(
            empresa=self.empresa, nombre="Proyecto diferente", creado_por=self.admin
        )
        Tarea.objects.create(proyecto=visible, titulo="Tarea visible")
        Tarea.objects.create(proyecto=oculto, titulo="Tarea diferente")

        response = self.client.get(reverse("tareas"), {"proyecto": visible.pk})
        self.assertContains(response, "Tarea visible")
        self.assertNotContains(response, "Tarea diferente")

    def test_empresa_conserva_al_menos_un_administrador(self):
        self.assertEqual(self.admin.rol, Usuario.Rol.ADMIN)
        self.assertEqual(
            Usuario.objects.filter(empresa=self.empresa, rol=Usuario.Rol.ADMIN, is_active=True).count(),
            1,
        )
        response = self.client.post(
            reverse("miembro_editar", args=[self.admin.pk]),
            {
                "first_name": self.admin.first_name,
                "last_name": self.admin.last_name,
                "email": self.admin.email,
                "rol": Usuario.Rol.COLABORADOR,
                "password": "",
                "equipos": [],
            },
        )
        self.assertEqual(response.status_code, 200, response.get("Location"))
        self.admin.refresh_from_db()
        self.assertEqual(self.admin.rol, Usuario.Rol.ADMIN)
        self.assertContains(response, "La empresa debe conservar al menos un administrador activo.")

    def test_vincula_issues_y_pull_requests_del_repositorio(self):
        proyecto = Proyecto.objects.create(
            empresa=self.empresa,
            nombre="Aplicación",
            repositorio_url="https://github.com/acme/app",
            creado_por=self.admin,
        )
        response = self.client.post(
            reverse("github_referencias", args=[proyecto.pk]),
            {
                "tipo": ReferenciaGitHub.Tipo.ISSUE,
                "titulo": "Añadir inicio de sesión",
                "url": "https://github.com/acme/app/issues/14",
            },
        )
        self.assertRedirects(response, reverse("github_referencias", args=[proyecto.pk]))
        issue = ReferenciaGitHub.objects.get(proyecto=proyecto)
        self.assertEqual(issue.tipo, ReferenciaGitHub.Tipo.ISSUE)

        response = self.client.post(
            reverse("github_referencias", args=[proyecto.pk]),
            {
                "tipo": ReferenciaGitHub.Tipo.PULL_REQUEST,
                "titulo": "Corrección de autenticación",
                "url": "https://github.com/acme/app/pull/18",
            },
        )
        self.assertRedirects(response, reverse("github_referencias", args=[proyecto.pk]))
        self.assertEqual(proyecto.referencias_github.count(), 2)

        response = self.client.post(
            reverse("github_referencias", args=[proyecto.pk]),
            {
                "tipo": ReferenciaGitHub.Tipo.ISSUE,
                "titulo": "Enlace de otro repositorio",
                "url": "https://github.com/another/repo/issues/1",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "debe pertenecer al repositorio de este proyecto")
        self.assertEqual(proyecto.referencias_github.count(), 2)

        response = self.client.post(
            reverse("github_referencia_eliminar", args=[proyecto.pk, issue.pk])
        )
        self.assertRedirects(response, reverse("github_referencias", args=[proyecto.pk]))
        self.assertFalse(ReferenciaGitHub.objects.filter(pk=issue.pk).exists())

    def test_solo_acepta_url_de_repositorio_y_referencia_coherente(self):
        response = self.client.post(
            reverse("proyecto_crear"),
            {
                "nombre": "App con URL incorrecta",
                "descripcion": "",
                "repositorio_url": "https://github.com/acme/app/issues/1",
                "estado": Proyecto.Estado.ACTIVO,
                "prioridad": Proyecto.Prioridad.NORMAL,
                "fecha_inicio": "",
                "fecha_fin": "",
                "equipo": "",
                "miembros": [str(self.admin.pk)],
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Escribe la URL HTTPS de un repositorio público")
        self.assertFalse(Proyecto.objects.filter(nombre="App con URL incorrecta").exists())

    def test_supervisor_solo_puede_ver_referencias_github(self):
        proyecto = Proyecto.objects.create(
            empresa=self.empresa,
            nombre="App",
            repositorio_url="https://github.com/acme/app",
            creado_por=self.admin,
        )
        supervisor = Usuario.objects.create_user(
            "supervisor2@uno.test",
            "ClaveSegura#2026",
            empresa=self.empresa,
            rol=Usuario.Rol.SUPERVISOR,
        )
        self.client.force_login(supervisor)
        self.assertEqual(
            self.client.get(reverse("github_referencias", args=[proyecto.pk])).status_code,
            200,
        )
        response = self.client.post(
            reverse("github_referencias", args=[proyecto.pk]),
            {
                "tipo": ReferenciaGitHub.Tipo.ISSUE,
                "titulo": "Issue",
                "url": "https://github.com/acme/app/issues/3",
            },
        )
        self.assertEqual(response.status_code, 403)
        self.assertFalse(ReferenciaGitHub.objects.exists())
