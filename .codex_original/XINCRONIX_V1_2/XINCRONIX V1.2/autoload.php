<?php
/**
 * Autoloader PSR-4 para namespaces
 */

spl_autoload_register(function ($class) {
    // Namespaces soportados
    $prefixes = [
        'App\\' => __DIR__ . '/app/',
        'Config\\' => __DIR__ . '/config/',
        'Helper\\' => __DIR__ . '/helpers/',
    ];
    
    foreach ($prefixes as $prefix => $baseDir) {
        if (strpos($class, $prefix) === 0) {
            // Remover el prefix
            $relative = substr($class, strlen($prefix));
            
            // Convertir namespace a ruta
            $file = $baseDir . str_replace('\\', '/', $relative) . '.php';
            
            if (file_exists($file)) {
                require $file;
                return;
            }
        }
    }
});

// Backward compatibility para clases antiguas (sin namespace)
// Carpeta 'class/' para clases genéricas
spl_autoload_register(function ($class) {
    $file = __DIR__ . '/class/' . $class . '.php';
    if (file_exists($file)) {
        require $file;
    }
});
?>
