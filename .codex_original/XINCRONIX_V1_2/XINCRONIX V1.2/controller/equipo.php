<?php
/**
 * equipo.php — Datos del equipo + chat interno 1 a 1
 * Ubicación: /controller/equipo.php
 *
 * Acciones:
 *   GET  init                              -> usuario en sesión + lista de miembros con stats reales
 *   GET  mensajes&con_id=&desde_id=0        -> historial de chat con un miembro (polling)
 *   POST enviar (destinatario_id, contenido)-> enviar mensaje de chat
 *   GET  no_leidos                          -> conteo de mensajes no leídos por remitente (para badges)
 */

session_start();
define('SECURE_ACCESS', true);

require_once __DIR__ . '/config.php';
require_once __DIR__ . '/../class/Response.php';
require_once __DIR__ . '/../class/Logger.php';

header('Content-Type: application/json; charset=utf-8');

if (!isset($_SESSION['user_id'])) {
    Response::unauthorized('Debe iniciar sesión primero');
}

$user_id    = (int) $_SESSION['user_id'];
$empresa_id = (int) ($_SESSION['empresa_id'] ?? 0);
$action     = $_GET['action'] ?? $_POST['action'] ?? null;

switch ($action) {
    case 'init':
        handleInit($user_id, $empresa_id);
        break;
    case 'mensajes':
        handleMensajes($user_id, $empresa_id);
        break;
    case 'enviar':
        handleEnviar($user_id, $empresa_id);
        break;
    case 'no_leidos':
        handleNoLeidos($user_id);
        break;
    default:
        Response::error('Acción no válida', 400);
}

function iniciales(string $nombres, string $apellidos): string {
    $i1 = mb_strtoupper(mb_substr(trim($nombres), 0, 1));
    $i2 = mb_strtoupper(mb_substr(trim($apellidos), 0, 1));
    return $i1 . $i2;
}

/* ────────────────────────────────────────────────────────────
 *  INIT — usuario actual + miembros de la empresa con stats reales
 * ──────────────────────────────────────────────────────────── */
