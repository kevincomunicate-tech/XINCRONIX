# Plan de sprints — Migración de Xincronix a Django

- **Metodología:** Scrum con sprints de **1 semana** (lunes a viernes).
- **Estimación:** *story points* en escala Fibonacci (1, 2, 3, 5, 8). Miden
  complejidad relativa, no horas: una historia de 5 es más o menos el doble
  de una de 3.
- **Velocidad:** en los Sprints 1 y 2 cada persona cerró unos 30 puntos por
  semana (6 por día hábil). Con esa cifra se planean los siguientes.
- **Fecha de entrega:** martes **1 de diciembre de 2026**.
- **Doliente:** la persona responsable de que la historia quede terminada.
- El backlog importable (GitHub Projects, Jira o Trello) está en
  [`backlog.csv`](backlog.csv).

## Publicarlo en GitHub (issues, sprints y tablero)

El script [`scripts/publicar_backlog.py`](../scripts/publicar_backlog.py) crea
todo con GitHub CLI a partir de `backlog.csv`:

| Plan | En GitHub |
|---|---|
| Sprint + sprint goal | Milestone (con fecha de cierre) |
| Historia de usuario | Issue (`HU-18 Listado de proyectos…`) |
| Story points | Etiqueta `sp:5` + campo numérico en el tablero |
| Doliente | Assignee |
| Prioridad, épica, tipo | Etiquetas |
| Backlog | Issues sin milestone, con la etiqueta `backlog` |
| Sprints terminados | Issues cerrados |

Pon primero los usuarios de GitHub de cada persona en `DOLIENTES`, al
inicio del script. Si se corre dos veces, no duplica nada.

## Equipo

| Persona | Sprint a cargo |
|---|---|
| Yohan | Sprint 1 — Fase 1 |
| Felipe | Sprint 2 — Fase 2 |
| Kevin | Sprint 3 — Fase 3 |
| Yohan, Felipe y Kevin | Sprint 4 — Fase 4 (Kevin se une el 30 nov) |

## Resumen de sprints

| Sprint | Fechas | Fase | Doliente | Puntos | Rama | Estado |
|---|---|---|---|---|---|---|
| Sprint 1 | 9 – 13 nov 2026 | Fase 1: base del proyecto y cuentas | Yohan | 29 | `feature/fase-1-auth-base` | ✅ Terminado |
| Sprint 2 | 16 – 20 nov 2026 | Fase 2: modelo de datos y panel | Felipe | 31 | `feature/fase-2-modelo-datos-panel` | ✅ Terminado |
| Sprint 3 | 23 – 27 nov 2026 | Fase 3: proyectos, tareas y analytics | Kevin | 34 | `feature/fase-3-proyectos-tareas-analytics` | 🔜 Por empezar |
| Sprint 4 | 23 nov – 1 dic 2026 (en paralelo con el 3) | Fase 4: ideas, canvas, equipo, sitio y entrega | Todos | 57 | `feature/fase-4-colaboracion-entrega` | ⏳ Planeado |

Cada historia se trabaja en su propia rama, que sale de la rama del
sprint: `feature/HU-17-listado-proyectos`.

---

## Sprint 1 — Base del proyecto y cuentas ✅

**Fechas:** 9 – 13 nov 2026 · **Doliente:** Yohan · **Puntos:** 29

> **Sprint goal:** Tener el proyecto Django funcionando con entorno virtual,
> y que un usuario pueda registrarse, iniciar sesión, cerrar sesión y
> recuperar su contraseña con el diseño original (claro y oscuro).

| Issue | Historia de usuario | Pts | Doliente | Estado |
|---|---|---|---|---|
| #1 | **HU-01** Entorno virtual, `requirements.txt` y `.env` | 2 | Yohan | ✅ |
| #2 | **HU-02** Estructura del proyecto (`config` + apps, idioma `es-co`, archivos estáticos) | 3 | Yohan | ✅ |
| #3 | **HU-03** Usuario propio con inicio de sesión por correo | 5 | Yohan | ✅ |
| #4 | **HU-04** Iniciar y cerrar sesión, con "recordar sesión" | 3 | Yohan | ✅ |
| #5 | **HU-05** Registro con nombre, correo y contraseña, validado en el servidor | 5 | Yohan | ✅ |
| #6 | **HU-06** Recuperar contraseña por correo (enlace de un solo uso) | 5 | Yohan | ✅ |
| #7 | **HU-07** Plantillas base (cuentas y dashboard) con modo oscuro | 3 | Yohan | ✅ |
| #8 | **HU-08** Pruebas automáticas de cuentas | 3 | Yohan | ✅ |

---

## Sprint 2 — Modelo de datos y panel ✅

**Fechas:** 16 – 20 nov 2026 · **Doliente:** Felipe · **Puntos:** 31

