
CREATE DATABASE IF NOT EXISTS xincronix_bd
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
USE xincronix_bd;

--  TABLA: empresa
CREATE TABLE IF NOT EXISTS empresa (
    id_empresa          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre              VARCHAR(200)  NOT NULL,
    nit                 VARCHAR(30)   UNIQUE NOT NULL,
    email               VARCHAR(150)  UNIQUE NOT NULL,
    telefono            VARCHAR(20),
    direccion           VARCHAR(300),
    industria           VARCHAR(100),
    plan_suscripcion    VARCHAR(50)   DEFAULT 'business',
    sector              VARCHAR(50),
    administrador       VARCHAR(120),
    num_empleados       VARCHAR(30),
    comprobante         VARCHAR(250),
    fecha_actualizacion TIMESTAMP     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    fecha_creacion      TIMESTAMP     DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ─────────────────────────────────────────────────────────────
--  TABLA: roles
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS roles (
    id_roles    INT AUTO_INCREMENT PRIMARY KEY,
    nombre      VARCHAR(80)  NOT NULL UNIQUE,
    descripcion TEXT
) ENGINE=InnoDB;

INSERT IGNORE INTO roles (id_roles, nombre, descripcion) VALUES
  (1, 'Administrador', 'Acceso completo a la plataforma'),
  (2, 'Manager',       'Gestión de equipos y proyectos'),
  (3, 'Colaborador',   'Acceso básico a tareas asignadas');

-- ─────────────────────────────────────────────────────────────
--  TABLA: perfiles_especificos
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS perfiles_especificos (
    id_perfil   INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre      VARCHAR(100) NOT NULL,
    descripcion TEXT
) ENGINE=InnoDB;

-- ─────────────────────────────────────────────────────────────
--  TABLA: usuarios
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario     INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombres        VARCHAR(100) NOT NULL,
    apellidos      VARCHAR(100) NOT NULL,
    email          VARCHAR(150) UNIQUE NOT NULL,
    password       VARCHAR(255) NOT NULL,
    cargo          VARCHAR(80),
    telefono       VARCHAR(20),
    avatar         VARCHAR(300),
    estado         TINYINT(1)   DEFAULT 1,
    fecha_creacion TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    id_empresa     INT UNSIGNED NOT NULL,
    id_roles       INT          NOT NULL DEFAULT 3,
    id_perfil      INT UNSIGNED,
    FOREIGN KEY (id_empresa) REFERENCES empresa(id_empresa) ON DELETE CASCADE,
    FOREIGN KEY (id_roles)   REFERENCES roles(id_roles)
) ENGINE=InnoDB;

