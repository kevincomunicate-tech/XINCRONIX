-- ============================================================
-- Xincronix — estructura de la base de datos (normalizada)
-- Generada desde los modelos de Django con MariaDB 10.11.
--
-- IMPORTANTE: esta es una referencia para revisar en phpMyAdmin.
-- Para crear la base de verdad usa:  python manage.py migrate
-- (Django crea estas tablas, las suyas y los 4 roles).
-- Django 5.2 necesita MariaDB 10.5+ o MySQL 8+.
-- ============================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

/*M!999999\- enable the sandbox mode */ 
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `empresa` (
  `id_empresa` bigint(20) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(200) NOT NULL,
  `nit` varchar(30) DEFAULT NULL,
  `email` varchar(150) NOT NULL,
  `telefono` varchar(20) NOT NULL,
  `direccion` varchar(300) NOT NULL,
  `sector` varchar(20) NOT NULL,
  `num_empleados` varchar(10) NOT NULL,
  `fecha_creacion` datetime(6) NOT NULL,
  `fecha_actualizacion` datetime(6) NOT NULL,
  PRIMARY KEY (`id_empresa`),
  UNIQUE KEY `nit` (`nit`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `roles` (
  `id_roles` int(11) NOT NULL AUTO_INCREMENT,
  `codigo` varchar(30) NOT NULL,
  `nombre` varchar(80) NOT NULL,
  `descripcion` longtext NOT NULL,
  PRIMARY KEY (`id_roles`),
  UNIQUE KEY `codigo` (`codigo`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `id_usuario` bigint(20) NOT NULL AUTO_INCREMENT,
  `nombres` varchar(100) NOT NULL,
  `apellidos` varchar(100) NOT NULL,
  `email` varchar(150) NOT NULL,
  `estado` tinyint(1) NOT NULL,
  `fecha_creacion` datetime(6) NOT NULL,
  `cargo` varchar(80) NOT NULL,
  `telefono` varchar(20) NOT NULL,
  `avatar` varchar(100) NOT NULL,
  `id_empresa` bigint(20) DEFAULT NULL,
  `id_roles` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `email` (`email`),
  KEY `usuarios_id_empresa_947d9ab9_fk_empresa_id_empresa` (`id_empresa`),
  KEY `usuarios_id_roles_908ce67c_fk_roles_id_roles` (`id_roles`),
  CONSTRAINT `usuarios_id_empresa_947d9ab9_fk_empresa_id_empresa` FOREIGN KEY (`id_empresa`) REFERENCES `empresa` (`id_empresa`),
  CONSTRAINT `usuarios_id_roles_908ce67c_fk_roles_id_roles` FOREIGN KEY (`id_roles`) REFERENCES `roles` (`id_roles`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `equipos` (
  `id_equipo` bigint(20) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(150) NOT NULL,
  `descripcion` longtext NOT NULL,
  `fecha_creacion` datetime(6) NOT NULL,
  `id_empresa` bigint(20) NOT NULL,
  PRIMARY KEY (`id_equipo`),
  UNIQUE KEY `uq_equipo_nombre_por_empresa` (`id_empresa`,`nombre`),
  CONSTRAINT `equipos_id_empresa_4e715381_fk_empresa_id_empresa` FOREIGN KEY (`id_empresa`) REFERENCES `empresa` (`id_empresa`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `miembros_equipo` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `rol_en_equipo` varchar(10) NOT NULL,
  `fecha_ingreso` datetime(6) NOT NULL,
  `id_equipo` bigint(20) NOT NULL,
  `id_usuario` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_miembro` (`id_equipo`,`id_usuario`),
  KEY `miembros_equipo_id_usuario_7ddc7b77_fk_usuarios_id_usuario` (`id_usuario`),
  CONSTRAINT `miembros_equipo_id_equipo_e2dfab96_fk_equipos_id_equipo` FOREIGN KEY (`id_equipo`) REFERENCES `equipos` (`id_equipo`),
  CONSTRAINT `miembros_equipo_id_usuario_7ddc7b77_fk_usuarios_id_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `proyecto` (
  `id_proyecto` bigint(20) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(150) NOT NULL,
  `descripcion` longtext NOT NULL,
  `estado` varchar(15) NOT NULL,
  `nivel_importancia` smallint(5) unsigned NOT NULL CHECK (`nivel_importancia` >= 0),
  `tipo_proyecto` varchar(15) NOT NULL,
  `fecha_inicio` date DEFAULT NULL,
  `fecha_fin` date DEFAULT NULL,
  `fecha_creacion` datetime(6) NOT NULL,
  `id_creador` bigint(20) DEFAULT NULL,
  `id_empresa` bigint(20) NOT NULL,
  `id_equipo` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id_proyecto`),
  KEY `idx_proyecto_empresa_estado` (`id_empresa`,`estado`),
  KEY `proyecto_id_creador_207002a5_fk_usuarios_id_usuario` (`id_creador`),
  KEY `proyecto_id_equipo_776f7660_fk_equipos_id_equipo` (`id_equipo`),
  CONSTRAINT `proyecto_id_creador_207002a5_fk_usuarios_id_usuario` FOREIGN KEY (`id_creador`) REFERENCES `usuarios` (`id_usuario`),
  CONSTRAINT `proyecto_id_empresa_6fd929e7_fk_empresa_id_empresa` FOREIGN KEY (`id_empresa`) REFERENCES `empresa` (`id_empresa`),
  CONSTRAINT `proyecto_id_equipo_776f7660_fk_equipos_id_equipo` FOREIGN KEY (`id_equipo`) REFERENCES `equipos` (`id_equipo`),
  CONSTRAINT `ck_proyecto_fechas` CHECK (`fecha_fin` is null or `fecha_inicio` is null or `fecha_fin` >= `fecha_inicio`),
  CONSTRAINT `ck_proyecto_importancia` CHECK (`nivel_importancia` >= 1 and `nivel_importancia` <= 4)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `proyecto_miembros` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `rol` varchar(15) NOT NULL,
  `fecha_ingreso` datetime(6) NOT NULL,
  `id_proyecto` bigint(20) NOT NULL,
  `id_usuario` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_proyecto_miembro` (`id_proyecto`,`id_usuario`),
  KEY `proyecto_miembros_id_usuario_8668de52_fk_usuarios_id_usuario` (`id_usuario`),
  CONSTRAINT `proyecto_miembros_id_proyecto_4e187d3f_fk_proyecto_id_proyecto` FOREIGN KEY (`id_proyecto`) REFERENCES `proyecto` (`id_proyecto`),
  CONSTRAINT `proyecto_miembros_id_usuario_8668de52_fk_usuarios_id_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tareas` (
  `id_tarea` bigint(20) NOT NULL AUTO_INCREMENT,
  `titulo` varchar(200) NOT NULL,
  `descripcion` longtext NOT NULL,
  `estado` varchar(15) NOT NULL,
  `prioridad` varchar(10) NOT NULL,
  `fecha_creacion` datetime(6) NOT NULL,
  `fecha_vencimiento` date DEFAULT NULL,
  `fecha_completada` datetime(6) DEFAULT NULL,
  `id_usuario` bigint(20) DEFAULT NULL,
  `id_creador` bigint(20) DEFAULT NULL,
  `id_proyecto` bigint(20) NOT NULL,
  PRIMARY KEY (`id_tarea`),
  KEY `idx_tareas_proyecto_estado` (`id_proyecto`,`estado`),
  KEY `tareas_id_usuario_01308f1b_fk_usuarios_id_usuario` (`id_usuario`),
  KEY `tareas_id_creador_32b68b50_fk_usuarios_id_usuario` (`id_creador`),
  CONSTRAINT `tareas_id_creador_32b68b50_fk_usuarios_id_usuario` FOREIGN KEY (`id_creador`) REFERENCES `usuarios` (`id_usuario`),
  CONSTRAINT `tareas_id_proyecto_3f503a90_fk_proyecto_id_proyecto` FOREIGN KEY (`id_proyecto`) REFERENCES `proyecto` (`id_proyecto`),
  CONSTRAINT `tareas_id_usuario_01308f1b_fk_usuarios_id_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `ideas` (
  `id_idea` bigint(20) NOT NULL AUTO_INCREMENT,
  `titulo` varchar(120) NOT NULL,
  `descripcion` longtext NOT NULL,
  `categoria` varchar(15) NOT NULL,
  `estado` varchar(15) NOT NULL,
  `color` varchar(10) NOT NULL,
  `fecha_creacion` datetime(6) NOT NULL,
  `id_usuario` bigint(20) DEFAULT NULL,
  `id_empresa` bigint(20) NOT NULL,
  PRIMARY KEY (`id_idea`),
  KEY `ideas_id_usuario_b9821647_fk_usuarios_id_usuario` (`id_usuario`),
  KEY `ideas_id_empresa_c6705dce_fk_empresa_id_empresa` (`id_empresa`),
  CONSTRAINT `ideas_id_empresa_c6705dce_fk_empresa_id_empresa` FOREIGN KEY (`id_empresa`) REFERENCES `empresa` (`id_empresa`),
  CONSTRAINT `ideas_id_usuario_b9821647_fk_usuarios_id_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `ideas_votos` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `fecha` datetime(6) NOT NULL,
  `id_idea` bigint(20) NOT NULL,
  `id_usuario` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_voto_idea` (`id_idea`,`id_usuario`),
  KEY `ideas_votos_id_usuario_d5545740_fk_usuarios_id_usuario` (`id_usuario`),
  CONSTRAINT `ideas_votos_id_idea_fcec1227_fk_ideas_id_idea` FOREIGN KEY (`id_idea`) REFERENCES `ideas` (`id_idea`),
  CONSTRAINT `ideas_votos_id_usuario_d5545740_fk_usuarios_id_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `lienzos` (
  `id_lienzo` bigint(20) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(60) NOT NULL,
  `contenido` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`contenido`)),
  `version` int(10) unsigned NOT NULL CHECK (`version` >= 0),
  `compartido_con_empresa` tinyint(1) NOT NULL,
  `fecha_creacion` datetime(6) NOT NULL,
  `fecha_actualizacion` datetime(6) NOT NULL,
  `id_ultimo_editor` bigint(20) DEFAULT NULL,
  `id_creador` bigint(20) DEFAULT NULL,
  `id_empresa` bigint(20) NOT NULL,
  `id_equipo` bigint(20) DEFAULT NULL,
  `id_proyecto` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id_lienzo`),
  KEY `lienzos_id_proyecto_8bab6206_fk_proyecto_id_proyecto` (`id_proyecto`),
  KEY `lienzos_id_ultimo_editor_9d497136_fk_usuarios_id_usuario` (`id_ultimo_editor`),
  KEY `lienzos_id_creador_fcc1321a_fk_usuarios_id_usuario` (`id_creador`),
  KEY `lienzos_id_empresa_f12a263e_fk_empresa_id_empresa` (`id_empresa`),
  KEY `lienzos_id_equipo_80c40d5b_fk_equipos_id_equipo` (`id_equipo`),
  CONSTRAINT `lienzos_id_creador_fcc1321a_fk_usuarios_id_usuario` FOREIGN KEY (`id_creador`) REFERENCES `usuarios` (`id_usuario`),
  CONSTRAINT `lienzos_id_empresa_f12a263e_fk_empresa_id_empresa` FOREIGN KEY (`id_empresa`) REFERENCES `empresa` (`id_empresa`),
  CONSTRAINT `lienzos_id_equipo_80c40d5b_fk_equipos_id_equipo` FOREIGN KEY (`id_equipo`) REFERENCES `equipos` (`id_equipo`),
  CONSTRAINT `lienzos_id_proyecto_8bab6206_fk_proyecto_id_proyecto` FOREIGN KEY (`id_proyecto`) REFERENCES `proyecto` (`id_proyecto`),
  CONSTRAINT `lienzos_id_ultimo_editor_9d497136_fk_usuarios_id_usuario` FOREIGN KEY (`id_ultimo_editor`) REFERENCES `usuarios` (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `lienzo_colaboradores` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `permiso` varchar(10) NOT NULL,
  `fecha_ingreso` datetime(6) NOT NULL,
  `id_lienzo` bigint(20) NOT NULL,
  `id_usuario` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_lienzo_colaborador` (`id_lienzo`,`id_usuario`),
  KEY `lienzo_colaboradores_id_usuario_83fdc601_fk_usuarios_id_usuario` (`id_usuario`),
  CONSTRAINT `lienzo_colaboradores_id_lienzo_88aaa20a_fk_lienzos_id_lienzo` FOREIGN KEY (`id_lienzo`) REFERENCES `lienzos` (`id_lienzo`),
  CONSTRAINT `lienzo_colaboradores_id_usuario_83fdc601_fk_usuarios_id_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `actividad` (
  `id_actividad` bigint(20) NOT NULL AUTO_INCREMENT,
  `tipo` varchar(10) NOT NULL,
  `descripcion` varchar(255) NOT NULL,
  `fecha` datetime(6) NOT NULL,
  `id_empresa` bigint(20) NOT NULL,
  `id_usuario` bigint(20) DEFAULT NULL,
  `id_proyecto` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id_actividad`),
  KEY `idx_actividad_empresa_fecha` (`id_empresa`,`fecha` DESC),
  KEY `actividad_id_usuario_c4865489_fk_usuarios_id_usuario` (`id_usuario`),
  KEY `actividad_id_proyecto_7d1043e6_fk_proyecto_id_proyecto` (`id_proyecto`),
  CONSTRAINT `actividad_id_empresa_cb1d3dc0_fk_empresa_id_empresa` FOREIGN KEY (`id_empresa`) REFERENCES `empresa` (`id_empresa`),
  CONSTRAINT `actividad_id_proyecto_7d1043e6_fk_proyecto_id_proyecto` FOREIGN KEY (`id_proyecto`) REFERENCES `proyecto` (`id_proyecto`),
  CONSTRAINT `actividad_id_usuario_c4865489_fk_usuarios_id_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `notificaciones` (
  `id_notificaciones` bigint(20) NOT NULL AUTO_INCREMENT,
  `titulo` varchar(100) NOT NULL,
  `mensaje` longtext NOT NULL,
  `tipo` varchar(10) NOT NULL,
  `url` varchar(300) NOT NULL,
  `leida` tinyint(1) NOT NULL,
  `fecha_envio` datetime(6) NOT NULL,
  `id_usuario` bigint(20) NOT NULL,
  PRIMARY KEY (`id_notificaciones`),
  KEY `idx_notificaciones_usuario` (`id_usuario`,`leida`),
  CONSTRAINT `notificaciones_id_usuario_7a6362fb_fk_usuarios_id_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `metrica_rendimiento` (
  `id_metrica` bigint(20) NOT NULL AUTO_INCREMENT,
  `tipo_metrica` varchar(100) NOT NULL,
  `valor` decimal(12,4) NOT NULL,
  `meta` decimal(12,4) DEFAULT NULL,
  `unidad` varchar(20) NOT NULL,
  `fecha_inicio_periodo` date NOT NULL,
  `fecha_fin_periodo` date NOT NULL,
  `id_empresa` bigint(20) NOT NULL,
  `id_usuario` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id_metrica`),
  KEY `idx_metrica_tipo_periodo` (`tipo_metrica`,`fecha_inicio_periodo`,`fecha_fin_periodo`),
  KEY `metrica_rendimiento_id_empresa_98350754_fk_empresa_id_empresa` (`id_empresa`),
  KEY `metrica_rendimiento_id_usuario_7c72a6f4_fk_usuarios_id_usuario` (`id_usuario`),
  CONSTRAINT `metrica_rendimiento_id_empresa_98350754_fk_empresa_id_empresa` FOREIGN KEY (`id_empresa`) REFERENCES `empresa` (`id_empresa`),
  CONSTRAINT `metrica_rendimiento_id_usuario_7c72a6f4_fk_usuarios_id_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`),
  CONSTRAINT `ck_metrica_periodo` CHECK (`fecha_fin_periodo` >= `fecha_inicio_periodo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `mensajes` (
  `id_mensajes` bigint(20) NOT NULL AUTO_INCREMENT,
  `contenido` longtext NOT NULL,
  `fecha_envio` datetime(6) NOT NULL,
  `leido` tinyint(1) NOT NULL,
  `id_destinatario` bigint(20) DEFAULT NULL,
  `id_equipo` bigint(20) DEFAULT NULL,
  `id_usuario` bigint(20) NOT NULL,
  PRIMARY KEY (`id_mensajes`),
  KEY `mensajes_id_destinatario_7cf3d1ea_fk_usuarios_id_usuario` (`id_destinatario`),
  KEY `mensajes_id_equipo_8b22db85_fk_equipos_id_equipo` (`id_equipo`),
  KEY `idx_mensajes_conversacion` (`id_usuario`,`id_destinatario`,`fecha_envio`),
  CONSTRAINT `mensajes_id_destinatario_7cf3d1ea_fk_usuarios_id_usuario` FOREIGN KEY (`id_destinatario`) REFERENCES `usuarios` (`id_usuario`),
  CONSTRAINT `mensajes_id_equipo_8b22db85_fk_equipos_id_equipo` FOREIGN KEY (`id_equipo`) REFERENCES `equipos` (`id_equipo`),
  CONSTRAINT `mensajes_id_usuario_64c6f5cf_fk_usuarios_id_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`),
  CONSTRAINT `ck_mensaje_un_destino` CHECK (`id_destinatario` is not null and `id_equipo` is null or `id_destinatario` is null and `id_equipo` is not null)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `reuniones` (
  `id_reunion` bigint(20) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(150) NOT NULL,
  `enlace` varchar(300) NOT NULL,
  `fecha` datetime(6) NOT NULL,
  `estado` varchar(12) NOT NULL,
  `grabacion_url` varchar(500) NOT NULL,
  `id_equipo` bigint(20) DEFAULT NULL,
  `id_usuario` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id_reunion`),
  KEY `reuniones_id_equipo_4fcd4e25_fk_equipos_id_equipo` (`id_equipo`),
  KEY `reuniones_id_usuario_6371ab90_fk_usuarios_id_usuario` (`id_usuario`),
  CONSTRAINT `reuniones_id_equipo_4fcd4e25_fk_equipos_id_equipo` FOREIGN KEY (`id_equipo`) REFERENCES `equipos` (`id_equipo`),
  CONSTRAINT `reuniones_id_usuario_6371ab90_fk_usuarios_id_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `calendario` (
  `id_calendario` bigint(20) NOT NULL AUTO_INCREMENT,
  `fecha_evento` datetime(6) NOT NULL,
  `nota` longtext NOT NULL,
  `id_usuario` bigint(20) NOT NULL,
  PRIMARY KEY (`id_calendario`),
  KEY `calendario_id_usuario_ff213115_fk_usuarios_id_usuario` (`id_usuario`),
  CONSTRAINT `calendario_id_usuario_ff213115_fk_usuarios_id_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `ia_conversaciones` (
  `id_conversacion` bigint(20) NOT NULL AUTO_INCREMENT,
  `titulo` varchar(200) NOT NULL,
  `fecha_inicio` datetime(6) NOT NULL,
  `fecha_ultima` datetime(6) NOT NULL,
  `activa` tinyint(1) NOT NULL,
  `id_usuario` bigint(20) NOT NULL,
  PRIMARY KEY (`id_conversacion`),
  KEY `ia_conversaciones_id_usuario_120f7335_fk_usuarios_id_usuario` (`id_usuario`),
  CONSTRAINT `ia_conversaciones_id_usuario_120f7335_fk_usuarios_id_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `ia_mensajes` (
  `id_ia_mensaje` bigint(20) NOT NULL AUTO_INCREMENT,
  `rol` varchar(10) NOT NULL,
  `contenido` longtext NOT NULL,
  `tokens_usados` int(10) unsigned DEFAULT NULL CHECK (`tokens_usados` >= 0),
  `modelo` varchar(60) NOT NULL,
  `fecha_envio` datetime(6) NOT NULL,
  `id_conversacion` bigint(20) NOT NULL,
  PRIMARY KEY (`id_ia_mensaje`),
  KEY `ia_mensajes_id_conversacion_0c0469da_fk_ia_conver` (`id_conversacion`),
  CONSTRAINT `ia_mensajes_id_conversacion_0c0469da_fk_ia_conver` FOREIGN KEY (`id_conversacion`) REFERENCES `ia_conversaciones` (`id_conversacion`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tickets_soporte` (
  `id_ticket` bigint(20) NOT NULL AUTO_INCREMENT,
  `asunto` varchar(200) NOT NULL,
  `descripcion` longtext NOT NULL,
  `prioridad` varchar(10) NOT NULL,
  `estado` varchar(12) NOT NULL,
  `fecha_creacion` datetime(6) NOT NULL,
  `fecha_cierre` datetime(6) DEFAULT NULL,
  `id_usuario` bigint(20) DEFAULT NULL,
  `id_empresa` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id_ticket`),
  KEY `tickets_soporte_id_usuario_ee201afd_fk_usuarios_id_usuario` (`id_usuario`),
  KEY `tickets_soporte_id_empresa_203cbbc2_fk_empresa_id_empresa` (`id_empresa`),
  CONSTRAINT `tickets_soporte_id_empresa_203cbbc2_fk_empresa_id_empresa` FOREIGN KEY (`id_empresa`) REFERENCES `empresa` (`id_empresa`),
  CONSTRAINT `tickets_soporte_id_usuario_ee201afd_fk_usuarios_id_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

-- Roles iniciales (los crea la migración cuentas/0002_roles_iniciales.py)
/*M!999999\- enable the sandbox mode */ 
INSERT INTO `roles` VALUES
(1,'admin','Administrador','Acceso completo a la empresa: usuarios, equipos y todos los proyectos.'),
(2,'manager','Manager','Gestiona equipos y proyectos de la empresa.'),
(3,'supervisor','Supervisor','Ve todos los proyectos y tareas de la empresa para hacer seguimiento.'),
(4,'colaborador','Colaborador','Trabaja en los proyectos, equipos y lienzos donde lo agregan.');

SET FOREIGN_KEY_CHECKS = 1;
