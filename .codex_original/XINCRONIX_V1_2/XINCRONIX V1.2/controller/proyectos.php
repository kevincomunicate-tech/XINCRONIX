<?php
// Iniciar sesión si no está iniciada
if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

// Cargar configuración
require_once __DIR__ . '/config.php';

// Configurar cabeceras para JSON
header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization');

// Manejar preflight CORS
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

// Verificar conexión PDO
if (!isset($GLOBALS['pdo']) || !($GLOBALS['pdo'] instanceof PDO)) {
    Response::serverError('Error de configuración del servidor');
    exit;
}

$pdo = $GLOBALS['pdo'];

// Verificar autenticación
if (!isset($_SESSION['user_id']) || !isset($_SESSION['empresa_id'])) {
    Response::error('No has iniciado sesión', 401);
    exit;
}

$id_empresa = (int) $_SESSION['empresa_id'];
$id_usuario = (int) $_SESSION['user_id'];

// Obtener la acción
$action = $_GET['action'] ?? $_POST['action'] ?? '';

// Enrutar según la acción
try {
    switch ($action) {
        case 'listar':
            listarProyectos($pdo, $id_empresa);
            break;
        
        case 'kanban':
            $id_proyecto = (int) ($_GET['id'] ?? $_POST['id_proyecto'] ?? 0);
            obtenerKanban($pdo, $id_proyecto, $id_empresa);
            break;
        
        case 'detalle':
            $id_proyecto = (int) ($_GET['id'] ?? 0);
            detalleProyecto($pdo, $id_proyecto, $id_empresa);
            break;
        
        case 'crear':
            if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
                Response::error('Método no permitido', 405);
            }
            crearProyecto($pdo, $id_empresa);
            break;
        
        case 'actualizar':
            if ($_SERVER['REQUEST_METHOD'] !== 'PUT' && $_SERVER['REQUEST_METHOD'] !== 'POST') {
                Response::error('Método no permitido', 405);
            }
            actualizarProyecto($pdo, $id_empresa);
            break;
        
        case 'cambiar_estado':
            if ($_SERVER['REQUEST_METHOD'] !== 'PUT' && $_SERVER['REQUEST_METHOD'] !== 'POST') {
                Response::error('Método no permitido', 405);
            }
            cambiarEstadoProyecto($pdo, $id_empresa);
            break;
        
        case 'crear_tarea':
            if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
                Response::error('Método no permitido', 405);
            }
            crearTarea($pdo, $id_empresa);
            break;
        
        case 'mover_tarea':
            if ($_SERVER['REQUEST_METHOD'] !== 'PUT' && $_SERVER['REQUEST_METHOD'] !== 'POST') {
                Response::error('Método no permitido', 405);
            }
            moverTarea($pdo, $id_empresa);
            break;
        
        case 'actualizar_tarea':
            if ($_SERVER['REQUEST_METHOD'] !== 'PUT' && $_SERVER['REQUEST_METHOD'] !== 'POST') {
                Response::error('Método no permitido', 405);
            }
            actualizarTarea($pdo, $id_empresa);
            break;
        
        case 'eliminar':
            if ($_SERVER['REQUEST_METHOD'] !== 'DELETE' && $_SERVER['REQUEST_METHOD'] !== 'POST') {
                Response::error('Método no permitido', 405);
            }
            $id_proyecto = (int) ($_GET['id'] ?? $_POST['id_proyecto'] ?? 0);
            eliminarProyecto($pdo, $id_proyecto, $id_empresa);
            break;
        
        case 'eliminar_tarea':
            if ($_SERVER['REQUEST_METHOD'] !== 'DELETE' && $_SERVER['REQUEST_METHOD'] !== 'POST') {
                Response::error('Método no permitido', 405);
            }
            $id_tarea = (int) ($_GET['id'] ?? $_POST['id_tarea'] ?? 0);
            eliminarTarea($pdo, $id_tarea, $id_empresa);
            break;
        
        default:
            Response::error('Acción no válida: ' . $action, 400);
    }
} catch (Exception $e) {
    Logger::error('Error en proyectos.php', ['error' => $e->getMessage(), 'trace' => $e->getTraceAsString()]);
    Response::serverError('Error interno del servidor: ' . $e->getMessage());
}

