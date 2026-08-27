<?php
/**
 * Gestión de Headers CORS y Seguridad
 * Se ejecuta en cada request para aplicar headers globales
 */

// Habilitar CORS
header('Access-Control-Allow-Origin: ' . (getenv('APP_URL') ?: '*'));
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization, X-CSRF-Token, X-Requested-With');
header('Access-Control-Max-Age: 86400');
header('Access-Control-Allow-Credentials: true');

// Manejar request OPTIONS (preflight de CORS)
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

// Headers de seguridad
header('X-Content-Type-Options: nosniff');
header('X-Frame-Options: SAMEORIGIN');
header('X-XSS-Protection: 1; mode=block');
header('Referrer-Policy: strict-origin-when-cross-origin');
header('Permissions-Policy: geolocation=(), microphone=(), camera=()');

// Prevenir cacheo en desarrollo
if (getenv('APP_DEBUG') === 'true') {
    header('Cache-Control: no-store, no-cache, must-revalidate, max-age=0');
    header('Pragma: no-cache');
    header('Expires: Thu, 01 Jan 1970 00:00:00 GMT');
}
?>
