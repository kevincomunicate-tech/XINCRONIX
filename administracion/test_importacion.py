"""Carga masiva: validación fila por fila, todo o nada, plantillas, permisos y comando."""

from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import Client, TestCase
from django.urls import reverse

from administracion import importacion as imp
from cuentas.models import Usuario
from dashboard.models import Proyecto

CLAVE = "Clave$egura2026"
CABECERA_USUARIOS = "email,nombre,apellido,perfil,cargo,telefono\n"
CABECERA_PROYECTOS = ("nombre,descripcion,creado_por_email,finalidad,metodologia,modalidad,visibilidad,estado,"
                      "fecha_inicio,fecha_fin,tecnologia,repositorio_url\n")


def csv_usuarios(*filas):
    return (CABECERA_USUARIOS + "\n".join(filas) + "\n").encode("utf-8")


def csv_proyectos(*filas):
    return (CABECERA_PROYECTOS + "\n".join(filas) + "\n").encode("utf-8")


class ValidacionUsuariosTests(TestCase):
    def setUp(self):
        self.existente = Usuario.objects.create_user("ya@prueba.com", CLAVE, first_name="Ya", last_name="Existe")

    def test_archivo_valido_se_importa_completo(self):
        r = imp.importar("usuarios", csv_usuarios("ana@prueba.com,Ana,Ruiz,estudiante,,", "beto@prueba.com,Beto,Luna,profesor,Coordinador,300"))
        self.assertEqual(r.creados, 2)
        self.assertFalse(r.errores)
        beto = Usuario.objects.get(email="beto@prueba.com")
        self.assertEqual((beto.first_name, beto.last_name, beto.perfil, beto.cargo), ("Beto", "Luna", "profesor", "Coordinador"))

    def test_importacion_usa_el_rol_global_e_impide_crear_admin(self):
        base = b"email,nombre,apellido,rol\n"
        resultado = imp.importar("usuarios", base + b"ana@prueba.com,Ana,Ruiz,supervisor\n")
        self.assertEqual(resultado.creados, 1)
        self.assertEqual(Usuario.objects.get(email="ana@prueba.com").rol, Usuario.Rol.SUPERVISOR)
        resultado = imp.importar("usuarios", base + b"admin@prueba.com,Ana,Ruiz,admin\n")
        self.assertTrue(resultado.errores)
        self.assertFalse(Usuario.objects.filter(email="admin@prueba.com").exists())

    def test_los_importados_no_tienen_contrasena(self):
        imp.importar("usuarios", csv_usuarios("ana@prueba.com,Ana,Ruiz,estudiante,,"))
        self.assertFalse(Usuario.objects.get(email="ana@prueba.com").has_usable_password())

    def test_campo_obligatorio_vacio_se_reporta(self):
        r = imp.validar("usuarios", csv_usuarios("ana@prueba.com,,Ruiz,estudiante,,"))
        self.assertEqual(r.errores, [(2, "«nombre» es obligatorio.")])

    def test_correo_invalido(self):
        r = imp.validar("usuarios", csv_usuarios("no-es-correo,Ana,Ruiz,estudiante,,"))
        self.assertTrue(any("no es un correo válido" in m for _, m in r.errores))

    def test_perfil_inexistente(self):
        r = imp.validar("usuarios", csv_usuarios("ana@prueba.com,Ana,Ruiz,administrador,,"))
        self.assertTrue(any("no existe" in m for _, m in r.errores))

    def test_correo_ya_registrado_sin_importar_mayusculas(self):
        r = imp.validar("usuarios", csv_usuarios("YA@prueba.com,Otro,Nombre,estudiante,,"))
        self.assertTrue(any("ya existe" in m for _, m in r.errores))

    def test_correo_repetido_dentro_del_archivo(self):
        r = imp.validar("usuarios", csv_usuarios("ana@prueba.com,Ana,Ruiz,estudiante,,", "ANA@prueba.com,Ana,Dos,estudiante,,"))
        self.assertTrue(any("más de una vez" in m for _, m in r.errores))

    def test_todo_o_nada_si_una_fila_falla_no_se_guarda_ninguna(self):
        antes = Usuario.objects.count()
        r = imp.importar("usuarios", csv_usuarios("ana@prueba.com,Ana,Ruiz,estudiante,,", "mala,Beto,Luna,estudiante,,"))
        self.assertTrue(r.errores)
        self.assertEqual(Usuario.objects.count(), antes)

    def test_validar_no_guarda_nada(self):
        antes = Usuario.objects.count()
        imp.validar("usuarios", csv_usuarios("ana@prueba.com,Ana,Ruiz,estudiante,,"))
        self.assertEqual(Usuario.objects.count(), antes)

    def test_nadie_se_importa_como_superusuario(self):
        imp.importar("usuarios", csv_usuarios("root@prueba.com,Root,Admin,profesor,,"))
        self.assertFalse(Usuario.objects.get(email="root@prueba.com").is_superuser)


