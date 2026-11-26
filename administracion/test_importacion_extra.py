"""Carga masiva: formatos reales de archivo y casos límite."""

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from administracion import importacion as imp
from cuentas.models import Usuario
from dashboard.models import Proyecto, ProyectoMiembro

CLAVE = "Clave$egura2026"
CAB_U = "email,nombre,apellido,perfil,cargo,telefono"
CAB_P = "nombre,descripcion,creado_por_email,finalidad,metodologia,modalidad,visibilidad,estado,fecha_inicio,fecha_fin,tecnologia,repositorio_url"


def u(*filas, cab=CAB_U, fin="\n"):
    return (cab + fin + fin.join(filas) + fin).encode("utf-8")


class ImportacionExtraTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.super = Usuario.objects.create_superuser("super@prueba.com", CLAVE, first_name="Super", last_name="Uno")
        cls.prof = Usuario.objects.create_user("prof@prueba.com", CLAVE, first_name="Carla", last_name="Mora", perfil="profesor")

    def test_archivo_con_saltos_de_linea_windows(self):
        r = imp.importar("usuarios", u("a1@prueba.com,Ana,Ruiz,estudiante,,", "a2@prueba.com,Beto,Luna,profesional,,", fin="\r\n"))
        self.assertEqual(r.creados, 2)

    def test_orden_de_columnas_distinto(self):
        r = imp.importar("usuarios", u("Ana,Ruiz,b1@prueba.com,estudiante,,", cab="nombre,apellido,email,perfil,cargo,telefono"))
        self.assertEqual(Usuario.objects.get(email="b1@prueba.com").first_name, "Ana")
        self.assertEqual(r.creados, 1)

    def test_columnas_extra_se_ignoran(self):
        r = imp.importar("usuarios", u("c1@prueba.com,Ana,Ruiz,estudiante,,,notas,sin_sentido", cab=CAB_U + ",notas,sin_sentido"))
        self.assertEqual(r.creados, 1)

    def test_espacios_alrededor_se_recortan(self):
        imp.importar("usuarios", u("  d1@prueba.com ,  Ana  , Ruiz ,estudiante,,"))
        usuario = Usuario.objects.get(email="d1@prueba.com")
        self.assertEqual((usuario.first_name, usuario.last_name), ("Ana", "Ruiz"))

    def test_encabezados_en_mayusculas(self):
        r = imp.importar("usuarios", u("e1@prueba.com,Ana,Ruiz,estudiante,,", cab="EMAIL,NOMBRE,APELLIDO,PERFIL,CARGO,TELEFONO"))
        self.assertEqual(r.creados, 1)

    def test_perfil_en_mayusculas_se_rechaza(self):
        r = imp.validar("usuarios", u("f1@prueba.com,Ana,Ruiz,ESTUDIANTE,,"))
        self.assertTrue(r.errores)

    def test_campos_opcionales_vacios_son_validos(self):
        r = imp.validar("usuarios", u("g1@prueba.com,Ana,Ruiz,estudiante,,"))
        self.assertFalse(r.errores)

    def test_tilde_y_enie_se_guardan(self):
        imp.importar("usuarios", u("h1@prueba.com,Peñaranda,Ñuñez,estudiante,,"))
        self.assertEqual(Usuario.objects.get(email="h1@prueba.com").last_name, "Ñuñez")

    def test_quinientas_filas_validas_se_importan_completas(self):
        filas = [f"lote{i}@prueba.com,Nombre{i},Apellido{i},estudiante,," for i in range(500)]
        r = imp.importar("usuarios", u(*filas))
        self.assertEqual(r.creados, 500)

    def test_solo_encabezado_sin_filas(self):
        with self.assertRaisesMessage(imp.ErrorImportacion, "no tiene filas"):
            imp.leer_csv((CAB_U + "\n").encode(), "usuarios")

    def test_proyecto_con_creador_en_mayusculas_se_importa(self):
        fila = "Notas,Descripción,PROF@PRUEBA.COM,educativo,kanban,individual,privado,planificacion,,,Django,"
        r = imp.importar("proyectos", (CAB_P + "\n" + fila + "\n").encode("utf-8"))
        self.assertEqual(r.creados, 1)
        self.assertEqual(Proyecto.objects.get(nombre="Notas").creado_por, self.prof)

    def test_proyecto_sin_fechas_es_valido(self):
        fila = "Sin fechas,Descripción,prof@prueba.com,otro,scrum,individual,privado,planificacion,,,,"
        self.assertFalse(imp.validar("proyectos", (CAB_P + "\n" + fila + "\n").encode("utf-8")).errores)

    def test_la_pantalla_importa_proyectos_y_crea_al_lider(self):
        c = Client()
        c.force_login(self.super)
        fila = "Pantalla,Descripción,prof@prueba.com,educativo,kanban,individual,privado,planificacion,,,,"
        archivo = SimpleUploadedFile("p.csv", (CAB_P + "\n" + fila + "\n").encode("utf-8"), content_type="text/csv")
        c.post(reverse("administracion:importar"), {"tipo": "proyectos", "accion": "importar", "archivo": archivo})
        proyecto = Proyecto.objects.get(nombre="Pantalla")
        self.assertEqual(ProyectoMiembro.objects.get(proyecto=proyecto).rol, "lider")

    def test_plantilla_de_proyectos_tiene_todas_las_columnas(self):
        texto = imp.plantilla("proyectos").decode("utf-8-sig").splitlines()[0]
        self.assertEqual(texto.split(","), imp.COLUMNAS["proyectos"])
