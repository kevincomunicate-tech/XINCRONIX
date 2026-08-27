<?php
if (!defined('SECURE_ACCESS')) {
    define('SECURE_ACCESS', true);
}

$envFile = __DIR__ . '/../.env';
if (file_exists($envFile)) {
    $lines = file($envFile, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    foreach ($lines as $line) {
        if (strpos(trim($line), '#') === 0) continue;
        if (strpos($line, '=') !== false) {
            list($name, $value) = explode('=', $line, 2);
            $name = trim($name);
            $value = trim($value);
            if (!array_key_exists($name, $_ENV)) {
                putenv("$name=$value");
                $_ENV[$name] = $value;
            }
        }
    }
}

require_once __DIR__ . '/../class/Response.php';
require_once __DIR__ . '/../class/Logger.php';

define('DB_HOST',     getenv('DB_HOST')     ?: 'localhost');
define('DB_PORT',     getenv('DB_PORT')     ?: '3306');
define('DB_NAME',     getenv('DB_DATABASE') ?: 'xincronix_bd');
define('DB_USER',     getenv('DB_USERNAME') ?: 'root');
define('DB_PASS',     getenv('DB_PASSWORD') ?: '');
define('DB_CHARSET',  'utf8mb4');

$pdoOptions = [
    PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
    PDO::ATTR_EMULATE_PREPARES   => false,
    PDO::MYSQL_ATTR_INIT_COMMAND => "SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci",
];

try {
    $dsn = sprintf(
        'mysql:host=%s;port=%s;dbname=%s;charset=%s',
        DB_HOST, DB_PORT, DB_NAME, DB_CHARSET
    );
    
    $pdo = new PDO($dsn, DB_USER, DB_PASS, $pdoOptions);
    
    // Hacer $pdo disponible globalmente
    $GLOBALS['pdo'] = $pdo;
    
} catch (PDOException $e) {
    Logger::error("BD connection error", ['message' => $e->getMessage()]);
    Response::serverError("No se pudo conectar a la base de datos");
    exit;
}