#!/bin/bash
# Script para configurar la aplicación Laravel - Xincronix

echo "========================================="
echo "Iniciando configuración de Xincronix"
echo "========================================="
echo ""

# Generar key de aplicación
echo "1. Generando clave de aplicación..."
php artisan key:generate
echo "✅ Clave generada"
echo ""

# Ejecutar migraciones
echo "2. Ejecutando migraciones..."
php artisan migrate:fresh
echo "✅ Migraciones completadas"
echo ""

# Ejecutar seeders
echo "3. Cargando datos de prueba..."
php artisan db:seed
echo "✅ Datos de prueba cargados"
echo ""

echo "========================================="
echo "✅ Configuración completada exitosamente"
echo "========================================="
echo ""
echo "Usuarios de prueba creados:"
echo "  - admin@xincronix.com / password123 (Admin)"
echo "  - manager@xincronix.com / password123 (Manager)"
echo "  - carlos@xincronix.com / password123 (Colaborador)"
echo "  - ana@xincronix.com / password123 (Colaborador)"
echo "  - pedro@xincronix.com / password123 (Colaborador)"
echo ""
echo "Para iniciar el servidor:"
echo "  php artisan serve"
echo ""
