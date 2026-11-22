# Roles y accesos

Todas las reglas están en **`config/politica_accesos.json`**. El código Python no
tiene correos, roles ni permisos escritos a mano: los **lee** de ese archivo.
Para cambiar una regla:

1. Edita el JSON.
2. Corre `python manage.py check`, que revisa el JSON y avisa si algo está mal
   escrito (errores `cuentas.E001` / `cuentas.E002`).
3. Reinicia `runserver`, porque el archivo se lee una sola vez al arrancar.

## Las secciones del JSON

| Sección | Para qué | Ejemplo |
|---|---|---|
| `superadministradores` | Correos con control total. Además deben ser `is_superuser` | `cuellaryohan100@gmail.com` |
| `roles` | Catálogo de roles con nombre y descripción | `admin`, `manager`, `supervisor`, `usuario` |
| `registro` | Rol de quien se registra (formulario o Google) | `"rol": "usuario"` |
| `perfiles.<perfil>.inicio` | A dónde entra cada perfil después del login | superadministrador → `administracion:inicio` |
| `perfiles.<perfil>.puede_asignar` | Qué roles puede dar | solo el superadministrador tiene la lista llena |
| `perfiles.<perfil>.acciones` | Acciones generales | `crear_empresa`, `crear_proyecto`, `editar_cuenta`, `eliminar_cuenta` |
| `perfiles.<perfil>.menu` | Enlaces extra del menú | "Usuarios" y "Empresas" para el superadministrador |
| `empresas` | Permisos sobre una empresa | el propietario la ve, edita, elimina y ve sus métricas |
| `proyectos` | Permisos sobre un proyecto | un editor ve, edita y maneja tareas |
| `rutas_restringidas` | URLs solo para ciertos perfiles | `/administracion/` → superadministrador |

El **perfil** de una persona es `superadministrador`, si está en la lista y es
superusuario activo, o el **código de su rol** en los demás casos.

## Permisos por relación y por perfil

Para empresas y proyectos, los permisos de una persona son la **unión** de:

- **`por_relacion`**: lo que le da su relación con ese objeto.
  - En una empresa: `propietario` o `integrante`.
  - En un proyecto: `creador`, `responsable`, `editor`, `observador` o `equipo`.
- **`por_perfil`**: lo que le da su perfil, según su **alcance**.
  - `todas`: en cualquier empresa.
  - `empresa`: solo en la empresa a la que pertenece.

Por ejemplo, Kevin es Manager de *Acme* y lo agregaron como **editor** a un proyecto
de *Nekros*:

- En los proyectos de *Acme* tiene `ver, editar, miembros, tareas` (perfil `manager`, alcance `empresa`).
- En el proyecto de *Nekros* tiene `ver, editar, tareas` (relación `editor`).
- En el resto de proyectos de *Nekros* no tiene nada.

## Cómo lo usa el código

| Dónde | Qué pregunta |
|---|---|
| `cuentas/middleware.py` | ¿Este perfil puede entrar a esta ruta? (`rutas_restringidas`) |
| `cuentas/decoradores.py` → `@requiere_accion("crear_proyecto")` | ¿El perfil tiene esta acción? |
| `politica.permisos_proyecto(usuario, proyecto)` + `exigir(permisos, "editar")` | ¿Tiene este permiso en este proyecto? Si no, 403 |
| `Proyecto.objects.visibles_para(usuario)` | Filtra en SQL los proyectos que puede ver |
| `cuentas/checks.py` | Revisa el JSON en cada `manage.py check` / `runserver` |

## Comando para ajustar la base

```
python manage.py aplicar_politica_roles --simular
python manage.py aplicar_politica_roles
python manage.py aplicar_politica_roles --quitar-administradores
```

1. `--simular` muestra los cambios y **no guarda nada**.
2. Sin opciones, el comando:
   - sincroniza la tabla `roles` con el JSON;
   - deja a los superadministradores como superusuario y staff;
   - le quita `is_superuser` / `is_staff` a todos los demás;
   - pone el rol de registro a quien no tenga rol.
3. `--quitar-administradores` es la **limpieza inicial, una sola vez**: pasa a
   Usuario a todo Administrador que no sea superadministrador. Después de eso,
   los administradores los asigna el superadministrador en `/administracion/`.
   Volver a correr el comando con esta opción **les quitaría el rol**.

## Superadministrador (`/administracion/`)

- **Usuarios**: listar, buscar, crear (con contraseña inicial), editar datos, rol,
  empresa y estado, y eliminar.
- **Empresas**: listar, crear, editar y eliminar. También asignar un
  **propietario**, que queda vinculado a la empresa, y **vincular o desvincular**
  usuarios. Al eliminar una empresa se borran sus proyectos; sus usuarios
  conservan la cuenta y quedan sin empresa.
- Las cuentas de superadministradores no aparecen en la lista: nadie puede editarlas
  ni eliminarlas desde ahí.

## Usuario normal

- **Mi cuenta** (`/cuentas/mi-cuenta/`):
  - editar sus datos;
  - cambiar o crear su contraseña;
  - **eliminar su cuenta**. Antes de confirmar ve qué se borra: su empresa
    solo se elimina si nadie más pertenece a ella.
- **Mi empresa** (`/app/empresa/`): crearla (queda como propietario), editarla,
  eliminarla y ver sus **métricas**: proyectos, tareas completadas y vencidas,
  integrantes y avance por proyecto.
- **Proyectos** (`/app/proyectos/`):
  - crear, editar y eliminar los suyos;
  - agregar personas por correo, aunque sean de otra empresa, como
    responsable, editor u observador;
  - crear, editar y eliminar tareas, con sus fechas.
  - Los responsables y editores también ajustan fechas y tareas.
