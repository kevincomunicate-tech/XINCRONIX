"""
Ajusta la base de datos a config/politica_accesos.json.

    python manage.py aplicar_politica_roles --simular   # muestra los cambios, no toca nada
    python manage.py aplicar_politica_roles             # los aplica
    python manage.py aplicar_politica_roles --quitar-administradores   # limpieza inicial (una vez)

Qué hace:
  1. Sincroniza la tabla "roles" con la sección "roles" del JSON.
  2. Las cuentas de "superadministradores" quedan como Administrador,
     superusuario y staff (acceso a /admin).
  3. Nadie más queda como superusuario ni staff, y quien no tenga rol
     recibe el de "registro" (usuario normal).
  4. Solo con --quitar-administradores: toda otra cuenta con rol
     Administrador pasa a usuario normal. Úsalo UNA vez para limpiar la base;
     después los administradores los asigna el superadministrador en
     /administracion/ y no hay que volver a quitarlos.

Se puede correr las veces que quieras: si todo ya está bien, no cambia nada.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from cuentas.models import Rol, Usuario
from cuentas.politica import obtener_politica


class Command(BaseCommand):
    help = "Ajusta roles y permisos de los usuarios según config/politica_accesos.json."

    def add_arguments(self, parser):
        parser.add_argument("--simular", action="store_true", help="Muestra los cambios sin guardarlos.")
        parser.add_argument(
            "--quitar-administradores", action="store_true",
            help="Pasa a usuario normal a todo Administrador que no sea superadministrador.",
        )

    def handle(self, *args, simular, quitar_administradores, **options):
        self.quitar_administradores = quitar_administradores
        politica = obtener_politica()
        self.cambios = []

        with transaction.atomic():
            self._sincronizar_roles(politica)
            self._ajustar_usuarios(politica)
            if simular:
                transaction.set_rollback(True)  # deshace todo al salir del bloque

        self._informar(simular, politica)

    # --- 1. Catálogo de roles ---

    def _sincronizar_roles(self, politica):
        for codigo, datos in politica.roles.items():
            rol, creado = Rol.objects.get_or_create(
                codigo=codigo, defaults={"nombre": datos["nombre"], "descripcion": datos.get("descripcion", "")}
            )
            esperado = {"nombre": datos["nombre"], "descripcion": datos.get("descripcion", "")}
            diferencias = {campo: valor for campo, valor in esperado.items() if getattr(rol, campo) != valor}
            Rol.objects.filter(pk=rol.pk).update(**diferencias)
            if creado:
                self.cambios.append(f"Rol '{codigo}' creado.")
            self.cambios += [f"Rol '{codigo}': {campo} actualizado." for campo in diferencias]

    # --- 2 y 3. Usuarios ---

    def _ajustar_usuarios(self, politica):
        rol_admin = Rol.objects.get(codigo=Rol.ADMIN)
        rol_normal = Rol.objects.get(codigo=politica.rol_registro)

        for usuario in Usuario.objects.select_related("rol").order_by("pk"):
            es_super = usuario.email.lower() in politica.superadministradores
            esperado = {
                "rol_id": rol_admin.pk if es_super else self._rol_sin_admin(usuario, rol_admin, rol_normal),
                "is_superuser": es_super,
                "is_staff": es_super,
            }
            diferencias = {campo: valor for campo, valor in esperado.items() if getattr(usuario, campo) != valor}
            Usuario.objects.filter(pk=usuario.pk).update(**diferencias)
            self.cambios += [f"{usuario.email}: {self._describir(campo, valor)}" for campo, valor in diferencias.items()]

        faltan = politica.superadministradores - {e.lower() for e in Usuario.objects.values_list("email", flat=True)}
        self.avisos = [f"El superadministrador {correo} no existe en esta base: créalo con createsuperuser." for correo in sorted(faltan)]

    def _rol_sin_admin(self, usuario, rol_admin, rol_normal):
        """Conserva el rol; el vacío (y Administrador con --quitar-administradores) pasa a usuario normal."""
        a_normal = {None} | ({rol_admin.pk} if self.quitar_administradores else set())
        return rol_normal.pk if usuario.rol_id in a_normal else usuario.rol_id

    ETIQUETAS = {"rol_id": "rol", "is_superuser": "superusuario", "is_staff": "acceso a /admin"}

    def _describir(self, campo, valor):
        texto = Rol.objects.get(pk=valor).nombre if campo == "rol_id" else ("sí" if valor else "no")
        return f"{self.ETIQUETAS[campo]} -> {texto}"

    # --- Resumen ---

    def _informar(self, simular, politica):
        titulo = "SIMULACIÓN (no se guardó nada)" if simular else "Cambios aplicados"
        self.stdout.write(self.style.MIGRATE_HEADING(titulo))
        for cambio in self.cambios or ["Nada que cambiar: la base ya cumple la política."]:
            self.stdout.write(f"  - {cambio}")
        for aviso in self.avisos:
            self.stdout.write(self.style.WARNING(f"  ! {aviso}"))
        self.stdout.write(f"Superadministradores: {', '.join(sorted(politica.superadministradores))}")
