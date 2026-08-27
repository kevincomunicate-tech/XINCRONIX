<?php
/* ══════════════════════════════════════════════════════════════
   controller/admin/dashboard.php
   Estadísticas globales para el panel de administrador
══════════════════════════════════════════════════════════════ */
session_start();
require_once dirname(__DIR__) . '/config.php';
header('Content-Type: application/json; charset=utf-8');

try {
    // ── Totales ───────────────────────────────────────────────
    $totalEmpresas = (int)$pdo->query("SELECT COUNT(*) FROM empresa")->fetchColumn();
    $totalUsuarios = (int)$pdo->query("SELECT COUNT(*) FROM usuarios WHERE estado = 1")->fetchColumn();

    // ── Pagos pendientes ─────────────────────────────────────
    $pagosPendientes = 0;
    try {
        $pagosPendientes = (int)$pdo->query(
            "SELECT COUNT(*) FROM solicitudes_pago WHERE estado = 'pendiente'"
        )->fetchColumn();
    } catch (PDOException $ignored) {}

    // ── Tickets ───────────────────────────────────────────────
    $ticketsAbiertos = $ticketsProceso = $ticketsCerrados = 0;
    try {
        $tk = $pdo->query("SELECT estado, COUNT(*) AS n FROM tickets_soporte GROUP BY estado")->fetchAll();
        foreach ($tk as $row) {
            if ($row['estado'] === 'abierto')  $ticketsAbiertos = (int)$row['n'];
            if ($row['estado'] === 'proceso')  $ticketsProceso  = (int)$row['n'];
            if ($row['estado'] === 'cerrado')  $ticketsCerrados = (int)$row['n'];
        }
    } catch (PDOException $ignored) {}

    // ── Empresas por plan ─────────────────────────────────────
    $planesRaw = $pdo->query("
        SELECT plan_suscripcion, COUNT(*) AS n
        FROM empresa
        GROUP BY plan_suscripcion
    ")->fetchAll();
    $planes = ['starter' => 0, 'business' => 0, 'enterprise' => 0];
    foreach ($planesRaw as $p) {
        $key = strtolower($p['plan_suscripcion'] ?? 'starter');
        if (isset($planes[$key])) $planes[$key] = (int)$p['n'];
    }
    // Normalizar a porcentajes para el donut
    $total = array_sum($planes) ?: 1;
    $planesP = array_map(fn($v) => round(($v / $total) * 100), $planes);

    // ── Empresas recientes (últimas 5) ────────────────────────
    $empresasRecientes = $pdo->query("
        SELECT id_empresa, nombre, email, plan_suscripcion, fecha_creacion
        FROM empresa
        ORDER BY fecha_creacion DESC
        LIMIT 5
    ")->fetchAll();

    // ── Registros por mes (últimos 7 meses) ──────────────────
    $registrosMeses = [];
    $meses = $pdo->query("
        SELECT
            DATE_FORMAT(fecha_creacion, '%b') AS mes,
            COUNT(*) AS n
        FROM empresa
        WHERE fecha_creacion >= DATE_SUB(NOW(), INTERVAL 7 MONTH)
        GROUP BY YEAR(fecha_creacion), MONTH(fecha_creacion)
        ORDER BY fecha_creacion ASC
        LIMIT 7
    ")->fetchAll();
    foreach ($meses as $m) $registrosMeses[] = (int)$m['n'];
    // Rellenar hasta 7 meses si hay menos datos
    while (count($registrosMeses) < 7) array_unshift($registrosMeses, 0);

    echo json_encode([
        'status' => 'success',
        'data'   => [
            'total_empresas'     => $totalEmpresas,
            'total_usuarios'     => $totalUsuarios,
            'pagos_pendientes'   => $pagosPendientes,
            'tickets_abiertos'   => $ticketsAbiertos,
            'tickets_proceso'    => $ticketsProceso,
            'tickets_cerrados'   => $ticketsCerrados,
            'planes'             => $planesP,
            'empresas_recientes' => $empresasRecientes,
            'registros_meses'    => $registrosMeses,
        ],
    ]);

} catch (PDOException $ex) {
    error_log('[Admin:Dashboard] error: ' . $ex->getMessage());
    echo json_encode(['status' => 'error', 'message' => 'Error al obtener estadísticas.']);
}