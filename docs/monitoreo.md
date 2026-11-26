# Panel de monitoreo del superadministrador

Ruta: **`/administracion/monitoreo/`**. En el menú aparece como **Monitoreo**.

Solo entra el **superusuario** (`is_superuser`): la ruta está dentro de `/administracion/`,
que exige ser superusuario en `cuentas/politica.py` y en el decorador `administrador`.

- Un usuario normal recibe **403**.
- Quien no ha iniciado sesión va al login.

El panel es de **solo lectura**. Lo único que modifica es cerrar sesiones.
Para cambiar usuarios se usa la pantalla de Administración.

## Pestañas

| Pestaña | Qué muestra |
|---|---|
| **Resumen** | Tarjetas (usuarios, proyectos, tareas), tamaño de la base, número de tablas y filas, sesiones activas, versión de Django. También **alertas** (tareas vencidas, proyectos sin tareas, cuentas desactivadas…), **distribución** (usuarios por perfil, tareas por estado…), **gráficas** de los últimos días y lo más **reciente** (registros, inicios de sesión, eventos) |
| **Tablas** | Todas las tablas de la base agrupadas, con su número de filas. Marca en rojo las que **faltan** (falta correr `migrate`) y lista las **tablas sin modelo** (tablas viejas que Django no usa) |
| **Tabla** (al pulsar *Ver*) | Las filas, con buscador y paginación. **Estructura** muestra columnas, tipos, nulos, únicos y relaciones. **Exportar CSV** descarga la tabla |
| **Registro** (al pulsar un id) | Todos los campos de una fila y cuántos registros de otras tablas apuntan a ella. Por ejemplo, las tareas de un proyecto, con enlace para verlas |
| **Sesiones** | Quién tiene la sesión abierta y cuándo vence. Permite **cerrar** una sesión, cerrar **todas** las de un usuario o **borrar las vencidas**. Tu propia sesión no se puede cerrar desde aquí |
| **Sistema** | Motor y versión de la base, servidor, tamaño, Django y Python, `DEBUG`, zona horaria y Google. También el resultado de `manage.py check` y las **migraciones** de cada app: aplicadas, con su fecha, y pendientes |

## Privacidad: lo que nunca se muestra

- Los campos sensibles se ven como `••••••` y **no se exportan** al CSV, ni siquiera la columna. Por ejemplo: `password`, tokens, secretos y claves de sesión.
- Las sesiones se muestran con una **huella**: un resumen que no permite reconstruir la clave. La clave real es la cookie `sessionid`.
- Algunas tablas solo se **cuentan** y no se abren fila por fila: `django_session` y los tokens de Google.

## Todo se configura en `config/monitoreo.json`

El código no tiene nada escrito a mano sobre qué mostrar: lee el JSON.

| Clave | Para qué | Ejemplo |
|---|---|---|
| `filas_por_pagina` | Filas por página en cada tabla | `25` |
| `dias_grafica` | Días que muestran las gráficas | `14` |
| `actividad_reciente` | Elementos en "lo más reciente" | `8` |
| `campos_ocultos.nombres` | Campos que nunca se muestran (nombre exacto) | `"password"` |
| `campos_ocultos.contienen` | Oculta todo campo cuyo nombre contenga ese texto | `"token"` |
| `tablas_solo_conteo.modelos` | Tablas que no se abren fila por fila | `"sessions.session"` |
| `grupos` | Nombre de cada grupo de tablas (por app) | `"dashboard": "Proyectos y trabajo"` |
| `tarjetas` | Tarjetas del resumen, con un detalle filtrado | Usuarios → "activos" |
| `alertas` | Conteos que conviene vigilar; `nivel`: danger, warning, info, secondary, success, primary | Tareas vencidas |
| `distribuciones` | Barras "X por Y" | `"campo": "perfil"` |
| `graficas` | Registros por día según un campo de fecha | `"campo_fecha": "date_joined"` |
| `recientes` | Últimos registros según un campo de fecha | Últimos inicios de sesión |

Los modelos se escriben como `app.modelo`, en minúsculas: `cuentas.usuario`,
`dashboard.tarea`. Los filtros usan la misma sintaxis que Django
(`campo__isnull`, `campo__lt`…). Además aceptan dos valores especiales:

- `"@hoy"`: la fecha de hoy.
- `"@ahora"`: la fecha y la hora actuales.

### Ejemplo: agregar una alerta

```json
{"texto": "Notificaciones sin leer", "nivel": "info", "modelo": "dashboard.notificacion",
 "filtro": {"leida": false}}
```

Después de editar el JSON:

1. Corre `python manage.py check`. Si algo está mal escrito, avisa con el error
   `administracion.E001` y dice qué falta: un modelo que no existe, un campo mal
   escrito o un nivel inválido.
2. Reinicia `runserver`, porque el archivo se lee una sola vez al arrancar.

## Funciona con SQLite, MariaDB/MySQL y PostgreSQL

La versión y el tamaño de la base se piden con una consulta propia de cada motor.
Están en `SQL_VERSION` y `SQL_TAMANO` de `administracion/monitoreo.py`.

Si una tabla no existe, el panel **no se rompe**: la marca como "falta la tabla"
y sigue con las demás.

## Archivos

| Archivo | Qué hace |
|---|---|
| `config/monitoreo.json` | Las reglas: qué se ve y qué se oculta |
| `administracion/monitoreo.py` | Lee y valida el JSON y hace las consultas, todas de solo lectura |
| `administracion/views_monitoreo.py` | Las vistas de cada pestaña, el CSV y el cierre de sesiones |
| `administracion/checks.py` | Revisa el JSON en `manage.py check` |
| `administracion/templates/administracion/monitoreo/` | Las plantillas |
| `administracion/test_monitoreo.py` | Pruebas: acceso, privacidad, filtros, sesiones y JSON |
