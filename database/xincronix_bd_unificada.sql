-- ============================================================
--  XINCRONIX — Base de datos unificada
--  Motor: MySQL 8 / MariaDB 10.6+
--  Charset: utf8mb4 (compatible migración a PostgreSQL)
--  Versión: 2.0 — Junio 2026
-- ============================================================

CREATE DATABASE IF NOT EXISTS xincronix_bd
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE xincronix_bd;

-- ============================================================
-- NOTA PARA MIGRACIÓN A POSTGRESQL:
--   - TINYINT(1) → BOOLEAN
--   - INT UNSIGNED AUTO_INCREMENT → SERIAL o BIGSERIAL
--   - VARCHAR(n) → VARCHAR(n) o TEXT
--   - TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE → trigger
--   - ENGINE=InnoDB → eliminar (no aplica en PostgreSQL)
--   - Comentarios con -- son válidos en ambos motores
-- ============================================================

-- ------------------------------------------------------------
-- 1. ROLES
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS roles (
    id_roles    INT          AUTO_INCREMENT PRIMARY KEY,
    nombre      VARCHAR(80)  NOT NULL UNIQUE,
    descripcion TEXT
) ENGINE=InnoDB;

INSERT IGNORE INTO roles (id_roles, nombre, descripcion) VALUES
  (1, 'Administrador', 'Acceso completo a la plataforma'),
  (2, 'Manager',       'Gestión de equipos y proyectos'),
  (3, 'Colaborador',   'Acceso básico a tareas asignadas');

