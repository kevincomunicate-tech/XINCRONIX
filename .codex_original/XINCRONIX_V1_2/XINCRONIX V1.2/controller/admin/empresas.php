<?php
/* ══════════════════════════════════════════════════════════════
   controller/admin/empresas.php
   CRUD completo para la tabla `empresa`

   FIXES aplicados:
   - createEmpresa(): se eliminó el campo duplicado `industria = :sector`
     en el INSERT y ahora se inserta correctamente.
   - updateEmpresa(): mismo fix para el UPDATE.
   - Ambas funciones validan y limpian la entrada antes de ejecutar.
   - Se añade manejo explícito de errores con mensajes descriptivos.
══════════════════════════════════════════════════════════════ */
session_start();
require_once dirname(__DIR__) . '/config.php';

header('Content-Type: application/json; charset=utf-8');

$method = $_SERVER['REQUEST_METHOD'];
$action = $method === 'GET' ? ($_GET['action'] ?? '') : ($_POST['action'] ?? '');

switch ($action) {
    case 'list':   listEmpresas();   break;
    case 'get':    getEmpresa();     break;
    case 'create': createEmpresa();  break;
    case 'update': updateEmpresa();  break;
    case 'delete': deleteEmpresa();  break;
    default:
        echo json_encode(['status' => 'error', 'message' => 'Acción no válida: ' . htmlspecialchars($action)]);
}

