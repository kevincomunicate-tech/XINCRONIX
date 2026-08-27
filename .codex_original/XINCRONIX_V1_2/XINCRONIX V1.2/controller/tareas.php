<?php
session_start();

define('SECURE_ACCESS', true);

require_once __DIR__ . '/config.php';
require_once __DIR__ . '/../class/Response.php';
require_once __DIR__ . '/../class/Logger.php';

header('Content-Type: application/json; charset=utf-8');

// ── Validar sesión ────────────────────────────────────────────
if (!isset($_SESSION['user_id'])) {
    Response::unauthorized('Debe iniciar sesión primero');
}

$user_id    = (int) $_SESSION['user_id'];
$empresa_id = (int) ($_SESSION['empresa_id'] ?? 0);

$action = $_GET['action'] ?? $_POST['action'] ?? null;

// Estados válidos del sistema (deben coincidir con el ENUM lógico usado en BD)
const ESTADOS_VALIDOS = ['Por Hacer', 'En Progreso', 'En Revisión', 'Completada'];

switch ($action) {
    case 'init':
        handleInit($user_id, $empresa_id);
        break;
    case 'listar':
        handleListar($user_id, $empresa_id);
        break;
    case 'obtener':
        handleObtener($user_id, $empresa_id);
        break;
    case 'crear':
        handleCrear($user_id, $empresa_id);
        break;
    case 'actualizar':
        handleActualizar($user_id, $empresa_id);
        break;
    case 'eliminar':
        handleEliminar($user_id, $empresa_id);
        break;
    default:
        Response::error('Acción no válida', 400);
}

/* ────────────────────────────────────────────────────────────
 *  Helpers
 * ──────────────────────────────────────────────────────────── */

/**
 * Genera iniciales tipo "Carlos Mora" -> "CM"
 */
function iniciales(string $nombres, string $apellidos): string {
    $i1 = mb_strtoupper(mb_substr(trim($nombres), 0, 1));
    $i2 = mb_strtoupper(mb_substr(trim($apellidos), 0, 1));
    return $i1 . $i2;
}

/**
 * Determina si una tarea está vencida (fecha pasada y no completada)
 */
function estaVencida(?string $fecha_vencimiento, string $estado): bool {
    if (empty($fecha_vencimiento) || $estado === 'Completada') return false;
    return strtotime($fecha_vencimiento) < strtotime(date('Y-m-d'));
}

/* ────────────────────────────────────────────────────────────
 *  INIT — Datos completos para pintar la pantalla de Tareas
 *  GET /controller/tareas.php?action=init
 * ──────────────────────────────────────────────────────────── */
