"""Reportes: filtros de varios criterios, validaciones, Excel y PDF, y acceso por rol.

Los archivos generados se abren de verdad (openpyxl para Excel, cabecera y tamaño para PDF)."""

import datetime as dt
import io
from unittest import mock

from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from openpyxl import load_workbook

from administracion import reportes as r
from cuentas.models import Usuario
from dashboard.models import InvitacionProyecto, Proyecto, ProyectoMiembro, Tarea

CLAVE = "Clave$egura2026"


def crit(campo, op="igual", valor="", valor2=""):
    return {"campo": campo, "operador": op, "valor": valor, "valor2": valor2}


class DatosBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.super = Usuario.objects.create_superuser("super@prueba.com", CLAVE, first_name="Yohan", last_name="Cuellar")
        cls.est = Usuario.objects.create_user("est@prueba.com", CLAVE, first_name="Ana", perfil="estudiante", last_name="Usuario")
        cls.est2 = Usuario.objects.create_user("est2@prueba.com", CLAVE, first_name="Beto", perfil="estudiante", is_active=False, last_name="Usuario")
        cls.prof = Usuario.objects.create_user("prof@prueba.com", CLAVE, first_name="Carla", perfil="profesor", last_name="Usuario")
        cls.p1 = Proyecto.objects.create(nombre="Tienda", creado_por=cls.est, modalidad="grupal", estado="en_progreso", descripcion="Descripción de prueba")
        cls.p2 = Proyecto.objects.create(nombre="Notas", creado_por=cls.prof, estado="planificacion", descripcion="Descripción de prueba")
        ProyectoMiembro.objects.create(proyecto=cls.p1, usuario=cls.est, rol="lider")
        ProyectoMiembro.objects.create(proyecto=cls.p1, usuario=cls.est2, rol="editor")
        ProyectoMiembro.objects.create(proyecto=cls.p2, usuario=cls.prof, rol="lider")
        cls.t1 = Tarea.objects.create(titulo="Carrito", proyecto=cls.p1, estado="hecha", prioridad="alta",
                                      fecha_vencimiento=dt.date(2026, 6, 1), asignado_a=cls.est, creado_por=cls.est)
        cls.t2 = Tarea.objects.create(titulo="Pagos", proyecto=cls.p1, estado="por_hacer", prioridad="baja",
                                      fecha_vencimiento=dt.date(2026, 12, 15), creado_por=cls.est)
        InvitacionProyecto.objects.create(proyecto=cls.p1, email="nuevo@prueba.com", rol="lector", creado_por=cls.est,
                                          vence_en=timezone.now() + dt.timedelta(days=7))


