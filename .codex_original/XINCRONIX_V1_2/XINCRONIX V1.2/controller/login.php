<?php
session_start();

// ─── Prevenir acceso directo 
if (!defined('SECURE_ACCESS')) {
    define('SECURE_ACCESS', true);
}

// Cargar configuración y servicios
require_once __DIR__ . '/config.php';
require_once __DIR__ . '/../class/Response.php';
require_once __DIR__ . '/../class/Logger.php';

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: https://tudominio.com'); // ⚠️ pon aquí tu dominio real, no '*'
header('Access-Control-Allow-Credentials: true');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

// Manejar preflight CORS
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

// Solo acepta POST
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    Response::error('Método no permitido', 405);
}

// ─── Verificar conexión PDO 
if (!isset($GLOBALS['pdo']) || !($GLOBALS['pdo'] instanceof PDO)) {
    Logger::error('PDO no disponible en login.php');
    Response::serverError('Error de configuración del servidor');
}

$pdo = $GLOBALS['pdo'];

// 1. PROTECCIÓN BÁSICA CONTRA FUERZA BRUTA

$ip          = $_SERVER['REMOTE_ADDR'] ?? '0.0.0.0';
$sessionKey  = 'login_attempts_' . md5($ip);
$timeKey     = 'login_last_attempt_' . md5($ip);
$maxIntentos = 10;
$ventana     = 15 * 60; // 15 minutos

// Reiniciar contador si pasó la ventana de tiempo
if (isset($_SESSION[$timeKey]) && (time() - $_SESSION[$timeKey]) > $ventana) {
    $_SESSION[$sessionKey] = 0;
}

$intentos = $_SESSION[$sessionKey] ?? 0;

if ($intentos >= $maxIntentos) {
    $restante = $ventana - (time() - ($_SESSION[$timeKey] ?? time()));
    $minutos  = ceil($restante / 60);
    Logger::warning('Fuerza bruta detectada', ['ip' => $ip, 'intentos' => $intentos]);
    Response::error("Demasiados intentos fallidos. Espera {$minutos} minuto(s).", 429);
}

// RECIBIR Y VALIDAR CAMPOS

$email    = strtolower(trim($_POST['email']    ?? ''));
$password = $_POST['password']                ?? '';
$remember = isset($_POST['remember']) && $_POST['remember'] === '1';

$errores = [];

if (empty($email) || !filter_var($email, FILTER_VALIDATE_EMAIL))
    $errores['email'] = 'Ingresa un correo electrónico válido.';

if (empty($password) || mb_strlen($password) < 8)
    $errores['password'] = 'La contraseña debe tener al menos 8 caracteres.';

if (!empty($errores)) {
    Response::validationError($errores);
}

// 3. BUSCAR USUARIO EN BASE DE DATOS

try {
    $stmt = $pdo->prepare("
        SELECT
            u.id_usuario,
            u.nombres,
            u.apellidos,
            u.email,
            u.password,
            u.cargo,
            u.avatar,
            u.estado,
            u.id_empresa,
            u.id_roles,
            e.nombre  AS nombre_empresa,
            r.nombre  AS nombre_rol
        FROM   usuarios u
        LEFT JOIN empresa e ON e.id_empresa = u.id_empresa
        LEFT JOIN roles   r ON r.id_roles   = u.id_roles
        WHERE  u.email = :email
        LIMIT  1
    ");
    $stmt->execute([':email' => $email]);
    $user = $stmt->fetch();

} catch (PDOException $e) {
    Logger::error('BD Error (login select)', $e);  
    Response::serverError('Error del servidor. Inténtalo de nuevo más tarde.');
}

// Función auxiliar: registrar intento fallido
function registrarFallo(string $sessionKey, string $timeKey): void {
    $_SESSION[$sessionKey] = ($_SESSION[$sessionKey] ?? 0) + 1;
    $_SESSION[$timeKey]    = time();
}

// Usuario no encontrado
if (!$user) {
    registrarFallo($sessionKey, $timeKey);
    Logger::warning('Intento de login fallido', ['email' => $email]);
    Response::error('Correo o contraseña incorrectos.');
}

// Cuenta inactiva
if (!(bool) $user['estado']) {
    Logger::warning('Intento de login con cuenta inactiva', ['email' => $email]);
    Response::error('Tu cuenta está inactiva o pendiente de verificación. Revisa tu correo o contacta a soporte.');
}

// Verificar contraseña
if (!password_verify($password, $user['password'])) {
    registrarFallo($sessionKey, $timeKey);
    Logger::warning('Contraseña incorrecta', ['email' => $email]);
    Response::error('Correo o contraseña incorrectos.');
}

// 4. AUTENTICACIÓN EXITOSA

// Reiniciar contador de intentos
$_SESSION[$sessionKey] = 0;

// Regenerar ID de sesión para prevenir session fixation
session_regenerate_id(true);

// Guardar datos útiles en sesión
$_SESSION['user_id']        = (int) $user['id_usuario'];
$_SESSION['empresa_id']     = (int) $user['id_empresa'];
$_SESSION['rol_id']         = (int) $user['id_roles'];
$_SESSION['rol_nombre']     = $user['nombre_rol']     ?? 'Colaborador';
$_SESSION['nombre']         = trim($user['nombres'] . ' ' . $user['apellidos']);
$_SESSION['nombre_empresa'] = $user['nombre_empresa'] ?? '';
$_SESSION['email']          = $user['email'];
$_SESSION['cargo']          = $user['cargo']          ?? '';
$_SESSION['avatar']         = $user['avatar']         ?? '';
$_SESSION['login_time']     = time();

// Cookie "Recordar sesión" (30 días)
if ($remember) {
    $token    = bin2hex(random_bytes(32));
    $expire   = time() + 60 * 60 * 24 * 30;
    $secure   = isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off';
    $sameSite = 'Strict';

    setcookie('xnx_remember', $token, [
        'expires'  => $expire,
        'path'     => '/',
        'domain'   => '',
        'secure'   => $secure,
        'httponly' => true,
        'samesite' => $sameSite,
    ]);
}

// Determinar URL de redirección según rol
$redirectMap = [
    1 => '../view/Panel.html',
    2 => '../view/Panel.html',
    3 => '../view/Panel.html',
];
$redirect = $redirectMap[(int) $user['id_roles']] ?? '../view/Panel.html';

// Registrar login exitoso
Logger::success('Usuario login', [
    'user_id' => (int) $user['id_usuario'],
    'email' => $user['email'],
    'rol' => $user['nombre_rol']
]);

Response::success([
    'nombre' => $_SESSION['nombre'],
    'rol' => $_SESSION['rol_nombre'],
    'redirect' => $redirect,
    'user_id' => (int) $user['id_usuario']
], '¡Bienvenido, ' . htmlspecialchars($user['nombres'], ENT_QUOTES, 'UTF-8') . '!');