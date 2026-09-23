CREATE TABLE IF NOT EXISTS actividades (
    id_actividad INT NOT NULL AUTO_INCREMENT,
    id_usuario INT UNSIGNED NOT NULL,
    id_empresa INT UNSIGNED NOT NULL,
    modulo VARCHAR(40) NOT NULL,
    accion VARCHAR(40) NOT NULL,
    detalle VARCHAR(255) NOT NULL,
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_actividad),
    KEY idx_actividades_usuario_fecha (id_usuario, fecha_creacion),
    CONSTRAINT fk_actividades_usuario FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
    CONSTRAINT fk_actividades_empresa FOREIGN KEY (id_empresa) REFERENCES empresa(id_empresa)
);
