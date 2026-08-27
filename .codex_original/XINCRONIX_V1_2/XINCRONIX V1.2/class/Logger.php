<?php
/**
 * Sistema de logging centralizado
 * Uso: Logger::info("Usuario login", ['user_id' => 123]);
 */

class Logger {
    
    const INFO = 'INFO';
    const WARNING = 'WARNING';
    const ERROR = 'ERROR';
    const DEBUG = 'DEBUG';
    const SUCCESS = 'SUCCESS';
    
    private static $logPath = __DIR__ . '/../logs/';
    
    public static function init() {
        if (!is_dir(self::$logPath)) {
            mkdir(self::$logPath, 0755, true);
        }
    }
    
    public static function info($message, $context = []) {
        self::write(self::INFO, $message, $context);
    }
    
    public static function warning($message, $context = []) {
        self::write(self::WARNING, $message, $context);
    }
    
    public static function error($message, $exception = null) {
        $context = [];
        if ($exception instanceof Exception) {
            $context = [
                'file' => $exception->getFile(),
                'line' => $exception->getLine(),
                'trace' => $exception->getTraceAsString()
            ];
        }
        self::write(self::ERROR, $message, $context);
    }
    
    public static function debug($message, $context = []) {
        if (getenv('APP_DEBUG') === 'true') {
            self::write(self::DEBUG, $message, $context);
        }
    }
    
    public static function success($action, $context = []) {
        $message = "✓ " . $action;
        self::write(self::SUCCESS, $message, $context);
    }
    
    private static function write($level, $message, $context = []) {
        self::init();
        
        $caller = self::getCaller();
        $timestamp = date('Y-m-d H:i:s');
        
        $contextStr = '';
        if (!empty($context)) {
            $contextStr = ' | ' . json_encode($context, JSON_UNESCAPED_UNICODE);
        }
        
        $logEntry = "[$timestamp] [$level] [{$caller}] $message$contextStr\n";
        
        // Archivo general
        file_put_contents(
            self::$logPath . date('Y-m-d') . '.log',
            $logEntry,
            FILE_APPEND | LOCK_EX
        );
        
        // Archivo de errores separado
        if ($level === self::ERROR) {
            file_put_contents(
                self::$logPath . 'errores-' . date('Y-m-d') . '.log',
                $logEntry,
                FILE_APPEND | LOCK_EX
            );
        }
    }
    
    private static function getCaller() {
        $trace = debug_backtrace();
        foreach ($trace as $frame) {
            if ($frame['function'] !== 'write' && $frame['function'] !== 'getCaller') {
                $file = basename($frame['file']);
                return "{$file}:{$frame['line']}";
            }
        }
        return 'unknown';
    }
}

Logger::init();
?>
