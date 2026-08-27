# 🚀 Xincronix - Sistema de Gestión Integrada

[![Laravel](https://img.shields.io/badge/Laravel-11.x-red?style=flat&logo=laravel)](https://laravel.com)
[![PHP](https://img.shields.io/badge/PHP-8.2+-blue?style=flat&logo=php)](https://www.php.net)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📋 Descripción

Xincronix es una plataforma integral de gestión empresarial construida con Laravel 11 que permite:

- ✅ Gestión de empresas y usuarios con control de acceso basado en roles
- ✅ Administración de proyectos, equipos y tareas
- ✅ Planificación de reuniones y eventos
- ✅ Sistema de mensajería interna
- ✅ Notificaciones en tiempo real
- ✅ Seguimiento de tickets de soporte
- ✅ Gestión de solicitudes de pago
- ✅ Análisis de métricas de rendimiento
- ✅ API RESTful con autenticación Sanctum

## 🚀 Inicio Rápido

### Windows
```bash
setup.bat
```

### Linux/Mac
```bash
bash setup.sh
```

### Manual
```bash
php artisan migrate:fresh
php artisan db:seed
php artisan serve
```

## 🔐 Usuarios de Prueba

| Email | Contraseña | Rol |
|-------|-----------|-----|
| admin@xincronix.com | password123 | Administrador |
| manager@xincronix.com | password123 | Manager |
| carlos@xincronix.com | password123 | Colaborador |

## 📚 Documentación

- [API Guide](API_GUIDE.md) - Documentación de endpoints
- [Migration Summary](MIGRATION_SUMMARY.md) - Detalles de la migración
- [Laravel Docs](https://laravel.com/docs) - Documentación oficial

## 🏗️ Características

✅ Multi-empresa
✅ Control de acceso por roles
✅ Gestión de proyectos Kanban
✅ Sistema de tareas
✅ Reuniones programadas
✅ Mensajería interna
✅ Notificaciones
✅ Calendario de eventos
✅ Tickets de soporte
✅ Solicitudes de pago
✅ Métricas de rendimiento
✅ API RESTful

## 📊 Modelos de Datos

- Empresa
- Usuario
- Rol
- PerfilEspecifico
- Equipo
- Proyecto
- Tarea
- Reunión
- Mensaje
- Notificación
- Calendario
- SolicitudPago
- TicketSoporte
- MetricaRendimiento

## 🔌 Endpoints Principales

```
POST   /api/login
GET    /api/me
POST   /api/logout
CRUD   /api/usuarios
CRUD   /api/proyectos
CRUD   /api/tareas
CRUD   /api/empresas
CRUD   /api/equipos
CRUD   /api/reuniones
CRUD   /api/mensajes
CRUD   /api/notificaciones
```

## 📝 Cambios Realizados

- ✅ 15 Modelos con relaciones completas
- ✅ 18 Migraciones de BD
- ✅ 14 Seeders con datos de prueba
- ✅ 15 Controladores API
- ✅ Autenticación Sanctum
- ✅ Rate limiting
- ✅ Validación de datos
- ✅ Paginación

## 📄 Licencia

MIT License - Ver [LICENSE](LICENSE)

---

**Estado:** ✅ Producción
**Versión:** 1.0.0
**Última actualización:** Junio 21, 2024
