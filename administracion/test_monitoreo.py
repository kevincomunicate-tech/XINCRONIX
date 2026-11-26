"""Panel de monitoreo del superadministrador (/administracion/monitoreo/)."""

from django.db import DatabaseError
from django.test import Client, TestCase
from django.urls import reverse

from cuentas.models import Usuario
from dashboard.models import Proyecto, Tarea

from . import monitoreo

CLAVE = "Clave$egura2026"


class Base(TestCase):
    def setUp(self):
        self.super = Usuario.objects.create_superuser("cuellaryohan100@gmail.com", CLAVE, first_name="Yohan", last_name="Usuario")
        self.ana = Usuario.objects.create_user("ana@x.com", CLAVE, first_name="Ana", last_name="Usuario")
        self.proyecto = Proyecto.objects.create(nombre="Web", creado_por=self.ana, descripcion="Descripción de prueba")
        Tarea.objects.create(titulo="Diseño", proyecto=self.proyecto)
        Tarea.objects.create(titulo="Pruebas", proyecto=Proyecto.objects.create(nombre="App", creado_por=self.ana, descripcion="Descripción de prueba"), descripcion="Descripción de prueba")
        self.client.force_login(self.super)


class AccesoTests(Base):
    PAGINAS = [
        ("administracion:monitoreo", []),
        ("administracion:monitoreo_tablas", []),
        ("administracion:monitoreo_sesiones", []),
        ("administracion:monitoreo_sistema", []),
        ("administracion:monitoreo_tabla", ["cuentas", "usuario"]),
        ("administracion:monitoreo_tabla", ["dashboard", "tarea"]),
    ]

    def test_superadministrador_ve_todas_las_paginas(self):
        for nombre, args in self.PAGINAS:
            with self.subTest(nombre=nombre, args=args):
                self.assertEqual(self.client.get(reverse(nombre, args=args)).status_code, 200)

    def test_usuario_normal_recibe_403(self):
        cliente = Client()
        cliente.force_login(self.ana)
        for nombre, args in self.PAGINAS:
            with self.subTest(nombre=nombre):
                self.assertEqual(cliente.get(reverse(nombre, args=args)).status_code, 403)

    def test_sin_sesion_va_al_login(self):
        respuesta = Client().get(reverse("administracion:monitoreo"))
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn(reverse("login"), respuesta["Location"])

    def test_menu_del_superadministrador_tiene_monitoreo(self):
        self.assertContains(self.client.get(reverse("administracion:inicio")), reverse("administracion:monitoreo"))


class ResumenTests(Base):
    def test_tarjetas_y_alertas_salen_del_json(self):
        r = self.client.get(reverse("administracion:monitoreo"))
        tarjetas = {t["texto"]: t["total"] for t in r.context["tarjetas"]}
        self.assertEqual((tarjetas["Usuarios"], tarjetas["Proyectos"], tarjetas["Tareas"]), (2, 2, 2))
        alertas = {a["texto"]: a["total"] for a in r.context["alertas"]}
        self.assertEqual(alertas["Cuentas desactivadas"], 0)
        self.assertEqual(alertas["Proyectos sin tareas"], 0)  # los dos proyectos tienen tarea

    def test_tabla_que_falta_no_rompe_la_pagina(self):
        def falla():
            raise DatabaseError("no such table")
        self.assertEqual(monitoreo.consultar(falla, por_defecto="falta"), "falta")


