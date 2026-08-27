@echo off
REM Script para configurar la aplicación Laravel - Xincronix

setlocal enabledelayedexpansion

echo =========================================
echo Iniciando configuracion de Xincronix
echo =========================================
echo.

REM Generar key de aplicación
echo 1. Generando clave de aplicación...
php artisan key:generate
echo ✓ Clave generada
echo.

REM Ejecutar migraciones
echo 2. Ejecutando migraciones...
php artisan migrate:fresh
echo ✓ Migraciones completadas
echo.

REM Ejecutar seeders
echo 3. Cargando datos de prueba...
php artisan db:seed
echo ✓ Datos de prueba cargados
echo.

echo =========================================
echo ✓ Configuracion completada exitosamente
echo =========================================
echo.
echo Usuarios de prueba creados:
echo   - admin@xincronix.com / password123 [Admin]
echo   - manager@xincronix.com / password123 [Manager]
echo   - carlos@xincronix.com / password123 [Colaborador]
echo   - ana@xincronix.com / password123 [Colaborador]
echo   - pedro@xincronix.com / password123 [Colaborador]
echo.
echo Para iniciar el servidor:
echo   php artisan serve
echo.
pause