function handleInit($user_id, $empresa_id) {
    global $pdo;

    try {
        // 1. Datos del usuario en sesión
        $stmt = $pdo->prepare("
            SELECT u.id_usuario, u.nombres, u.apellidos, u.email, u.cargo, u.avatar,
                   e.nombre AS nombre_empresa, r.nombre AS nombre_rol
            FROM usuarios u
            LEFT JOIN empresa e ON e.id_empresa = u.id_empresa
            LEFT JOIN roles r   ON r.id_roles   = u.id_roles
            WHERE u.id_usuario = :id
            LIMIT 1
        ");
        $stmt->execute([':id' => $user_id]);
        $usuario = $stmt->fetch();

        if (!$usuario) {
            Response::unauthorized('Sesión inválida, vuelva a iniciar sesión');
        }

        $usuario['iniciales'] = iniciales($usuario['nombres'], $usuario['apellidos']);
        unset($usuario['email']); // no es necesario exponerlo en el frontend de tareas

        // 2. Proyectos de la empresa (para selects de "Nueva tarea" y filtro)
        $stmt = $pdo->prepare("
            SELECT id_proyecto, nombre
            FROM proyecto
            WHERE id_empresa = :empresa_id
            ORDER BY nombre ASC
        ");
        $stmt->execute([':empresa_id' => $empresa_id]);
        $proyectos = $stmt->fetchAll();

        // 3. Tareas del usuario (todas las de su empresa para que vea equipo, no solo las suyas)
        $stmt = $pdo->prepare("
            SELECT
                t.id_tarea, t.titulo, t.descripcion, t.estado,
                t.fecha_creacion, t.fecha_vencimiento,
                t.id_proyecto, p.nombre AS proyecto_nombre,
                t.id_usuario,
                u.nombres AS usuario_nombres, u.apellidos AS usuario_apellidos, u.avatar AS usuario_avatar
            FROM tareas t
            INNER JOIN proyecto p ON p.id_proyecto = t.id_proyecto
            LEFT JOIN usuarios u  ON u.id_usuario = t.id_usuario
            WHERE p.id_empresa = :empresa_id
            ORDER BY
                (t.estado = 'Completada') ASC,
                t.fecha_vencimiento IS NULL, t.fecha_vencimiento ASC,
                t.fecha_creacion DESC
        ");
        $stmt->execute([':empresa_id' => $empresa_id]);
        $tareas = $stmt->fetchAll();

        $vencidas = 0;
        $completadas = 0;
        $en_progreso = 0;

        foreach ($tareas as &$t) {
            $t['vencida'] = estaVencida($t['fecha_vencimiento'], $t['estado']);
            $t['usuario_iniciales'] = $t['usuario_nombres']
                ? iniciales($t['usuario_nombres'], $t['usuario_apellidos'])
                : '—';

            if ($t['vencida']) $vencidas++;
            if ($t['estado'] === 'Completada') $completadas++;
            if ($t['estado'] === 'En Progreso') $en_progreso++;
        }
        unset($t);

        $stats = [
            'total'       => count($tareas),
            'completadas' => $completadas,
            'en_progreso' => $en_progreso,
            'vencidas'    => $vencidas,
        ];

        Response::success([
            'usuario'   => $usuario,
            'proyectos' => $proyectos,
            'tareas'    => $tareas,
            'stats'     => $stats,
        ], 'Datos cargados');

    } catch (PDOException $e) {
        Logger::error('Error en init de tareas', $e);
        Response::serverError('Error al cargar los datos');
    }
}

/* ────────────────────────────────────────────────────────────
 *  LISTAR — GET ?action=listar&proyecto_id=&estado=&q=&vencidas=1
 * ──────────────────────────────────────────────────────────── */
function handleListar($user_id, $empresa_id) {
    global $pdo;

    $proyecto_id = intval($_GET['proyecto_id'] ?? 0);
    $estado      = trim($_GET['estado'] ?? '');
    $q           = trim($_GET['q'] ?? '');
    $soloVencidas = isset($_GET['vencidas']) && $_GET['vencidas'] == '1';
    $limit       = min(intval($_GET['limit'] ?? 100), 500);
    $offset      = max(intval($_GET['offset'] ?? 0), 0);

    $query = "
        SELECT
            t.id_tarea, t.titulo, t.descripcion, t.estado,
            t.fecha_creacion, t.fecha_vencimiento,
            t.id_proyecto, p.nombre AS proyecto_nombre,
            t.id_usuario,
            u.nombres AS usuario_nombres, u.apellidos AS usuario_apellidos
        FROM tareas t
        INNER JOIN proyecto p ON p.id_proyecto = t.id_proyecto
        LEFT JOIN usuarios u  ON u.id_usuario = t.id_usuario
        WHERE p.id_empresa = :empresa_id
    ";
    $params = [':empresa_id' => $empresa_id];

    if ($proyecto_id > 0) {
        $query .= " AND t.id_proyecto = :proyecto_id";
        $params[':proyecto_id'] = $proyecto_id;
    }

    if (!empty($estado) && in_array($estado, ESTADOS_VALIDOS, true)) {
        $query .= " AND t.estado = :estado";
        $params[':estado'] = $estado;
    }

    if (!empty($q)) {
        $query .= " AND t.titulo LIKE :q";
        $params[':q'] = '%' . $q . '%';
    }

    if ($soloVencidas) {
        $query .= " AND t.fecha_vencimiento < CURDATE() AND t.estado <> 'Completada'";
    }

    $query .= " ORDER BY t.fecha_vencimiento IS NULL, t.fecha_vencimiento ASC, t.fecha_creacion DESC
                LIMIT :limit OFFSET :offset";

    try {
        $stmt = $pdo->prepare($query);
        foreach ($params as $key => $value) {
            $stmt->bindValue($key, $value);
        }
        $stmt->bindValue(':limit', $limit, PDO::PARAM_INT);
        $stmt->bindValue(':offset', $offset, PDO::PARAM_INT);
        $stmt->execute();
        $tareas = $stmt->fetchAll();

        foreach ($tareas as &$t) {
            $t['vencida'] = estaVencida($t['fecha_vencimiento'], $t['estado']);
        }
        unset($t);

        Response::success($tareas, 'Tareas obtenidas');

    } catch (PDOException $e) {
        Logger::error('Error al listar tareas', $e);
        Response::serverError('Error al listar tareas');
    }
}

/* ────────────────────────────────────────────────────────────
 *  OBTENER — GET ?action=obtener&id=
 * ──────────────────────────────────────────────────────────── */
function handleObtener($user_id, $empresa_id) {
    global $pdo;

    $id = intval($_GET['id'] ?? 0);
    if ($id <= 0) {
        Response::error('ID inválido', 400);
    }

    try {
        $stmt = $pdo->prepare("
            SELECT t.*
            FROM tareas t
            INNER JOIN proyecto p ON p.id_proyecto = t.id_proyecto
            WHERE t.id_tarea = :id AND p.id_empresa = :empresa_id
            LIMIT 1
        ");
        $stmt->execute([':id' => $id, ':empresa_id' => $empresa_id]);
        $tarea = $stmt->fetch();

        if (!$tarea) {
            Response::notFound('Tarea no encontrada');
        }

        Response::success($tarea);

    } catch (PDOException $e) {
        Logger::error('Error al obtener tarea', $e);
        Response::serverError();
    }
}

/* ────────────────────────────────────────────────────────────
 *  CREAR — POST ?action=crear
 * ──────────────────────────────────────────────────────────── */
function handleCrear($user_id, $empresa_id) {
    global $pdo;

    $titulo            = trim($_POST['titulo'] ?? '');
    $descripcion       = trim($_POST['descripcion'] ?? '');
    $proyecto_id       = intval($_POST['proyecto_id'] ?? 0);
    $estado            = $_POST['estado'] ?? 'Por Hacer';
    $fecha_vencimiento = $_POST['fecha_vencimiento'] ?? null;
    $asignado_id       = intval($_POST['id_usuario'] ?? $user_id); // por defecto, quien crea

    $errores = [];

    if (mb_strlen($titulo) < 5 || mb_strlen($titulo) > 200) {
        $errores['titulo'] = 'Título requerido (mínimo 5, máximo 200 caracteres)';
    }

    if ($proyecto_id <= 0) {
        $errores['proyecto_id'] = 'Proyecto requerido';
    }

    if (!in_array($estado, ESTADOS_VALIDOS, true)) {
        $errores['estado'] = 'Estado inválido';
    }

    if (!empty($fecha_vencimiento) && !strtotime($fecha_vencimiento)) {
        $errores['fecha_vencimiento'] = 'Fecha inválida';
    }

    if (!empty($errores)) {
        Response::validationError($errores);
    }

    try {
        // El proyecto debe pertenecer a la misma empresa del usuario
        $stmt = $pdo->prepare("
            SELECT id_proyecto FROM proyecto
            WHERE id_proyecto = :proyecto_id AND id_empresa = :empresa_id
        ");
        $stmt->execute([':proyecto_id' => $proyecto_id, ':empresa_id' => $empresa_id]);

        if (!$stmt->fetch()) {
            Response::forbidden('No tiene permiso para agregar tareas a este proyecto');
        }

        // El usuario asignado (si se especificó otro) debe ser de la misma empresa
        $stmt = $pdo->prepare("SELECT id_usuario FROM usuarios WHERE id_usuario = :id AND id_empresa = :empresa_id");
        $stmt->execute([':id' => $asignado_id, ':empresa_id' => $empresa_id]);
        if (!$stmt->fetch()) {
            $asignado_id = $user_id;
        }

        $stmt = $pdo->prepare("
            INSERT INTO tareas (titulo, descripcion, estado, fecha_vencimiento, id_proyecto, id_usuario, fecha_creacion)
            VALUES (:titulo, :descripcion, :estado, :fecha_vencimiento, :proyecto_id, :asignado_id, NOW())
        ");
        $stmt->execute([
            ':titulo'            => $titulo,
            ':descripcion'       => $descripcion ?: null,
            ':estado'            => $estado,
            ':fecha_vencimiento' => !empty($fecha_vencimiento) ? date('Y-m-d', strtotime($fecha_vencimiento)) : null,
            ':proyecto_id'       => $proyecto_id,
            ':asignado_id'       => $asignado_id,
        ]);

        $tarea_id = $pdo->lastInsertId();

        Logger::success('Tarea creada', ['tarea_id' => $tarea_id, 'user_id' => $user_id, 'proyecto_id' => $proyecto_id]);
        Response::created(['id' => (int) $tarea_id, 'titulo' => $titulo], 'Tarea creada exitosamente');

    } catch (PDOException $e) {
        Logger::error('Error al crear tarea', $e);
        Response::serverError('Error al crear tarea');
    }
}

/* ────────────────────────────────────────────────────────────
 *  ACTUALIZAR — POST ?action=actualizar
 * ──────────────────────────────────────────────────────────── */
function handleActualizar($user_id, $empresa_id) {
    global $pdo;

    $id                = intval($_POST['id'] ?? 0);
    $titulo            = array_key_exists('titulo', $_POST) ? trim($_POST['titulo']) : null;
    $descripcion       = array_key_exists('descripcion', $_POST) ? trim($_POST['descripcion']) : null;
    $estado            = $_POST['estado'] ?? null;
    $fecha_vencimiento = array_key_exists('fecha_vencimiento', $_POST) ? $_POST['fecha_vencimiento'] : null;
    $proyecto_id       = intval($_POST['proyecto_id'] ?? 0);

    if ($id <= 0) {
        Response::error('ID inválido', 400);
    }

    $errores = [];

    if ($titulo !== null && ($mb = mb_strlen($titulo)) > 0 && ($mb < 5 || $mb > 200)) {
        $errores['titulo'] = 'Título debe tener entre 5 y 200 caracteres';
    }

    if ($estado !== null && !in_array($estado, ESTADOS_VALIDOS, true)) {
        $errores['estado'] = 'Estado inválido';
    }

    if (!empty($fecha_vencimiento) && !strtotime($fecha_vencimiento)) {
        $errores['fecha_vencimiento'] = 'Fecha inválida';
    }

    if (!empty($errores)) {
        Response::validationError($errores);
    }

    try {
        // Verificar que la tarea pertenezca a la empresa del usuario
        $stmt = $pdo->prepare("
            SELECT t.id_tarea FROM tareas t
            INNER JOIN proyecto p ON p.id_proyecto = t.id_proyecto
            WHERE t.id_tarea = :id AND p.id_empresa = :empresa_id
        ");
        $stmt->execute([':id' => $id, ':empresa_id' => $empresa_id]);

        if (!$stmt->fetch()) {
            Response::forbidden('No tiene permiso para editar esta tarea');
        }

        $updates = [];
        $params  = [':id' => $id];

        if (!empty($titulo)) {
            $updates[] = "titulo = :titulo";
            $params[':titulo'] = $titulo;
        }

        if ($descripcion !== null) {
            $updates[] = "descripcion = :descripcion";
            $params[':descripcion'] = $descripcion;
        }

        if ($estado !== null) {
            $updates[] = "estado = :estado";
            $params[':estado'] = $estado;
        }

        if (!empty($fecha_vencimiento)) {
            $updates[] = "fecha_vencimiento = :fecha_vencimiento";
            $params[':fecha_vencimiento'] = date('Y-m-d', strtotime($fecha_vencimiento));
        }

        if ($proyecto_id > 0) {
            // validar que el nuevo proyecto sea de la misma empresa
            $check = $pdo->prepare("SELECT id_proyecto FROM proyecto WHERE id_proyecto = :pid AND id_empresa = :eid");
            $check->execute([':pid' => $proyecto_id, ':eid' => $empresa_id]);
            if ($check->fetch()) {
                $updates[] = "id_proyecto = :proyecto_id";
                $params[':proyecto_id'] = $proyecto_id;
            }
        }

        if (empty($updates)) {
            Response::error('No hay cambios para guardar', 400);
        }

        $query = "UPDATE tareas SET " . implode(', ', $updates) . " WHERE id_tarea = :id";
        $stmt = $pdo->prepare($query);
        $stmt->execute($params);

        Logger::success('Tarea actualizada', ['tarea_id' => $id, 'user_id' => $user_id]);
        Response::success(['id' => $id], 'Tarea actualizada');

    } catch (PDOException $e) {
        Logger::error('Error al actualizar tarea', $e);
        Response::serverError('Error al actualizar tarea');
    }
}

/* ────────────────────────────────────────────────────────────
 *  ELIMINAR — GET ?action=eliminar&id=
 * ──────────────────────────────────────────────────────────── */
function handleEliminar($user_id, $empresa_id) {
    global $pdo;

    $id = intval($_GET['id'] ?? 0);
    if ($id <= 0) {
        Response::error('ID inválido', 400);
    }

    try {
        $stmt = $pdo->prepare("
            SELECT t.id_tarea FROM tareas t
            INNER JOIN proyecto p ON p.id_proyecto = t.id_proyecto
            WHERE t.id_tarea = :id AND p.id_empresa = :empresa_id
        ");
        $stmt->execute([':id' => $id, ':empresa_id' => $empresa_id]);

        if (!$stmt->fetch()) {
            Response::forbidden('No tiene permiso para eliminar esta tarea');
        }

        $stmt = $pdo->prepare("DELETE FROM tareas WHERE id_tarea = :id");
        $stmt->execute([':id' => $id]);

        Logger::success('Tarea eliminada', ['tarea_id' => $id, 'user_id' => $user_id]);
        Response::success(['id' => $id], 'Tarea eliminada');

    } catch (PDOException $e) {
        Logger::error('Error al eliminar tarea', $e);
        Response::serverError('Error al eliminar tarea');
    }
}