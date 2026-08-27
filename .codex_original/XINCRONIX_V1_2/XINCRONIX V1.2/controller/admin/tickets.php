<?php
/* ══════════════════════════════════════════════════════════════
   controller/admin/tickets.php
   CRUD de tickets de soporte técnico
══════════════════════════════════════════════════════════════ */
session_start();
require_once dirname(__DIR__) . '/config.php';
header('Content-Type: application/json; charset=utf-8');

// ── Crear tabla si no existe ──────────────────────────────────
try {
    $pdo->exec("
        CREATE TABLE IF NOT EXISTS tickets_soporte (
            id_ticket      INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            asunto         VARCHAR(200) NOT NULL,
            descripcion    TEXT,
            prioridad      VARCHAR(20)  DEFAULT 'media',
            estado         VARCHAR(30)  DEFAULT 'abierto',
            id_empresa     INT UNSIGNED,
            fecha_creacion TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
            fecha_cierre   TIMESTAMP    NULL,
            FOREIGN KEY (id_empresa) REFERENCES empresa(id_empresa) ON DELETE SET NULL
        ) ENGINE=InnoDB
    ");
} catch (PDOException $ignored) {}

$action = $_SERVER['REQUEST_METHOD'] === 'GET' ? ($_GET['action'] ?? '') : ($_POST['action'] ?? '');

switch ($action) {
    case 'list':   listTickets();   break;
    case 'create': createTicket();  break;
    case 'update': updateTicket();  break;
    case 'delete': deleteTicket();  break;
    default: echo json_encode(['status'=>'error','message'=>'Acción no válida.']);
}

function listTickets(): void {
    global $pdo;
    try {
        $stmt = $pdo->query("
            SELECT
                t.id_ticket, t.asunto, t.descripcion,
                t.prioridad, t.estado,
                t.fecha_creacion, t.fecha_cierre,
                e.nombre AS nombre_empresa
            FROM tickets_soporte t
            LEFT JOIN empresa e ON e.id_empresa = t.id_empresa
            ORDER BY
                FIELD(t.prioridad,'alta','media','baja'),
                FIELD(t.estado,'abierto','proceso','cerrado'),
                t.fecha_creacion DESC
        ");
        echo json_encode(['status'=>'success','data'=>$stmt->fetchAll()]);
    } catch (PDOException $ex) {
        error_log('[Admin:Tickets] list: '.$ex->getMessage());
        echo json_encode(['status'=>'error','message'=>'Error al obtener tickets.']);
    }
}

function createTicket(): void {
    global $pdo;
    $asunto      = trim($_POST['asunto']      ?? '');
    $descripcion = trim($_POST['descripcion'] ?? '');
    $prioridad   = trim($_POST['prioridad']   ?? 'media');
    $estado      = trim($_POST['estado']      ?? 'abierto');
    $id_empresa  = (int)($_POST['id_empresa'] ?? 0) ?: null;

    if (empty($asunto) || empty($descripcion)) {
        echo json_encode(['status'=>'error','message'=>'Asunto y descripción son obligatorios.']);
        return;
    }
    if (!in_array($prioridad, ['alta','media','baja'])) $prioridad = 'media';
    if (!in_array($estado, ['abierto','proceso','cerrado'])) $estado = 'abierto';

    try {
        $stmt = $pdo->prepare("
            INSERT INTO tickets_soporte
                (asunto, descripcion, prioridad, estado, id_empresa, fecha_creacion)
            VALUES
                (:asunto, :descripcion, :prioridad, :estado, :id_empresa, NOW())
        ");
        $stmt->execute([
            ':asunto'      => $asunto,
            ':descripcion' => $descripcion,
            ':prioridad'   => $prioridad,
            ':estado'      => $estado,
            ':id_empresa'  => $id_empresa,
        ]);
        echo json_encode(['status'=>'success','message'=>'Ticket creado.','id'=>$pdo->lastInsertId()]);
    } catch (PDOException $ex) {
        error_log('[Admin:Tickets] create: '.$ex->getMessage());
        echo json_encode(['status'=>'error','message'=>'Error al crear el ticket.']);
    }
}

function updateTicket(): void {
    global $pdo;
    $id          = (int)($_POST['id_ticket']   ?? 0);
    $asunto      = trim($_POST['asunto']        ?? '');
    $descripcion = trim($_POST['descripcion']   ?? '');
    $prioridad   = trim($_POST['prioridad']     ?? 'media');
    $estado      = trim($_POST['estado']        ?? 'abierto');
    $id_empresa  = (int)($_POST['id_empresa']   ?? 0) ?: null;

    if (!$id) { echo json_encode(['status'=>'error','message'=>'ID inválido.']); return; }

    try {
        $fechaCierre = $estado === 'cerrado' ? 'NOW()' : 'NULL';
        $stmt = $pdo->prepare("
            UPDATE tickets_soporte SET
                asunto      = :asunto,
                descripcion = :descripcion,
                prioridad   = :prioridad,
                estado      = :estado,
                id_empresa  = :id_empresa,
                fecha_cierre = " . ($estado === 'cerrado' ? 'NOW()' : 'fecha_cierre') . "
            WHERE id_ticket = :id
        ");
        $stmt->execute([
            ':asunto'      => $asunto,
            ':descripcion' => $descripcion,
            ':prioridad'   => $prioridad,
            ':estado'      => $estado,
            ':id_empresa'  => $id_empresa,
            ':id'          => $id,
        ]);
        echo json_encode(['status'=>'success','message'=>'Ticket actualizado.']);
    } catch (PDOException $ex) {
        error_log('[Admin:Tickets] update: '.$ex->getMessage());
        echo json_encode(['status'=>'error','message'=>'Error al actualizar.']);
    }
}

function deleteTicket(): void {
    global $pdo;
    $id = (int)($_POST['id_ticket'] ?? 0);
    if (!$id) { echo json_encode(['status'=>'error','message'=>'ID inválido.']); return; }
    try {
        $pdo->prepare("DELETE FROM tickets_soporte WHERE id_ticket = :id")->execute([':id' => $id]);
        echo json_encode(['status'=>'success','message'=>'Ticket eliminado.']);
    } catch (PDOException $ex) {
        error_log('[Admin:Tickets] delete: '.$ex->getMessage());
        echo json_encode(['status'=>'error','message'=>'Error al eliminar.']);
    }
}