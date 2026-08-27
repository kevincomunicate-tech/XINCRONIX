<?php
/**
 * dashboard.php — Controlador del Dashboard (VERSIÓN DEBUG)
 * Ubicación: /controller/dashboard.php
 */

// ⚡ Activar reporte de errores para depuración
error_reporting(E_ALL);
ini_set('display_errors', 0); // No mostrar en pantalla, pero sí en log
ini_set('log_errors', 1);

session_start();

// Cargar configuración y servicios
require_once __DIR__ . '/config.php';

// Si no existe Response.php, crear uno básico
if (file_exists(__DIR__ . '/../class/Response.php')) {
    require_once __DIR__ . '/../class/Response.php';
} else {
    // Response básico de emergencia
    class Response {
        public static function success($data, $message = 'OK', $code = 200) {
            http_response_code($code);
            echo json_encode([
                'status' => 'success',
                'message' => $message,
                'data' => $data
            ], JSON_UNESCAPED_UNICODE);
            exit;
        }
        
        public static function error($message, $code = 400) {
            http_response_code($code);
            echo json_encode([
                'status' => 'error',
                'message' => $message
            ], JSON_UNESCAPED_UNICODE);
            exit;
        }
        
        public static function serverError($message = 'Error interno') {
            self::error($message, 500);
        }
    }
}

if (file_exists(__DIR__ . '/../class/Logger.php')) {
    require_once __DIR__ . '/../class/Logger.php';
}

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
header('Access-Control-Allow-Credentials: true');

// Manejar preflight CORS
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

// Solo acepta GET
if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
    Response::error('Método no permitido', 405);
}

// Verificar conexión PDO
if (!isset($GLOBALS['pdo']) || !($GLOBALS['pdo'] instanceof PDO)) {
    // Intentar conexión de emergencia
    try {
        $pdo = new PDO(
            'mysql:host=localhost;port=3306;dbname=xincronix_bd;charset=utf8mb4',
            'root',
            '',
            [
                PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
                PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
                PDO::ATTR_EMULATE_PREPARES => false
            ]
        );
        $GLOBALS['pdo'] = $pdo;
    } catch (PDOException $e) {
        Response::error('Error de conexión a la base de datos: ' . $e->getMessage(), 500);
    }
}

$pdo = $GLOBALS['pdo'];

// ════════════════════════════════════════════════════════════
// DEBUG: Mostrar estado de la sesión
// ════════════════════════════════════════════════════════════
$sessionDebug = [
    'session_id' => session_id(),
    'session_status' => session_status(),
    'user_id' => $_SESSION['user_id'] ?? 'NO DEFINIDO',
    'empresa_id' => $_SESSION['empresa_id'] ?? 'NO DEFINIDO',
    'nombre' => $_SESSION['nombre'] ?? 'NO DEFINIDO',
    'email' => $_SESSION['email'] ?? 'NO DEFINIDO',
    'todas_las_variables' => array_keys($_SESSION)
];

// Si no hay sesión, devolver datos de ejemplo para pruebas
if (!isset($_SESSION['user_id']) || !isset($_SESSION['empresa_id'])) {
    
    // ⚡ CAMBIO: En lugar de devolver error, devolver datos de ejemplo
    // Así podemos ver si el frontend funciona
    
    $dashboard = [
        'usuario' => [
            'nombre' => 'Usuario Demo',
            'cargo' => 'Administrador',
            'email' => 'demo@xincronix.com',
            'avatar' => null,
            'empresa' => 'Empresa Demo',
            'rol' => 'Administrador'
        ],
        'estadisticas' => [
            'proyectos_activos' => 12,
            'proyectos_este_mes' => 2,
            'tareas_completadas' => 94,
            'tareas_esta_semana' => 15,
            'agentes_activos' => 3,
            'agentes_en_espera' => 1,
            'issues_abiertos' => 7
        ],
        'actividades' => [
            [
                'tipo' => 'tarea_completada',
                'usuario' => 'Ana López',
                'descripcion' => 'completó la tarea',
                'detalle' => 'Diseño de sistema v1',
                'tiempo_relativo' => 'hace 12 min'
            ],
            [
                'tipo' => 'tarea_completada',
                'usuario' => 'Agente Redactor',
                'descripcion' => 'generó el informe',
                'detalle' => 'Q1 2025',
                'tiempo_relativo' => 'hace 32 min'
            ],
            [
                'tipo' => 'ticket_abierto',
                'usuario' => 'Juan Castro',
                'descripcion' => 'abrió un issue en',
                'detalle' => 'API exportación CSV',
                'tiempo_relativo' => 'hace 1h'
            ],
            [
                'tipo' => 'tarea_completada',
                'usuario' => 'Agente Analítico',
                'descripcion' => 'detectó cuello de botella en',
                'detalle' => 'Sprint 14',
                'tiempo_relativo' => 'hace 2h'
            ],
            [
                'tipo' => 'tarea_completada',
                'usuario' => 'María Ruiz',
                'descripcion' => 'subió archivos al proyecto',
                'detalle' => 'Dashboard v2',
                'tiempo_relativo' => 'hace 3h'
            ]
        ],
        'proyectos' => [
            [
                'nombre' => 'Dashboard v2',
                'porcentaje' => 72,
                'total_tareas' => 25,
                'tareas_completadas' => 18
            ],
            [
                'nombre' => 'API Exportación',
                'porcentaje' => 45,
                'total_tareas' => 20,
                'tareas_completadas' => 9
            ],
            [
                'nombre' => 'Modelo IA tickets',
                'porcentaje' => 91,
                'total_tareas' => 33,
                'tareas_completadas' => 30
            ]
        ],
        'debug' => $sessionDebug,
        'modo' => 'DEMO - Sin sesión activa'
    ];
    
    Response::success($dashboard, 'Dashboard cargado en modo demo (sin sesión)');
}