// FUNCIONES

/* Lista todos los proyectos de la empresa*/

function listarProyectos(PDO $pdo, int $id_empresa): void {
    try {
        $filtroEstado = $_GET['estado'] ?? '';
        
        $sql = "
            SELECT 
                p.id_proyecto,
                p.nombre,
                p.descripcion,
                p.estado,
                p.nivel_importancia,
                p.tipo_proyecto,
                p.fecha_inicio,
                p.fecha_fin,
                p.fecha_creacion,
                e.nombre as equipo,
                COUNT(t.id_tarea) as total_tareas,
                SUM(CASE WHEN t.estado IN ('Completada', 'Hecho') THEN 1 ELSE 0 END) as tareas_completadas
            FROM proyecto p
            LEFT JOIN equipos e ON p.id_equipo = e.id_equipo
            LEFT JOIN tareas t ON p.id_proyecto = t.id_proyecto
            WHERE p.id_empresa = :id_empresa
        ";
        
        $params = [':id_empresa' => $id_empresa];
        
        if (!empty($filtroEstado)) {
            $sql .= " AND p.estado = :estado";
            $params[':estado'] = $filtroEstado;
        }
        
        $sql .= "
            GROUP BY p.id_proyecto, p.nombre, p.descripcion, p.estado, p.nivel_importancia,
                     p.tipo_proyecto, p.fecha_inicio, p.fecha_fin, p.fecha_creacion, e.nombre
            ORDER BY p.fecha_creacion DESC, p.nivel_importancia DESC
        ";
        
        $stmt = $pdo->prepare($sql);
        $stmt->execute($params);
        $proyectos = $stmt->fetchAll();
        
        $resultado = array_map(function($proy) {
            $total = (int) $proy['total_tareas'];
            $completadas = (int) $proy['tareas_completadas'];
            $porcentaje = $total > 0 ? round(($completadas / $total) * 100) : 0;
            
            $colorEstado = [
                'Activo' => '#10b981',
                'Pendiente' => '#f59e0b',
                'En Progreso' => '#3b82f6',
                'Completado' => '#6366f1',
                'Cancelado' => '#ef4444',
                'En Espera' => '#8b5cf6'
            ];
            
            return [
                'id' => (int) $proy['id_proyecto'],
                'nombre' => $proy['nombre'],
                'descripcion' => $proy['descripcion'],
                'estado' => $proy['estado'] ?? 'Activo',
                'color_estado' => $colorEstado[$proy['estado']] ?? '#6b7280',
                'importancia' => (int) $proy['nivel_importancia'],
                'tipo' => $proy['tipo_proyecto'],
                'equipo' => $proy['equipo'],
                'fecha_inicio' => $proy['fecha_inicio'],
                'fecha_fin' => $proy['fecha_fin'],
                'fecha_creacion' => $proy['fecha_creacion'],
                'total_tareas' => $total,
                'tareas_completadas' => $completadas,
                'porcentaje' => $porcentaje
            ];
        }, $proyectos);
        
        Response::success([
            'proyectos' => $resultado,
            'total' => count($resultado)
        ], 'Proyectos cargados correctamente');
        
    } catch (PDOException $e) {
        Logger::error('Error al listar proyectos', $e);
        Response::serverError('Error al cargar proyectos: ' . $e->getMessage());
    }
}

/**
 * Obtiene las tareas de un proyecto en formato kanban
 */
