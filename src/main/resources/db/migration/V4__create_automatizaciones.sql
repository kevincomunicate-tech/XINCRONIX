CREATE TABLE IF NOT EXISTS automatizaciones (
    id_automatizacion INT NOT NULL AUTO_INCREMENT,
    id_empresa INT UNSIGNED NOT NULL,
    id_usuario_creador INT UNSIGNED NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    disparador VARCHAR(150) NOT NULL,
    descripcion TEXT NULL,
    activa BOOLEAN NOT NULL DEFAULT TRUE,
    ejecuciones BIGINT NOT NULL DEFAULT 0,
    exitos BIGINT NOT NULL DEFAULT 0,
    errores BIGINT NOT NULL DEFAULT 0,
    ultima_ejecucion DATETIME NULL,
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_automatizacion),
    KEY idx_automatizaciones_empresa (id_empresa),
    KEY idx_automatizaciones_creador (id_usuario_creador),
    CONSTRAINT fk_automatizaciones_empresa
        FOREIGN KEY (id_empresa) REFERENCES empresa(id_empresa),
    CONSTRAINT fk_automatizaciones_creador
        FOREIGN KEY (id_usuario_creador) REFERENCES usuarios(id_usuario)
);
