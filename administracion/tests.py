"""CRUD de usuarios y empresas del superadministrador."""

from django.test import TestCase
from django.urls import reverse

from cuentas.models import Empresa, Rol, Usuario
from dashboard.models import Proyecto

CLAVE = "Clave$egura2026"


class Base(TestCase):
    def setUp(self):
        self.super = Usuario.objects.create_superuser("cuellaryohan100@gmail.com", CLAVE, first_name="Yohan")
        self.ana = Usuario.objects.create_user("ana@x.com", CLAVE, first_name="Ana")
        self.client.force_login(self.super)


class UsuariosCrudTests(Base):
    def test_crear_usuario_con_rol_y_empresa(self):
        acme = Empresa.objects.create(nombre="Acme")
        r = self.client.post(reverse("administracion:crear_usuario"), {
            "first_name": "Luis", "last_name": "Pérez", "email": "Luis@X.com", "password": CLAVE,
            "rol": Rol.objects.get(codigo=Rol.ADMIN).pk, "empresa": acme.pk, "is_active": "on",
        })
        self.assertRedirects(r, reverse("administracion:inicio"))
        luis = Usuario.objects.get(email="luis@x.com")
        self.assertEqual((luis.rol.codigo, luis.empresa), (Rol.ADMIN, acme))
        self.assertTrue(luis.check_password(CLAVE))

    def test_contrasena_debil_rechazada(self):
        r = self.client.post(reverse("administracion:crear_usuario"), {
            "first_name": "Luis", "email": "luis@x.com", "password": "12345678", "rol": Rol.objects.get(codigo=Rol.USUARIO).pk,
        })
        self.assertEqual(r.status_code, 200)
        self.assertFalse(Usuario.objects.filter(email="luis@x.com").exists())

    def test_eliminar_usuario(self):
        r = self.client.post(reverse("administracion:eliminar_usuario", args=[self.ana.pk]))
        self.assertRedirects(r, reverse("administracion:inicio"))
        self.assertFalse(Usuario.objects.filter(pk=self.ana.pk).exists())

    def test_superadministradores_intocables(self):
        for nombre in ("editar_usuario", "eliminar_usuario"):
            self.assertEqual(self.client.get(reverse(f"administracion:{nombre}", args=[self.super.pk])).status_code, 404)
        r = self.client.post(reverse("administracion:editar_usuario", args=[self.ana.pk]), {
            "email": "cuellaryohan100@gmail.com", "rol": Rol.objects.get(codigo=Rol.USUARIO).pk,
        })
        self.assertContains(r, "reservado para el superadministrador")


class EmpresasCrudTests(Base):
    def test_crear_empresa_vinculada_a_un_usuario(self):
        r = self.client.post(reverse("administracion:crear_empresa"), {"nombre": "Nekros", "nit": "", "propietario": self.ana.pk})
        empresa = Empresa.objects.get(nombre="Nekros")
        self.assertRedirects(r, reverse("administracion:empresa_detalle", args=[empresa.pk]))
        self.ana.refresh_from_db()
        self.assertEqual((empresa.propietario, self.ana.empresa, empresa.nit), (self.ana, empresa, None))

    def test_vincular_y_desvincular(self):
        empresa = Empresa.objects.create(nombre="Nekros")
        url = reverse("administracion:vincular_usuario", args=[empresa.pk])
        self.assertRedirects(self.client.post(url, {"usuario": self.ana.pk}), reverse("administracion:empresa_detalle", args=[empresa.pk]))
        self.ana.refresh_from_db()
        self.assertEqual(self.ana.empresa, empresa)
        self.client.post(reverse("administracion:desvincular_usuario", args=[empresa.pk, self.ana.pk]))
        self.ana.refresh_from_db()
        self.assertIsNone(self.ana.empresa)

    def test_no_se_puede_vincular_al_superadministrador(self):
        empresa = Empresa.objects.create(nombre="Nekros")
        r = self.client.post(reverse("administracion:vincular_usuario", args=[empresa.pk]), {"usuario": self.super.pk})
        self.assertEqual(r.status_code, 200)
        self.assertIn("usuario", r.context["vincular_form"].errors)

    def test_editar_y_eliminar_empresa(self):
        empresa = Empresa.objects.create(nombre="Nekros")
        self.ana.empresa = empresa
        self.ana.save()
        Proyecto.objects.create(nombre="P", empresa=empresa)
        self.client.post(reverse("administracion:editar_empresa", args=[empresa.pk]), {"nombre": "Nekros SAS", "sector": "tecnologia"})
        empresa.refresh_from_db()
        self.assertEqual((empresa.nombre, empresa.sector), ("Nekros SAS", "tecnologia"))
        self.assertContains(self.client.get(reverse("administracion:eliminar_empresa", args=[empresa.pk])), "conservan su cuenta")
        self.assertRedirects(self.client.post(reverse("administracion:eliminar_empresa", args=[empresa.pk])), reverse("administracion:empresas"))
        self.assertFalse(Empresa.objects.exists() or Proyecto.objects.exists())
        self.assertTrue(Usuario.objects.filter(pk=self.ana.pk, empresa__isnull=True).exists())

    def test_solo_el_superadministrador(self):
        self.client.force_login(self.ana)
        for url in (reverse("administracion:empresas"), reverse("administracion:crear_usuario")):
            self.assertEqual(self.client.get(url).status_code, 403)

    def test_menu_marca_solo_la_seccion_actual(self):
        r = self.client.get(reverse("administracion:empresas"))
        activos = [item["texto"] for item in r.context["menu_perfil"] if item["activo"]]
        self.assertEqual(activos, ["Empresas"])
