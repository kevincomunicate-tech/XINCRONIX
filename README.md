# Xincronix — Django
## Objetivos del producto (Product Goal)

Construir una plataforma completa de gestión de proyectos, tareas, ideas y analytics (Xincronix) migrada a **Django 5.2**, con autenticación de usuarios, panel funcional y las funcionalidades principales del sistema original, lista para uso real.

## Sprint actual

**Sprint 2** — Modelos de datos y panel con información real  
**Duración:**  10 – 28 de noviembre 2026

### Sprint Goal
Implementar los modelos de **Proyectos**, **Tareas** y **Actividad**, y mostrar datos reales en el dashboard (ya no mock/estáticos), manteniendo la autenticación y el modo oscuro funcionando.

### Criterios de éxito del Sprint
- [ ] Modelos `Proyecto`, `Tarea` y `Actividad` creados y migrados
- [ ] Panel (`/app/`) muestra proyectos y tareas reales del usuario autenticado
- [ ] Crear, listar y ver detalle básico de proyectos y tareas
- [ ] Tests básicos de los nuevos modelos y vistas

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

# 7. Levantar el servidor
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

## Recuperar contraseña en desarrollo

Los correos **no se envían**: se imprimen en la terminal donde corre
`runserver`. Copia el enlace de ahí y ábrelo en el navegador.

## Pruebas

```bash
python manage.py test
```

## Avance de la migración

- [x] Fase 1: entorno, proyecto, login, registro, recuperar contraseña, modo oscuro
- [ ] Fase 2: modelos (proyectos, tareas, actividad) y panel con datos reales
- [ ] Fase 3: proyectos, tareas y analytics
- [ ] Fase 4: ideas, canvas, página de inicio e información
