"""Reglas de superusuarios. Debe quedar siempre al menos UN superusuario ACTIVO.

Caja blanca: modelo, señales, borrados y cambios en lote, servicio.
Caja negra: lo que ve quien usa la web (mensajes, redirecciones, sesión)."""

from django.db import transaction
from django.test import Client, TestCase
from django.urls import reverse

from cuentas.models import SuperusuarioProtegido, Usuario
from cuentas.servicios import eliminar_cuenta

CLAVE = "Clave$egura2026"


def superusuarios_activos():
    return Usuario.objects.filter(is_superuser=True, is_active=True).count()


class CajaBlancaUltimoSuperusuarioTests(TestCase):
    def test_borrar_el_unico_superusuario_activo_se_bloquea(self):
        solo = Usuario.objects.create_superuser("solo@prueba.com", CLAVE, first_name="Prueba", last_name="Usuario")
        with self.assertRaises(SuperusuarioProtegido), transaction.atomic():
            solo.delete()
        self.assertEqual(superusuarios_activos(), 1)

    def test_borrar_uno_de_dos_si_queda_otro_activo(self):
        a = Usuario.objects.create_superuser("a@prueba.com", CLAVE, first_name="Prueba", last_name="Usuario")
        Usuario.objects.create_superuser("b@prueba.com", CLAVE, first_name="Prueba", last_name="Usuario")
        a.delete()
        self.assertEqual(superusuarios_activos(), 1)

    def test_un_superusuario_inactivo_no_cuenta_como_respaldo(self):
        # Hay dos superusuarios, pero uno está desactivado: el activo es el último.
        activo = Usuario.objects.create_superuser("activo@prueba.com", CLAVE, first_name="Prueba", last_name="Usuario")
        Usuario.objects.create_superuser("inactivo@prueba.com", CLAVE, is_active=False, first_name="Prueba", last_name="Usuario")
        with self.assertRaises(SuperusuarioProtegido), transaction.atomic():
            activo.delete()
        self.assertTrue(Usuario.objects.filter(pk=activo.pk).exists())

    def test_desactivar_el_ultimo_se_bloquea_al_guardar(self):
        solo = Usuario.objects.create_superuser("solo@prueba.com", CLAVE, first_name="Prueba", last_name="Usuario")
        solo.is_active = False
        with self.assertRaises(SuperusuarioProtegido):
            solo.save()
        self.assertEqual(superusuarios_activos(), 1)

    def test_quitar_el_permiso_al_ultimo_se_bloquea_al_guardar(self):
        solo = Usuario.objects.create_superuser("solo@prueba.com", CLAVE, first_name="Prueba", last_name="Usuario")
        solo.is_superuser = False
        with self.assertRaises(SuperusuarioProtegido):
            solo.save()
        solo.refresh_from_db()
        self.assertTrue(solo.is_superuser)

    def test_guardar_cambios_normales_del_ultimo_si_esta_permitido(self):
        solo = Usuario.objects.create_superuser("solo@prueba.com", CLAVE, first_name="Prueba", last_name="Usuario")
        solo.first_name = "Yohan"
        solo.save()
        solo.last_login = None
        solo.save(update_fields=["last_login"])  # lo que hace cada inicio de sesión
        self.assertEqual(Usuario.objects.get(pk=solo.pk).first_name, "Yohan")

    def test_crear_superusuarios_siempre_se_permite(self):
        Usuario.objects.create_superuser("a@prueba.com", CLAVE, first_name="Prueba", last_name="Usuario")
        Usuario.objects.create_superuser("b@prueba.com", CLAVE, first_name="Prueba", last_name="Usuario")
        self.assertEqual(superusuarios_activos(), 2)


class CajaBlancaLotesTests(TestCase):
    """Los borrados y cambios en lote pasan por UsuarioQuerySet, no por las señales."""

    def setUp(self):
        self.a = Usuario.objects.create_superuser("a@prueba.com", CLAVE, first_name="Prueba", last_name="Usuario")
        self.b = Usuario.objects.create_superuser("b@prueba.com", CLAVE, first_name="Prueba", last_name="Usuario")

    def test_borrar_los_dos_en_un_lote_se_bloquea_y_no_borra_nada(self):
        with self.assertRaises(SuperusuarioProtegido):
            Usuario.objects.filter(is_superuser=True).delete()
        self.assertEqual(superusuarios_activos(), 2)

    def test_borrar_un_superusuario_en_lote_si_queda_otro(self):
        Usuario.objects.filter(pk=self.a.pk).delete()
        self.assertEqual(superusuarios_activos(), 1)

    def test_desactivar_todos_en_lote_se_bloquea(self):
        with self.assertRaises(SuperusuarioProtegido):
            Usuario.objects.filter(is_superuser=True).update(is_active=False)
        self.assertEqual(superusuarios_activos(), 2)

    def test_quitar_el_permiso_a_todos_en_lote_se_bloquea(self):
        with self.assertRaises(SuperusuarioProtegido):
            Usuario.objects.filter(is_superuser=True).update(is_superuser=False)
        self.assertEqual(superusuarios_activos(), 2)

    def test_cambios_que_no_tocan_permisos_en_lote_si_se_permiten(self):
        Usuario.objects.filter(is_superuser=True).update(cargo="Director")
        self.assertEqual(Usuario.objects.filter(cargo="Director").count(), 2)

    def test_un_lote_que_no_incluye_superusuarios_no_se_bloquea(self):
        normal = Usuario.objects.create_user("n@prueba.com", CLAVE, first_name="Prueba", last_name="Usuario")
        Usuario.objects.filter(pk=normal.pk).update(is_active=False)
        normal.refresh_from_db()
        self.assertFalse(normal.is_active)