function handleInit($user_id, $empresa_id) {
    global $pdo;

    try {
        $stmt = $pdo->prepare("
            SELECT u.id_usuario, u.nombres, u.apellidos, u.email, u.cargo, u.avatar,
                   r.nombre AS nombre_rol
            FROM usuarios u
            LEFT JOIN roles r ON r.id_roles = u.id_roles
            WHERE u.id_usuario = :id
            LIMIT 1
        ");
        $stmt->execute([':id' => $user_id]);
        $usuario = $stmt->fetch();

        if (!$usuario) {
            Response::unauthorized('Sesión inválida, vuelva a iniciar sesión');
        }
        $usuario['iniciales'] = iniciales($usuario['nombres'], $usuario['apellidos']);

        // Miembros de la misma empresa
        $stmt = $pdo->prepare("
            SELECT u.id_usuario, u.nombres, u.apellidos, u.email, u.cargo, u.avatar, u.estado,
                   r.nombre AS nombre_rol
            FROM usuarios u
            LEFT JOIN roles r ON r.id_roles = u.id_roles
            WHERE u.id_empresa = :empresa_id
            ORDER BY u.nombres ASC
        ");
        $stmt->execute([':empresa_id' => $empresa_id]);
        $miembros = $stmt->fetchAll();

        // Stats reales por miembro: tareas activas, proyectos distintos, % on-time
        $stmtTareas = $pdo->prepare("
            SELECT
                COUNT(*) AS total_tareas,
                SUM(CASE WHEN t.estado <> 'Completada' THEN 1 ELSE 0 END) AS activas,
                COUNT(DISTINCT t.id_proyecto) AS proyectos,
                SUM(CASE WHEN t.estado = 'Completada' AND
                          (t.fecha_vencimiento IS NULL OR t.fecha_vencimiento >= DATE(t.fecha_creacion))
                     THEN 1 ELSE 0 END) AS a_tiempo,
                SUM(CASE WHEN t.estado = 'Completada' THEN 1 ELSE 0 END) AS completadas
            FROM tareas t
            WHERE t.id_usuario = :id_usuario
        ");

        foreach ($miembros as &$m) {
            $m['iniciales'] = iniciales($m['nombres'], $m['apellidos']);

            $stmtTareas->execute([':id_usuario' => $m['id_usuario']]);
            $s = $stmtTareas->fetch();

            $m['tareas_activas'] = (int) ($s['activas'] ?? 0);
            $m['proyectos']      = (int) ($s['proyectos'] ?? 0);
            $completadas = (int) ($s['completadas'] ?? 0);
            $aTiempo     = (int) ($s['a_tiempo'] ?? 0);
            $m['on_time'] = $completadas > 0 ? round(($aTiempo / $completadas) * 100) : 100;

            // Carga de trabajo aproximada: tareas activas / 10 (tope visual)
            $m['carga_pct'] = min(100, round($m['tareas_activas'] * 12));

            unset($m['email_publico']);
        }
        unset($m);

        Response::success([
            'usuario'  => $usuario,
            'miembros' => $miembros,
        ], 'Datos de equipo cargados');

    } catch (PDOException $e) {
        Logger::error('Error en init de equipo', $e);
        Response::serverError('Error al cargar el equipo');
    }
}

/* ────────────────────────────────────────────────────────────
 *  MENSAJES — historial de chat con un miembro específico
 *  GET ?action=mensajes&con_id=5&desde_id=0
 * ──────────────────────────────────────────────────────────── */
function handleMensajes($user_id, $empresa_id) {
    global $pdo;

    $con_id    = intval($_GET['con_id'] ?? 0);
    $desde_id  = intval($_GET['desde_id'] ?? 0); // para polling incremental

    if ($con_id <= 0) {
        Response::error('Debe indicar con_id (usuario destino)', 400);
    }

    try {
        // Validar que el contacto sea de la misma empresa
        $stmt = $pdo->prepare("SELECT id_usuario FROM usuarios WHERE id_usuario = :id AND id_empresa = :empresa_id");
        $stmt->execute([':id' => $con_id, ':empresa_id' => $empresa_id]);
        if (!$stmt->fetch()) {
            Response::forbidden('No puede chatear con este usuario');
        }

        $query = "
            SELECT id_mensajes, contenido, fecha_envio, leido, id_usuario, id_destinatario
            FROM mensajes
            WHERE ((id_usuario = :me AND id_destinatario = :con)
                OR (id_usuario = :con2 AND id_destinatario = :me2))
        ";
        $params = [':me' => $user_id, ':con' => $con_id, ':con2' => $con_id, ':me2' => $user_id];

        if ($desde_id > 0) {
            $query .= " AND id_mensajes > :desde_id";
            $params[':desde_id'] = $desde_id;
        }

        $query .= " ORDER BY id_mensajes ASC LIMIT 200";

        $stmt = $pdo->prepare($query);
        $stmt->execute($params);
        $mensajes = $stmt->fetchAll();

        foreach ($mensajes as &$m) {
            $m['propio'] = ((int) $m['id_usuario'] === $user_id);
        }
        unset($m);

        // Marcar como leídos los mensajes que el contacto me envió
        $stmt = $pdo->prepare("
            UPDATE mensajes SET leido = 1
            WHERE id_usuario = :con AND id_destinatario = :me AND leido = 0
        ");
        $stmt->execute([':con' => $con_id, ':me' => $user_id]);

        Response::success($mensajes);

    } catch (PDOException $e) {
        Logger::error('Error al obtener mensajes', $e);
        Response::serverError('Error al obtener mensajes');
    }
}

/* ────────────────────────────────────────────────────────────
 *  ENVIAR — POST ?action=enviar (destinatario_id, contenido)
 * ──────────────────────────────────────────────────────────── */
function handleEnviar($user_id, $empresa_id) {
    global $pdo;

    $destinatario_id = intval($_POST['destinatario_id'] ?? 0);
    $contenido        = trim($_POST['contenido'] ?? '');

    if ($destinatario_id <= 0) {
        Response::error('Destinatario inválido', 400);
    }
    if ($contenido === '' || mb_strlen($contenido) > 2000) {
        Response::validationError(['contenido' => 'El mensaje no puede estar vacío (máx. 2000 caracteres)']);
    }
    if ($destinatario_id === $user_id) {
        Response::error('No puedes enviarte un mensaje a ti mismo', 400);
    }

    try {
        $stmt = $pdo->prepare("SELECT id_usuario FROM usuarios WHERE id_usuario = :id AND id_empresa = :empresa_id");
        $stmt->execute([':id' => $destinatario_id, ':empresa_id' => $empresa_id]);
        if (!$stmt->fetch()) {
            Response::forbidden('No puede enviar mensajes a este usuario');
        }

        $stmt = $pdo->prepare("
            INSERT INTO mensajes (contenido, id_usuario, id_destinatario, fecha_envio, estado, leido)
            VALUES (:contenido, :remitente, :destinatario, NOW(), 1, 0)
        ");
        $stmt->execute([
            ':contenido'   => $contenido,
            ':remitente'   => $user_id,
            ':destinatario'=> $destinatario_id,
        ]);

        $id = $pdo->lastInsertId();

        Response::created([
            'id_mensajes'      => (int) $id,
            'contenido'        => $contenido,
            'fecha_envio'      => date('Y-m-d H:i:s'),
            'id_usuario'       => $user_id,
            'id_destinatario'  => $destinatario_id,
            'propio'           => true,
        ], 'Mensaje enviado');

    } catch (PDOException $e) {
        Logger::error('Error al enviar mensaje', $e);
        Response::serverError('Error al enviar mensaje');
    }
}

/* ────────────────────────────────────────────────────────────
 *  NO_LEIDOS — conteo de mensajes pendientes por remitente
 * ──────────────────────────────────────────────────────────── */
function handleNoLeidos($user_id) {
    global $pdo;

    try {
        $stmt = $pdo->prepare("
            SELECT id_usuario AS remitente_id, COUNT(*) AS cantidad
            FROM mensajes
            WHERE id_destinatario = :me AND leido = 0
            GROUP BY id_usuario
        ");
        $stmt->execute([':me' => $user_id]);
        $resultado = $stmt->fetchAll();

        Response::success($resultado);

    } catch (PDOException $e) {
        Logger::error('Error al contar no leídos', $e);
        Response::serverError();
    }
}