class MotorDeFiltrosTests(DatosBase):
    def total(self, clave, criterios, logica="y"):
        return r.filas(clave, criterios, logica)[2]

    def test_sin_criterios_trae_todo(self):
        self.assertEqual(self.total("usuarios", []), Usuario.objects.count())

    def test_un_criterio_por_perfil(self):
        self.assertEqual(self.total("usuarios", [crit("perfil", valor="estudiante")]), 2)

    def test_varios_criterios_en_y(self):
        cr = [crit("perfil", valor="estudiante"), crit("is_active", valor="sí")]
        self.assertEqual(self.total("usuarios", cr), 1)  # solo Ana está activa

    def test_varios_criterios_en_o(self):
        cr = [crit("perfil", valor="profesor"), crit("first_name", "contiene", "ana")]
        self.assertEqual(self.total("usuarios", cr, logica="o"), 2)

    def test_contiene_no_distingue_mayusculas(self):
        self.assertEqual(self.total("usuarios", [crit("email", "contiene", "PRUEBA.COM")]), Usuario.objects.count())

    def test_distinto_de(self):
        self.assertEqual(self.total("usuarios", [crit("perfil", "distinto", "estudiante")]), Usuario.objects.exclude(perfil="estudiante").count())

    def test_rango_de_fechas_incluye_el_dia_final(self):
        cr = [crit("fecha_vencimiento", "entre", "2026-06-01", "2026-06-01")]
        self.assertEqual(self.total("tareas", cr), 1)  # solo "Carrito" vence ese día

    def test_fechas_al_reves_se_rechazan(self):
        with self.assertRaisesMessage(r.ErrorReporte, "no puede ser anterior"):
            self.total("tareas", [crit("fecha_vencimiento", "entre", "2026-12-01", "2026-01-01")])

    def test_menor_que_incluye_el_dia_indicado(self):
        self.assertEqual(self.total("tareas", [crit("fecha_vencimiento", "menor_que", "2026-06-01")]), 1)

    def test_vacio_y_no_vacio_en_fechas(self):
        # "Carrito" está hecha: el modelo le pone fecha de completado. Solo "Pagos" queda vacía.
        self.assertEqual(self.total("tareas", [crit("fecha_completada", "vacio")]), 1)
        self.assertEqual(self.total("tareas", [crit("fecha_completada", "no_vacio")]), 1)
        self.assertEqual(self.total("tareas", [crit("fecha_vencimiento", "no_vacio")]), 2)

    def test_responsable_vacio(self):
        self.assertEqual(self.total("tareas", [crit("asignado_a__email", "vacio")]), 1)  # "Pagos" no tiene responsable

    def test_filtro_por_relacion(self):
        self.assertEqual(self.total("tareas", [crit("proyecto__nombre", "contiene", "tienda")]), 2)
        self.assertEqual(self.total("tareas", [crit("asignado_a__email", "contiene", "est@")]), 1)

    def test_integrantes_por_permiso(self):
        self.assertEqual(self.total("integrantes", [crit("rol", valor="lider")]), 2)

    def test_proyectos_cuentan_integrantes(self):
        cols, datos, _ = r.filas("proyectos", [crit("nombre", "igual", "Tienda")], columnas=["nombre", "total_miembros"])
        self.assertEqual(datos, [["Tienda", 2]])

    def test_etiquetas_legibles_para_opciones(self):
        cols, datos, _ = r.filas("proyectos", [crit("nombre", "igual", "Tienda")], columnas=["nombre", "estado"])
        self.assertEqual(datos[0][1], "En progreso")

    def test_orden_por_defecto(self):
        _, datos, _ = r.filas("usuarios", [], columnas=["email"])
        self.assertEqual([f[0] for f in datos], sorted(f[0] for f in datos))


class ValidacionesDelMotorTests(DatosBase):
    def assertRechaza(self, clave, criterios, logica="y", columnas=None):
        with self.assertRaises(r.ErrorReporte):
            r.construir(clave, criterios, logica, columnas)

    def test_tabla_inventada(self):
        self.assertRechaza("sesiones", [])

    def test_campo_inventado_no_se_puede_filtrar(self):
        self.assertRechaza("usuarios", [crit("contrasena_real", valor="x")])

    def test_campo_sensible_no_se_puede_filtrar(self):
        self.assertRechaza("usuarios", [crit("password", "contiene", "pbkdf2")])

    def test_campo_sensible_no_se_puede_pedir_como_columna(self):
        cols, _, _ = r.filas("usuarios", [], columnas=["password", "email"])
        self.assertEqual([c.ruta for c in cols], ["email"])  # ignorada; no se devuelve el hash

    def test_operador_que_no_aplica(self):
        self.assertRechaza("usuarios", [crit("perfil", "entre", "a", "b")])

    def test_contiene_en_una_fecha(self):
        self.assertRechaza("tareas", [crit("fecha_vencimiento", "contiene", "2026")])

    def test_fecha_mal_escrita(self):
        self.assertRechaza("tareas", [crit("fecha_vencimiento", "igual", "31/12/2026")])

    def test_opcion_que_no_existe(self):
        self.assertRechaza("tareas", [crit("estado", "igual", "volando")])

    def test_booleano_mal_escrito(self):
        self.assertRechaza("usuarios", [crit("is_active", "igual", "tal vez")])

    def test_demasiados_criterios(self):
        self.assertRechaza("usuarios", [crit("perfil", valor="x")] * (r.MAX_CRITERIOS + 1))

    def test_logica_invalida(self):
        self.assertRechaza("usuarios", [], logica="xor")

    def test_entre_sin_dos_valores(self):
        self.assertRechaza("tareas", [crit("fecha_vencimiento", "entre", "2026-01-01")])

    def test_criterio_de_texto_vacio_en_igual(self):
        self.assertRechaza("usuarios", [crit("email", "igual", "")])