// ─────────────────────────────────────────────
// LIST
// ─────────────────────────────────────────────
function listEmpresas(): void
{
    global $pdo;
    try {
        $stmt = $pdo->query("
            SELECT
                e.id_empresa,
                e.nombre,
                e.nit,
                e.email,
                e.telefono,
                e.direccion,
                e.sector,
                e.industria,
                e.plan_suscripcion,
                e.administrador,
                e.num_empleados,
                e.comprobante,
                e.fecha_creacion,
                e.fecha_actualizacion,
                COUNT(u.id_usuario) AS total_usuarios
            FROM empresa e
            LEFT JOIN usuarios u ON u.id_empresa = e.id_empresa
            GROUP BY e.id_empresa
            ORDER BY e.fecha_creacion DESC
        ");
        echo json_encode(['status' => 'success', 'data' => $stmt->fetchAll()]);
    } catch (PDOException $e) {
        error_log('[Admin:Empresas] list: ' . $e->getMessage());
        echo json_encode(['status' => 'error', 'message' => 'Error al obtener las empresas.']);
    }
}

// ─────────────────────────────────────────────
// GET (single)
// ─────────────────────────────────────────────
function getEmpresa(): void
{
    global $pdo;
    $id = (int)($_GET['id'] ?? 0);
    if (!$id) {
        echo json_encode(['status' => 'error', 'message' => 'ID inválido.']);
        return;
    }
    try {
        $stmt = $pdo->prepare("SELECT * FROM empresa WHERE id_empresa = :id LIMIT 1");
        $stmt->execute([':id' => $id]);
        $row = $stmt->fetch();
        if (!$row) {
            echo json_encode(['status' => 'error', 'message' => 'Empresa no encontrada.']);
            return;
        }
        echo json_encode(['status' => 'success', 'data' => $row]);
    } catch (PDOException $e) {
        error_log('[Admin:Empresas] get: ' . $e->getMessage());
        echo json_encode(['status' => 'error', 'message' => 'Error al obtener la empresa.']);
    }
}

// ─────────────────────────────────────────────
// CREATE
// FIX: el INSERT original duplicaba `:sector` para la columna `industria`,
//      causando un error de parámetro nombrado repetido en PDO.
//      Ahora `industria` usa su propio parámetro `:industria`.
// ─────────────────────────────────────────────
function createEmpresa(): void
{
    global $pdo;

    $nombre        = trim($_POST['nombre']        ?? '');
    $nit           = trim($_POST['nit']           ?? '');
    $email         = strtolower(trim($_POST['email'] ?? ''));
    $telefono      = trim($_POST['telefono']      ?? '');
    $sector        = trim($_POST['sector']        ?? '');
    $industria     = $sector; // mismo valor; columna separada en el schema
    $plan          = strtolower(trim($_POST['plan'] ?? 'business'));
    $administrador = trim($_POST['administrador'] ?? '');
    $num_empleados = trim($_POST['num_empleados'] ?? '');
    $direccion     = trim($_POST['direccion']     ?? '');

    // ── Validación ────────────────────────────────────────────
    $errores = [];
    if ($nombre === '')                                               $errores[] = 'El nombre es obligatorio.';
    if ($nit    === '')                                               $errores[] = 'El NIT es obligatorio.';
    if ($email  === '' || !filter_var($email, FILTER_VALIDATE_EMAIL)) $errores[] = 'Email no válido.';
    if (!in_array($plan, ['starter', 'business', 'enterprise'], true)) $errores[] = 'Plan no válido.';

    if (!empty($errores)) {
        echo json_encode(['status' => 'error', 'message' => implode(' ', $errores)]);
        return;
    }

    try {
        // Verificar duplicado de email o NIT
        $dup = $pdo->prepare(
            "SELECT id_empresa FROM empresa WHERE email = :email OR nit = :nit LIMIT 1"
        );
        $dup->execute([':email' => $email, ':nit' => $nit]);
        if ($dup->fetch()) {
            echo json_encode(['status' => 'error', 'message' => 'Ya existe una empresa con ese email o NIT.']);
            return;
        }

        // ── INSERT corregido ──────────────────────────────────
        $stmt = $pdo->prepare("
            INSERT INTO empresa
                (nombre, nit, email, telefono, sector, industria, plan_suscripcion,
                 administrador, num_empleados, direccion, fecha_creacion)
            VALUES
                (:nombre, :nit, :email, :telefono, :sector, :industria, :plan,
                 :administrador, :num_empleados, :direccion, NOW())
        ");
        $stmt->execute([
            ':nombre'        => $nombre,
            ':nit'           => $nit,
            ':email'         => $email,
            ':telefono'      => $telefono,
            ':sector'        => $sector,
            ':industria'     => $industria,   // ← FIX: parámetro propio, no reutilizar :sector
            ':plan'          => $plan,
            ':administrador' => $administrador,
            ':num_empleados' => $num_empleados,
            ':direccion'     => $direccion,
        ]);

        $newId = (int)$pdo->lastInsertId();
        echo json_encode([
            'status'  => 'success',
            'message' => 'Empresa creada correctamente.',
            'id'      => $newId,
        ]);

    } catch (PDOException $e) {
        error_log('[Admin:Empresas] create: ' . $e->getMessage());
        // Código SQLSTATE 23000 = Integrity constraint violation (duplicado)
        if (str_starts_with((string)$e->getCode(), '23')) {
            echo json_encode(['status' => 'error', 'message' => 'Email o NIT ya registrado.']);
        } else {
            echo json_encode(['status' => 'error', 'message' => 'Error al crear la empresa: ' . $e->getMessage()]);
        }
    }
}

// ─────────────────────────────────────────────
// UPDATE
// FIX: mismo fix que en CREATE para el parámetro :industria.
// ─────────────────────────────────────────────
function updateEmpresa(): void
{
    global $pdo;

    $id            = (int)($_POST['id_empresa']  ?? 0);
    $nombre        = trim($_POST['nombre']        ?? '');
    $nit           = trim($_POST['nit']           ?? '');
    $email         = strtolower(trim($_POST['email'] ?? ''));
    $telefono      = trim($_POST['telefono']      ?? '');
    $sector        = trim($_POST['sector']        ?? '');
    $industria     = $sector;
    $plan          = strtolower(trim($_POST['plan'] ?? ''));
    $administrador = trim($_POST['administrador'] ?? '');
    $num_empleados = trim($_POST['num_empleados'] ?? '');
    $direccion     = trim($_POST['direccion']     ?? '');

    if (!$id || $nombre === '' || $email === '') {
        echo json_encode(['status' => 'error', 'message' => 'Datos incompletos (id, nombre o email vacíos).']);
        return;
    }
    if (!in_array($plan, ['starter', 'business', 'enterprise', ''], true)) {
        $plan = 'business'; // valor por defecto seguro
    }

    try {
        // Verificar duplicado excluyendo la propia empresa
        $dup = $pdo->prepare("
            SELECT id_empresa FROM empresa
            WHERE (email = :email OR nit = :nit)
              AND id_empresa != :id
            LIMIT 1
        ");
        $dup->execute([':email' => $email, ':nit' => $nit, ':id' => $id]);
        if ($dup->fetch()) {
            echo json_encode(['status' => 'error', 'message' => 'Otro registro ya usa ese email o NIT.']);
            return;
        }

        // ── UPDATE corregido ──────────────────────────────────
        $stmt = $pdo->prepare("
            UPDATE empresa SET
                nombre               = :nombre,
                nit                  = :nit,
                email                = :email,
                telefono             = :telefono,
                sector               = :sector,
                industria            = :industria,   -- ← FIX
                plan_suscripcion     = :plan,
                administrador        = :administrador,
                num_empleados        = :num_empleados,
                direccion            = :direccion,
                fecha_actualizacion  = NOW()
            WHERE id_empresa = :id
        ");
        $stmt->execute([
            ':nombre'        => $nombre,
            ':nit'           => $nit,
            ':email'         => $email,
            ':telefono'      => $telefono,
            ':sector'        => $sector,
            ':industria'     => $industria,   // ← FIX
            ':plan'          => $plan,
            ':administrador' => $administrador,
            ':num_empleados' => $num_empleados,
            ':direccion'     => $direccion,
            ':id'            => $id,
        ]);

        if ($stmt->rowCount() === 0) {
            // La empresa existe pero no hubo cambios reales → también es éxito
            echo json_encode(['status' => 'success', 'message' => 'Sin cambios detectados.']);
        } else {
            echo json_encode(['status' => 'success', 'message' => 'Empresa actualizada correctamente.']);
        }

    } catch (PDOException $e) {
        error_log('[Admin:Empresas] update: ' . $e->getMessage());
        if (str_starts_with((string)$e->getCode(), '23')) {
            echo json_encode(['status' => 'error', 'message' => 'Email o NIT ya registrado en otra empresa.']);
        } else {
            echo json_encode(['status' => 'error', 'message' => 'Error al actualizar la empresa: ' . $e->getMessage()]);
        }
    }
}

// ─────────────────────────────────────────────
// DELETE
// ─────────────────────────────────────────────
function deleteEmpresa(): void
{
    global $pdo;
    $id = (int)($_POST['id_empresa'] ?? 0);
    if (!$id) {
        echo json_encode(['status' => 'error', 'message' => 'ID inválido.']);
        return;
    }
    try {
        $stmt = $pdo->prepare("DELETE FROM empresa WHERE id_empresa = :id");
        $stmt->execute([':id' => $id]);
        if ($stmt->rowCount() === 0) {
            echo json_encode(['status' => 'error', 'message' => 'Empresa no encontrada.']);
            return;
        }
        echo json_encode(['status' => 'success', 'message' => 'Empresa eliminada correctamente.']);
    } catch (PDOException $e) {
        error_log('[Admin:Empresas] delete: ' . $e->getMessage());
        echo json_encode(['status' => 'error', 'message' => 'Error al eliminar: ' . $e->getMessage()]);
    }
}