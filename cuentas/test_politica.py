"""Pruebas de la política de accesos (config/politica_accesos.json)."""

import copy
import json
import tempfile
from io import StringIO
from pathlib import Path

from django.conf import settings
from django.contrib.admin.sites import AdminSite
from django.core.management import call_command
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse

from administracion.forms import AsignacionForm
from cuentas.admin import UsuarioAdmin
from cuentas.checks import revisar_politica_accesos
from cuentas.models import Empresa, Rol, Usuario
from cuentas.politica import SUPERADMINISTRADOR, PoliticaInvalida, leer_politica, obtener_politica, validar

CORREO_SUPER = "cuellaryohan100@gmail.com"
CLAVE = "Clave$egura2026"


def politica_original():
    return json.loads(Path(settings.POLITICA_ACCESOS).read_text(encoding="utf-8"))


class ValidacionJsonTests(TestCase):
    def test_el_json_del_proyecto_es_valido(self):
        self.assertEqual(validar(politica_original()), [])
        self.assertEqual(revisar_politica_accesos(None), [])

    def test_detecta_errores(self):
        datos = copy.deepcopy(politica_original())
        datos["registro"]["rol"] = "jefe"
        datos["perfiles"]["usuario"]["puede_asignar"] = ["dios"]
        del datos["perfiles"]["manager"]
        datos["rutas_restringidas"]["/secreto/"] = ["nadie"]
        errores = validar(datos)
        self.assertIn("'registro.rol' es 'jefe', que no existe en 'roles'.", errores)
        self.assertIn("Falta el perfil 'manager' en 'perfiles'.", errores)
        self.assertIn("El perfil 'usuario' puede asignar 'dios', que no existe en 'roles'.", errores)
        self.assertIn("La ruta '/secreto/' permite el perfil 'nadie', que no existe en 'perfiles'.", errores)

    def test_detecta_permisos_y_acciones_inventados(self):
        datos = copy.deepcopy(politica_original())
        datos["perfiles"]["usuario"]["acciones"].append("volar")
        datos["proyectos"]["por_relacion"]["editor"].append("borrar_todo")
        datos["proyectos"]["por_relacion"]["amigo"] = ["ver"]
        datos["empresas"]["por_perfil"]["admin"]["alcance"] = "galaxia"
        errores = " ".join(validar(datos))
        self.assertIn("la acción 'volar', que no existe", errores)
        self.assertIn("'proyectos.por_relacion.editor' tiene el permiso 'borrar_todo'", errores)
        self.assertIn("usa la relación 'amigo', que no existe", errores)
        self.assertIn("'empresas.por_perfil.admin.alcance' debe ser uno de", errores)

    def test_json_mal_escrito(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as archivo:
            archivo.write('{"version": 1,')  # falta cerrar
        with self.assertRaises(PoliticaInvalida):
            leer_politica(archivo.name)
        with override_settings(POLITICA_ACCESOS=archivo.name):
            self.assertEqual(revisar_politica_accesos(None)[0].id, "cuentas.E001")


class Base(TestCase):
    def setUp(self):
        obtener_politica.cache_clear()
        self.empresa = Empresa.objects.create(nombre="Acme")
        self.super = Usuario.objects.create_superuser(CORREO_SUPER, CLAVE, first_name="Yohan")
        self.normal = Usuario.objects.create_user("ana@acme.com", CLAVE, empresa=self.empresa)
        self.admin_empresa = Usuario.objects.create_user(
            "jefe@acme.com", CLAVE, empresa=self.empresa, rol=Rol.objects.get(codigo=Rol.ADMIN)
        )


class PerfilTests(Base):
    def test_permisos_salen_del_json(self):
        politica = obtener_politica()
        self.assertTrue(politica.puede(self.normal, "crear_empresa"))
        self.assertFalse(politica.puede(self.super, "eliminar_cuenta"))
        self.assertEqual(politica.permisos_empresa(self.normal, self.empresa), {"ver", "metricas"})  # integrante
        self.assertEqual(politica.permisos_empresa(self.admin_empresa, self.empresa), {"ver", "editar", "metricas"})

    def test_perfiles(self):
        politica = obtener_politica()
        self.assertEqual(politica.perfil_de(self.super), SUPERADMINISTRADOR)
        self.assertEqual(politica.perfil_de(self.normal), "usuario")
        self.assertEqual(politica.perfil_de(self.admin_empresa), "admin")

    def test_el_correo_solo_no_basta(self):
        # Mismo correo de la lista pero sin ser superusuario: NO es superadministrador
        self.super.is_superuser = False
        self.assertNotEqual(obtener_politica().perfil_de(self.super), SUPERADMINISTRADOR)

    def test_solo_el_superadministrador_asigna_roles(self):
        politica = obtener_politica()
        self.assertTrue(politica.puede_asignar(self.super, Rol.ADMIN))
        self.assertFalse(politica.puede_asignar(self.admin_empresa, Rol.ADMIN))
        self.assertFalse(politica.puede_asignar(self.normal, Rol.MANAGER))


class EnrutamientoTests(Base):
    def entrar(self, correo, **extra):
        return self.client.post(reverse("login"), {"username": correo, "password": CLAVE, **extra})

    def test_cada_perfil_entra_a_su_inicio(self):
        self.assertRedirects(self.entrar(CORREO_SUPER), reverse("administracion:inicio"))
        self.client.post(reverse("logout"))
        self.assertRedirects(self.entrar("ana@acme.com"), reverse("panel"))

    def test_respeta_la_pagina_de_origen(self):
        r = self.entrar("ana@acme.com", next=reverse("tareas"))
        self.assertRedirects(r, reverse("tareas"))

    def test_registro_queda_como_usuario_normal(self):
        r = self.client.post(reverse("registro"), {"nombre": "Luis Pérez", "email": "luis@x.com", "password": CLAVE})
        self.assertRedirects(r, reverse("panel"))
        self.assertEqual(Usuario.objects.get(email="luis@x.com").rol.codigo, Rol.USUARIO)

    def test_administracion_protegida(self):
        url = reverse("administracion:inicio")
        self.assertRedirects(self.client.get(url), f"{reverse('login')}?next={url}")  # sin sesión
        self.client.force_login(self.normal)
        r = self.client.get(url)
        self.assertEqual(r.status_code, 403)                                    # usuario normal
        self.assertContains(r, "no está disponible para tu perfil", status_code=403)  # templates/403.html
        self.client.force_login(self.admin_empresa)
        self.assertEqual(self.client.get(url).status_code, 403)                 # admin de empresa
        self.client.force_login(self.super)
        self.assertEqual(self.client.get(url).status_code, 200)                 # superadministrador

    def test_menu_segun_perfil(self):
        self.client.force_login(self.super)
        self.assertContains(self.client.get(reverse("panel")), reverse("administracion:inicio"))
        self.client.force_login(self.normal)
        self.assertNotContains(self.client.get(reverse("panel")), reverse("administracion:inicio"))


class AsignacionTests(Base):
    def test_superadministrador_da_rol_administrador(self):
        self.client.force_login(self.super)
        url = reverse("administracion:editar_usuario", args=[self.normal.pk])
        rol_admin = Rol.objects.get(codigo=Rol.ADMIN)
        r = self.client.post(url, {"email": self.normal.email, "first_name": "Ana", "rol": rol_admin.pk,
                                   "empresa": self.empresa.pk, "is_active": "on"})
        self.assertRedirects(r, reverse("administracion:inicio"))
        self.normal.refresh_from_db()
        self.assertEqual(self.normal.rol, rol_admin)

    def test_nadie_mas_puede_dar_administrador(self):
        rol_admin = Rol.objects.get(codigo=Rol.ADMIN)
        form = AsignacionForm({"email": self.normal.email, "rol": rol_admin.pk, "is_active": "on"}, instance=self.normal, asignador=self.admin_empresa)
        self.assertFalse(form.is_valid())
        self.assertIn("rol", form.errors)

    def test_no_puede_editarse_a_si_mismo(self):
        self.client.force_login(self.super)
        r = self.client.get(reverse("administracion:editar_usuario", args=[self.super.pk]))
        self.assertEqual(r.status_code, 404)

    def test_admin_de_django_limita_los_roles(self):
        modelo_admin = UsuarioAdmin(Usuario, AdminSite())
        campo = Usuario._meta.get_field("rol")
        peticion = RequestFactory().get("/")
        peticion.user = self.admin_empresa
        self.assertEqual(modelo_admin.formfield_for_foreignkey(campo, peticion).queryset.count(), 0)
        self.assertIn("is_superuser", modelo_admin.get_readonly_fields(peticion))
        peticion.user = self.super
        self.assertEqual(modelo_admin.formfield_for_foreignkey(campo, peticion).queryset.count(), 4)  # los 4 roles del JSON
        self.assertNotIn("is_superuser", modelo_admin.get_readonly_fields(peticion))


class ComandoTests(Base):
    def correr(self, *args):
        salida = StringIO()
        call_command("aplicar_politica_roles", *args, stdout=salida)
        return salida.getvalue()

    def test_simular_no_cambia_nada(self):
        salida = self.correr("--simular", "--quitar-administradores")
        self.assertIn("SIMULACIÓN", salida)
        self.assertIn("jefe@acme.com: rol -> Usuario", salida)
        self.admin_empresa.refresh_from_db()
        self.assertEqual(self.admin_empresa.rol.codigo, Rol.ADMIN)

    def test_sin_bandera_respeta_los_administradores_asignados(self):
        self.correr()
        self.admin_empresa.refresh_from_db()
        self.assertEqual(self.admin_empresa.rol.codigo, Rol.ADMIN)

    def test_aplica_la_politica(self):
        self.correr("--quitar-administradores")
        self.admin_empresa.refresh_from_db()
        self.super.refresh_from_db()
        self.assertEqual(self.admin_empresa.rol.codigo, Rol.USUARIO)
        self.assertFalse(self.admin_empresa.is_staff or self.admin_empresa.is_superuser)
        self.assertEqual(self.super.rol.codigo, Rol.ADMIN)
        self.assertTrue(self.super.is_superuser and self.super.is_staff)

    def test_quita_superusuario_a_quien_no_esta_en_la_lista(self):
        intruso = Usuario.objects.create_superuser("otro@x.com", CLAVE)
        self.correr()
        intruso.refresh_from_db()
        self.assertFalse(intruso.is_superuser or intruso.is_staff)

    def test_se_puede_correr_varias_veces(self):
        self.correr()
        self.assertIn("Nada que cambiar", self.correr())