class TablasTests(Base):
    def test_contrasena_nunca_se_muestra(self):
        hash_ana = self.ana.password
        lista = self.client.get(reverse("administracion:monitoreo_tabla", args=["cuentas", "usuario"]))
        detalle = self.client.get(reverse("administracion:monitoreo_registro", args=["cuentas", "usuario", self.ana.pk]))
        for respuesta in (lista, detalle):
            self.assertNotContains(respuesta, hash_ana)
            self.assertContains(respuesta, monitoreo.OCULTO)

    def test_csv_no_trae_campos_sensibles(self):
        r = self.client.get(reverse("administracion:monitoreo_exportar", args=["cuentas", "usuario"]))
        contenido = b"".join(r.streaming_content).decode()
        encabezado = contenido.lstrip("﻿").splitlines()[0].split(",")
        self.assertNotIn("password", encabezado)
        self.assertNotIn(self.ana.password, contenido)
        self.assertIn("ana@x.com", contenido)

    def test_buscar_y_filtrar_por_campo(self):
        url = reverse("administracion:monitoreo_tabla", args=["dashboard", "tarea"])
        self.assertEqual(self.client.get(url, {"q": "Diseño"}).context["total"], 1)
        self.assertEqual(self.client.get(url, {"campo": "proyecto", "valor": self.proyecto.pk}).context["total"], 1)
        self.assertEqual(self.client.get(url, {"campo": "proyecto", "valor": "no-es-numero"}).context["total"], 0)

    def test_registro_muestra_relaciones_inversas(self):
        r = self.client.get(reverse("administracion:monitoreo_registro", args=["dashboard", "proyecto", self.proyecto.pk]))
        tareas = next(i for i in r.context["inversas"] if i["campo"] == "proyecto" and "tarea" in i["tabla"])
        self.assertEqual(tareas["total"], 1)

    def test_tablas_solo_conteo_y_tablas_inexistentes(self):
        self.assertEqual(self.client.get(reverse("administracion:monitoreo_tabla", args=["sessions", "session"])).status_code, 404)
        self.assertEqual(self.client.get(reverse("administracion:monitoreo_tabla", args=["nada", "nada"])).status_code, 404)
        self.assertEqual(self.client.get(reverse("administracion:monitoreo_registro", args=["cuentas", "usuario", "abc"])).status_code, 404)

    def test_catalogo_cuenta_las_filas(self):
        tablas = {t["etiqueta"]: t for g in monitoreo.catalogo() for t in g["tablas"]}
        self.assertEqual(tablas["dashboard.tarea"]["total"], 2)
        self.assertFalse(tablas["sessions.session"]["abrir"])


class SesionesTests(Base):
    def test_cerrar_sesiones_de_un_usuario_sin_cerrar_la_propia(self):
        cliente_ana = Client()
        cliente_ana.force_login(self.ana)
        r = self.client.get(reverse("administracion:monitoreo_sesiones"))
        self.assertEqual(r.context["usuarios_conectados"], 2)
        self.assertNotContains(r, cliente_ana.session.session_key)  # solo se ve la huella

        self.client.post(reverse("administracion:monitoreo_cerrar_sesiones"), {"accion": "usuario", "usuario": self.ana.pk})

        self.assertEqual(cliente_ana.get(reverse("panel")).status_code, 302)  # Ana debe volver a iniciar sesión
        self.assertEqual(self.client.get(reverse("administracion:monitoreo_sesiones")).status_code, 200)

    def test_cerrar_una_sesion_por_huella(self):
        cliente_ana = Client()
        cliente_ana.force_login(self.ana)
        huella = monitoreo.huella(cliente_ana.session.session_key)
        self.client.post(reverse("administracion:monitoreo_cerrar_sesiones"), {"accion": "una", "sesion": huella})
        self.assertEqual(cliente_ana.get(reverse("panel")).status_code, 302)

    def test_cerrar_sesiones_exige_post(self):
        self.assertEqual(self.client.get(reverse("administracion:monitoreo_cerrar_sesiones")).status_code, 405)


class ConfiguracionJsonTests(TestCase):
    def test_json_del_proyecto_es_valido(self):
        from django.conf import settings
        monitoreo.leer_monitoreo(settings.MONITOREO)

    def test_errores_se_explican(self):
        from django.conf import settings
        import json
        from pathlib import Path

        datos = json.loads(Path(settings.MONITOREO).read_text(encoding="utf-8"))
        datos["alertas"] = [
            {"texto": "Modelo malo", "nivel": "info", "modelo": "cuentas.nada"},
            {"texto": "Filtro malo", "nivel": "info", "modelo": "cuentas.usuario", "filtro": {"no_existe": 1}},
            {"texto": "Nivel malo", "nivel": "rojo", "modelo": "cuentas.usuario"},
        ]
        errores = " | ".join(monitoreo.validar(datos))
        self.assertIn("cuentas.nada", errores)
        self.assertIn("no_existe", errores)
        self.assertIn("'nivel'", errores)