> **Sprint goal:** Reconstruir la base de datos normalizada (3FN) con
> trabajo en equipo en proyectos y canvas, y que el Panel muestre datos
> reales.

| Issue | Historia de usuario | Pts | Doliente | Estado |
|---|---|---|---|---|
| #9 | **HU-09** Modelo de empresa, roles, usuarios y equipos (3FN, con los nombres de las tablas originales) | 5 | Felipe | ✅ |
| #10 | **HU-10** Modelos de proyectos, miembros del proyecto y tareas | 5 | Felipe | ✅ |
| #11 | **HU-11** Modelos de ideas, lienzos, actividad, notificaciones, métricas y comunicación | 5 | Felipe | ✅ |
| #12 | **HU-12** Permisos de trabajo en equipo (`visibles_para` / `puede_editar`) con pruebas | 5 | Felipe | ✅ |
| #13 | **HU-13** Soporte para MariaDB/MySQL desde `.env` | 1 | Felipe | ✅ |
| #14 | **HU-14** Administración de Django (`/admin`) para todas las tablas | 2 | Felipe | ✅ |
| #15 | **HU-15** Panel: estadísticas reales (proyectos activos, tareas completadas, vencidas) | 3 | Felipe | ✅ |
| #16 | **HU-16** Panel: actividad reciente y progreso de cada proyecto | 3 | Felipe | ✅ |
| #17 | **HU-17** Documentación del modelo de datos (diagrama ER y SQL) | 2 | Felipe | ✅ |

---

## Sprint 3 — Proyectos, tareas y analytics 🔜

**Fechas:** 23 – 27 nov 2026 · **Doliente:** Kevin · **Puntos:** 34

> **Sprint goal:** Que el equipo pueda gestionar sus proyectos y tareas
> desde la aplicación (crear, asignar, mover en el Kanban) respetando los
> permisos, y ver el avance en Analytics.

| Issue | Historia de usuario | Pts | Doliente | Prioridad |
|---|---|---|---|---|
| #18 | **HU-18** Listado de proyectos con filtros (Todos, Activos, Pendientes) | 3 | Kevin | Must |
| #19 | **HU-19** Crear, editar y eliminar proyectos, y cambiar su estado | 5 | Kevin | Must |
| #20 | **HU-20** Miembros del proyecto: agregar, quitar y cambiar el rol | 5 | Kevin | Must |
| #21 | **HU-21** Kanban del proyecto con arrastrar y soltar (guarda el estado) | 5 | Kevin | Must |
| #22 | **HU-22** Tareas: lista con estadísticas, filtros y búsqueda | 3 | Kevin | Must |
| #23 | **HU-23** Tareas: crear, editar, eliminar y asignar responsable | 5 | Kevin | Must |
| #24 | **HU-24** Analytics: indicadores y gráfico de tareas completadas (30 días) | 5 | Kevin | Should |
| #25 | **HU-25** Analytics: métricas frente a la meta y exportar a CSV | 3 | Kevin | Could |

> ⚠️ **Riesgo:** 34 puntos supera la capacidad (unos 30). Si el viernes no
> alcanza, **HU-25** (prioridad *Could*) pasa al Sprint 4.

---

## Sprint 4 — Colaboración, sitio y entrega ⏳

**Fechas:** 23 nov – 1 dic 2026 · **Doliente:** todo el equipo · **Puntos:** 57

Para llegar al **1 de diciembre**, este sprint corre **en paralelo** con el
Sprint 3: Yohan y Felipe empiezan el lunes 23 de noviembre, y Kevin se une
el lunes 30, al terminar el Sprint 3. Por eso Kevin solo lleva el despliegue
y lo compartido.

> **Sprint goal:** Completar el trabajo en equipo (ideas, canvas
> compartido, gestión de equipos), publicar el sitio y dejar el
> proyecto listo para desplegar y sustentar.

| Issue | Historia de usuario | Pts | Doliente | Prioridad |
|---|---|---|---|---|
| #26 | **HU-26** Canvas guardado en la base de datos con control de versión | 8 | Yohan | Must |
| #27 | **HU-27** Compartir un lienzo con personas, un equipo, un proyecto o toda la empresa | 5 | Yohan | Must |
| #28 | **HU-28** Página de inicio pública y páginas de información | 5 | Yohan | Should |
| #29 | **HU-29** Tablero de ideas en la base de datos (crear, votar, mover) | 8 | Felipe | Must |
| #30 | **HU-30** Gestión de usuarios de la empresa (crear, invitar, cambiar rol, desactivar) | 5 | Felipe | Must |
| #31 | **HU-31** Equipos: crear equipos y gestionar sus miembros | 5 | Felipe | Must |
| #32 | **HU-32** Notificaciones en la campana del panel | 3 | Felipe | Should |
| #33 | **HU-33** Perfil del usuario (foto, cargo, teléfono) y datos de la empresa | 5 | Yohan | Should |
| #34 | **HU-34** Configuración de despliegue (DEBUG apagado, `collectstatic`, MySQL) | 5 | Kevin | Must |
| #35 | **HU-35** Pruebas de punta a punta y corrección de errores | 5 | Todos | Must |
| #36 | **HU-36** Manual de usuario, README final y preparación de la sustentación | 3 | Todos | Must |

