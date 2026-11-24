# Cambios: roles por JSON, CRUD, Google y flechas de regreso

## Qué se agregó

| Tema | Qué hace | Dónde |
|---|---|---|
| Política JSON | Roles, acciones y permisos sobre empresas y proyectos, sin `if` por rol | `config/politica_accesos.json`, `cuentas/politica.py` |
| Rol "Usuario" | El antiguo "colaborador" ahora se llama **Usuario** (usuario normal) | migración `cuentas/0003` |
| Superadministrador | CRUD de **usuarios** y de **empresas**; vincula y desvincula usuarios; asigna roles | `/administracion/` |
| Mi cuenta | Ver y editar datos, cambiar o crear la contraseña, **eliminar la cuenta** | `/cuentas/mi-cuenta/` |
| Mi empresa | Crear la empresa (queda como propietario), editarla, eliminarla y ver sus **métricas** | `/app/empresa/` |
| Proyectos | CRUD completo; invitar personas por correo (también de otra empresa) como responsable, editor u observador | `/app/proyectos/` |
| Tareas | CRUD dentro del proyecto, con fechas y responsable; lista "Mis tareas" | `/app/tareas/` |
| Google | Botón **Continuar con Google** en el login y el registro (django-allauth) | `docs/google_login.md` |
| Flechas | Flecha de regreso en el login, el registro, recuperar contraseña y todas las páginas internas | `templates/partials/volver*.html` |
| Portada | `/` muestra la página pública original (`index.html`) a quien no ha iniciado sesión | `sitio/templates/sitio/index.html` |

## Cambios en la base de datos (migraciones)

- `cuentas/0003_empresa_propietario_y_rol_usuario`:
  - agrega la columna `empresa.id_propietario`;
  - pone como propietario al primer administrador (o al primer integrante) de cada empresa;
  - renombra el rol `colaborador` a `usuario`;
  - si se elimina una empresa, sus usuarios **ya no se borran**: quedan sin empresa.
- `dashboard/0002_proyecto_rol_editor`: el rol de proyecto `colaborador` pasa a `editor`.
- django-allauth agrega sus tablas: `account_*` y `socialaccount_*`.

## Dependencias nuevas

`django-allauth`, más lo que necesita para hablar con Google: `requests`, `PyJWT`,
`cryptography` y `oauthlib`. Todas están en `requirements.txt`.

## Pruebas

102 pruebas pasan en SQLite y en MariaDB 10.11: `python manage.py test`.
