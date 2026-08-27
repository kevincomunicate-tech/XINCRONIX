<?php
/**
 * Clase para estandarizar respuestas JSON
 * Uso en controladores: Response::success($data, "Mensaje");
 */

class Response {
    
    public static function success($data = null, $message = "Operación exitosa", $code = 200) {
        self::json([
            'success' => true,
            'status_code' => $code,
            'message' => $message,
            'data' => $data,
            'timestamp' => date('c'),
            'errors' => []
        ], $code);
    }
    
    public static function error($message, $code = 400, $errors = []) {
        self::json([
            'success' => false,
            'status_code' => $code,
            'message' => $message,
            'data' => null,
            'timestamp' => date('c'),
            'errors' => $errors
        ], $code);
    }
    
    public static function created($data, $message = "Recurso creado") {
        self::success($data, $message, 201);
    }
    
    public static function notFound($message = "Recurso no encontrado") {
        self::error($message, 404);
    }
    
    public static function unauthorized($message = "No autorizado") {
        self::error($message, 401);
    }
    
    public static function forbidden($message = "Acceso prohibido") {
        self::error($message, 403);
    }
    
    public static function validationError($errors, $message = "Error de validación") {
        self::error($message, 422, $errors);
    }
    
    public static function serverError($message = "Error interno del servidor") {
        self::error($message, 500);
    }
    
    private static function json($data, $code = 200) {
        http_response_code($code);
        header('Content-Type: application/json; charset=utf-8');
        echo json_encode($data, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
        exit;
    }
}
?>