function obtenerKanban(PDO $pdo, int $id_proyecto, int $id_empresa): void {
    try {
        if ($id_proyecto <= 0) {
            Response::error('ID de proyecto requerido', 400);
            return;
        }
        
        $stmt = $pdo->prepare("
            SELECT id_proyecto, nombre, estado 
            FROM proyecto 
            WHERE id_proyecto = :id AND id_empresa = :id_empresa
        ");
        $stmt->execute([':id' => $id_proyecto, ':id_empresa' => $id_empresa]);
        $proyecto = $stmt->fetch();
        
        if (!$proyecto) {
            Response::error('Proyecto no encontrado', 404);
            return;
        }
        
        $stmt = $pdo->prepare("
            SELECT 
                t.id_tarea,
                t.titulo,
                t.descripcion,
                t.estado,
                t.fecha_creacion,
                t.fecha_vencimiento,
                t.id_usuario,
                CONCAT(u.nombres, ' ', u.apellidos) as asignado,
                u.avatar
            FROM tareas t
            LEFT JOIN usuarios u ON t.id_usuario = u.id_usuario
            WHERE t.id_proyecto = :id_proyecto
            ORDER BY t.fecha_creacion DESC
        ");
        $stmt->execute([':id_proyecto' => $id_proyecto]);
        $tareas = $stmt->fetchAll();
        
        $kanban = [
            'proyecto' => [
                'id' => (int) $proyecto['id_proyecto'],
                'nombre' => $proyecto['nombre'],
                'estado' => $proyecto['estado']
            ],
            'columnas' => [
                'pendiente' => ['titulo' => 'Pendiente', 'tareas' => [], 'total' => 0],
                'en_progreso' => ['titulo' => 'En progreso', 'tareas' => [], 'total' => 0],
                'en_revision' => ['titulo' => 'En revisión', 'tareas' => [], 'total' => 0],
                'hecho' => ['titulo' => 'Hecho', 'tareas' => [], 'total' => 0]
            ]
        ];
        
        $mapeoEstados = [
            'Por Hacer' => 'pendiente',
            'Pendiente' => 'pendiente',
            'En Progreso' => 'en_progreso',
            'En Revisión' => 'en_revision',
            'Revisión' => 'en_revision',
            'Completada' => 'hecho',
            'Hecho' => 'hecho'
        ];
        
        foreach ($tareas as $tarea) {
            $columna = $mapeoEstados[$tarea['estado']] ?? 'pendiente';
            $nombreAsignado = $tarea['asignado'] ?? 'Sin asignar';
            
            $kanban['columnas'][$columna]['tareas'][] = [
                'id' => (int) $tarea['id_tarea'],
                'titulo' => $tarea['titulo'],
                'descripcion' => $tarea['descripcion'],
                'estado' => $tarea['estado'],
                'fecha_creacion' => $tarea['fecha_creacion'],
                'fecha_vencimiento' => $tarea['fecha_vencimiento'],
                'asignado' => [
                    'id' => (int) $tarea['id_usuario'],
                    'nombre' => $nombreAsignado,
                    'iniciales' => obtenerIniciales($nombreAsignado),
                    'avatar' => $tarea['avatar']
                ],
                'vencida' => $tarea['fecha_vencimiento'] && strtotime($tarea['fecha_vencimiento']) < time()
            ];
        }
        
        foreach ($kanban['columnas'] as $key => $columna) {
            $kanban['columnas'][$key]['total'] = count($columna['tareas']);
        }
        
        Response::success($kanban, 'Kanban cargado correctamente');
        
    } catch (PDOException $e) {
        Logger::error('Error al obtener kanban', $e);
        Response::serverError('Error al cargar el kanban: ' . $e->getMessage());
    }
}

/**
 * Obtiene el detalle de un proyecto específico
 */
function detalleProyecto(PDO $pdo, int $id_proyecto, int $id_empresa): void {
    try {
        if ($id_proyecto <= 0) {
            Response::error('ID de proyecto requerido', 400);
            return;
        }
        
        $stmt = $pdo->prepare("
            SELECT 
                p.id_proyecto, p.nombre, p.descripcion, p.estado, p.nivel_importancia,
                p.tipo_proyecto, p.fecha_inicio, p.fecha_fin, p.fecha_creacion,
                p.id_empresa, p.id_equipo,
                e.nombre as equipo,
                COUNT(t.id_tarea) as total_tareas,
                SUM(CASE WHEN t.estado IN ('Completada', 'Hecho') THEN 1 ELSE 0 END) as tareas_completadas
            FROM proyecto p
            LEFT JOIN equipos e ON p.id_equipo = e.id_equipo
            LEFT JOIN tareas t ON p.id_proyecto = t.id_proyecto
            WHERE p.id_proyecto = :id AND p.id_empresa = :id_empresa
            GROUP BY p.id_proyecto, p.nombre, p.descripcion, p.estado, p.nivel_importancia,
                     p.tipo_proyecto, p.fecha_inicio, p.fecha_fin, p.fecha_creacion,
                     p.id_empresa, p.id_equipo, e.nombre
        ");
        $stmt->execute([':id' => $id_proyecto, ':id_empresa' => $id_empresa]);
        $proyecto = $stmt->fetch();
        
        if (!$proyecto) {
            Response::error('Proyecto no encontrado', 404);
            return;
        }
        
        Response::success([
            'proyecto' => $proyecto
        ], 'Proyecto cargado correctamente');
        
    } catch (PDOException $e) {
        Logger::error('Error al obtener proyecto', $e);
        Response::serverError('Error al cargar proyecto: ' . $e->getMessage());
    }
}

/**
 * Crea un nuevo proyecto
 */
function crearProyecto(PDO $pdo, int $id_empresa): void {
    try {
        $input = json_decode(file_get_contents('php://input'), true);
        if (!$input) {
            $input = $_POST;
        }
        
        $nombre = trim($input['nombre'] ?? '');
        $descripcion = trim($input['descripcion'] ?? '');
        $tipo = trim($input['tipo_proyecto'] ?? '');
        $importancia = (int) ($input['nivel_importancia'] ?? 1);
        $fecha_inicio = $input['fecha_inicio'] ?? date('Y-m-d');
        $fecha_fin = !empty($input['fecha_fin']) ? $input['fecha_fin'] : null;
        $id_equipo = !empty($input['id_equipo']) ? (int) $input['id_equipo'] : null;
        $estado = $input['estado'] ?? 'Activo';
        
        if (empty($nombre)) {
            Response::error('El nombre del proyecto es obligatorio');
            return;
        }
        
        $sql = "
            INSERT INTO proyecto (nombre, descripcion, estado, nivel_importancia, tipo_proyecto, 
                                  fecha_inicio, fecha_fin, id_empresa, id_equipo)
            VALUES (:nombre, :descripcion, :estado, :importancia, :tipo, 
                    :fecha_inicio, :fecha_fin, :id_empresa, :id_equipo)
        ";
        
        $stmt = $pdo->prepare($sql);
        $stmt->execute([
            ':nombre' => $nombre,
            ':descripcion' => $descripcion,
            ':estado' => $estado,
            ':importancia' => $importancia,
            ':tipo' => $tipo,
            ':fecha_inicio' => $fecha_inicio,
            ':fecha_fin' => $fecha_fin,
            ':id_empresa' => $id_empresa,
            ':id_equipo' => $id_equipo
        ]);
        
        $id_proyecto = (int) $pdo->lastInsertId();
        
        Logger::info('Proyecto creado', [
            'id' => $id_proyecto,
            'nombre' => $nombre,
            'estado' => $estado,
            'empresa_id' => $id_empresa
        ]);
        
        Response::created([
            'id' => $id_proyecto,
            'nombre' => $nombre,
            'estado' => $estado
        ], 'Proyecto creado exitosamente');
        
    } catch (PDOException $e) {
        Logger::error('Error al crear proyecto', $e);
        Response::serverError('Error al crear proyecto: ' . $e->getMessage());
    }
}

/**
 * Actualiza un proyecto existente
 */
function actualizarProyecto(PDO $pdo, int $id_empresa): void {
    try {
        $input = json_decode(file_get_contents('php://input'), true);
        if (!$input) {
            $input = $_POST;
        }
        
        $id_proyecto = (int) ($input['id_proyecto'] ?? 0);
        $nombre = trim($input['nombre'] ?? '');
        $descripcion = trim($input['descripcion'] ?? '');
        $tipo = trim($input['tipo_proyecto'] ?? '');
        $importancia = (int) ($input['nivel_importancia'] ?? 1);
        $fecha_fin = !empty($input['fecha_fin']) ? $input['fecha_fin'] : null;
        $estado = $input['estado'] ?? 'Activo';
        $id_equipo = !empty($input['id_equipo']) ? (int) $input['id_equipo'] : null;
        
        if ($id_proyecto <= 0) {
            Response::error('ID de proyecto requerido', 400);
            return;
        }
        
        if (empty($nombre)) {
            Response::error('El nombre del proyecto es obligatorio');
            return;
        }
        
        $stmt = $pdo->prepare("SELECT id_proyecto FROM proyecto WHERE id_proyecto = :id AND id_empresa = :id_empresa");
        $stmt->execute([':id' => $id_proyecto, ':id_empresa' => $id_empresa]);
        
        if (!$stmt->fetch()) {
            Response::error('Proyecto no encontrado', 404);
            return;
        }
        
        $stmt = $pdo->prepare("
            UPDATE proyecto 
            SET nombre = :nombre,
                descripcion = :descripcion,
                tipo_proyecto = :tipo,
                nivel_importancia = :importancia,
                fecha_fin = :fecha_fin,
                estado = :estado,
                id_equipo = :id_equipo
            WHERE id_proyecto = :id AND id_empresa = :id_empresa
        ");
        $stmt->execute([
            ':nombre' => $nombre,
            ':descripcion' => $descripcion,
            ':tipo' => $tipo,
            ':importancia' => $importancia,
            ':fecha_fin' => $fecha_fin,
            ':estado' => $estado,
            ':id_equipo' => $id_equipo,
            ':id' => $id_proyecto,
            ':id_empresa' => $id_empresa
        ]);
        
        Logger::info('Proyecto actualizado', [
            'id' => $id_proyecto,
            'nombre' => $nombre,
            'estado' => $estado
        ]);
        
        Response::success([
            'id' => $id_proyecto,
            'nombre' => $nombre,
            'estado' => $estado
        ], 'Proyecto actualizado exitosamente');
        
    } catch (PDOException $e) {
        Logger::error('Error al actualizar proyecto', $e);
        Response::serverError('Error al actualizar proyecto: ' . $e->getMessage());
    }
}

/**
 * Cambia el estado de un proyecto
 */
function cambiarEstadoProyecto(PDO $pdo, int $id_empresa): void {
    try {
        $input = json_decode(file_get_contents('php://input'), true);
        if (!$input) {
            $input = $_POST;
        }
        
        $id_proyecto = (int) ($input['id_proyecto'] ?? 0);
        $nuevo_estado = $input['estado'] ?? '';
        
        if ($id_proyecto <= 0 || empty($nuevo_estado)) {
            Response::error('Datos incompletos');
            return;
        }
        
        $estadosValidos = ['Activo', 'Pendiente', 'En Progreso', 'Completado', 'Cancelado', 'En Espera'];
        if (!in_array($nuevo_estado, $estadosValidos)) {
            Response::error('Estado no válido');
            return;
        }
        
        $stmt = $pdo->prepare("SELECT id_proyecto FROM proyecto WHERE id_proyecto = :id AND id_empresa = :id_empresa");
        $stmt->execute([':id' => $id_proyecto, ':id_empresa' => $id_empresa]);
        
        if (!$stmt->fetch()) {
            Response::error('Proyecto no encontrado', 404);
            return;
        }
        
        $stmt = $pdo->prepare("
            UPDATE proyecto 
            SET estado = :estado
            WHERE id_proyecto = :id AND id_empresa = :id_empresa
        ");
        $stmt->execute([
            ':estado' => $nuevo_estado,
            ':id' => $id_proyecto,
            ':id_empresa' => $id_empresa
        ]);
        
        Logger::info('Estado de proyecto actualizado', [
            'id' => $id_proyecto,
            'nuevo_estado' => $nuevo_estado
        ]);
        
        Response::success([
            'id' => $id_proyecto,
            'estado' => $nuevo_estado
        ], 'Estado actualizado correctamente');
        
    } catch (PDOException $e) {
        Logger::error('Error al cambiar estado', $e);
        Response::serverError('Error al cambiar estado: ' . $e->getMessage());
    }
}

/**
 * Crea una nueva tarea
 */
function crearTarea(PDO $pdo, int $id_empresa): void {
    try {
        $input = json_decode(file_get_contents('php://input'), true);
        if (!$input) {
            $input = $_POST;
        }
        
        $titulo = trim($input['titulo'] ?? '');
        $descripcion = trim($input['descripcion'] ?? '');
        $id_proyecto = (int) ($input['id_proyecto'] ?? 0);
        $id_usuario = !empty($input['id_usuario']) ? (int) $input['id_usuario'] : null;
        $id_equipo = !empty($input['id_equipo']) ? (int) $input['id_equipo'] : null;
        $fecha_vencimiento = !empty($input['fecha_vencimiento']) ? $input['fecha_vencimiento'] : null;
        $estado = $input['estado'] ?? 'Por Hacer';
        
        if (empty($titulo)) {
            Response::error('El título de la tarea es obligatorio');
            return;
        }
        
        if ($id_proyecto <= 0) {
            Response::error('El proyecto es obligatorio');
            return;
        }
        
        $stmt = $pdo->prepare("SELECT id_proyecto FROM proyecto WHERE id_proyecto = :id AND id_empresa = :id_empresa");
        $stmt->execute([':id' => $id_proyecto, ':id_empresa' => $id_empresa]);
        
        if (!$stmt->fetch()) {
            Response::error('Proyecto no válido', 404);
            return;
        }
        
        $stmt = $pdo->prepare("
            INSERT INTO tareas (titulo, descripcion, estado, fecha_vencimiento, id_proyecto, id_usuario, id_equipo)
            VALUES (:titulo, :descripcion, :estado, :fecha_vencimiento, :id_proyecto, :id_usuario, :id_equipo)
        ");
        $stmt->execute([
            ':titulo' => $titulo,
            ':descripcion' => $descripcion,
            ':estado' => $estado,
            ':fecha_vencimiento' => $fecha_vencimiento,
            ':id_proyecto' => $id_proyecto,
            ':id_usuario' => $id_usuario,
            ':id_equipo' => $id_equipo
        ]);
        
        $id_tarea = (int) $pdo->lastInsertId();
        
        Logger::info('Tarea creada', [
            'id' => $id_tarea,
            'titulo' => $titulo,
            'proyecto_id' => $id_proyecto
        ]);
        
        Response::created([
            'id' => $id_tarea,
            'titulo' => $titulo,
            'estado' => $estado
        ], 'Tarea creada exitosamente');
        
    } catch (PDOException $e) {
        Logger::error('Error al crear tarea', $e);
        Response::serverError('Error al crear tarea: ' . $e->getMessage());
    }
}

/**
 * Mueve una tarea a otra columna del kanban
 * (valida que la tarea pertenezca a un proyecto de la empresa del usuario)
 */
function moverTarea(PDO $pdo, int $id_empresa): void {
    try {
        $input = json_decode(file_get_contents('php://input'), true);
        if (!$input) {
            $input = $_POST;
        }
        
        $id_tarea = (int) ($input['id_tarea'] ?? 0);
        $nuevo_estado = $input['estado'] ?? '';
        
        if ($id_tarea <= 0 || empty($nuevo_estado)) {
            Response::error('Datos incompletos');
            return;
        }
        
        $mapeoEstados = [
            'pendiente' => 'Por Hacer',
            'en_progreso' => 'En Progreso',
            'en_revision' => 'En Revisión',
            'hecho' => 'Completada'
        ];
        
        $estadoBD = $mapeoEstados[$nuevo_estado] ?? $nuevo_estado;
        
        $stmt = $pdo->prepare("
            UPDATE tareas t
            INNER JOIN proyecto p ON t.id_proyecto = p.id_proyecto
            SET t.estado = :estado 
            WHERE t.id_tarea = :id AND p.id_empresa = :id_empresa
        ");
        $stmt->execute([
            ':estado' => $estadoBD,
            ':id' => $id_tarea,
            ':id_empresa' => $id_empresa
        ]);
        
        if ($stmt->rowCount() === 0) {
            Response::error('Tarea no encontrada', 404);
            return;
        }
        
        Logger::info('Tarea movida', [
            'id_tarea' => $id_tarea,
            'nuevo_estado' => $estadoBD
        ]);
        
        Response::success([
            'id_tarea' => $id_tarea,
            'estado' => $estadoBD
        ], 'Tarea actualizada correctamente');
        
    } catch (PDOException $e) {
        Logger::error('Error al mover tarea', $e);
        Response::serverError('Error al actualizar tarea: ' . $e->getMessage());
    }
}

/**
 * Actualiza una tarea existente
 * (valida que la tarea pertenezca a un proyecto de la empresa del usuario)
 */
function actualizarTarea(PDO $pdo, int $id_empresa): void {
    try {
        $input = json_decode(file_get_contents('php://input'), true);
        if (!$input) {
            $input = $_POST;
        }
        
        $id_tarea = (int) ($input['id_tarea'] ?? 0);
        $titulo = trim($input['titulo'] ?? '');
        $descripcion = trim($input['descripcion'] ?? '');
        $id_usuario = !empty($input['id_usuario']) ? (int) $input['id_usuario'] : null;
        $fecha_vencimiento = !empty($input['fecha_vencimiento']) ? $input['fecha_vencimiento'] : null;
        
        if ($id_tarea <= 0) {
            Response::error('ID de tarea requerido');
            return;
        }
        
        if (empty($titulo)) {
            Response::error('El título es obligatorio');
            return;
        }
        
        $stmt = $pdo->prepare("
            UPDATE tareas t
            INNER JOIN proyecto p ON t.id_proyecto = p.id_proyecto
            SET t.titulo = :titulo, 
                t.descripcion = :descripcion, 
                t.id_usuario = :id_usuario,
                t.fecha_vencimiento = :fecha_vencimiento
            WHERE t.id_tarea = :id AND p.id_empresa = :id_empresa
        ");
        $stmt->execute([
            ':titulo' => $titulo,
            ':descripcion' => $descripcion,
            ':id_usuario' => $id_usuario,
            ':fecha_vencimiento' => $fecha_vencimiento,
            ':id' => $id_tarea,
            ':id_empresa' => $id_empresa
        ]);
        
        if ($stmt->rowCount() === 0) {
            Response::error('Tarea no encontrada', 404);
            return;
        }
        
        Response::success(['id_tarea' => $id_tarea], 'Tarea actualizada');
        
    } catch (PDOException $e) {
        Logger::error('Error al actualizar tarea', $e);
        Response::serverError('Error al actualizar tarea: ' . $e->getMessage());
    }
}

/**
 * Elimina un proyecto y sus tareas
 */
function eliminarProyecto(PDO $pdo, int $id_proyecto, int $id_empresa): void {
    try {
        if ($id_proyecto <= 0) {
            Response::error('ID de proyecto requerido', 400);
            return;
        }
        
        $stmt = $pdo->prepare("DELETE FROM proyecto WHERE id_proyecto = :id AND id_empresa = :id_empresa");
        $stmt->execute([':id' => $id_proyecto, ':id_empresa' => $id_empresa]);
        
        if ($stmt->rowCount() === 0) {
            Response::error('Proyecto no encontrado', 404);
            return;
        }
        
        Logger::info('Proyecto eliminado', ['id' => $id_proyecto]);
        Response::success(null, 'Proyecto eliminado correctamente');
        
    } catch (PDOException $e) {
        Logger::error('Error al eliminar proyecto', $e);
        Response::serverError('Error al eliminar proyecto: ' . $e->getMessage());
    }
}

/**
 * Elimina una tarea
 */
function eliminarTarea(PDO $pdo, int $id_tarea, int $id_empresa): void {
    try {
        if ($id_tarea <= 0) {
            Response::error('ID de tarea requerido', 400);
            return;
        }
        
        $stmt = $pdo->prepare("
            DELETE t FROM tareas t
            INNER JOIN proyecto p ON t.id_proyecto = p.id_proyecto
            WHERE t.id_tarea = :id AND p.id_empresa = :id_empresa
        ");
        $stmt->execute([':id' => $id_tarea, ':id_empresa' => $id_empresa]);
        
        if ($stmt->rowCount() === 0) {
            Response::error('Tarea no encontrada', 404);
            return;
        }
        
        Response::success(null, 'Tarea eliminada correctamente');
        
    } catch (PDOException $e) {
        Logger::error('Error al eliminar tarea', $e);
        Response::serverError('Error al eliminar tarea: ' . $e->getMessage());
    }
}

/**
 * Obtiene las iniciales de un nombre
 */
function obtenerIniciales(string $nombre): string {
    $palabras = explode(' ', trim($nombre));
    $iniciales = '';
    
    foreach ($palabras as $palabra) {
        if (!empty($palabra)) {
            $iniciales .= mb_strtoupper(mb_substr($palabra, 0, 1));
        }
    }
    
    return mb_substr($iniciales, 0, 2) ?: 'SA';
}