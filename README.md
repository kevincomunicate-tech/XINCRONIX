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

# 7. (Opcional) Cargar un equipo, proyectos y tareas de ejemplo en la empresa
#    del usuario. El usuario debe existir antes (paso 6 o /cuentas/registro/);
#    si no tiene empresa, se le crea "Empresa demo".
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
├── cuentas/             empresas, roles y usuarios: login, registro, recuperar contraseña
├── dashboard/           panel, equipos, proyectos, tareas, actividad (luego analytics, ideas, canvas)
├── sitio/               página pública de inicio
├── templates/           plantillas base compartidas
└── static/              CSS, JS e imágenes
```

## Rutas

| URL | Página |
|---|---|
| `/` | Inicio (por ahora redirige al login o al panel) |
| `/cuentas/login/` | Iniciar sesión |
| `/cuentas/registro/` | Crear cuenta (y la empresa) |
| `/cuentas/recuperar/` | Recuperar contraseña |
| `/app/` | Panel (requiere sesión) |
| `/admin/` | Administración de Django |

## Modelo de datos

Las tablas siguen el esquema de [xincronix_bd.sql](xincronix_bd.sql)
(mismos nombres de tablas, columnas, índices y restricciones). Ese archivo
es solo una referencia: las tablas las crea `python manage.py migrate`.

| Tabla | App | Qué guarda |
|---|---|---|
| `empresa` | cuentas | la empresa; todo lo demás pertenece a una |
| `roles` | cuentas | admin, manager, supervisor y colaborador (los crea la migración) |
| `usuarios` | cuentas | nombres, apellidos, correo, cargo, empresa y rol |
| `equipos` / `miembros_equipo` | dashboard | equipos de la empresa y quién está en cada uno |
| `proyecto` / `proyecto_miembros` | dashboard | proyectos (estado, importancia 1-4, tipo, fechas, equipo) y sus miembros |
| `tareas` | dashboard | estado, prioridad, vencimiento, asignada a y creada por |
| `actividad` | dashboard | historial ("Ana completó la tarea X") que se muestra en el panel |

Reglas:

- Al registrarse se crea la empresa y quien se registra queda como **administrador**.
- Nadie ve datos de otra empresa. Admin, manager y supervisor ven todos los
  proyectos de su empresa; un colaborador solo los que creó, aquellos donde
  lo agregaron como miembro o los de sus equipos.
- No se guarda nada que se pueda calcular: el **% de avance** de un proyecto
  se obtiene contando sus tareas completadas.
- Estados, tipos y prioridades son opciones fijas (no texto libre).
- Mientras se construyen las pantallas de la fase 3, los proyectos, equipos y
  tareas se crean desde `/admin/` (eso también registra la actividad).
- Las demás tablas del esquema (ideas, lienzos, mensajes, notificaciones, IA,
  etc.) se agregan en las fases siguientes.

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
