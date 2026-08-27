<?php
/* ══════════════════════════════════════════════════════════════
   controller/admin/pagos.php
   Revisión y aprobación de solicitudes de pago
══════════════════════════════════════════════════════════════ */
session_start();
require_once dirname(__DIR__) . '/config.php';
header('Content-Type: application/json; charset=utf-8');

$action = $_SERVER['REQUEST_METHOD'] === 'GET' ? ($_GET['action'] ?? '') : ($_POST['action'] ?? '');

switch ($action) {
    case 'list':    listPagos();    break;
    case 'aprobar': aprobarPago();  break;
    case 'rechazar':rechazarPago(); break;
    default: echo json_encode(['status'=>'error','message'=>'Acción no válida.']);
}

function listPagos(): void {
    global $pdo;
    try {
        $stmt = $pdo->query("
            SELECT
                sp.id_solicitud, sp.plan, sp.metodo_pago,
                sp.referencia, sp.notas, sp.ruta_comprobante,
                sp.estado, sp.fecha_creacion, sp.fecha_revision,
                e.nombre AS nombre_empresa, e.email AS email_empresa
            FROM solicitudes_pago sp
            LEFT JOIN empresa e ON e.id_empresa = sp.id_empresa
            ORDER BY
                FIELD(sp.estado, 'pendiente', 'aprobado', 'rechazado'),
                sp.fecha_creacion DESC
        ");
        echo json_encode(['status'=>'success','data'=>$stmt->fetchAll()]);
    } catch (PDOException $ex) {
        error_log('[Admin:Pagos] list: '.$ex->getMessage());
        echo json_encode(['status'=>'error','message'=>'Error al obtener pagos.']);
    }
}

function aprobarPago(): void {
    global $pdo;
    $id = (int)($_POST['id_solicitud'] ?? 0);
    if (!$id) { echo json_encode(['status'=>'error','message'=>'ID inválido.']); return; }
    try {
        $pdo->beginTransaction();

        // Marcar solicitud como aprobada
        $pdo->prepare("
            UPDATE solicitudes_pago
            SET estado = 'aprobado', fecha_revision = NOW()
            WHERE id_solicitud = :id
        ")->execute([':id' => $id]);

        // Activar empresa asociada (estado en usuarios = 1)
        $stmt = $pdo->prepare("
            SELECT id_empresa FROM solicitudes_pago WHERE id_solicitud = :id
        ");
        $stmt->execute([':id' => $id]);
        $row = $stmt->fetch();
        if ($row) {
            $pdo->prepare("
                UPDATE usuarios SET estado = 1
                WHERE id_empresa = :eid
            ")->execute([':eid' => $row['id_empresa']]);
        }

        $pdo->commit();
        echo json_encode(['status'=>'success','message'=>'Pago aprobado y empresa activada.']);
    } catch (PDOException $ex) {
        $pdo->rollBack();
        error_log('[Admin:Pagos] aprobar: '.$ex->getMessage());
        echo json_encode(['status'=>'error','message'=>'Error al aprobar el pago.']);
    }
}

function rechazarPago(): void {
    global $pdo;
    $id = (int)($_POST['id_solicitud'] ?? 0);
    if (!$id) { echo json_encode(['status'=>'error','message'=>'ID inválido.']); return; }
    try {
        $pdo->prepare("
            UPDATE solicitudes_pago
            SET estado = 'rechazado', fecha_revision = NOW()
            WHERE id_solicitud = :id
        ")->execute([':id' => $id]);
        echo json_encode(['status'=>'success','message'=>'Pago rechazado.']);
    } catch (PDOException $ex) {
        error_log('[Admin:Pagos] rechazar: '.$ex->getMessage());
        echo json_encode(['status'=>'error','message'=>'Error al rechazar el pago.']);
    }
}