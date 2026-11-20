# Xincronix

**Plataforma de gestión de proyectos, tareas, ideas y analytics para equipos de trabajo**

Xincronix es una aplicación web donde los equipos de una empresa organizan su
trabajo en un solo lugar: proyectos, tareas, ideas y una pizarra colaborativa,
con indicadores para medir el avance.

Este repositorio contiene la versión migrada de HTML/CSS/JS a **Python +
Django 5.2**, con una base de datos normalizada, autenticación de usuarios y
trabajo en equipo con permisos por empresa, equipo y proyecto.

---

## Product Goal

> Ofrecer a las empresas una plataforma segura y colaborativa, construida en
> Python con Django, donde cada equipo gestione sus proyectos y tareas,
> comparta ideas, diseñe en conjunto sobre un canvas y mida su rendimiento,
> viendo cada persona solo la información que le corresponde.

El objetivo es entregar el **1 de diciembre de 2026** un producto usable en
producción, con una experiencia igual o mejor que la versión original.

### Módulos

| Módulo | Qué hace |
|---|---|
| **Cuentas** | Registro, inicio de sesión, recuperación de contraseña y roles |
| **Empresas y equipos** | Cada empresa con sus usuarios, equipos y permisos |
| **Panel** | Resumen del trabajo: estadísticas, actividad reciente y progreso |
| **Proyectos** | Proyectos con miembros y tablero Kanban |
| **Tareas** | Asignación, estados, prioridades y fechas de vencimiento |
| **Analytics** | Indicadores, metas y tendencia de productividad |
| **Tablero de ideas** | Proponer, votar y priorizar ideas en equipo |
| **Canvas** | Pizarra colaborativa compartida |

Todo con interfaz en **modo claro y oscuro**.

---

## Equipo

