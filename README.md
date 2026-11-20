# Xincronix

**Plataforma de gestión de proyectos, tareas, ideas y analytics**

Xincronix es una aplicación web moderna que permite a equipos y freelancers organizar proyectos, gestionar tareas, capturar ideas y visualizar el progreso de su trabajo en un solo lugar.

Este repositorio contiene la versión migrada a **Python + Django 5.2**, con una arquitectura limpia, autenticación de usuarios y un panel de control funcional.

---

## Product Goal

Construir una plataforma completa, segura y escalable de gestión de trabajo que permita a los usuarios:

- Crear y administrar proyectos
- Gestionar tareas con estados y prioridades
- Registrar actividad e historial
- Capturar y organizar ideas
- Visualizar analytics básicos de productividad
- Trabajar con una interfaz moderna (modo claro/oscuro)

El objetivo es entregar un producto usable en producción, con una experiencia comparable o superior a la versión original en HTML/CSS/JS.

---

## Estado actual del proyecto

| Fase | Descripción                                      | Estado     |
|------|--------------------------------------------------|------------|
| 1    | Entorno, autenticación, registro y modo oscuro   | Completada |
| 2    | Modelos de datos + panel con información real    | En curso   |
| 3    | Proyectos, tareas y analytics                    | Pendiente  |
| 4    | Ideas, canvas y página de inicio pública         | Pendiente  |

---

## Sprint actual — Sprint 2

**Nombre:** Modelos de datos y panel con datos reales  
**Duración:** 10 – 28 de noviembre 2026

### Sprint Goal

Implementar los modelos de dominio principales (`Proyecto`, `Tarea` y `Actividad`) y conectar el panel de control para que muestre información real del usuario autenticado, eliminando los datos mock.

### Objetivos del Sprint (Definition of Done)

- [ ] Crear los modelos `Proyecto`, `Tarea` y `Actividad` con sus relaciones
- [ ] Generar y aplicar las migraciones correspondientes
- [ ] Mostrar en `/app/` los proyectos y tareas reales del usuario logueado
- [ ] Permitir crear, listar y ver el detalle básico de proyectos y tareas
- [ ] Implementar tests unitarios básicos de modelos y vistas
- [ ] Mantener funcionando la autenticación y el modo oscuro

---

## Requisitos técnicos

- Python 3.10 o superior
- pip
- Git

---

## Instalación (primera vez)

```bash
# 1. Clonar el repositorio
git clone <url-del-repositorio>
cd xincronix

# 2. Crear y activar entorno virtual
python -m venv .venv

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (cmd)
.venv\Scripts\activate.bat

# Linux / macOS
source .venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
# Windows
copy .env.example .env

# Linux / macOS
cp .env.example .env

# 5. Aplicar migraciones
python manage.py migrate

# 6. (Opcional) Crear superusuario
python manage.py createsuperuser

# 7. Iniciar el servidor de desarrollo
python manage.py runserver