-- ─────────────────────────────────────────────────────────────
--  TABLA: solicitudes_pago
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS solicitudes_pago (
    id_solicitud     INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_empresa       INT UNSIGNED NOT NULL,
    plan             VARCHAR(50),
    metodo_pago      VARCHAR(50),
    referencia       VARCHAR(100),
    notas            TEXT,
    ruta_comprobante VARCHAR(300),
    estado           VARCHAR(30)  DEFAULT 'pendiente',
    fecha_creacion   TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    fecha_revision   TIMESTAMP    NULL,
    FOREIGN KEY (id_empresa) REFERENCES empresa(id_empresa) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ─────────────────────────────────────────────────────────────
--  TABLA: equipos
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS equipos (
    id_equipo    INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre       VARCHAR(150) NOT NULL,
    descripcion  TEXT,
    miembros     INT          DEFAULT 0,
    fecha_inicio TIMESTAMP    NULL,
    fecha_fin    TIMESTAMP    NULL,
    id_empresa   INT UNSIGNED NOT NULL,
    FOREIGN KEY (id_empresa) REFERENCES empresa(id_empresa) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ─────────────────────────────────────────────────────────────
--  TABLA: proyecto
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS proyecto (
    id_proyecto       INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre            VARCHAR(150) NOT NULL,
    descripcion       TEXT,
    estado            VARCHAR(50)  DEFAULT 'Activo',
    nivel_importancia INT          DEFAULT 1,
    tipo_proyecto     VARCHAR(50),
    fecha_inicio      DATE,
    fecha_fin         DATE,
    id_empresa        INT UNSIGNED NOT NULL,
    id_equipo         INT UNSIGNED,
    FOREIGN KEY (id_empresa) REFERENCES empresa(id_empresa) ON DELETE CASCADE,
    FOREIGN KEY (id_equipo)  REFERENCES equipos(id_equipo)  ON DELETE SET NULL
) ENGINE=InnoDB;

-- ─────────────────────────────────────────────────────────────
--  TABLA: tareas
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS tareas (
    id_tarea          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    titulo            VARCHAR(200) NOT NULL,
    descripcion       TEXT,
    estado            VARCHAR(50)  DEFAULT 'Por Hacer',
    fecha_creacion    TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    fecha_vencimiento DATE,
    id_proyecto       INT UNSIGNED NOT NULL,
    id_usuario        INT UNSIGNED,
    id_equipo         INT UNSIGNED,
    FOREIGN KEY (id_proyecto) REFERENCES proyecto(id_proyecto) ON DELETE CASCADE,
    FOREIGN KEY (id_usuario)  REFERENCES usuarios(id_usuario)  ON DELETE SET NULL,
    FOREIGN KEY (id_equipo)   REFERENCES equipos(id_equipo)    ON DELETE SET NULL
) ENGINE=InnoDB;

-- ─────────────────────────────────────────────────────────────
--  TABLA: reuniones
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS reuniones (
    id_reunion    INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre        VARCHAR(150) NOT NULL,
    enlace        VARCHAR(300),
    fecha         TIMESTAMP    NOT NULL,
    estado        VARCHAR(50)  DEFAULT 'Programada',
    grabacion_url VARCHAR(500),
    id_equipo     INT UNSIGNED,
    id_usuario    INT UNSIGNED,
    FOREIGN KEY (id_equipo)  REFERENCES equipos(id_equipo)   ON DELETE SET NULL,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE SET NULL
) ENGINE=InnoDB;

-- ─────────────────────────────────────────────────────────────
--  TABLA: calendario
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS calendario (
    id_calendario INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    fecha_evento  TIMESTAMP    NOT NULL,
    nota          TEXT,
    id_usuario    INT UNSIGNED NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ─────────────────────────────────────────────────────────────
--  TABLA: mensajes
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS mensajes (
    id_mensajes  INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    contenido    TEXT         NOT NULL,
    fecha_envio  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    estado       TINYINT(1)   DEFAULT 0,
    id_usuario   INT UNSIGNED NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ─────────────────────────────────────────────────────────────
--  TABLA: notificaciones
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS notificaciones (
    id_notificaciones INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    titulo            VARCHAR(100) NOT NULL,
    mensaje           TEXT         NOT NULL,
    tipo              VARCHAR(50),
    fecha_envio       TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    estado            TINYINT(1)   DEFAULT 0,
    leida             TINYINT(1)   DEFAULT 0,
    id_usuario        INT UNSIGNED NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ─────────────────────────────────────────────────────────────
--  TABLA: metrica_rendimiento
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS metrica_rendimiento (
    id_metrica           INT UNSIGNED   AUTO_INCREMENT PRIMARY KEY,
    tipo_metrica         VARCHAR(100)   NOT NULL,
    valor                DECIMAL(12, 4) NOT NULL,
    fecha_inicio_periodo DATE           NOT NULL,
    fecha_fin_periodo    DATE           NOT NULL,
    id_usuario           INT UNSIGNED   NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ─────────────────────────────────────────────────────────────
--  TABLA: tickets_soporte
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS tickets_soporte (
    id_ticket      INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    asunto         VARCHAR(200) NOT NULL,
    descripcion    TEXT,
    prioridad      VARCHAR(20)  DEFAULT 'media',
    estado         VARCHAR(30)  DEFAULT 'abierto',
    id_empresa     INT UNSIGNED,
    fecha_creacion TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    fecha_cierre   TIMESTAMP    NULL,
    FOREIGN KEY (id_empresa) REFERENCES empresa(id_empresa) ON DELETE SET NULL
) ENGINE=InnoDB;

-- ─────────────────────────────────────────────────────────────
--  ÍNDICES
-- ─────────────────────────────────────────────────────────────
CREATE INDEX idx_usuarios_email       ON usuarios(email);
CREATE INDEX idx_usuarios_empresa     ON usuarios(id_empresa);
CREATE INDEX idx_tareas_proyecto      ON tareas(id_proyecto);
CREATE INDEX idx_tareas_usuario       ON tareas(id_usuario);
CREATE INDEX idx_notificaciones_user  ON notificaciones(id_usuario);
CREATE INDEX idx_metrica_usuario      ON metrica_rendimiento(id_usuario);
CREATE INDEX idx_proyecto_empresa     ON proyecto(id_empresa);
CREATE INDEX idx_solicitudes_empresa  ON solicitudes_pago(id_empresa);
CREATE INDEX idx_solicitudes_estado   ON solicitudes_pago(estado);

-- ─────────────────────────────────────────────────────────────
--  DATOS DE PRUEBA (opcional — comentar en producción)
-- ─────────────────────────────────────────────────────────────
-- Empresa demo
INSERT IGNORE INTO empresa (id_empresa, nombre, nit, email, telefono, sector, plan_suscripcion, administrador)
VALUES (1, 'Empresa Demo', '900123456-1', 'admin@demo.xincronix.com', '3001234567', 'Tecnología', 'business', 'Admin Demo');

-- Usuario admin demo  (password: Demo1234!)
INSERT IGNORE INTO usuarios (id_usuario, nombres, apellidos, email, password, cargo, id_empresa, id_roles, estado)
VALUES (1, 'Admin', 'Demo', 'admin@demo.xincronix.com',
        '$2y$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi',
        'Super Admin', 1, 1, 1);
