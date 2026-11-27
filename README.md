# Xincronix — plataforma de proyectos de software

Xincronix es una aplicación Django para gestionar proyectos de tecnología y software. Cada proyecto pertenece a su creador y puede reunir colaboradores invitados.

## Capacidades

- Proyectos con asistente de orientación (finalidad, metodología Scrum, GAES, Pomodoro o Kanban, modalidad individual o grupal).
- Visibilidad a elección del líder: **privado** (solo el equipo) o **público** con un enlace de solo lectura que no pide inicio de sesión. Muestra nombre, descripción, avance y tareas, pero no personas ni documentos. El líder puede generar un enlace nuevo, y el anterior deja de funcionar.
- Invitar a alguien está siempre disponible para el líder. Si el proyecto era individual, pasa a grupal automáticamente al invitar.
- El líder da permisos a cada integrante: **Colaborador** (edita tareas, calendario, canvas y documentos) o **Solo lectura**. Puede cambiarlos cuando quiera.
- Tablero Kanban arrastrable, calendario, roadmap, estadísticas, documentos, correcciones del supervisor y canvas compartido.
- Área de administración en `/administracion/`, para el rol global **Administrador**: gestión de cuentas y panel de **Monitoreo** de solo lectura (`/administracion/monitoreo/`).
- **Reportes** (`/administracion/reportes/`), para el rol global Administrador: filtros de hasta 4 criterios (con «todos» o «alguno»), elección de columnas, vista previa y exportación a **Excel** (encabezados, filtros, panel fijo y hoja de criterios) o **PDF** (horizontal, con pie de página). Librerías: `openpyxl` y `reportlab`.
- Asistente Gemini con respuestas en vivo e historial privado por proyecto, repositorios GitHub, inicio con Google y correos SMTP. Consulta [la configuración de las integraciones](docs/integraciones.md).
- Mensajes directos, reuniones por proyecto, calendario personal y tickets de soporte (app `comunicacion`; por ahora solo tiene modelos).

## Ejecución local

Requiere Python 3.11+ y pip.

En Windows, ejecuta `iniciar_servidor.bat` desde la carpeta del proyecto. Se recomienda Python 3.13.

| Archivo | Qué hace |
|---|---|
| `descargar_env.bat` | Crea tu `.env` local a partir de `.env.example`. Si ya existe, lo conserva. |
| `instalar_controladores.bat` | Prepara el entorno virtual e instala las dependencias y el controlador del motor elegido. |
| `iniciar_servidor.bat` | Prepara el entorno, aplica migraciones y arranca Xincronix. |
| `correr_pruebas.bat` | Prepara el entorno y ejecuta las pruebas con SQLite en memoria. |

También puedes ejecutar manualmente el flujo de Windows en PowerShell con SQLite:

```powershell
cd XINCRONIX
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
if (-not (Test-Path -LiteralPath .env)) { Copy-Item -LiteralPath .env.example -Destination .env }
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py runserver
```

Ejecuta `createsuperuser` solo para crear el primer administrador o cuando necesites otro superusuario técnico. Si ya tienes un `.env`, conserva sus valores y completa las integraciones que uses con la [guía de configuración](docs/integraciones.md).

En Linux:

```bash
cd XINCRONIX
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
test -f .env || cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Abre `http://127.0.0.1:8000/`. Las cuentas normales se registran en `/cuentas/registro/`. Las cuentas con rol Administrador entran a `/administracion/`.

Datos de ejemplo: `python manage.py cargar_demo correo@ejemplo.com` (el usuario debe existir y quedará como líder de esos proyectos).

## Base de datos

SQLite es el motor predeterminado. Si eliges MySQL o PostgreSQL, configura su conexión en `.env`. En Windows, el instalador prepara el controlador de Python para el motor elegido. En Linux, instala `mysqlclient==2.3.1` para MySQL o `psycopg[binary]>=3.1.12,<4` para PostgreSQL dentro del entorno virtual.

Si ya tienes una base de Xincronix en Django, respáldala y ejecuta `python manage.py migrate` para incorporar los roles globales, el estado de las invitaciones y los chats del asistente. Se conservan las cuentas y proyectos existentes. Para una base nueva, crea el primer administrador después de migrar.

## Integridad de los datos

- Los campos importantes son obligatorios: nombres y apellidos, nombre y descripción del proyecto, título de tareas y eventos, asunto y descripción de los tickets, contenido de mensajes, comentarios de correcciones, etc. La base de datos rechaza un texto vacío aunque se salte la web.
- Las relaciones se validan. El responsable de una tarea debe ser integrante del proyecto; una corrección solo puede apuntar a una tarea de su mismo proyecto; el supervisor debe tener el rol global Supervisor; un mensaje no puede ir a la misma persona que lo envía.
- El historial (quién creó una tarea o subió un documento) puede quedar vacío solo si esa cuenta se borra; el trabajo se conserva.
- Para revisar lo guardado: `python manage.py auditar_datos`. Muestra cada problema y termina con error si encuentra alguno.
- `createsuperuser` pide nombres y apellidos.

## Superusuarios

- Debe quedar **siempre al menos un superusuario activo**. El sistema lo impide al borrar, desactivar, quitar el permiso o hacerlo en lote, también desde la consola.
- Un superusuario puede borrar a otro o borrarse a sí mismo, siempre que quede otro activo.
- La administración requiere el rol global Administrador. El indicador `is_staff` por sí solo no concede acceso.
- El panel de administración de Django (`/admin/`) no existe en esta versión.

## Pruebas

En Windows, ejecuta `correr_pruebas.bat`. También puedes ejecutarlas manualmente:

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

- El rol global Administrador permite gestionar cuentas y ver el monitoreo. La gestión de otras cuentas administradoras queda reservada al superusuario técnico.
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
