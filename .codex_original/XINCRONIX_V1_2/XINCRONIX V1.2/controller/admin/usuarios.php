<?php
// controller/admin/usuarios.php
// CRUD completo de usuarios para el panel de super administrador
// ─────────────────────────────────────────────────────────────
session_start();
require_once dirname(__DIR__) . '/config.php';

header('Content-Type: application/json; charset=utf-8');

$action = $_SERVER['REQUEST_METHOD'] === 'GET' ? ($_GET['action'] ?? '') : ($_POST['action'] ?? '');

switch ($action) {
    case 'list':   listUsuarios();   break;
    case 'create': createUsuario();  break;
    case 'update': updateUsuario();  break;
    case 'toggle': toggleUsuario();  break;
    case 'delete': deleteUsuario();  break;
    default: echo json_encode(['status' => 'error', 'message' => 'Acción no válida.']);
}

function listUsuarios(): void {
    global $pdo;
    try {
        $stmt = $pdo->query("
            SELECT
                u.id_usuario, u.nombres, u.apellidos, u.email,
                u.cargo, u.telefono, u.avatar, u.estado,
                u.id_empresa, u.id_roles, u.fecha_creacion,
                e.nombre AS nombre_empresa,
                r.nombre AS nombre_rol
            FROM usuarios u
            LEFT JOIN empresa e ON e.id_empresa = u.id_empresa
            LEFT JOIN roles   r ON r.id_roles   = u.id_roles
            ORDER BY u.fecha_creacion DESC
        ");
        echo json_encode(['status' => 'success', 'data' => $stmt->fetchAll()]);
    } catch (PDOException $ex) {
        error_log('[Admin:Usuarios] list: ' . $ex->getMessage());
        echo json_encode(['status' => 'error', 'message' => 'Error al obtener usuarios.']);
    }
}

function createUsuario(): void {
    global $pdo;
    $nombres    = trim($_POST['nombres']    ?? '');
    $apellidos  = trim($_POST['apellidos']  ?? '');
    $email      = strtolower(trim($_POST['email'] ?? ''));
    $password   = $_POST['password'] ?? '';
    $id_empresa = (int)($_POST['id_empresa'] ?? 0);
    $id_roles   = (int)($_POST['id_roles']   ?? 3);
    $cargo      = trim($_POST['cargo']    ?? '');
    $telefono   = trim($_POST['telefono'] ?? '');

    if (empty($nombres) || empty($apellidos) || !filter_var($email, FILTER_VALIDATE_EMAIL) || !$id_empresa) {
        echo json_encode(['status' => 'error', 'message' => 'Datos incompletos o inválidos.']);
        return;
    }
    if (strlen($password) < 8) {
        echo json_encode(['status' => 'error', 'message' => 'La contraseña debe tener mínimo 8 caracteres.']);
        return;
    }

    try {
        $dup = $pdo->prepare("SELECT id_usuario FROM usuarios WHERE email = :email LIMIT 1");
        $dup->execute([':email' => $email]);
        if ($dup->fetch()) {
            echo json_encode(['status' => 'error', 'message' => 'Ya existe un usuario con ese email.']);
            return;
        }

        $hash = password_hash($password, PASSWORD_BCRYPT, ['cost' => 12]);
        $stmt = $pdo->prepare("
            INSERT INTO usuarios
                (nombres, apellidos, email, password, cargo, telefono, id_empresa, id_roles, estado, fecha_creacion)
            VALUES
                (:nombres, :apellidos, :email, :password, :cargo, :telefono, :id_empresa, :id_roles, 1, NOW())
        ");
        $stmt->execute([
            ':nombres'    => $nombres,
            ':apellidos'  => $apellidos,
            ':email'      => $email,
            ':password'   => $hash,
            ':cargo'      => $cargo,
            ':telefono'   => $telefono,
            ':id_empresa' => $id_empresa,
            ':id_roles'   => $id_roles,
        ]);
        echo json_encode(['status' => 'success', 'message' => 'Usuario creado correctamente.', 'id' => $pdo->lastInsertId()]);
    } catch (PDOException $ex) {
        error_log('[Admin:Usuarios] create: ' . $ex->getMessage());
        echo json_encode(['status' => 'error', 'message' => 'Error al crear el usuario.']);
    }
}

function updateUsuario(): void {
    global $pdo;
    $id        = (int)($_POST['id_usuario'] ?? 0);
    $nombres   = trim($_POST['nombres']   ?? '');
    $apellidos = trim($_POST['apellidos'] ?? '');
    $email     = strtolower(trim($_POST['email'] ?? ''));
    $id_empresa= (int)($_POST['id_empresa'] ?? 0);
    $id_roles  = (int)($_POST['id_roles']   ?? 3);
    $cargo     = trim($_POST['cargo']    ?? '');
    $telefono  = trim($_POST['telefono'] ?? '');
    $estado    = (int)($_POST['estado']  ?? 1);
    $password  = $_POST['password'] ?? '';

    if (!$id || empty($nombres) || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
        echo json_encode(['status' => 'error', 'message' => 'Datos inválidos.']);
        return;
    }

    try {
        // Verificar email duplicado excluyendo propio
        $dup = $pdo->prepare("SELECT id_usuario FROM usuarios WHERE email = :email AND id_usuario != :id LIMIT 1");
        $dup->execute([':email' => $email, ':id' => $id]);
        if ($dup->fetch()) {
            echo json_encode(['status' => 'error', 'message' => 'Otro usuario ya usa ese email.']);
            return;
        }

        // Actualizar campos base
        $stmt = $pdo->prepare("
            UPDATE usuarios SET
                nombres   = :nombres, apellidos = :apellidos,
                email     = :email,   cargo     = :cargo,
                telefono  = :telefono, id_empresa = :id_empresa,
                id_roles  = :id_roles, estado    = :estado
            WHERE id_usuario = :id
        ");
        $stmt->execute([
            ':nombres'    => $nombres,   ':apellidos' => $apellidos,
            ':email'      => $email,     ':cargo'     => $cargo,
            ':telefono'   => $telefono,  ':id_empresa'=> $id_empresa,
            ':id_roles'   => $id_roles,  ':estado'    => $estado,
            ':id'         => $id,
        ]);

        // Actualizar contraseña solo si se proporcionó
        if (!empty($password)) {
            if (strlen($password) < 8) {
                echo json_encode(['status' => 'error', 'message' => 'La contraseña debe tener mínimo 8 caracteres.']);
                return;
            }
            $hash = password_hash($password, PASSWORD_BCRYPT, ['cost' => 12]);
            $pdo->prepare("UPDATE usuarios SET password = :p WHERE id_usuario = :id")
                ->execute([':p' => $hash, ':id' => $id]);
        }

        echo json_encode(['status' => 'success', 'message' => 'Usuario actualizado correctamente.']);
    } catch (PDOException $ex) {
        error_log('[Admin:Usuarios] update: ' . $ex->getMessage());
        echo json_encode(['status' => 'error', 'message' => 'Error al actualizar el usuario.']);
    }
}

function toggleUsuario(): void {
    global $pdo;
    $id     = (int)($_POST['id_usuario'] ?? 0);
    $estado = (int)($_POST['estado']     ?? 0);
    if (!$id) { echo json_encode(['status' => 'error', 'message' => 'ID inválido.']); return; }
    try {
        $pdo->prepare("UPDATE usuarios SET estado = :e WHERE id_usuario = :id")
            ->execute([':e' => $estado, ':id' => $id]);
        echo json_encode(['status' => 'success', 'message' => 'Estado actualizado.']);
    } catch (PDOException $ex) {
        error_log('[Admin:Usuarios] toggle: ' . $ex->getMessage());
        echo json_encode(['status' => 'error', 'message' => 'Error al cambiar el estado.']);
    }
}

function deleteUsuario(): void {
    global $pdo;
    $id = (int)($_POST['id_usuario'] ?? 0);
    if (!$id) { echo json_encode(['status' => 'error', 'message' => 'ID inválido.']); return; }
    try {
        $stmt = $pdo->prepare("DELETE FROM usuarios WHERE id_usuario = :id");
        $stmt->execute([':id' => $id]);
        if ($stmt->rowCount() === 0) {
            echo json_encode(['status' => 'error', 'message' => 'Usuario no encontrado.']);
            return;
        }
        echo json_encode(['status' => 'success', 'message' => 'Usuario eliminado correctamente.']);
    } catch (PDOException $ex) {
        error_log('[Admin:Usuarios] delete: ' . $ex->getMessage());
        echo json_encode(['status' => 'error', 'message' => 'Error al eliminar el usuario.']);
    }
}