class ExcelTests(DatosBase):
    def abrir(self, clave, criterios, logica="y", columnas=None):
        contenido = r.exportar_excel(clave, criterios, logica, columnas or [], "Yohan")
        return load_workbook(io.BytesIO(contenido))

    def test_estructura_y_formato(self):
        libro = self.abrir("tareas", [crit("proyecto__nombre", "contiene", "tienda")], columnas=["titulo", "estado", "fecha_vencimiento"])
        hoja = libro["Reporte"]
        self.assertEqual(hoja["A1"].value, "Xincronix · Reporte de Tareas")
        self.assertEqual(hoja["A6"].value, "Tarea")
        self.assertEqual(hoja["A6"].font.bold, True)
        self.assertEqual(hoja["A6"].fill.fgColor.rgb[-6:], "1F3A5F")  # encabezado azul
        self.assertTrue(hoja.freeze_panes)  # encabezado fijo
        self.assertIsNotNone(hoja.auto_filter.ref)  # filtros de Excel activos
        self.assertEqual(hoja.max_row, 6 + 2)  # encabezado + 2 tareas
        fechas = [hoja.cell(row=7, column=3).number_format, hoja.cell(row=8, column=3).number_format]
        self.assertIn("dd/mm/yyyy", fechas[0])

    def test_el_resumen_muestra_etiquetas_y_no_codigos(self):
        libro = self.abrir("proyectos", [crit("estado", "igual", "en_progreso")], columnas=["nombre"])
        self.assertIn("En progreso", libro["Criterios"]["B3"].value)
        self.assertNotIn("en_progreso", libro["Criterios"]["B3"].value)

    def test_las_fechas_no_traen_microsegundos(self):
        libro = self.abrir("tareas", [], columnas=["fecha_creacion"])
        valor = libro["Reporte"]["A7"].value
        self.assertEqual(valor.microsecond, 0)

    def test_hoja_de_criterios(self):
        libro = self.abrir("usuarios", [crit("perfil", valor="estudiante")])
        self.assertEqual(libro.sheetnames, ["Reporte", "Criterios"])
        self.assertIn("Estudiante", libro["Criterios"]["B3"].value)

    def test_texto_peligroso_no_es_formula(self):
        Usuario.objects.create_user("inyeccion@prueba.com", CLAVE, first_name='=HYPERLINK("http://robo.example")', last_name="Usuario")
        libro = self.abrir("usuarios", [crit("email", "igual", "inyeccion@prueba.com")], columnas=["first_name"])
        celda = libro["Reporte"]["A7"]
        self.assertEqual(celda.data_type, "s")
        self.assertTrue(str(celda.value).startswith("'="))

    def test_limite_de_filas_se_avisa(self):
        with mock.patch.object(r, "MAX_FILAS_EXPORTACION", 2):
            libro = self.abrir("usuarios", [], columnas=["email"])
        self.assertIn("se exportan los primeros 2", libro["Reporte"]["A4"].value)
        self.assertEqual(libro["Reporte"].max_row, 6 + 2)

    def test_valor_vacio_no_rompe(self):
        libro = self.abrir("tareas", [], columnas=["asignado_a__email"])
        self.assertIsNotNone(libro["Reporte"])


class PdfTests(DatosBase):
    def test_pdf_valido_con_cabecera_y_pie(self):
        contenido = r.exportar_pdf("usuarios", [crit("perfil", valor="estudiante")], "y", ["email", "perfil"], "Yohan")
        self.assertTrue(contenido.startswith(b"%PDF-"))
        self.assertIn(b"%%EOF", contenido[-64:])
        self.assertGreater(len(contenido), 1500)

    def test_pdf_sin_resultados_tambien_sale(self):
        contenido = r.exportar_pdf("usuarios", [crit("email", "igual", "nadie@ninguno.com")], "y", [], "Yohan")
        self.assertTrue(contenido.startswith(b"%PDF-"))

    def test_pdf_escapa_html_en_los_datos(self):
        Usuario.objects.create_user("html@prueba.com", CLAVE, first_name="<b>x</b>", last_name="Usuario")
        contenido = r.exportar_pdf("usuarios", [crit("email", "igual", "html@prueba.com")], "y", ["first_name"], "Yohan")
        self.assertTrue(contenido.startswith(b"%PDF-"))  # si no escapara, reportlab fallaría o el PDF sería inválido


