# 🚀 Guía de Uso - Xincronix API

## Instalación y Configuración Inicial

### 1. Configuración Rápida (Windows)
Ejecuta el script `setup.bat`:
```bash
setup.bat
```

### 2. Configuración Rápida (Linux/Mac)
Ejecuta el script `setup.sh`:
```bash
bash setup.sh
```

### 3. Configuración Manual
Si prefieres hacer los pasos uno a uno:

```bash
# Generar clave de aplicación
php artisan key:generate

# Crear base de datos (si es necesario)
# Crear base de datos en tu servidor MySQL/PostgreSQL

# Ejecutar migraciones
php artisan migrate:fresh

# Cargar datos de prueba
php artisan db:seed

# Iniciar servidor
php artisan serve
```

## Base de Datos

La aplicación usa las siguientes tablas:
- `empresa` - Empresas registradas
- `usuarios` - Usuarios del sistema
- `roles` - Roles de usuarios (Administrador, Manager, Colaborador)
- `perfiles_especificos` - Perfiles profesionales
- `equipos` - Equipos de trabajo
- `proyecto` - Proyectos
- `tareas` - Tareas del proyecto
- `reuniones` - Reuniones programadas
- `mensajes` - Mensajes entre usuarios
- `notificaciones` - Notificaciones
- `calendario` - Eventos de calendario
- `solicitudes_pago` - Solicitudes de pago
- `tickets_soporte` - Tickets de soporte
- `metrica_rendimiento` - Métricas de rendimiento

## Autenticación

### Endpoint: POST /api/login
**Descripción:** Inicio de sesión

**Request:**
```json
{
  "email": "admin@xincronix.com",
  "password": "password123",
  "remember": false
}
```

**Response:**
```json
{
  "success": true,
  "message": "Bienvenido, Juan!",
  "data": {
    "token": "1|abcd1234...",
    "token_type": "Bearer",
    "redirect": "/Panel",
    "usuario": {
      "id_usuario": 1,
      "nombre": "Juan Administrador",
      "email": "admin@xincronix.com",
      "id_empresa": 1,
      "empresa": "Xincronix Solutions",
      "id_roles": 1,
      "rol": "Administrador"
    }
  }
}
```

### Endpoint: POST /api/logout
**Descripción:** Cerrar sesión

**Headers:**
```
Authorization: Bearer {token}
```

**Response:**
```json
{
  "success": true,
  "message": "Sesion cerrada",
  "data": null
}
```

### Endpoint: GET /api/me
**Descripción:** Obtener información del usuario autenticado

**Headers:**
```
Authorization: Bearer {token}
```

## Recursos API

### Usuarios
```
GET    /api/usuarios           - Listar usuarios
POST   /api/usuarios           - Crear usuario
GET    /api/usuarios/{id}      - Obtener usuario
PUT    /api/usuarios/{id}      - Actualizar usuario
DELETE /api/usuarios/{id}      - Eliminar usuario
```

### Proyectos
```
GET    /api/proyectos                      - Listar proyectos
POST   /api/proyectos                      - Crear proyecto
GET    /api/proyectos/{id}                 - Obtener proyecto
PUT    /api/proyectos/{id}                 - Actualizar proyecto
DELETE /api/proyectos/{id}                 - Eliminar proyecto
GET    /api/proyectos/{id}/kanban          - Vista Kanban del proyecto
PATCH  /api/proyectos/{id}/estado          - Cambiar estado del proyecto
```

### Tareas
```
GET    /api/tareas                         - Listar tareas
POST   /api/tareas                         - Crear tarea
GET    /api/tareas/{id}                    - Obtener tarea
PUT    /api/tareas/{id}                    - Actualizar tarea
DELETE /api/tareas/{id}                    - Eliminar tarea
GET    /api/tareas/init                    - Inicializar tareas
PATCH  /api/tareas/{id}/mover              - Mover tarea entre estados
```

### Empresas
```
GET    /api/empresas           - Listar empresas
POST   /api/empresas           - Crear empresa
GET    /api/empresas/{id}      - Obtener empresa
PUT    /api/empresas/{id}      - Actualizar empresa
DELETE /api/empresas/{id}      - Eliminar empresa
```

### Equipos
```
GET    /api/equipos            - Listar equipos
POST   /api/equipos            - Crear equipo
GET    /api/equipos/{id}       - Obtener equipo
PUT    /api/equipos/{id}       - Actualizar equipo
DELETE /api/equipos/{id}       - Eliminar equipo
```

### Mensajes
```
GET    /api/mensajes           - Listar mensajes
POST   /api/mensajes           - Crear mensaje
GET    /api/mensajes/{id}      - Obtener mensaje
PUT    /api/mensajes/{id}      - Actualizar mensaje
DELETE /api/mensajes/{id}      - Eliminar mensaje
GET    /api/mensajes/equipo    - Mensajes del equipo
GET    /api/mensajes/no-leidos - Mensajes no leídos
```

### Notificaciones
```
GET    /api/notificaciones     - Listar notificaciones
POST   /api/notificaciones     - Crear notificación
GET    /api/notificaciones/{id} - Obtener notificación
PUT    /api/notificaciones/{id} - Actualizar notificación
DELETE /api/notificaciones/{id} - Eliminar notificación
```

### Reuniones
```
GET    /api/reuniones          - Listar reuniones
POST   /api/reuniones          - Crear reunión
GET    /api/reuniones/{id}     - Obtener reunión
PUT    /api/reuniones/{id}     - Actualizar reunión
DELETE /api/reuniones/{id}     - Eliminar reunión
```

### Calendario
```
GET    /api/calendario         - Listar eventos
POST   /api/calendario         - Crear evento
GET    /api/calendario/{id}    - Obtener evento
PUT    /api/calendario/{id}    - Actualizar evento
DELETE /api/calendario/{id}    - Eliminar evento
```