| Integrante | GitHub | Responsabilidad |
|---|---|---|
| Yohan | [@FIRE31690](https://github.com/FIRE31690) | Sprint 1 · Canvas, página de inicio y perfil (Sprint 4) |
| Felipe | [@FelipeNavarrete0313](https://github.com/FelipeNavarrete0313) | Sprint 2 · Ideas, usuarios, equipos y notificaciones (Sprint 4) |
| Kevin | [@kevincomunicate-tech](https://github.com/kevincomunicate-tech) | Sprint 3 · Despliegue (Sprint 4) |

---

## Sprints

Scrum con sprints de **1 semana**. Estimación en story points (Fibonacci).

| Sprint | Fechas | Módulos | Responsable | Puntos | Estado |
|---|---|---|---|---|---|
| **Sprint 1** | 9 – 13 nov 2026 | Cuentas | Yohan | 29 | ✅ Completado |
| **Sprint 2** | 16 – 20 nov 2026 | Empresas y equipos · Panel | Felipe | 31 | 🔄 En cierre |
| **Sprint 3** | 23 – 27 nov 2026 | Proyectos · Tareas · Analytics | Kevin | 34 | ⏳ Pendiente |
| **Sprint 4** | 23 nov – 1 dic 2026 | Ideas · Canvas · Entrega | Los tres | 57 | ⏳ Pendiente |

El Sprint 4 corre **en paralelo** con el Sprint 3 para llegar al 1 de
diciembre: Yohan y Felipe empiezan el 23 de noviembre y Kevin se une el 30.

### Sprint Goals

- **Sprint 1 — Cuentas:** que cualquier persona pueda registrarse, iniciar
  sesión, cerrar sesión y recuperar su contraseña de forma segura, sobre la
  base del proyecto en Django.
- **Sprint 2 — Empresas, equipos y panel:** reconstruir la base de datos
  normalizada (3FN) con permisos de trabajo en equipo, y que el panel muestre
  datos reales de cada empresa.
- **Sprint 3 — Proyectos, tareas y analytics:** que el equipo cree y gestione
  sus proyectos, reparta y mueva tareas en el Kanban según sus permisos, y
  mida el avance con indicadores.
- **Sprint 4 — Ideas, canvas y entrega:** entregar los módulos colaborativos
  (tablero de ideas y canvas compartido), completar la gestión de equipos y
  dejar el producto listo para desplegar y sustentar.

El plan completo (historias de usuario, criterios de aceptación y reparto) está
en [`docs/plan_sprints.md`](docs/plan_sprints.md).

---

## Sprint actual — Sprint 2

**Nombre:** Empresas, equipos y panel con datos reales
**Fechas:** 16 – 20 de noviembre de 2026
**Responsable:** Felipe ([@FelipeNavarrete0313](https://github.com/FelipeNavarrete0313))

### Sprint Goal

> Reconstruir la base de datos normalizada (3FN) con soporte para el trabajo
> en equipo en proyectos y canvas, y que el panel muestre datos reales del
> usuario autenticado, eliminando los datos de ejemplo.

### Checklist del sprint

- [x] Modelos de empresa, roles, usuarios y equipos, normalizados en 3FN
- [x] Modelos de proyectos (con miembros), tareas, ideas, lienzos, actividad, notificaciones y métricas
- [x] Migraciones generadas y aplicadas, con los 4 roles creados automáticamente
- [x] Permisos de trabajo en equipo: cada usuario solo ve lo que le corresponde
- [x] Soporte para SQLite y MariaDB/MySQL
- [x] Administración de todas las tablas en `/admin`
- [x] Pruebas automáticas de modelos y permisos (35 pruebas)
- [x] Documentación del modelo de datos (diagrama ER y SQL)
- [ ] Panel `/app/` con estadísticas, actividad reciente y progreso reales
- [x] Autenticación y modo oscuro siguen funcionando

> Crear, editar y ver proyectos y tareas desde la aplicación es parte del
> **Sprint 3**.

---

## Tecnologías

- **Backend:** Python 3.10+ · Django 5.2 (LTS)
- **Base de datos:** SQLite (desarrollo) · MariaDB 10.5+ o MySQL 8+
- **Frontend:** plantillas de Django · Bootstrap 5.3 · Bootstrap Icons · Chart.js
- **Otros:** python-dotenv (configuración) · Pillow (fotos de perfil)

## Requisitos

- Python 3.10 o superior
- pip
- Git
- (Opcional) MariaDB 10.5+ o MySQL 8+. El XAMPP con MariaDB 10.4 **no** es
  compatible con Django 5.2.

---

## Instalación (primera vez)

```bash
# 1. Clonar el repositorio
git clone https://github.com/kevincomunicate-tech/XINCRONIX.git
cd XINCRONIX

# 2. Crear el entorno virtual
python -m venv .venv

# 3. Activarlo
#    Windows (PowerShell):  .venv\Scripts\Activate.ps1
#    Windows (cmd):         .venv\Scripts\activate.bat
#    Linux / macOS:         source .venv/bin/activate

# 4. Instalar las dependencias
pip install -r requirements.txt

# 5. Crear el archivo .env a partir del ejemplo (y cambiar la clave secreta)
#    Windows:        copy .env.example .env
#    Linux / macOS:  cp .env.example .env

# 6. Crear las tablas de la base de datos (incluye los 4 roles)
python manage.py migrate

# 7. (Opcional) Crear un administrador para /admin
python manage.py createsuperuser

# 8. Iniciar el servidor de desarrollo
python manage.py runserver
```

Abre http://127.0.0.1:8000

## Uso diario

```bash
source .venv/bin/activate      # o .venv\Scripts\Activate.ps1 en Windows
python manage.py runserver
```

Si instalas un paquete nuevo, actualiza la lista de dependencias:

```bash
pip install nombre-del-paquete
pip freeze > requirements.txt
```

Si alguien cambió los modelos, después de hacer `git pull` aplica sus migraciones:

```bash
python manage.py migrate
```

---

## Base de datos

Por defecto se usa **SQLite** (un archivo `db.sqlite3`, sin instalar nada).

Para usar **MariaDB/MySQL** (por ejemplo, con phpMyAdmin):

1. Crea la base vacía `xincronix_bd` con cotejamiento `utf8mb4_unicode_ci`.
2. En `.env` configura:
   ```
   DB_ENGINE=mysql
   DB_NAME=xincronix_bd
   DB_USER=root
   DB_PASSWORD=
   DB_HOST=127.0.0.1
   DB_PORT=3306
   ```
3. Ejecuta `python manage.py migrate`.

El diagrama entidad-relación y los cambios respecto a la base anterior están en
[`docs/modelo_datos.md`](docs/modelo_datos.md). La estructura en SQL, para
revisarla en phpMyAdmin, está en [`docs/xincronix_bd.sql`](docs/xincronix_bd.sql).

> **Borra los datos desde la aplicación o desde `/admin`**, no con `DELETE`
> directo en phpMyAdmin: Django es quien aplica el borrado en cascada.

---

## Estructura

```
XINCRONIX/
├── .venv/               entorno virtual (no se sube a git)
├── .env                 secretos (no se sube a git)
├── .env.example         guía para crear .env
├── requirements.txt     dependencias exactas
├── manage.py            comandos de Django
├── config/              configuración general (settings, urls)
├── cuentas/             empresas, roles, usuarios y equipos · login y registro
├── dashboard/           proyectos, tareas, ideas, canvas, actividad y métricas
├── comunicacion/        mensajes, reuniones, calendario, asistente IA y soporte
├── sitio/               página pública de inicio
├── templates/           plantillas base compartidas
├── static/              CSS, JS e imágenes
├── docs/                modelo de datos y plan de sprints
└── scripts/             publicar el backlog en GitHub
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

---

## Pruebas

```bash
python manage.py test
```

Para probar contra MariaDB/MySQL, configura `DB_ENGINE=mysql` en `.env` antes de correrlas.

---

## Flujo de trabajo con Git

- `main` solo recibe cambios revisados.
- Cada sprint trabaja en su rama: `feature/fase-3-proyectos-tareas-analytics`.
- Cada historia de usuario va en su propia rama: `feature/HU-18-listado-proyectos`.
- Los cambios entran por **pull request**, revisado por otra persona.
- En la descripción del pull request escribe `Closes #N` para cerrar el issue al unirlo.

### Definición de terminado

Una historia está terminada cuando:

1. Cumple sus criterios de aceptación.
2. Tiene pruebas automáticas y `python manage.py test` pasa completo.
3. Funciona en modo claro, modo oscuro y en móvil.
4. Respeta los permisos de trabajo en equipo.
5. Incluye su migración, si cambia el modelo de datos.
6. Su pull request fue revisado por otra persona.