**Carga por persona:** Yohan 23 · Felipe 21 · Kevin 5 · compartido 8.
Yohan y Felipe tienen 7 días hábiles (unos 42 puntos de capacidad); Kevin,
2 días (unos 12).

> ⚠️ **Riesgo:** no hay margen después del 1 de diciembre. Si algo se
> atrasa, las primeras en salir son las de prioridad *Should*: HU-28
> (sitio público), HU-32 (notificaciones) y HU-33 (perfil).

---

## Product backlog (fuera de los sprints)

Ordenado por prioridad. Se planea después de la entrega o si sobra tiempo.

| Historia | Pts | Prioridad |
|---|---|---|
| **HU-37** Chat del equipo (mensajes directos y de equipo) | 8 | Should |
| **HU-38** Reuniones y calendario | 8 | Could |
| **HU-39** Asistente virtual con IA | 13 | Could |
| **HU-40** Tickets de soporte | 5 | Could |
| **HU-41** Iniciar sesión con Google | 5 | Could |
| **HU-42** Importar los datos de la base anterior (contraseñas bcrypt) | 5 | Could |
| **HU-43** Automatizaciones | 13 | Won't (por ahora) |

---

## Criterios de aceptación (Sprints 3 y 4)

**HU-18 Listado de proyectos**
- Solo aparecen los proyectos que la persona puede ver (`visibles_para`).
- Los filtros Todos, Activos y Pendientes cambian la lista sin perder la sesión.
- Muestra el progreso calculado (% de tareas completadas).

**HU-19 Crear, editar y eliminar proyectos**
- Solo quien puede editar (`puede_editar`) ve los botones de editar y eliminar.
- La fecha de fin no puede ser anterior a la de inicio.
- Cada cambio queda en la actividad reciente.

**HU-20 Miembros del proyecto**
- Solo se pueden agregar personas de la misma empresa.
- Roles: responsable, editor u observador (este último solo lee).

**HU-21 Kanban**
- Cuatro columnas: Por hacer, En progreso, En revisión, Completada.
- Al soltar una tarjeta, el estado se guarda en el servidor (con token CSRF).
- Un observador no puede mover tarjetas.

**HU-22 y HU-23 Tareas**
- Estadísticas: total, completadas, en progreso y vencidas.
- Filtros por estado, por proyecto y búsqueda por texto.
- Solo se asignan personas que trabajan en el proyecto.

**HU-24 y HU-25 Analytics**
- El gráfico usa `fecha_completada` de los últimos 30 días.
- Cada métrica muestra "Cumplida" o "En curso" frente a su meta.
- El CSV se descarga con los datos de la empresa de quien lo pide.

**HU-26 y HU-27 Canvas**
- El lienzo se carga y guarda desde la base de datos (`contenido` en JSON).
- Si dos personas guardan a la vez, la segunda recibe aviso y no pisa el trabajo de la otra (`version`).
- Un lector ve el lienzo pero no puede dibujar.

**HU-29 Ideas**
- Un voto por persona e idea; el total se cuenta.
- Las ideas son de la empresa, no del navegador (adiós a `localStorage`).

**HU-30 y HU-31 Usuarios y equipos**
- Solo Administrador o Manager pueden crear usuarios y equipos.
- Un equipo solo admite personas de su misma empresa.

**HU-34 Despliegue**
- `DEBUG=False`, `ALLOWED_HOSTS` configurado y `collectstatic` sin errores.
- Funciona con MariaDB 10.5+ o MySQL 8+.

---

## Definición de terminado (DoD)

Una historia está **terminada** cuando:

1. Cumple todos sus criterios de aceptación.
2. Tiene pruebas automáticas y `python manage.py test` pasa completo.
3. Funciona en modo claro y oscuro, y en móvil.
4. Respeta los permisos de trabajo en equipo.
5. Si cambia los modelos, incluye su migración.
6. Pasó revisión de código (pull request aprobado por otra persona).
7. Está unida a la rama del sprint.

## Ceremonias (sprints de 1 semana)

| Ceremonia | Cuándo | Duración |
|---|---|---|
| Sprint planning | Lunes, al inicio | 45 min |
| Daily | Todos los días | 15 min |
| Sprint review (demo) | Viernes | 30 min |
| Retrospectiva | Viernes, después de la review | 30 min |