// Si hay sesión, obtener datos reales de la BD
$id_empresa = (int) $_SESSION['empresa_id'];
$id_usuario = (int) $_SESSION['user_id'];

try {
    // ════════════════════════════════════════════════════════════
    // 1. ESTADÍSTICAS GENERALES
    // ════════════════════════════════════════════════════════════
    
    // Proyectos activos
    $stmt = $pdo->prepare("
        SELECT COUNT(*) as total
        FROM proyecto
        WHERE id_empresa = :id_empresa
          AND estado = 'Activo'
    ");
    $stmt->execute([':id_empresa' => $id_empresa]);
    $proyectosActivos = (int) $stmt->fetch()['total'];

    // Proyectos creados este mes
    $stmt = $pdo->prepare("
        SELECT COUNT(*) as total
        FROM proyecto
        WHERE id_empresa = :id_empresa
          AND MONTH(fecha_inicio) = MONTH(CURRENT_DATE())
          AND YEAR(fecha_inicio) = YEAR(CURRENT_DATE())
    ");
    $stmt->execute([':id_empresa' => $id_empresa]);
    $proyectosEsteMes = (int) $stmt->fetch()['total'];

    // Tareas completadas
    $stmt = $pdo->prepare("
        SELECT COUNT(*) as total
        FROM tareas t
        INNER JOIN proyecto p ON t.id_proyecto = p.id_proyecto
        WHERE p.id_empresa = :id_empresa
          AND t.estado = 'Completada'
    ");
    $stmt->execute([':id_empresa' => $id_empresa]);
    $tareasCompletadas = (int) $stmt->fetch()['total'];

    // Tareas completadas esta semana
    $stmt = $pdo->prepare("
        SELECT COUNT(*) as total
        FROM tareas t
        INNER JOIN proyecto p ON t.id_proyecto = p.id_proyecto
        WHERE p.id_empresa = :id_empresa
          AND t.estado = 'Completada'
          AND YEARWEEK(t.fecha_vencimiento, 1) = YEARWEEK(CURRENT_DATE(), 1)
    ");
    $stmt->execute([':id_empresa' => $id_empresa]);
    $tareasSemana = (int) $stmt->fetch()['total'];

    // Issues abiertos
    $stmt = $pdo->prepare("
        SELECT COUNT(*) as total
        FROM tickets_soporte
        WHERE id_empresa = :id_empresa
          AND estado = 'abierto'
    ");
    $stmt->execute([':id_empresa' => $id_empresa]);
    $issuesAbiertos = (int) $stmt->fetch()['total'];

    // ════════════════════════════════════════════════════════════
    // 2. DATOS DEL USUARIO
    // ════════════════════════════════════════════════════════════
    $stmt = $pdo->prepare("
        SELECT 
            u.nombres,
            u.apellidos,
            u.cargo,
            u.avatar,
            u.email,
            e.nombre as empresa,
            r.nombre as rol
        FROM usuarios u
        LEFT JOIN empresa e ON u.id_empresa = e.id_empresa
        LEFT JOIN roles r ON u.id_roles = r.id_roles
        WHERE u.id_usuario = :id_usuario
    ");
    $stmt->execute([':id_usuario' => $id_usuario]);
    $usuario = $stmt->fetch();

    // ════════════════════════════════════════════════════════════
    // 3. ACTIVIDAD RECIENTE
    // ════════════════════════════════════════════════════════════
    $actividades = [];

    // Últimas tareas completadas
    $stmt = $pdo->prepare("
        SELECT 
            t.titulo as tarea,
            CONCAT(u.nombres, ' ', u.apellidos) as usuario,
            t.fecha_creacion
        FROM tareas t
        INNER JOIN proyecto p ON t.id_proyecto = p.id_proyecto
        LEFT JOIN usuarios u ON t.id_usuario = u.id_usuario
        WHERE p.id_empresa = :id_empresa
        ORDER BY t.fecha_creacion DESC
        LIMIT 5
    ");
    $stmt->execute([':id_empresa' => $id_empresa]);
    
    while ($row = $stmt->fetch()) {
        $actividades[] = [
            'tipo' => 'tarea_completada',
            'usuario' => $row['usuario'] ?? 'Sistema',
            'descripcion' => 'trabajó en la tarea',
            'detalle' => $row['tarea'],
            'tiempo_relativo' => tiempoRelativo($row['fecha_creacion'])
        ];
    }

    // ════════════════════════════════════════════════════════════
    // 4. PROYECTOS ACTIVOS
    // ════════════════════════════════════════════════════════════
    $proyectos = [];

    $stmt = $pdo->prepare("
        SELECT 
            p.nombre,
            COUNT(t.id_tarea) as total_tareas,
            SUM(CASE WHEN t.estado = 'Completada' THEN 1 ELSE 0 END) as tareas_completadas
        FROM proyecto p
        LEFT JOIN tareas t ON p.id_proyecto = t.id_proyecto
        WHERE p.id_empresa = :id_empresa
          AND p.estado = 'Activo'
        GROUP BY p.id_proyecto
        ORDER BY p.nivel_importancia DESC
        LIMIT 5
    ");
    $stmt->execute([':id_empresa' => $id_empresa]);

    while ($row = $stmt->fetch()) {
        $porcentaje = $row['total_tareas'] > 0 
            ? round(($row['tareas_completadas'] / $row['total_tareas']) * 100) 
            : 0;
        
        $proyectos[] = [
            'nombre' => $row['nombre'],
            'porcentaje' => $porcentaje,
            'total_tareas' => (int) $row['total_tareas'],
            'tareas_completadas' => (int) $row['tareas_completadas']
        ];
    }

    // ════════════════════════════════════════════════════════════
    // 5. RESPUESTA
    // ════════════════════════════════════════════════════════════
    $dashboard = [
        'usuario' => [
            'nombre' => trim($usuario['nombres'] . ' ' . $usuario['apellidos']),
            'cargo' => $usuario['cargo'] ?? '',
            'email' => $usuario['email'],
            'avatar' => $usuario['avatar'],
            'empresa' => $usuario['empresa'],
            'rol' => $usuario['rol']
        ],
        'estadisticas' => [
            'proyectos_activos' => $proyectosActivos,
            'proyectos_este_mes' => $proyectosEsteMes,
            'tareas_completadas' => $tareasCompletadas,
            'tareas_esta_semana' => $tareasSemana,
            'agentes_activos' => 3,
            'agentes_en_espera' => 1,
            'issues_abiertos' => $issuesAbiertos
        ],
        'actividades' => $actividades,
        'proyectos' => $proyectos,
        'debug' => $sessionDebug,
        'modo' => 'REAL - Con sesión activa'
    ];

    Response::success($dashboard, 'Dashboard cargado correctamente');

} catch (PDOException $e) {
    Response::error('Error en base de datos: ' . $e->getMessage(), 500);
}

/**
 * Calcula el tiempo relativo de una fecha
 */
function tiempoRelativo(string $fecha): string {
    $timestamp = strtotime($fecha);
    $diferencia = time() - $timestamp;
    
    if ($diferencia < 60) {
        return 'hace unos segundos';
    } elseif ($diferencia < 3600) {
        $minutos = floor($diferencia / 60);
        return "hace {$minutos} min";
    } elseif ($diferencia < 86400) {
        $horas = floor($diferencia / 3600);
        return "hace {$horas}h";
    } elseif ($diferencia < 604800) {
        $dias = floor($diferencia / 86400);
        return "hace {$dias} día(s)";
    } else {
        return date('d/m/Y', $timestamp);
    }
}