-- ------------------------------------------------------------
-- 2. PERFILES ESPECÍFICOS
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS perfiles_especificos (
    id_perfil   INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre      VARCHAR(100) NOT NULL,
    descripcion TEXT
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 3. EMPRESA
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS empresa (
    id_empresa          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre              VARCHAR(200) NOT NULL,
    nit                 VARCHAR(30)  NOT NULL UNIQUE,
    email               VARCHAR(150) NOT NULL UNIQUE,
    telefono            VARCHAR(20),
    direccion           VARCHAR(300),
    industria           VARCHAR(100),
    plan_suscripcion    VARCHAR(50)  DEFAULT 'business',
    sector              VARCHAR(50),
    administrador       VARCHAR(120),
    num_empleados       VARCHAR(30),
    comprobante         VARCHAR(250),
    fecha_actualizacion TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    fecha_creacion      TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

INSERT IGNORE INTO empresa
  (id_empresa, nombre, nit, email, telefono, plan_suscripcion, sector, administrador, fecha_actualizacion, fecha_creacion)
VALUES
  (1, 'Empresa Demo',  '900123456-1',     'admin@demo.xincronix.com', '3001234567', 'business', 'Tecnología', 'Admin Demo', '2026-06-16 23:34:55', '2026-06-16 23:34:55'),
  (2, 'Avengers',      '900.12312.1234',  'avengers@correo.com',      '3001234567', 'business', 'Tecnología', 'tony stark', '2026-06-19 06:11:36', '2026-06-19 06:11:36');

-- ------------------------------------------------------------
-- 4. USUARIOS
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario     INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombres        VARCHAR(100) NOT NULL,
    apellidos      VARCHAR(100) NOT NULL,
    email          VARCHAR(150) NOT NULL UNIQUE,
    password       VARCHAR(255) NOT NULL,
    cargo          VARCHAR(80),
    telefono       VARCHAR(20),
    avatar         VARCHAR(300),
    estado         TINYINT(1)   NOT NULL DEFAULT 1,  -- 1=activo, 0=inactivo
    fecha_creacion TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    id_empresa     INT UNSIGNED NOT NULL,
    id_roles       INT          NOT NULL DEFAULT 3,
    id_perfil      INT UNSIGNED DEFAULT NULL,
    CONSTRAINT fk_usuarios_empresa FOREIGN KEY (id_empresa) REFERENCES empresa(id_empresa)  ON DELETE CASCADE,
    CONSTRAINT fk_usuarios_rol     FOREIGN KEY (id_roles)   REFERENCES roles(id_roles),
    CONSTRAINT fk_usuarios_perfil  FOREIGN KEY (id_perfil)  REFERENCES perfiles_especificos(id_perfil) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE INDEX IF NOT EXISTS idx_usuarios_email   ON usuarios(email);
CREATE INDEX IF NOT EXISTS idx_usuarios_empresa ON usuarios(id_empresa);

INSERT IGNORE INTO usuarios
  (id_usuario, nombres, apellidos, email, password, cargo, telefono, estado, fecha_creacion, id_empresa, id_roles, id_perfil)
VALUES
  (1, 'Admin',     'Demo',    'admin@demo.xincronix.com', '$2y$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Super Admin', NULL,          1, '2026-06-16 23:35:00', 1, 1, NULL),
  (2, 'tony',      'stark',   'avengers@correo.com',      '$2y$12$Xfw1b3jPWsQInG/W2Dlt5OYbWHHqveBdbUzdrOup1OoyAYXqe52yK', 'CEO',         '3001234567',  1, '2026-06-19 06:11:37', 2, 1, NULL),
  (3, 'cristiano', 'ronaldo', 'elbicho@gmail.com',        '$2y$12$2qlX9PGXQ0zDXxIvKozrKOSNATXhfCDYeEVs22zsdJpKc6dEcj/aC', 'Empleado',    '3203289054',  1, '2026-06-20 20:18:40', 2, 2, NULL);

-- ------------------------------------------------------------
-- 5. SOLICITUDES DE PAGO
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS solicitudes_pago (
    id_solicitud     INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_empresa       INT UNSIGNED NOT NULL,
    plan             VARCHAR(50),
    metodo_pago      VARCHAR(50),
    referencia       VARCHAR(100),
    notas            TEXT,
    ruta_comprobante VARCHAR(300),
    estado           VARCHAR(30)  NOT NULL DEFAULT 'pendiente',  -- pendiente | aprobado | rechazado
    fecha_creacion   TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_revision   TIMESTAMP    NULL,
    CONSTRAINT fk_spago_empresa FOREIGN KEY (id_empresa) REFERENCES empresa(id_empresa) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE INDEX IF NOT EXISTS idx_solicitudes_empresa ON solicitudes_pago(id_empresa);
CREATE INDEX IF NOT EXISTS idx_solicitudes_estado  ON solicitudes_pago(estado);

INSERT IGNORE INTO solicitudes_pago
  (id_solicitud, id_empresa, plan, metodo_pago, referencia, notas, ruta_comprobante, estado, fecha_creacion, fecha_revision)
VALUES
  (1, 2, 'business', 'transfer', 'XNX-XDVMK8', '', 'uploads/comprobantes/comp_1781849495_8f82a4e695c8.pdf', 'aprobado', '2026-06-19 06:11:37', '2026-06-19 06:12:33');

-- ------------------------------------------------------------
-- 6. EQUIPOS
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS equipos (
    id_equipo    INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre       VARCHAR(150) NOT NULL,
    descripcion  TEXT,
    miembros     INT          NOT NULL DEFAULT 0,
    fecha_inicio TIMESTAMP    NULL,
    fecha_fin    TIMESTAMP    NULL,
    id_empresa   INT UNSIGNED NOT NULL,
    CONSTRAINT fk_equipos_empresa FOREIGN KEY (id_empresa) REFERENCES empresa(id_empresa) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 7. MIEMBROS DE EQUIPO  (tabla de unión — faltaba en ambas versiones)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS miembros_equipo (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_equipo       INT UNSIGNED NOT NULL,
    id_usuario      INT UNSIGNED NOT NULL,
    rol_en_equipo   VARCHAR(80)  DEFAULT 'Miembro',
    fecha_ingreso   TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_miembro (id_equipo, id_usuario),
    CONSTRAINT fk_me_equipo   FOREIGN KEY (id_equipo)  REFERENCES equipos(id_equipo)   ON DELETE CASCADE,
    CONSTRAINT fk_me_usuario  FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 8. PROYECTOS
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS proyecto (
    id_proyecto       INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre            VARCHAR(150) NOT NULL,
    descripcion       TEXT,
    estado            VARCHAR(50)  NOT NULL DEFAULT 'Activo',  -- Activo | En Progreso | Finalizado | Cancelado
    nivel_importancia INT          NOT NULL DEFAULT 1,          -- 1 (baja) → 5 (crítica)
    tipo_proyecto     VARCHAR(50),
    fecha_inicio      DATE,
    fecha_fin         DATE,
    fecha_creacion    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    id_empresa        INT UNSIGNED NOT NULL,
    id_equipo         INT UNSIGNED DEFAULT NULL,
    CONSTRAINT fk_proyecto_empresa FOREIGN KEY (id_empresa) REFERENCES empresa(id_empresa) ON DELETE CASCADE,
    CONSTRAINT fk_proyecto_equipo  FOREIGN KEY (id_equipo)  REFERENCES equipos(id_equipo)  ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE INDEX IF NOT EXISTS idx_proyecto_empresa ON proyecto(id_empresa);

INSERT IGNORE INTO proyecto
  (id_proyecto, nombre, descripcion, estado, nivel_importancia, tipo_proyecto, fecha_inicio, fecha_fin, fecha_creacion, id_empresa, id_equipo)
VALUES
  (7,  'API rest',    'terminar rapido', 'En Progreso', 3, 'Backend', '2026-06-20', '2026-06-21', '2026-06-20 06:00:29', 2, NULL),
  (10, 'api de grok', '',                'Activo',      2, 'Backend', '2026-06-20', '2026-06-21', '2026-06-20 06:04:14', 2, NULL);

-- ------------------------------------------------------------
-- 9. TAREAS
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tareas (
    id_tarea          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    titulo            VARCHAR(200) NOT NULL,
    descripcion       TEXT,
    estado            VARCHAR(50)  NOT NULL DEFAULT 'Por Hacer',  -- Por Hacer | En Progreso | Revisión | Completada
    prioridad         VARCHAR(20)  NOT NULL DEFAULT 'media',       -- baja | media | alta | crítica
    fecha_creacion    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_vencimiento DATE,
    id_proyecto       INT UNSIGNED NOT NULL,
    id_usuario        INT UNSIGNED DEFAULT NULL,
    id_equipo         INT UNSIGNED DEFAULT NULL,
    CONSTRAINT fk_tareas_proyecto FOREIGN KEY (id_proyecto) REFERENCES proyecto(id_proyecto)   ON DELETE CASCADE,
    CONSTRAINT fk_tareas_usuario  FOREIGN KEY (id_usuario)  REFERENCES usuarios(id_usuario)    ON DELETE SET NULL,
    CONSTRAINT fk_tareas_equipo   FOREIGN KEY (id_equipo)   REFERENCES equipos(id_equipo)      ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE INDEX IF NOT EXISTS idx_tareas_proyecto ON tareas(id_proyecto);
CREATE INDEX IF NOT EXISTS idx_tareas_usuario  ON tareas(id_usuario);

INSERT IGNORE INTO tareas
  (id_tarea, titulo, descripcion, estado, prioridad, fecha_creacion, fecha_vencimiento, id_proyecto, id_usuario, id_equipo)
VALUES
  (1, 'instalar laravel',  'instalar laravel y composer desde el cmd',                                                          'Por Hacer', 'media', '2026-06-20 06:31:51', '2026-06-20', 7,  NULL, NULL),
  (2, 'instalar laravel',  '',                                                                                                  'Por Hacer', 'media', '2026-06-20 06:32:35', '2026-06-20', 7,  NULL, NULL),
  (3, 'instalar composer', 'instalar el composer y las extensiones de visual studio para que funcione el proyecto xincronix',   'Por Hacer', 'media', '2026-06-20 19:59:01', '2026-06-20', 10, 2,    NULL);

-- ------------------------------------------------------------
-- 10. REUNIONES
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS reuniones (
    id_reunion    INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre        VARCHAR(150) NOT NULL,
    enlace        VARCHAR(300),
    fecha         TIMESTAMP    NOT NULL,
    estado        VARCHAR(50)  NOT NULL DEFAULT 'Programada',  -- Programada | En Curso | Finalizada | Cancelada
    grabacion_url VARCHAR(500),
    id_equipo     INT UNSIGNED DEFAULT NULL,
    id_usuario    INT UNSIGNED DEFAULT NULL,
    CONSTRAINT fk_reuniones_equipo   FOREIGN KEY (id_equipo)  REFERENCES equipos(id_equipo)   ON DELETE SET NULL,
    CONSTRAINT fk_reuniones_usuario  FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE SET NULL
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 11. CALENDARIO
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS calendario (
    id_calendario INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    fecha_evento  TIMESTAMP    NOT NULL,
    nota          TEXT,
    id_usuario    INT UNSIGNED NOT NULL,
    CONSTRAINT fk_calendario_usuario FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 12. MENSAJES
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS mensajes (
    id_mensajes    INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    contenido      TEXT         NOT NULL,
    fecha_envio    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado         TINYINT(1)   NOT NULL DEFAULT 0,  -- 0=enviado, 1=entregado
    leido          TINYINT(1)   NOT NULL DEFAULT 0,
    id_usuario     INT UNSIGNED NOT NULL,             -- remitente
    id_destinatario INT UNSIGNED DEFAULT NULL,        -- NULL = broadcast / grupo
    CONSTRAINT fk_mensajes_remitente    FOREIGN KEY (id_usuario)      REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    CONSTRAINT fk_mensajes_destinatario FOREIGN KEY (id_destinatario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE INDEX IF NOT EXISTS idx_mensajes_conversacion  ON mensajes(id_usuario, id_destinatario, fecha_envio);
CREATE INDEX IF NOT EXISTS idx_mensajes_destinatario  ON mensajes(id_destinatario);

INSERT IGNORE INTO mensajes (id_mensajes, contenido, fecha_envio, estado, leido, id_usuario, id_destinatario) VALUES
  (1, 'hola bicho, como va el proyecto', '2026-06-20 20:19:02', 1, 1, 2, 3),
  (2, 'manito vamos en la inmunda',      '2026-06-20 20:21:08', 1, 1, 3, 2),
  (3, 'como asi?',                       '2026-06-20 20:26:25', 1, 1, 2, 3);

-- ------------------------------------------------------------
-- 13. NOTIFICACIONES
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS notificaciones (
    id_notificaciones INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    titulo            VARCHAR(100) NOT NULL,
    mensaje           TEXT         NOT NULL,
    tipo              VARCHAR(50),                     -- info | advertencia | error | tarea | reunion
    fecha_envio       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado            TINYINT(1)   NOT NULL DEFAULT 0,
    leida             TINYINT(1)   NOT NULL DEFAULT 0,
    id_usuario        INT UNSIGNED NOT NULL,
    CONSTRAINT fk_notificaciones_usuario FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE INDEX IF NOT EXISTS idx_notificaciones_user ON notificaciones(id_usuario);

-- ------------------------------------------------------------
-- 14. MÉTRICAS DE RENDIMIENTO
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS metrica_rendimiento (
    id_metrica           INT UNSIGNED   AUTO_INCREMENT PRIMARY KEY,
    tipo_metrica         VARCHAR(100)   NOT NULL,
    valor                DECIMAL(12, 4) NOT NULL,
    meta                 DECIMAL(12, 4) DEFAULT NULL,
    unidad               VARCHAR(20)    DEFAULT NULL,
    fecha_inicio_periodo DATE           NOT NULL,
    fecha_fin_periodo    DATE           NOT NULL,
    id_usuario           INT UNSIGNED   NOT NULL,
    CONSTRAINT fk_metrica_usuario FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE INDEX IF NOT EXISTS idx_metrica_usuario     ON metrica_rendimiento(id_usuario);
CREATE INDEX IF NOT EXISTS idx_metrica_tipo_periodo ON metrica_rendimiento(tipo_metrica, fecha_inicio_periodo, fecha_fin_periodo);

-- ------------------------------------------------------------
-- 15. TICKETS DE SOPORTE
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tickets_soporte (
    id_ticket      INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    asunto         VARCHAR(200) NOT NULL,
    descripcion    TEXT,
    prioridad      VARCHAR(20)  NOT NULL DEFAULT 'media',  -- baja | media | alta | crítica
    estado         VARCHAR(30)  NOT NULL DEFAULT 'abierto', -- abierto | en_revision | cerrado
    id_empresa     INT UNSIGNED DEFAULT NULL,
    fecha_creacion TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_cierre   TIMESTAMP    NULL,
    CONSTRAINT fk_tickets_empresa FOREIGN KEY (id_empresa) REFERENCES empresa(id_empresa) ON DELETE SET NULL
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 16. ASISTENTE IA — Conversaciones
--     Para el historial del asistente virtual por usuario/empresa
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ia_conversaciones (
    id_conversacion INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_usuario      INT UNSIGNED NOT NULL,
    id_empresa      INT UNSIGNED NOT NULL,
    titulo          VARCHAR(200) DEFAULT 'Nueva conversación',
    fecha_inicio    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_ultima    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    activa          TINYINT(1)   NOT NULL DEFAULT 1,
    CONSTRAINT fk_iaconv_usuario  FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    CONSTRAINT fk_iaconv_empresa  FOREIGN KEY (id_empresa) REFERENCES empresa(id_empresa)  ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE INDEX IF NOT EXISTS idx_iaconv_usuario  ON ia_conversaciones(id_usuario);
CREATE INDEX IF NOT EXISTS idx_iaconv_empresa  ON ia_conversaciones(id_empresa);

-- ------------------------------------------------------------
-- 17. ASISTENTE IA — Mensajes
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ia_mensajes (
    id_ia_mensaje   INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_conversacion INT UNSIGNED NOT NULL,
    rol             VARCHAR(20)  NOT NULL DEFAULT 'user',  -- user | assistant | system
    contenido       TEXT         NOT NULL,
    tokens_usados   INT          DEFAULT NULL,
    modelo          VARCHAR(60)  DEFAULT 'claude-sonnet-4-6',
    fecha_envio     TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_iamsg_conv FOREIGN KEY (id_conversacion) REFERENCES ia_conversaciones(id_conversacion) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE INDEX IF NOT EXISTS idx_iamsg_conv ON ia_mensajes(id_conversacion);

-- ------------------------------------------------------------
-- 18. LARAVEL — Tablas de framework (requeridas por Sanctum/Jobs/Cache)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id         BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(255) NOT NULL,
    email      VARCHAR(255) NOT NULL UNIQUE,
    email_verified_at TIMESTAMP NULL DEFAULT NULL,
    password   VARCHAR(255) NOT NULL,
    remember_token VARCHAR(100) DEFAULT NULL,
    created_at TIMESTAMP NULL DEFAULT NULL,
    updated_at TIMESTAMP NULL DEFAULT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS personal_access_tokens (
    id             BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    tokenable_type VARCHAR(255)    NOT NULL,
    tokenable_id   BIGINT UNSIGNED NOT NULL,
    name           TEXT            NOT NULL,
    token          VARCHAR(64)     NOT NULL UNIQUE,
    abilities      TEXT            DEFAULT NULL,
    last_used_at   TIMESTAMP       NULL DEFAULT NULL,
    expires_at     TIMESTAMP       NULL DEFAULT NULL,
    created_at     TIMESTAMP       NULL DEFAULT NULL,
    updated_at     TIMESTAMP       NULL DEFAULT NULL,
    INDEX personal_access_tokens_tokenable_index (tokenable_type, tokenable_id),
    INDEX personal_access_tokens_expires_at_index (expires_at)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS password_reset_tokens (
    email      VARCHAR(255) NOT NULL PRIMARY KEY,
    token      VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NULL DEFAULT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS cache (
    `key`       VARCHAR(255) NOT NULL PRIMARY KEY,
    `value`     MEDIUMTEXT   NOT NULL,
    expiration  INT          NOT NULL,
    INDEX cache_expiration_index (expiration)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS cache_locks (
    `key`       VARCHAR(255) NOT NULL PRIMARY KEY,
    owner       VARCHAR(255) NOT NULL,
    expiration  INT          NOT NULL,
    INDEX cache_locks_expiration_index (expiration)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS jobs (
    id           BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    queue        VARCHAR(255)    NOT NULL,
    payload      LONGTEXT        NOT NULL,
    attempts     TINYINT UNSIGNED NOT NULL,
    reserved_at  INT UNSIGNED    DEFAULT NULL,
    available_at INT UNSIGNED    NOT NULL,
    created_at   INT UNSIGNED    NOT NULL,
    INDEX jobs_queue_index (queue)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS job_batches (
    id             VARCHAR(255) NOT NULL PRIMARY KEY,
    name           VARCHAR(255) NOT NULL,
    total_jobs     INT          NOT NULL,
    pending_jobs   INT          NOT NULL,
    failed_jobs    INT          NOT NULL,
    failed_job_ids LONGTEXT     NOT NULL,
    options        MEDIUMTEXT   DEFAULT NULL,
    cancelled_at   INT          DEFAULT NULL,
    created_at     INT          NOT NULL,
    finished_at    INT          DEFAULT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS failed_jobs (
    id         BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    uuid       VARCHAR(255) NOT NULL UNIQUE,
    connection TEXT         NOT NULL,
    queue      TEXT         NOT NULL,
    payload    LONGTEXT     NOT NULL,
    exception  LONGTEXT     NOT NULL,
    failed_at  TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS sessions (
    id            VARCHAR(255) NOT NULL PRIMARY KEY,
    user_id       BIGINT UNSIGNED DEFAULT NULL,
    ip_address    VARCHAR(45)  DEFAULT NULL,
    user_agent    TEXT         DEFAULT NULL,
    payload       LONGTEXT     NOT NULL,
    last_activity INT          NOT NULL,
    INDEX sessions_user_id_index (user_id),
    INDEX sessions_last_activity_index (last_activity)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS migrations (
    id        INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    migration VARCHAR(255) NOT NULL,
    batch     INT          NOT NULL
) ENGINE=InnoDB;

INSERT IGNORE INTO migrations (id, migration, batch) VALUES
  (1, '0001_01_01_000000_create_users_table',                  1),
  (2, '0001_01_01_000001_create_cache_table',                  1),
  (3, '0001_01_01_000002_create_jobs_table',                   1),
  (4, '2026_06_21_065851_create_personal_access_tokens_table', 1);

-- ============================================================
-- FIN DEL SCRIPT
-- ============================================================