### Roles
```
GET    /api/roles              - Listar roles
POST   /api/roles              - Crear rol
GET    /api/roles/{id}         - Obtener rol
PUT    /api/roles/{id}         - Actualizar rol
DELETE /api/roles/{id}         - Eliminar rol
```

### Tickets de Soporte
```
GET    /api/tickets-soporte    - Listar tickets
POST   /api/tickets-soporte    - Crear ticket
GET    /api/tickets-soporte/{id} - Obtener ticket
PUT    /api/tickets-soporte/{id} - Actualizar ticket
DELETE /api/tickets-soporte/{id} - Eliminar ticket
```

### Solicitudes de Pago
```
GET    /api/solicitudes-pago   - Listar solicitudes
POST   /api/solicitudes-pago   - Crear solicitud
GET    /api/solicitudes-pago/{id} - Obtener solicitud
PUT    /api/solicitudes-pago/{id} - Actualizar solicitud
DELETE /api/solicitudes-pago/{id} - Eliminar solicitud
```

### Métricas de Rendimiento
```
GET    /api/metricas-rendimiento  - Listar métricas
POST   /api/metricas-rendimiento  - Crear métrica
GET    /api/metricas-rendimiento/{id} - Obtener métrica
PUT    /api/metricas-rendimiento/{id} - Actualizar métrica
DELETE /api/metricas-rendimiento/{id} - Eliminar métrica
```

## Ejemplos de Uso

### Crear un Proyecto
```bash
curl -X POST http://localhost:8000/api/proyectos \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Mi Nuevo Proyecto",
    "descripcion": "Descripción del proyecto",
    "estado": "Planeación",
    "fecha_inicio": "2024-06-21",
    "fecha_fin": "2024-08-21",
    "id_equipo": 1
  }'
```

### Crear una Tarea
```bash
curl -X POST http://localhost:8000/api/tareas \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "Nueva Tarea",
    "descripcion": "Descripción de la tarea",
    "estado": "Pendiente",
    "prioridad": "Alta",
    "fecha_vencimiento": "2024-06-28",
    "id_proyecto": 1,
    "id_usuario": 3,
    "id_equipo": 1
  }'
```

### Enviar un Mensaje
```bash
curl -X POST http://localhost:8000/api/mensajes \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "asunto": "Asunto del mensaje",
    "mensaje": "Contenido del mensaje",
    "id_destinatario": 2
  }'
```

## Paginación

Todos los endpoints GET (excepto show) soportan paginación:

```
GET /api/usuarios?limit=20&page=1
```

**Respuesta paginada:**
```json
{
  "success": true,
  "message": "Registros obtenidos",
  "data": [
    { ... },
    { ... }
  ],
  "pagination": {
    "total": 100,
    "per_page": 20,
    "current_page": 1,
    "last_page": 5
  }
}
```

## Códigos de Estado HTTP

- `200` - OK
- `201` - Creado
- `400` - Solicitud inválida
- `401` - No autenticado
- `403` - No autorizado
- `404` - No encontrado
- `422` - Error de validación
- `429` - Demasiadas solicitudes
- `500` - Error del servidor

## Estructura de Respuesta

**Éxito:**
```json
{
  "success": true,
  "message": "Mensaje de éxito",
  "data": { ... },
  "pagination": { ... }
}
```

**Error:**
```json
{
  "success": false,
  "message": "Mensaje de error",
  "data": null,
  "errors": { ... }
}
```

## Relaciones Entre Modelos

### Empresa
- ✅ Usuarios (1:N)
- ✅ Proyectos (1:N)
- ✅ Equipos (1:N)
- ✅ SolicitudesPago (1:N)
- ✅ TicketsSoporte (1:N)

### Usuario
- ✅ Empresa (N:1)
- ✅ Rol (N:1)
- ✅ PerfilEspecifico (N:1)
- ✅ Tareas (1:N)
- ✅ MensajesEnviados (1:N)
- ✅ MensajesRecibidos (1:N)
- ✅ Notificaciones (1:N)
- ✅ Reuniones (1:N)
- ✅ CalendarioEventos (1:N)
- ✅ MetricasRendimiento (1:N)

### Proyecto
- ✅ Empresa (N:1)
- ✅ Equipo (N:1)
- ✅ Tareas (1:N)

### Tarea
- ✅ Proyecto (N:1)
- ✅ Usuario (N:1)
- ✅ Equipo (N:1)

### Equipo
- ✅ Empresa (N:1)
- ✅ Proyectos (1:N)
- ✅ Tareas (1:N)
- ✅ Reuniones (1:N)

## Variables de Entorno

Configurar en `.env`:

```
APP_NAME=Xincronix
APP_ENV=local
APP_DEBUG=true
APP_URL=http://localhost:8000

DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=xincronix
DB_USERNAME=root
DB_PASSWORD=

SANCTUM_STATEFUL_DOMAINS=localhost:3000

MAIL_FROM_ADDRESS=noreply@xincronix.com
```

## Solución de Problemas

### Error: "No existe la tabla"
```bash
php artisan migrate:fresh
```

### Error: "No autenticado"
Asegúrate de incluir el header:
```
Authorization: Bearer {token}
```

### Error: "Demasiadas solicitudes (429)"
Espera 15 minutos antes de intentar nuevamente (rate limiter activo en login).

### Error: "Validación fallida (422)"
Verifica que todos los campos requeridos sean válidos y del tipo correcto.

## Soporte

Para reportar errores o sugerencias, revisa los logs:
```bash
tail -f storage/logs/laravel.log
```

---

**Última actualización:** Junio 21, 2024
