<?php
/**
 * registro.php — Controlador de registro empresarial
 * Ubicación: /controller/registro.php
 */

session_start();

// ─── Prevenir acceso directo ──────────────────────────────────
if (!defined('SECURE_ACCESS')) {
    define('SECURE_ACCESS', true);
}

// Cargar configuración y servicios
require_once __DIR__ . '/config.php';
require_once __DIR__ . '/../class/Response.php';
require_once __DIR__ . '/../class/Logger.php';

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

// Manejar preflight CORS
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    Response::error('Método no permitido', 405);
}

// ─── Verificar conexión PDO ──────────────────────────────────
if (!isset($GLOBALS['pdo']) || !($GLOBALS['pdo'] instanceof PDO)) {
    Logger::error('PDO no disponible en registro.php');
    Response::serverError('Error de configuración del servidor');
}

$pdo = $GLOBALS['pdo'];

/**
 * Sanitiza un string
 */
function sanitize(string $val): string {
    return htmlspecialchars(strip_tags(trim($val)), ENT_QUOTES, 'UTF-8');
}

/**
 * Genera respuesta JSON consistente
 */
function jsonResponse(array $data, int $code = 200): void {
    http_response_code($code);
    echo json_encode($data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    exit;
}

// ════════════════════════════════════════════════════════════
// RECIBIR Y VALIDAR DATOS
// ════════════════════════════════════════════════════════════
$nombre_empresa = sanitize($_POST['nombre_empresa'] ?? '');
$nit            = sanitize($_POST['nit']            ?? '');
$sector         = sanitize($_POST['sector']         ?? '');
$num_empleados  = sanitize($_POST['num_empleados']  ?? '');
$nombres        = sanitize($_POST['nombres']        ?? '');
$apellidos      = sanitize($_POST['apellidos']      ?? '');
$cargo          = sanitize($_POST['cargo']          ?? '');
$email          = strtolower(trim($_POST['email']   ?? ''));
$telefono       = sanitize($_POST['telefono']       ?? '');
$password       = $_POST['password']                ?? '';
$plan           = sanitize($_POST['plan']           ?? 'business');
$metodo_pago    = sanitize($_POST['metodo_pago']    ?? '');
$referencia     = sanitize($_POST['referencia']     ?? '');
$notas          = sanitize($_POST['notas']          ?? '');

$errores = [];

// Validaciones
if (empty($nombre_empresa) || mb_strlen($nombre_empresa) > 200)
    $errores['nombre_empresa'] = 'El nombre de la empresa es obligatorio (máx. 200 caracteres).';

if (empty($nit) || mb_strlen($nit) > 30)
    $errores['nit'] = 'El NIT/RUT es obligatorio (máx. 30 caracteres).';

if (empty($sector))
    $errores['sector'] = 'El sector es obligatorio.';

if (empty($num_empleados))
    $errores['num_empleados'] = 'El rango de empleados es obligatorio.';

if (empty($nombres))
    $errores['nombres'] = 'El nombre del administrador es obligatorio.';

if (empty($email) || !filter_var($email, FILTER_VALIDATE_EMAIL))
    $errores['email'] = 'El correo electrónico no es válido.';

if (mb_strlen($email) > 150)
    $errores['email'] = 'El correo no puede superar los 150 caracteres.';

if (empty($telefono))
    $errores['telefono'] = 'El teléfono es obligatorio.';

if (empty($password))
    $errores['password'] = 'La contraseña es obligatoria.';
elseif (mb_strlen($password) < 8)
    $errores['password'] = 'La contraseña debe tener mínimo 8 caracteres.';
elseif (mb_strlen($password) > 128)
    $errores['password'] = 'La contraseña no puede superar los 128 caracteres.';

$planesValidos = ['starter', 'business', 'enterprise'];
if (!in_array($plan, $planesValidos, true))
    $errores['plan'] = 'Plan de suscripción no válido.';

if (!empty($errores)) {
    jsonResponse([
        'status' => 'error',
        'type' => 'validation',
        'message' => 'Por favor corrige los errores.',
        'errors' => $errores
    ], 422);
}

// ════════════════════════════════════════════════════════════
// PROCESAR ARCHIVO (COMPROBANTE)
// ════════════════════════════════════════════════════════════
$ruta_comprobante = null;

if (isset($_FILES['comprobante']) && $_FILES['comprobante']['error'] !== UPLOAD_ERR_NO_FILE) {
    
    $file = $_FILES['comprobante'];
    
    if ($file['error'] !== UPLOAD_ERR_OK) {
        $uploadErrors = [
            UPLOAD_ERR_INI_SIZE   => 'El archivo supera el límite permitido por el servidor.',
            UPLOAD_ERR_FORM_SIZE  => 'El archivo supera el tamaño máximo del formulario.',
            UPLOAD_ERR_PARTIAL    => 'El archivo se subió de forma incompleta.',
            UPLOAD_ERR_NO_TMP_DIR => 'No se encontró el directorio temporal del servidor.',
            UPLOAD_ERR_CANT_WRITE => 'No se pudo escribir el archivo en el disco.',
        ];
        $msg = $uploadErrors[$file['error']] ?? 'Error desconocido al subir el archivo.';
        Logger::error('Error al subir comprobante', ['error_code' => $file['error']]);
        jsonResponse(['status' => 'error', 'message' => $msg], 400);
    }
    
    // Validar tipo MIME
    $finfo      = new finfo(FILEINFO_MIME_TYPE);
    $mimeReal   = $finfo->file($file['tmp_name']);
    $mimesOk    = ['application/pdf', 'image/png', 'image/jpeg'];
    $extOk      = ['pdf', 'png', 'jpg', 'jpeg'];
    $extArchivo = strtolower(pathinfo($file['name'], PATHINFO_EXTENSION));
    
    if (!in_array($mimeReal, $mimesOk, true) || !in_array($extArchivo, $extOk, true)) {
        jsonResponse(['status' => 'error', 'message' => 'El comprobante debe ser PDF, PNG o JPG.'], 400);
    }
    
    // Límite de 10 MB
    if ($file['size'] > 10 * 1024 * 1024) {
        jsonResponse(['status' => 'error', 'message' => 'El comprobante no puede superar los 10 MB.'], 400);
    }
    
    // Crear directorio si no existe
    $uploadDir = dirname(__DIR__) . '/uploads/comprobantes/';
    if (!is_dir($uploadDir) && !mkdir($uploadDir, 0755, true)) {
        Logger::error('No se pudo crear directorio de uploads', ['dir' => $uploadDir]);
        jsonResponse(['status' => 'error', 'message' => 'Error al guardar el archivo. Contacta a soporte.'], 500);
    }
    
    $nombreArchivo = 'comp_' . time() . '_' . bin2hex(random_bytes(6)) . '.' . $extArchivo;
    $rutaDestino   = $uploadDir . $nombreArchivo;
    
    if (!move_uploaded_file($file['tmp_name'], $rutaDestino)) {
        Logger::error('No se pudo mover archivo subido', ['ruta' => $rutaDestino]);
        jsonResponse(['status' => 'error', 'message' => 'No se pudo guardar el comprobante. Inténtalo de nuevo.'], 500);
    }
    
    $ruta_comprobante = 'uploads/comprobantes/' . $nombreArchivo;
}

// ════════════════════════════════════════════════════════════
// INICIAR TRANSACCIÓN
// ════════════════════════════════════════════════════════════
try {
    
    // Verificar email duplicado
    $stmt = $pdo->prepare("SELECT id_usuario FROM usuarios WHERE email = :email LIMIT 1");
    $stmt->execute([':email' => $email]);
    if ($stmt->fetch()) {
        Logger::warning('Intento de registro con email duplicado', ['email' => $email]);
        jsonResponse(['status' => 'error', 'message' => 'Ya existe una cuenta registrada con ese correo electrónico.'], 409);
    }
    
    // Verificar NIT duplicado
    $stmt = $pdo->prepare("SELECT id_empresa FROM empresa WHERE nit = :nit LIMIT 1");
    $stmt->execute([':nit' => $nit]);
    if ($stmt->fetch()) {
        Logger::warning('Intento de registro con NIT duplicado', ['nit' => $nit]);
        jsonResponse(['status' => 'error', 'message' => 'Ya existe una empresa registrada con ese NIT/RUT.'], 409);
    }
    
    // Iniciar transacción
    $pdo->beginTransaction();
    
    // Insertar empresa
    $stmt = $pdo->prepare("
        INSERT INTO empresa
            (nombre, nit, email, telefono, industria, plan_suscripcion,
             sector, administrador, num_empleados, comprobante, fecha_creacion)
        VALUES
            (:nombre, :nit, :email, :telefono, :industria, :plan,
             :sector, :administrador, :num_empleados, :comprobante, NOW())
    ");
    $stmt->execute([
        ':nombre'        => $nombre_empresa,
        ':nit'           => $nit,
        ':email'         => $email,
        ':telefono'      => $telefono,
        ':industria'     => $sector,
        ':plan'          => $plan,
        ':sector'        => $sector,
        ':administrador' => trim($nombres . ' ' . $apellidos),
        ':num_empleados' => $num_empleados,
        ':comprobante'   => $ruta_comprobante,
    ]);
    
    $id_empresa = (int) $pdo->lastInsertId();
    
    if (!$id_empresa) {
        throw new RuntimeException('No se obtuvo el ID de la empresa insertada.');
    }
    
    // Insertar usuario administrador
    $password_hash = password_hash($password, PASSWORD_BCRYPT, ['cost' => 12]);
    
    $stmt = $pdo->prepare("
        INSERT INTO usuarios
            (nombres, apellidos, email, password, cargo, telefono,
             id_empresa, id_roles, estado, fecha_creacion)
        VALUES
            (:nombres, :apellidos, :email, :password, :cargo, :telefono,
             :id_empresa, 1, 1, NOW())
    ");
    $stmt->execute([
        ':nombres'    => $nombres,
        ':apellidos'  => $apellidos ?: '-',
        ':email'      => $email,
        ':password'   => $password_hash,
        ':cargo'      => $cargo,
        ':telefono'   => $telefono,
        ':id_empresa' => $id_empresa,
    ]);
    
    // Registrar solicitud de pago
    $stmt = $pdo->prepare("
        INSERT INTO solicitudes_pago
            (id_empresa, plan, metodo_pago, referencia, notas,
             ruta_comprobante, estado, fecha_creacion)
        VALUES
            (:id_empresa, :plan, :metodo_pago, :referencia, :notas,
             :ruta_comprobante, 'pendiente', NOW())
    ");
    $stmt->execute([
        ':id_empresa'       => $id_empresa,
        ':plan'             => $plan,
        ':metodo_pago'      => $metodo_pago,
        ':referencia'       => $referencia,
        ':notas'            => $notas,
        ':ruta_comprobante' => $ruta_comprobante,
    ]);
    
    // Confirmar transacción
    $pdo->commit();
    
    Logger::success('Empresa registrada', [
        'empresa' => $nombre_empresa,
        'nit' => $nit,
        'plan' => $plan
    ]);
    
    jsonResponse([
        'status' => 'success',
        'message' => 'Registro completado. Tu solicitud está en revisión.',
        'data' => [
            'empresa_id' => $id_empresa
        ]
    ], 201);
    
} catch (PDOException $e) {
    // Revertir transacción
    if ($pdo->inTransaction()) {
        $pdo->rollBack();
    }
    
    // Eliminar archivo subido si la transacción falló
    if ($ruta_comprobante) {
        $rutaFisica = dirname(__DIR__) . '/' . $ruta_comprobante;
        if (file_exists($rutaFisica)) {
            @unlink($rutaFisica);
        }
    }
    
    Logger::error('BD Error (registro)', [
        'message' => $e->getMessage(),
        'code' => $e->getCode()
    ]);
    
    // Código 23000 = UNIQUE constraint violation
    if ((string) $e->getCode() === '23000') {
        jsonResponse(['status' => 'error', 'message' => 'Ya existe una cuenta con ese correo o NIT.'], 409);
    } else {
        jsonResponse(['status' => 'error', 'message' => 'Error al registrar la empresa. Por favor inténtalo de nuevo.'], 500);
    }
    
} catch (RuntimeException $e) {
    if ($pdo->inTransaction()) {
        $pdo->rollBack();
    }
    
    Logger::error('Runtime Error (registro)', ['message' => $e->getMessage()]);
    jsonResponse(['status' => 'error', 'message' => 'Error interno al procesar el registro. Inténtalo de nuevo.'], 500);
    
} catch (Exception $e) {
    if ($pdo->inTransaction()) {
        $pdo->rollBack();
    }
    
    Logger::error('Error inesperado (registro)', ['message' => $e->getMessage()]);
    jsonResponse(['status' => 'error', 'message' => 'Error inesperado. Contacta a soporte.'], 500);
}