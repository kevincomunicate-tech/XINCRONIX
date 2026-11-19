# Xincronix — Django

Migración del proyecto Xincronix (HTML/CSS/JS) a **Python + Django 5.2**.

## Requisitos

- Python 3.10 o superior

## Instalación (primera vez)

```bash
# 1. Crear el entorno virtual
python -m venv .venv

# 2. Activarlo
#    Windows (PowerShell):  .venv\Scripts\Activate.ps1
#    Windows (cmd):         .venv\Scripts\activate.bat
#    Linux / macOS:         source .venv/bin/activate

# 3. Instalar las dependencias
pip install -r requirements.txt

# 4. Crear tu archivo .env a partir del ejemplo (y cambiar la clave)
#    Windows:  copy .env.example .env
#    Linux:    cp .env.example .env

# 5. Crear las tablas de la base de datos
python manage.py migrate

# 6. (Opcional) Crear un administrador para /admin
python manage.py createsuperuser

# 7. (Opcional) Cargar proyectos y tareas de ejemplo para ver el panel con datos
#    El usuario debe existir antes (paso 6 o /cuentas/registro/)
python manage.py cargar_demo tu@correo.com

# 8. Levantar el servidor
python manage.py runserver
```

Abre http://127.0.0.1:8000

## Uso diario

```bash
source .venv/bin/activate      # o .venv\Scripts\Activate.ps1 en Windows
python manage.py runserver
```

Si instalas un paquete nuevo, actualiza la lista:

```bash
pip install nombre-del-paquete
pip freeze > requirements.txt
```

## Estructura

```
xincronix/
├── .venv/               entorno virtual (no se sube a git)
├── .env                 secretos (no se sube a git)
├── .env.example         guía para crear .env
├── requirements.txt     dependencias exactas
├── manage.py            comandos de Django
├── config/              configuración general (settings, urls)
├── cuentas/             usuarios: login, registro, recuperar contraseña
├── dashboard/           panel, proyectos, tareas, analytics, ideas, canvas
├── sitio/               página pública de inicio
├── templates/           plantillas base compartidas
└── static/              CSS, JS e imágenes
```

## Rutas

| URL | Página |
|---|---|
| `/` | Inicio (por ahora redirige al login o al panel) |
| `/cuentas/login/` | Iniciar sesión |
| `/cuentas/registro/` | Crear cuenta |
| `/cuentas/recuperar/` | Recuperar contraseña |
| `/app/` | Panel (requiere sesión) |
| `/admin/` | Administración de Django |

## Modelo de datos (app `dashboard`)

| Tabla | Qué guarda |
|---|---|
| `Proyecto` | nombre, estado, prioridad, fechas y su **propietario** |
| `MiembroProyecto` | qué usuarios participan en cada proyecto (sin repetidos) |
| `Tarea` | pertenece a un proyecto; estado, prioridad, vencimiento, asignada a / creada por |
| `Actividad` | historial ("Ana completó la tarea X") que se muestra en el panel |

Reglas del esquema:

- No se guarda nada que se pueda calcular: el **% de avance** de un proyecto
  se obtiene contando sus tareas completadas.
- Estados y prioridades son opciones fijas (no texto libre).
- Cada usuario solo ve los proyectos de los que es dueño o miembro.
- Mientras se construyen las pantallas de la fase 3, los proyectos y tareas
  se crean desde `/admin/` (eso también registra la actividad).

## Recuperar contraseña en desarrollo

Los correos **no se envían**: se imprimen en la terminal donde corre
`runserver`. Copia el enlace de ahí y ábrelo en el navegador.

## Pruebas

```bash
python manage.py test
```

## Avance de la migración

- [x] Fase 1: entorno, proyecto, login, registro, recuperar contraseña, modo oscuro
- [x] Fase 2: modelos (proyectos, tareas, actividad) y panel con datos reales
- [ ] Fase 3: proyectos, tareas y analytics
- [ ] Fase 4: ideas, canvas, página de inicio e información
