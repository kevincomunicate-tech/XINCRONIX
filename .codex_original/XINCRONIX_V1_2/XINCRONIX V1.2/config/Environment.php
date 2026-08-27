<?php
/**
 * Gestor de variables de entorno
 * Uso: $db_host = Environment::get('DB_HOST');
 */

class Environment {
    private static $variables = [];
    private static $loaded = false;
    
    public static function load($file = '.env') {
        if (self::$loaded) return;
        
        if (!file_exists($file)) {
            die("ERROR: Archivo .env no encontrado en: " . realpath($file));
        }
        
        $lines = file($file, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
        
        foreach ($lines as $line) {
            // Ignorar comentarios
            if (strpos(trim($line), '#') === 0) continue;
            
            // Parsear KEY=VALUE
            if (strpos($line, '=') !== false) {
                list($key, $value) = explode('=', $line, 2);
                $key = trim($key);
                $value = trim($value);
                
                // Remover comillas
                $value = str_replace(['"', "'"], '', $value);
                
                self::$variables[$key] = $value;
                // También establecer en $_ENV y putenv
                putenv("$key=$value");
            }
        }
        
        self::$loaded = true;
    }
    
    public static function get($key, $default = null) {
        return self::$variables[$key] ?? $default;
    }
    
    public static function has($key) {
        return isset(self::$variables[$key]);
    }
    
    public static function require(...$keys) {
        $missing = [];
        foreach ($keys as $key) {
            if (!self::has($key)) {
                $missing[] = $key;
            }
        }
        
        if (!empty($missing)) {
            die("ERROR: Variables de entorno requeridas no encontradas: " . 
                implode(', ', $missing));
        }
    }
}

// Cargar automáticamente
Environment::load(__DIR__ . '/../.env');
?>
