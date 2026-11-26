# Xincronix — plataforma de proyectos de software

Xincronix es una aplicación Django para gestionar proyectos de tecnología y software. Cada proyecto pertenece a su creador y puede reunir colaboradores invitados.

## Capacidades

- Proyectos con asistente de orientación (finalidad, metodología Scrum, GAES, Pomodoro o Kanban, modalidad individual o grupal).
- Visibilidad a elección del líder: **privado** (solo el equipo) o **público** con un enlace de solo lectura que no pide inicio de sesión. Muestra nombre, descripción, avance y tareas, pero no personas ni documentos. El líder puede generar un enlace nuevo, y el anterior deja de funcionar.
- Invitar a alguien está siempre disponible para el líder. Si el proyecto era individual, pasa a grupal automáticamente al invitar.
- El líder da permisos a cada integrante: **Colaborador** (edita tareas, calendario, canvas y documentos) o **Solo lectura**. Puede cambiarlos cuando quiera.
- Tablero Kanban arrastrable, calendario, roadmap, estadísticas, documentos, correcciones del supervisor y canvas compartido.
- Área de administración en `/administracion/`, solo para el **superusuario**: gestión de cuentas y panel de **Monitoreo** de solo lectura (`/administracion/monitoreo/`).
- **Reportes** (`/administracion/reportes/`), solo para el superusuario, el cargo más alto: filtros de hasta 4 criterios (con «todos» o «alguno»), elección de columnas, vista previa y exportación a **Excel** (encabezados, filtros, panel fijo y hoja de criterios) o **PDF** (horizontal, con pie de página). Librerías: `openpyxl` y `reportlab`.
- Mensajes directos, reuniones por proyecto, calendario personal y tickets de soporte (app `comunicacion`; por ahora solo tiene modelos).

## Ejecución local

Requiere Python 3.11+ y pip.

En Windows (PowerShell):

```powershell
cd XINCRONIX
python -m venv .venv
.\.venv\Scripts\Activate
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

En Linux:

```bash
cd XINCRONIX
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Abre `http://127.0.0.1:8000/`. Las cuentas normales se registran en `/cuentas/registro/`. El superusuario entra a `/administracion/`.

Datos de ejemplo: `python manage.py cargar_demo correo@ejemplo.com` (el usuario debe existir y quedará como líder de esos proyectos).

## Base de datos

Esta versión **no migra datos de versiones anteriores**. Cada persona del equipo debe recrear su base:

1. Hacer un respaldo de la base actual, si la necesita.
2. Crear una base nueva (o un archivo SQLite nuevo).
3. Ejecutar `python manage.py migrate` y `python manage.py createsuperuser`.

## Integridad de los datos

- Los campos importantes son obligatorios: nombres y apellidos, nombre y descripción del proyecto, título de tareas y eventos, asunto y descripción de los tickets, contenido de mensajes, comentarios de correcciones, etc. La base de datos rechaza un texto vacío aunque se salte la web.
- Las relaciones se validan: el responsable de una tarea debe ser integrante del proyecto; una corrección solo puede apuntar a una tarea de su mismo proyecto; el supervisor debe ser profesor; un mensaje no puede ir a la misma persona que lo envía.
- El historial (quién creó una tarea o subió un documento) puede quedar vacío solo si esa cuenta se borra; el trabajo se conserva.
- Para revisar lo guardado: `python manage.py auditar_datos`. Muestra cada problema y termina con error si encuentra alguno.
- `createsuperuser` pide nombres y apellidos.

## Superusuarios

- Debe quedar **siempre al menos un superusuario activo**. El sistema lo impide al borrar, desactivar, quitar el permiso o hacerlo en lote, también desde la consola.
- Un superusuario puede borrar a otro o borrarse a sí mismo, siempre que quede otro activo.
- Un `staff` que no sea superusuario no tiene acceso a la administración.
- El panel de administración de Django (`/admin/`) no existe en esta versión.

## Pruebas

```bash
python manage.py test
```

- **Caja blanca** (`test_caja_blanca.py`, `test_superusuarios.py`): lógica interna de la política, el gestor de usuarios, la regla de superusuarios (modelo, lotes, señales y servicio), la visibilidad y los permisos por rol, las validaciones y las propiedades de los modelos.
- **Caja negra** (`test_caja_negra*.py`, `test_comandos.py`): HTTP como lo haría una persona. Matriz de acceso por rol, flujo completo de proyectos, invitaciones, tablero, calendario, documentos, correcciones, canvas, aislamiento entre proyectos y reglas de administración.
- **Adversarias** (`test_adversarias.py`): un cliente exigente que intenta romper la aplicación con entradas raras, métodos HTTP extraños, escalada de privilegios y consultas fuera de lo permitido.

Cobertura (opcional):

```bash
pip install coverage
coverage run --source=cuentas,dashboard,administracion,comunicacion manage.py test
coverage report -m
```

`coverage` no está en `requirements.txt` porque solo se usa para revisar las pruebas.

## Seguridad

- Solo el superusuario administra cuentas y ve el monitoreo.
- Los documentos del proyecto solo aceptan PDF, Office, texto, imagen o ZIP, de hasta 10 MB.
- El canvas tiene un límite de 512 KB y de profundidad de anidación.
- El monitoreo nunca muestra contraseñas, tokens ni claves de sesión, no permite filtrar por esos campos y no los exporta. Las celdas del CSV que empiezan con `= + - @` se escapan.

## Correo e invitaciones

Por defecto el correo se imprime en consola: el enlace de la invitación aparece donde corre `runserver`. Para correos reales, configura un backend SMTP en `.env`; no subas credenciales al repositorio.

## Limitaciones conocidas

- **Los documentos se guardan en `media/` y, mientras `DEBUG` esté activo, se sirven por su URL sin pedir inicio de sesión.** Quien tenga el enlace puede abrirlo. Antes de producción hay que servirlos con una vista protegida o un almacenamiento privado.
- No hay límite de intentos de inicio de sesión. Antes de producción conviene agregarlo.
- El canvas guarda el último envío recibido; no hay edición simultánea en tiempo real.
- El calendario no sincroniza con Google Calendar, Outlook ni otros servicios.
- Antes de producción, cambia `DJANGO_SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, el correo y la base de datos.