class ValidacionProyectosTests(TestCase):
    def setUp(self):
        self.creador = Usuario.objects.create_user("prof@prueba.com", CLAVE, first_name="Carla", last_name="Mora", perfil="profesor")

    def fila(self, **cambios):
        base = {"nombre": "App de notas", "descripcion": "Notas de clase", "creado_por_email": "prof@prueba.com",
                "finalidad": "educativo", "metodologia": "kanban", "modalidad": "individual", "visibilidad": "privado",
                "estado": "planificacion", "fecha_inicio": "2026-03-01", "fecha_fin": "2026-06-30", "tecnologia": "Django", "repositorio_url": ""}
        base.update(cambios)
        return ",".join(base[c] for c in ["nombre", "descripcion", "creado_por_email", "finalidad", "metodologia", "modalidad",
                                          "visibilidad", "estado", "fecha_inicio", "fecha_fin", "tecnologia", "repositorio_url"])

    def test_proyecto_valido_queda_con_su_creador_como_lider(self):
        r = imp.importar("proyectos", csv_proyectos(self.fila()))
        self.assertEqual(r.creados, 1)
        p = Proyecto.objects.get(nombre="App de notas")
        self.assertEqual(p.creado_por, self.creador)
        self.assertEqual(p.proyectomiembro_set.get().rol, "lider")

    def test_creador_inexistente(self):
        r = imp.validar("proyectos", csv_proyectos(self.fila(creado_por_email="nadie@prueba.com")))
        self.assertTrue(any("no existe en la plataforma" in m for _, m in r.errores))

    def test_fechas_al_reves(self):
        r = imp.validar("proyectos", csv_proyectos(self.fila(fecha_inicio="2026-07-01", fecha_fin="2026-06-01")))
        self.assertTrue(r.errores)

    def test_fecha_con_formato_malo(self):
        r = imp.validar("proyectos", csv_proyectos(self.fila(fecha_inicio="01/03/2026")))
        self.assertTrue(any("no es una fecha válida" in m for _, m in r.errores))

    def test_opcion_inventada_en_estado_o_finalidad(self):
        r = imp.validar("proyectos", csv_proyectos(self.fila(estado="volando")))
        self.assertTrue(r.errores)
        r = imp.validar("proyectos", csv_proyectos(self.fila(finalidad="militar")))
        self.assertTrue(r.errores)

    def test_individual_no_admite_integrantes_al_importar(self):
        # La regla de integridad se aplica igual que en la web: la carga solo crea proyectos individuales.
        r = imp.importar("proyectos", csv_proyectos(self.fila(modalidad="grupal")))
        self.assertEqual(r.creados, 1)
        self.assertEqual(Proyecto.objects.get(nombre="App de notas").modalidad, "grupal")

    def test_descripcion_vacia_se_rechaza(self):
        r = imp.validar("proyectos", csv_proyectos(self.fila(descripcion="")))
        self.assertTrue(any("descripcion" in m for _, m in r.errores))

    def test_una_mala_no_arrastra_a_las_buenas(self):
        antes = Proyecto.objects.count()
        imp.importar("proyectos", csv_proyectos(self.fila(), self.fila(nombre="Mala", estado="raro")))
        self.assertEqual(Proyecto.objects.count(), antes)