class AccesoYRutasTests(DatosBase):
    def cliente(self, usuario=None):
        c = Client()
        if usuario:
            c.force_login(usuario)
        return c

    def test_solo_el_superusuario_ve_la_pagina(self):
        self.assertEqual(self.cliente(self.super).get(reverse("administracion:reportes")).status_code, 200)
        self.assertEqual(self.cliente(self.prof).get(reverse("administracion:reportes")).status_code, 403)
        self.assertEqual(self.cliente().get(reverse("administracion:reportes")).status_code, 302)

    def test_solo_el_superusuario_exporta(self):
        url = reverse("administracion:reportes_exportar", args=["xlsx"])
        self.assertEqual(self.cliente(self.est).get(url).status_code, 403)
        self.assertEqual(self.cliente().get(url).status_code, 302)

    def test_vista_previa_con_criterios_multiples(self):
        r_ = self.cliente(self.super).get(reverse("administracion:reportes"), {
            "tabla": "usuarios", "logica": "y", "ver": "1",
            "c1_campo": "perfil", "c1_op": "igual", "c1_valor": "estudiante",
            "c2_campo": "is_active", "c2_op": "igual", "c2_valor": "no",
            "columnas": ["email", "is_active"]})
        self.assertEqual(r_.status_code, 200)
        self.assertEqual(r_.context["total"], 1)  # Beto: estudiante e inactivo
        self.assertContains(r_, "est2@prueba.com")

    def test_criterio_invalido_muestra_mensaje_y_no_rompe(self):
        r_ = self.cliente(self.super).get(reverse("administracion:reportes"), {"tabla": "usuarios", "ver": "1", "c1_campo": "password", "c1_valor": "x"}, follow=True)
        self.assertEqual(r_.status_code, 200)
        self.assertContains(r_, "no se puede filtrar")

    def test_exportar_excel_descarga_el_archivo(self):
        r_ = self.cliente(self.super).get(reverse("administracion:reportes_exportar", args=["xlsx"]), {"tabla": "tareas", "c1_campo": "estado", "c1_valor": "hecha"})
        self.assertEqual(r_.status_code, 200)
        self.assertIn("spreadsheetml", r_["Content-Type"])
        self.assertIn('filename="reporte_tareas_', r_["Content-Disposition"])
        self.assertEqual(load_workbook(io.BytesIO(r_.content))["Reporte"].max_row, 6 + 1)

    def test_exportar_pdf_descarga_el_archivo(self):
        r_ = self.cliente(self.super).get(reverse("administracion:reportes_exportar", args=["pdf"]), {"tabla": "proyectos"})
        self.assertEqual(r_["Content-Type"], "application/pdf")
        self.assertTrue(r_.content.startswith(b"%PDF-"))

    def test_formato_inventado_se_rechaza(self):
        self.assertEqual(self.cliente(self.super).get("/administracion/reportes/exportar/exe/").status_code, 400)

    def test_exportar_con_error_vuelve_a_la_pagina_con_mensaje(self):
        r_ = self.cliente(self.super).get(reverse("administracion:reportes_exportar", args=["xlsx"]), {"tabla": "usuarios", "c1_campo": "email", "c1_op": "entre", "c1_valor": "x", "c1_valor2": "y"})
        self.assertEqual(r_.status_code, 302)
        self.assertIn("/administracion/reportes/", r_["Location"])

    def test_el_boton_de_reportes_aparece_en_administracion(self):
        self.assertContains(self.cliente(self.super).get(reverse("administracion:inicio")), reverse("administracion:reportes"))

    def test_el_reporte_no_muestra_secretos_en_ninguna_salida(self):
        r_ = self.cliente(self.super).get(reverse("administracion:reportes"), {"tabla": "usuarios", "ver": "1", "columnas": ["email", "password"]})
        self.assertNotContains(r_, self.est.password)
        self.assertNotContains(r_, "pbkdf2_sha256")