class CajaBlancaServicioTests(TestCase):
    def test_eliminar_cuenta_respeta_la_regla(self):
        solo = Usuario.objects.create_superuser("solo@prueba.com", CLAVE, first_name="Prueba", last_name="Usuario")
        with self.assertRaises(SuperusuarioProtegido):
            eliminar_cuenta(solo)
        self.assertTrue(Usuario.objects.filter(pk=solo.pk).exists())

    def test_eliminar_cuenta_normal_siempre_funciona(self):
        normal = Usuario.objects.create_user("n@prueba.com", CLAVE, first_name="Prueba", last_name="Usuario")
        Usuario.objects.create_superuser("solo@prueba.com", CLAVE, first_name="Prueba", last_name="Usuario")
        eliminar_cuenta(normal)
        self.assertFalse(Usuario.objects.filter(pk=normal.pk).exists())


class CajaNegraSuperusuariosTests(TestCase):
    def setUp(self):
        self.a = Usuario.objects.create_superuser("a@prueba.com", CLAVE, first_name="A", last_name="Usuario")
        self.b = Usuario.objects.create_superuser("b@prueba.com", CLAVE, first_name="B", last_name="Usuario")
        self.normal = Usuario.objects.create_user("n@prueba.com", CLAVE, perfil="estudiante", first_name="Prueba", last_name="Usuario")
        self.cliente = Client()
        self.cliente.force_login(self.a)

    def _datos(self, usuario, activo=True):
        datos = {"first_name": usuario.first_name, "last_name": usuario.last_name, "email": usuario.email,
                 "perfil": usuario.perfil, "cargo": "", "telefono": ""}
        if activo:
            datos["is_active"] = "on"
        return datos

    def test_admin_desactiva_a_otro_superusuario_si_queda_el_suyo(self):
        self.cliente.post(reverse("administracion:editar_usuario", args=[self.b.pk]), self._datos(self.b, activo=False))
        self.b.refresh_from_db()
        self.assertFalse(self.b.is_active)

    def test_admin_no_puede_desactivarse_siendo_el_ultimo(self):
        self.cliente.post(reverse("administracion:editar_usuario", args=[self.b.pk]), self._datos(self.b, activo=False))
        r = self.cliente.post(reverse("administracion:editar_usuario", args=[self.a.pk]), self._datos(self.a, activo=False), follow=True)
        self.a.refresh_from_db()
        self.assertTrue(self.a.is_active)
        self.assertContains(r, "quedaría el sistema sin ningún superusuario activo")

    def test_editar_perfil_del_ultimo_superusuario_si_esta_permitido(self):
        datos = self._datos(self.a)
        datos["cargo"] = "Coordinador"
        self.cliente.post(reverse("administracion:editar_usuario", args=[self.a.pk]), datos)
        self.a.refresh_from_db()
        self.assertEqual(self.a.cargo, "Coordinador")

    def test_superusuario_que_se_borra_y_queda_otro_pierde_la_sesion(self):
        r = self.cliente.post(reverse("administracion:eliminar_usuario", args=[self.a.pk]))
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r["Location"], reverse("login"))
        self.assertFalse(Usuario.objects.filter(pk=self.a.pk).exists())
        self.assertEqual(Client().get(reverse("administracion:inicio")).status_code, 302)

    def test_mi_cuenta_del_ultimo_superusuario_no_se_borra(self):
        self.b.delete()  # ahora "a" es el único
        r = self.cliente.post(reverse("eliminar_cuenta"), {"confirmacion": "a@prueba.com"}, follow=True)
        self.assertContains(r, "quedaría el sistema sin ningún superusuario activo")
        self.assertTrue(Usuario.objects.filter(pk=self.a.pk).exists())

    def test_mi_cuenta_de_un_superusuario_con_otro_activo_si_se_borra(self):
        r = self.cliente.post(reverse("eliminar_cuenta"), {"confirmacion": "a@prueba.com"})
        self.assertEqual(r.status_code, 302)
        self.assertFalse(Usuario.objects.filter(pk=self.a.pk).exists())
        self.assertTrue(Usuario.objects.filter(pk=self.b.pk, is_active=True).exists())

    def test_superusuario_no_puede_borrar_en_lote_a_todos(self):
        # Un superusuario no tiene forma de dejar el sistema sin administrador desde la web.
        self.cliente.post(reverse("administracion:eliminar_usuario", args=[self.b.pk]))
        self.assertEqual(superusuarios_activos(), 1)

    def test_normal_no_toca_superusuarios(self):
        c = Client()
        c.force_login(self.normal)
        self.assertEqual(c.post(reverse("administracion:eliminar_usuario", args=[self.a.pk])).status_code, 403)
        self.assertEqual(c.post(reverse("administracion:editar_usuario", args=[self.a.pk]), self._datos(self.a, activo=False)).status_code, 403)
        self.a.refresh_from_db()
        self.assertTrue(self.a.is_active)

    def test_desactivar_a_un_superusuario_saca_su_sesion(self):
        cliente_b = Client()
        cliente_b.force_login(self.b)
        self.cliente.post(reverse("administracion:editar_usuario", args=[self.b.pk]), self._datos(self.b, activo=False))
        self.assertEqual(cliente_b.get(reverse("administracion:inicio")).status_code, 302)