class FormatoDelArchivoTests(TestCase):
    def test_archivo_vacio(self):
        with self.assertRaisesMessage(imp.ErrorImportacion, "vacío"):
            imp.leer_csv(b"", "usuarios")

    def test_faltan_columnas(self):
        with self.assertRaisesMessage(imp.ErrorImportacion, "Faltan columnas"):
            imp.leer_csv(b"email,nombre\nana@prueba.com,Ana\n", "usuarios")

    def test_no_es_utf8(self):
        with self.assertRaisesMessage(imp.ErrorImportacion, "UTF-8"):
            imp.leer_csv(CABECERA_USUARIOS.encode() + b"ana@prueba.com,\xff\xfe,Ruiz,estudiante,,\n", "usuarios")

    def test_sin_filas_de_datos(self):
        with self.assertRaisesMessage(imp.ErrorImportacion, "no tiene filas"):
            imp.leer_csv(CABECERA_USUARIOS.encode(), "usuarios")

    def test_archivo_demasiado_grande(self):
        with self.assertRaisesMessage(imp.ErrorImportacion, "2 MB"):
            imp.leer_csv(b"x" * (imp.MAX_BYTES + 1), "usuarios")

    def test_demasiadas_filas(self):
        filas = "\n".join(f"u{i}@prueba.com,A,B,estudiante,," for i in range(imp.MAX_FILAS + 1))
        with self.assertRaisesMessage(imp.ErrorImportacion, "máximo"):
            imp.leer_csv((CABECERA_USUARIOS + filas).encode(), "usuarios")

    def test_separador_punto_y_coma_y_bom(self):
        contenido = ("﻿" + "email;nombre;apellido;perfil;cargo;telefono\n" + "ana@prueba.com;Ana;Ruiz;estudiante;;\n").encode("utf-8")
        r = imp.importar("usuarios", contenido)
        self.assertEqual(r.creados, 1)

    def test_lineas_en_blanco_se_ignoran(self):
        r = imp.validar("usuarios", csv_usuarios("ana@prueba.com,Ana,Ruiz,estudiante,,", "", "  ,,,,,"))
        self.assertEqual(r.total, 1)

    def test_tipo_no_valido(self):
        with self.assertRaisesMessage(imp.ErrorImportacion, "no válido"):
            imp.leer_csv(b"x", "sesiones")

    def test_valores_con_formula_se_guardan_como_texto(self):
        imp.importar("usuarios", csv_usuarios('ana@prueba.com,"=HYPERLINK(""http://robo"")",Ruiz,estudiante,,'))
        self.assertEqual(Usuario.objects.get(email="ana@prueba.com").first_name, '=HYPERLINK("http://robo")')


class PantallaYPermisosTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.super = Usuario.objects.create_superuser("super@prueba.com", CLAVE, first_name="Super", last_name="Uno")
        cls.normal = Usuario.objects.create_user("n@prueba.com", CLAVE, first_name="Normal", last_name="Uno", perfil="estudiante")

    def archivo(self, contenido):
        from django.core.files.uploadedfile import SimpleUploadedFile
        return SimpleUploadedFile("datos.csv", contenido, content_type="text/csv")

    def test_solo_el_superusuario_ve_la_pantalla(self):
        self.assertEqual(Client().get(reverse("administracion:importar")).status_code, 302)
        c = Client()
        c.force_login(self.normal)
        self.assertEqual(c.get(reverse("administracion:importar")).status_code, 403)
        c.force_login(self.super)
        self.assertEqual(c.get(reverse("administracion:importar")).status_code, 200)

    def test_vista_previa_no_guarda(self):
        c = Client()
        c.force_login(self.super)
        antes = Usuario.objects.count()
        r = c.post(reverse("administracion:importar"), {"tipo": "usuarios", "accion": "validar",
                                                        "archivo": self.archivo(csv_usuarios("ana@prueba.com,Ana,Ruiz,estudiante,,"))})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Usuario.objects.count(), antes)
        self.assertContains(r, "Todas las filas son válidas")

    def test_importar_desde_la_pantalla(self):
        c = Client()
        c.force_login(self.super)
        c.post(reverse("administracion:importar"), {"tipo": "usuarios", "accion": "importar",
                                                  "archivo": self.archivo(csv_usuarios("ana@prueba.com,Ana,Ruiz,estudiante,,"))})
        self.assertTrue(Usuario.objects.filter(email="ana@prueba.com").exists())

    def test_la_pantalla_muestra_los_errores_por_linea(self):
        c = Client()
        c.force_login(self.super)
        r = c.post(reverse("administracion:importar"), {"tipo": "usuarios", "accion": "validar",
                                                        "archivo": self.archivo(csv_usuarios("mala,Ana,Ruiz,estudiante,,"))})
        self.assertContains(r, "no es un correo válido")
        self.assertContains(r, "<td>2</td>")

    def test_error_de_formato_no_rompe_la_pantalla(self):
        c = Client()
        c.force_login(self.super)
        r = c.post(reverse("administracion:importar"), {"tipo": "usuarios", "accion": "validar", "archivo": self.archivo(b"")})
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "vacío")

    def test_plantillas_se_descargan(self):
        c = Client()
        c.force_login(self.super)
        for tipo in ("usuarios", "proyectos"):
            r = c.get(reverse("administracion:importar_plantilla", args=[tipo]))
            self.assertEqual(r.status_code, 200)
            self.assertIn(f"plantilla_{tipo}.csv", r["Content-Disposition"])
            self.assertTrue(r.content.decode("utf-8-sig").startswith(",".join(imp.COLUMNAS[tipo][:2])))
        self.assertEqual(c.get("/administracion/importar/plantilla/sesiones/").status_code, 400)

    def test_normal_no_descarga_plantillas(self):
        c = Client()
        c.force_login(self.normal)
        self.assertEqual(c.get(reverse("administracion:importar_plantilla", args=["usuarios"])).status_code, 403)

    def test_el_boton_aparece_en_administracion(self):
        c = Client()
        c.force_login(self.super)
        self.assertContains(c.get(reverse("administracion:inicio")), reverse("administracion:importar"))


class ComandoTests(TestCase):
    def escribir(self, contenido):
        import tempfile, os
        ruta = os.path.join(tempfile.mkdtemp(), "datos.csv")
        with open(ruta, "wb") as f:
            f.write(contenido)
        return ruta

    def test_comando_importa(self):
        ruta = self.escribir(csv_usuarios("ana@prueba.com,Ana,Ruiz,estudiante,,"))
        call_command("importar_csv", "usuarios", ruta, stdout=StringIO())
        self.assertTrue(Usuario.objects.filter(email="ana@prueba.com").exists())

    def test_comando_simular_no_guarda(self):
        ruta = self.escribir(csv_usuarios("ana@prueba.com,Ana,Ruiz,estudiante,,"))
        salida = StringIO()
        call_command("importar_csv", "usuarios", ruta, "--simular", stdout=salida)
        self.assertIn("No se guardó nada", salida.getvalue())
        self.assertFalse(Usuario.objects.filter(email="ana@prueba.com").exists())

    def test_comando_falla_con_errores_y_no_guarda(self):
        ruta = self.escribir(csv_usuarios("ana@prueba.com,Ana,Ruiz,estudiante,,", "mala,B,C,estudiante,,"))
        with self.assertRaises(CommandError):
            call_command("importar_csv", "usuarios", ruta, stdout=StringIO())
        self.assertFalse(Usuario.objects.filter(email="ana@prueba.com").exists())

    def test_comando_archivo_inexistente(self):
        with self.assertRaises(CommandError):
            call_command("importar_csv", "usuarios", "/no/existe.csv", stdout=StringIO())
