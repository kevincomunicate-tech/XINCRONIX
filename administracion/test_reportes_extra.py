"""Reportes: más combinaciones de filtros, exportaciones y casos límite."""

import datetime as dt
import io

from django.test import TestCase
from django.utils import timezone
from openpyxl import load_workbook

from administracion import reportes as r
from cuentas.models import Usuario
from dashboard.models import InvitacionProyecto, Proyecto, ProyectoMiembro, Tarea

CLAVE = "Clave$egura2026"


def crit(campo, op="igual", valor="", valor2=""):
    return {"campo": campo, "operador": op, "valor": valor, "valor2": valor2}


class ReportesExtraTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ana = Usuario.objects.create_user("ana@prueba.com", CLAVE, first_name="Ana", last_name="Ruiz", perfil="estudiante")
        cls.beto = Usuario.objects.create_user("beto@prueba.com", CLAVE, first_name="Beto", last_name="Luna", perfil="profesor")
        cls.p1 = Proyecto.objects.create(nombre="Tienda", descripcion="d", creado_por=cls.ana, estado="en_progreso", modalidad="grupal")
        cls.p2 = Proyecto.objects.create(nombre="Notas", descripcion="d", creado_por=cls.beto, estado="planificacion")
        ProyectoMiembro.objects.create(proyecto=cls.p1, usuario=cls.ana, rol="lider")
        ProyectoMiembro.objects.create(proyecto=cls.p1, usuario=cls.beto, rol="lector")
        ProyectoMiembro.objects.create(proyecto=cls.p2, usuario=cls.beto, rol="lider")
        Tarea.objects.create(titulo="Carrito", proyecto=cls.p1, estado="hecha", creado_por=cls.ana, asignado_a=cls.ana)
        Tarea.objects.create(titulo="Pagos", proyecto=cls.p1, estado="por_hacer", creado_por=cls.ana)
        InvitacionProyecto.objects.create(proyecto=cls.p1, email="x@prueba.com", rol="lector", creado_por=cls.ana,
                                          vence_en=timezone.now() + dt.timedelta(days=3))

    def total(self, clave, criterios, logica="y"):
        return r.filas(clave, criterios, logica)[2]

    def test_cada_tabla_se_exporta_a_excel_con_columnas_por_defecto(self):
        for clave in r.CATALOGO:
            with self.subTest(tabla=clave):
                libro = load_workbook(io.BytesIO(r.exportar_excel(clave, [], "y", [], "Yohan")))
                self.assertGreaterEqual(libro["Reporte"].max_row, 6)

    def test_cada_tabla_se_exporta_a_pdf(self):
        for clave in r.CATALOGO:
            with self.subTest(tabla=clave):
                self.assertTrue(r.exportar_pdf(clave, [], "y", [], "Yohan").startswith(b"%PDF-"))

    def test_fecha_de_registro_que_incluye_hoy(self):
        hoy = timezone.localdate().isoformat()
        self.assertEqual(self.total("usuarios", [crit("date_joined", "entre", hoy, hoy)]), Usuario.objects.count())

    def test_distinto_de_estado(self):
        self.assertEqual(self.total("proyectos", [crit("estado", "distinto", "planificacion")]), 1)

    def test_o_suma_los_dos_conjuntos(self):
        cr = [crit("nombre", "igual", "Tienda"), crit("nombre", "igual", "Notas")]
        self.assertEqual(self.total("proyectos", cr, logica="o"), 2)

    def test_y_con_criterios_contradictorios_da_cero_sin_error(self):
        cr = [crit("estado", "igual", "planificacion"), crit("estado", "igual", "en_progreso")]
        self.assertEqual(self.total("proyectos", cr), 0)

    def test_el_orden_de_columnas_se_respeta_en_excel(self):
        libro = load_workbook(io.BytesIO(r.exportar_excel("proyectos", [], "y", ["estado", "nombre"], "Yohan")))
        self.assertEqual([libro["Reporte"].cell(6, i).value for i in (1, 2)], ["Estado", "Proyecto"])

    def test_booleanos_se_muestran_como_si_o_no(self):
        libro = load_workbook(io.BytesIO(r.exportar_excel("usuarios", [crit("email", "igual", "ana@prueba.com")], "y", ["is_active"], "Yohan")))
        self.assertEqual(libro["Reporte"]["A7"].value, "Sí")

    def test_limite_de_filas_en_la_consulta(self):
        _, datos, total = r.filas("usuarios", [], limite=1)
        self.assertEqual(len(datos), 1)
        self.assertEqual(total, Usuario.objects.count())

    def test_integrantes_por_nombre_de_proyecto(self):
        self.assertEqual(self.total("integrantes", [crit("proyecto__nombre", "contiene", "tien")]), 2)

    def test_operador_que_no_aplica_a_un_campo_de_opciones(self):
        with self.assertRaises(r.ErrorReporte):
            r.construir("proyectos", [crit("estado", "contiene", "prog")])
