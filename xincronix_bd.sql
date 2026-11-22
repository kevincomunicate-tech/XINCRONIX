-- phpMyAdmin SQL Dump
-- version 5.2.3
-- https://www.phpmyadmin.net/
--
-- Servidor: localhost
-- Tiempo de generación: 22-11-2026 a las 21:44:52
-- Versión del servidor: 10.11.19-MariaDB
-- Versión de PHP: 8.5.13

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `xincronix_bd`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `account_emailaddress`
--

CREATE TABLE `account_emailaddress` (
  `id` int(11) NOT NULL,
  `email` varchar(254) NOT NULL,
  `verified` tinyint(1) NOT NULL,
  `primary` tinyint(1) NOT NULL,
  `user_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `account_emailconfirmation`
--

CREATE TABLE `account_emailconfirmation` (
  `id` int(11) NOT NULL,
  `created` datetime(6) NOT NULL,
  `sent` datetime(6) DEFAULT NULL,
  `key` varchar(64) NOT NULL,
  `email_address_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `actividad`
--

CREATE TABLE `actividad` (
  `id_actividad` bigint(20) NOT NULL,
  `tipo` varchar(10) NOT NULL,
  `descripcion` varchar(255) NOT NULL,
  `fecha` datetime(6) NOT NULL,
  `id_empresa` bigint(20) NOT NULL,
  `id_usuario` bigint(20) DEFAULT NULL,
  `id_proyecto` bigint(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `actividad`
--

INSERT INTO `actividad` (`id_actividad`, `tipo`, `descripcion`, `fecha`, `id_empresa`, `id_usuario`, `id_proyecto`) VALUES
(1, 'proyecto', 'creó el proyecto Rediseño del sitio web', '2026-11-20 10:12:30.953000', 1, 1, 1),
(2, 'tarea', 'completó la tarea Definir paleta de colores', '2026-11-20 13:12:30.953000', 1, 1, 1),
(3, 'tarea', 'completó la tarea Maquetar página de inicio', '2026-11-20 16:12:30.953000', 1, 1, 1),
(4, 'tarea', 'creó la tarea Adaptar a móviles', '2026-11-20 19:12:30.953000', 1, 1, 1),
(5, 'tarea', 'creó la tarea Revisar accesibilidad', '2026-11-20 22:12:30.953000', 1, 1, 1),
(6, 'proyecto', 'creó el proyecto App de inventario', '2026-11-21 01:12:30.953000', 1, 1, 2),
(7, 'tarea', 'completó la tarea Modelo de datos', '2026-11-21 04:12:30.953000', 1, 1, 2),
(8, 'tarea', 'creó la tarea Pantalla de productos', '2026-11-21 07:12:30.953000', 1, 1, 2),
(9, 'tarea', 'creó la tarea Reportes en PDF', '2026-11-21 10:12:30.953000', 1, 1, 2),
(10, 'proyecto', 'creó el proyecto Campaña de lanzamiento', '2026-11-21 13:12:30.953000', 1, 1, 3),
(11, 'tarea', 'creó la tarea Guion del video', '2026-11-21 16:12:30.953000', 1, 1, 3),
(12, 'tarea', 'creó la tarea Publicaciones en redes', '2026-11-21 19:12:30.953000', 1, 1, 3);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `auth_group`
--

CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL,
  `name` varchar(150) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `auth_group_permissions`
--

CREATE TABLE `auth_group_permissions` (
  `id` bigint(20) NOT NULL,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `auth_permission`
--

CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `auth_permission`
--

INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES
(1, 'Can add log entry', 1, 'add_logentry'),
(2, 'Can change log entry', 1, 'change_logentry'),
(3, 'Can delete log entry', 1, 'delete_logentry'),
(4, 'Can view log entry', 1, 'view_logentry'),
(5, 'Can add permission', 2, 'add_permission'),
(6, 'Can change permission', 2, 'change_permission'),
(7, 'Can delete permission', 2, 'delete_permission'),
(8, 'Can view permission', 2, 'view_permission'),
(9, 'Can add group', 3, 'add_group'),
(10, 'Can change group', 3, 'change_group'),
(11, 'Can delete group', 3, 'delete_group'),
(12, 'Can view group', 3, 'view_group'),
(13, 'Can add content type', 4, 'add_contenttype'),
(14, 'Can change content type', 4, 'change_contenttype'),
(15, 'Can delete content type', 4, 'delete_contenttype'),
(16, 'Can view content type', 4, 'view_contenttype'),
(17, 'Can add session', 5, 'add_session'),
(18, 'Can change session', 5, 'change_session'),
(19, 'Can delete session', 5, 'delete_session'),
(20, 'Can view session', 5, 'view_session'),
(21, 'Can add usuario', 6, 'add_usuario'),
(22, 'Can change usuario', 6, 'change_usuario'),
(23, 'Can delete usuario', 6, 'delete_usuario'),
(24, 'Can view usuario', 6, 'view_usuario'),
(25, 'Can add empresa', 7, 'add_empresa'),
(26, 'Can change empresa', 7, 'change_empresa'),
(27, 'Can delete empresa', 7, 'delete_empresa'),
(28, 'Can view empresa', 7, 'view_empresa'),
(29, 'Can add rol', 8, 'add_rol'),
(30, 'Can change rol', 8, 'change_rol'),
(31, 'Can delete rol', 8, 'delete_rol'),
(32, 'Can view rol', 8, 'view_rol'),
(33, 'Can add equipo', 9, 'add_equipo'),
(34, 'Can change equipo', 9, 'change_equipo'),
(35, 'Can delete equipo', 9, 'delete_equipo'),
(36, 'Can view equipo', 9, 'view_equipo'),
(37, 'Can add miembro del equipo', 10, 'add_miembroequipo'),
(38, 'Can change miembro del equipo', 10, 'change_miembroequipo'),
(39, 'Can delete miembro del equipo', 10, 'delete_miembroequipo'),
(40, 'Can view miembro del equipo', 10, 'view_miembroequipo'),
(41, 'Can add miembro del proyecto', 11, 'add_miembroproyecto'),
(42, 'Can change miembro del proyecto', 11, 'change_miembroproyecto'),
(43, 'Can delete miembro del proyecto', 11, 'delete_miembroproyecto'),
(44, 'Can view miembro del proyecto', 11, 'view_miembroproyecto'),
(45, 'Can add proyecto', 12, 'add_proyecto'),
(46, 'Can change proyecto', 12, 'change_proyecto'),
(47, 'Can delete proyecto', 12, 'delete_proyecto'),
(48, 'Can view proyecto', 12, 'view_proyecto'),
(49, 'Can add actividad', 13, 'add_actividad'),
(50, 'Can change actividad', 13, 'change_actividad'),
(51, 'Can delete actividad', 13, 'delete_actividad'),
(52, 'Can view actividad', 13, 'view_actividad'),
(53, 'Can add tarea', 14, 'add_tarea'),
(54, 'Can change tarea', 14, 'change_tarea'),
(55, 'Can delete tarea', 14, 'delete_tarea'),
(56, 'Can view tarea', 14, 'view_tarea'),
(57, 'Can add email address', 15, 'add_emailaddress'),
(58, 'Can change email address', 15, 'change_emailaddress'),
(59, 'Can delete email address', 15, 'delete_emailaddress'),
(60, 'Can view email address', 15, 'view_emailaddress'),
(61, 'Can add email confirmation', 16, 'add_emailconfirmation'),
(62, 'Can change email confirmation', 16, 'change_emailconfirmation'),
(63, 'Can delete email confirmation', 16, 'delete_emailconfirmation'),
(64, 'Can view email confirmation', 16, 'view_emailconfirmation'),
(65, 'Can add social account', 17, 'add_socialaccount'),
(66, 'Can change social account', 17, 'change_socialaccount'),
(67, 'Can delete social account', 17, 'delete_socialaccount'),
(68, 'Can view social account', 17, 'view_socialaccount'),
(69, 'Can add social application', 18, 'add_socialapp'),
(70, 'Can change social application', 18, 'change_socialapp'),
(71, 'Can delete social application', 18, 'delete_socialapp'),
(72, 'Can view social application', 18, 'view_socialapp'),
(73, 'Can add social application token', 19, 'add_socialtoken'),
(74, 'Can change social application token', 19, 'change_socialtoken'),
(75, 'Can delete social application token', 19, 'delete_socialtoken'),
(76, 'Can view social application token', 19, 'view_socialtoken'),
(77, 'Can add equipo', 20, 'add_equipo'),
(78, 'Can change equipo', 20, 'change_equipo'),
(79, 'Can delete equipo', 20, 'delete_equipo'),
(80, 'Can view equipo', 20, 'view_equipo'),
(81, 'Can add miembro de equipo', 21, 'add_miembroequipo'),
(82, 'Can change miembro de equipo', 21, 'change_miembroequipo'),
(83, 'Can delete miembro de equipo', 21, 'delete_miembroequipo'),
(84, 'Can view miembro de equipo', 21, 'view_miembroequipo'),
(85, 'Can add idea', 22, 'add_idea'),
(86, 'Can change idea', 22, 'change_idea'),
(87, 'Can delete idea', 22, 'delete_idea'),
(88, 'Can view idea', 22, 'view_idea'),
(89, 'Can add lienzo', 23, 'add_lienzo'),
(90, 'Can change lienzo', 23, 'change_lienzo'),
(91, 'Can delete lienzo', 23, 'delete_lienzo'),
(92, 'Can view lienzo', 23, 'view_lienzo'),
(93, 'Can add colaborador del lienzo', 24, 'add_lienzocolaborador'),
(94, 'Can change colaborador del lienzo', 24, 'change_lienzocolaborador'),
(95, 'Can delete colaborador del lienzo', 24, 'delete_lienzocolaborador'),
(96, 'Can view colaborador del lienzo', 24, 'view_lienzocolaborador'),
(97, 'Can add métrica de rendimiento', 25, 'add_metricarendimiento'),
(98, 'Can change métrica de rendimiento', 25, 'change_metricarendimiento'),
(99, 'Can delete métrica de rendimiento', 25, 'delete_metricarendimiento'),
(100, 'Can view métrica de rendimiento', 25, 'view_metricarendimiento'),
(101, 'Can add notificación', 26, 'add_notificacion'),
(102, 'Can change notificación', 26, 'change_notificacion'),
(103, 'Can delete notificación', 26, 'delete_notificacion'),
(104, 'Can view notificación', 26, 'view_notificacion'),
(105, 'Can add miembro del proyecto', 27, 'add_proyectomiembro'),
(106, 'Can change miembro del proyecto', 27, 'change_proyectomiembro'),
(107, 'Can delete miembro del proyecto', 27, 'delete_proyectomiembro'),
(108, 'Can view miembro del proyecto', 27, 'view_proyectomiembro'),
(109, 'Can add voto', 28, 'add_votoidea'),
(110, 'Can change voto', 28, 'change_votoidea'),
(111, 'Can delete voto', 28, 'delete_votoidea'),
(112, 'Can view voto', 28, 'view_votoidea'),
(113, 'Can add conversación con IA', 29, 'add_conversacionia'),
(114, 'Can change conversación con IA', 29, 'change_conversacionia'),
(115, 'Can delete conversación con IA', 29, 'delete_conversacionia'),
(116, 'Can view conversación con IA', 29, 'view_conversacionia'),
(117, 'Can add evento del calendario', 30, 'add_eventocalendario'),
(118, 'Can change evento del calendario', 30, 'change_eventocalendario'),
(119, 'Can delete evento del calendario', 30, 'delete_eventocalendario'),
(120, 'Can view evento del calendario', 30, 'view_eventocalendario'),
(121, 'Can add mensaje', 31, 'add_mensaje'),
(122, 'Can change mensaje', 31, 'change_mensaje'),
(123, 'Can delete mensaje', 31, 'delete_mensaje'),
(124, 'Can view mensaje', 31, 'view_mensaje'),
(125, 'Can add mensaje de IA', 32, 'add_mensajeia'),
(126, 'Can change mensaje de IA', 32, 'change_mensajeia'),
(127, 'Can delete mensaje de IA', 32, 'delete_mensajeia'),
(128, 'Can view mensaje de IA', 32, 'view_mensajeia'),
(129, 'Can add reunión', 33, 'add_reunion'),
(130, 'Can change reunión', 33, 'change_reunion'),
(131, 'Can delete reunión', 33, 'delete_reunion'),
(132, 'Can view reunión', 33, 'view_reunion'),
(133, 'Can add ticket de soporte', 34, 'add_ticketsoporte'),
(134, 'Can change ticket de soporte', 34, 'change_ticketsoporte'),
(135, 'Can delete ticket de soporte', 34, 'delete_ticketsoporte'),
(136, 'Can view ticket de soporte', 34, 'view_ticketsoporte');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `calendario`
--

CREATE TABLE `calendario` (
  `id_calendario` bigint(20) NOT NULL,
  `fecha_evento` datetime(6) NOT NULL,
  `nota` longtext NOT NULL,
  `id_usuario` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `django_admin_log`
--

CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext DEFAULT NULL,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) UNSIGNED NOT NULL CHECK (`action_flag` >= 0),
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `django_content_type`
--

CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `django_content_type`
--

INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES
(15, 'account', 'emailaddress'),
(16, 'account', 'emailconfirmation'),
(1, 'admin', 'logentry'),
(3, 'auth', 'group'),
(2, 'auth', 'permission'),
(29, 'comunicacion', 'conversacionia'),
(30, 'comunicacion', 'eventocalendario'),
(31, 'comunicacion', 'mensaje'),
(32, 'comunicacion', 'mensajeia'),
(33, 'comunicacion', 'reunion'),
(34, 'comunicacion', 'ticketsoporte'),
(4, 'contenttypes', 'contenttype'),
(7, 'cuentas', 'empresa'),
(20, 'cuentas', 'equipo'),
(21, 'cuentas', 'miembroequipo'),
(8, 'cuentas', 'rol'),
(6, 'cuentas', 'usuario'),
(13, 'dashboard', 'actividad'),
(9, 'dashboard', 'equipo'),
(22, 'dashboard', 'idea'),
(23, 'dashboard', 'lienzo'),
(24, 'dashboard', 'lienzocolaborador'),
(25, 'dashboard', 'metricarendimiento'),
(10, 'dashboard', 'miembroequipo'),
(11, 'dashboard', 'miembroproyecto'),
(26, 'dashboard', 'notificacion'),
(12, 'dashboard', 'proyecto'),
(27, 'dashboard', 'proyectomiembro'),
(14, 'dashboard', 'tarea'),
(28, 'dashboard', 'votoidea'),
(5, 'sessions', 'session'),
(17, 'socialaccount', 'socialaccount'),
(18, 'socialaccount', 'socialapp'),
(19, 'socialaccount', 'socialtoken');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `django_migrations`
--

CREATE TABLE `django_migrations` (
  `id` bigint(20) NOT NULL,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `django_migrations`
--

INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES
(1, 'contenttypes', '0001_initial', '2026-11-21 19:19:59.369522'),
(2, 'contenttypes', '0002_remove_content_type_name', '2026-11-21 19:20:00.887847'),
(3, 'auth', '0001_initial', '2026-11-21 19:20:03.465524'),
(4, 'auth', '0002_alter_permission_name_max_length', '2026-11-21 19:20:03.897701'),
(5, 'auth', '0003_alter_user_email_max_length', '2026-11-21 19:20:03.941588'),
(6, 'auth', '0004_alter_user_username_opts', '2026-11-21 19:20:03.982884'),
(7, 'auth', '0005_alter_user_last_login_null', '2026-11-21 19:20:04.051841'),
(8, 'auth', '0006_require_contenttypes_0002', '2026-11-21 19:20:04.067046'),
(9, 'auth', '0007_alter_validators_add_error_messages', '2026-11-21 19:20:04.096391'),
(10, 'auth', '0008_alter_user_username_max_length', '2026-11-21 19:20:04.125693'),
(11, 'auth', '0009_alter_user_last_name_max_length', '2026-11-21 19:20:04.150209'),
(12, 'auth', '0010_alter_group_name_max_length', '2026-11-21 19:20:04.464796'),
(13, 'auth', '0011_update_proxy_permissions', '2026-11-21 19:20:04.520322'),
(14, 'auth', '0012_alter_user_first_name_max_length', '2026-11-21 19:20:04.558914'),
(15, 'cuentas', '0001_initial', '2026-11-21 19:20:08.809983'),
(16, 'admin', '0001_initial', '2026-11-21 19:20:10.032691'),
(17, 'admin', '0002_logentry_remove_auto_add', '2026-11-21 19:20:10.125817'),
(18, 'admin', '0003_logentry_add_action_flag_choices', '2026-11-21 19:20:10.188624'),
(19, 'cuentas', '0002_roles_iniciales', '2026-11-21 19:20:10.715819'),
(20, 'cuentas', '0003_usuarios_esquema', '2026-11-21 19:20:18.776137'),
(21, 'dashboard', '0001_initial', '2026-11-21 19:20:31.866115'),
(22, 'sessions', '0001_initial', '2026-11-21 19:20:32.465811'),
(23, 'account', '0001_initial', '2026-11-21 21:56:45.318303'),
(24, 'account', '0002_email_max_length', '2026-11-21 21:56:45.731333'),
(25, 'account', '0003_alter_emailaddress_create_unique_verified_email', '2026-11-21 21:56:46.271153'),
(26, 'account', '0004_alter_emailaddress_drop_unique_email', '2026-11-21 21:56:46.973893'),
(27, 'account', '0005_emailaddress_idx_upper_email', '2026-11-21 21:56:47.083302'),
(28, 'account', '0006_emailaddress_lower', '2026-11-21 21:56:47.182596'),
(29, 'account', '0007_emailaddress_idx_email', '2026-11-21 21:56:47.653035'),
(30, 'account', '0008_emailaddress_unique_primary_email_fixup', '2026-11-21 21:56:47.779289'),
(31, 'account', '0009_emailaddress_unique_primary_email', '2026-11-21 21:56:47.882363'),
(32, 'comunicacion', '0001_initial', '2026-11-21 21:56:49.007831'),
(33, 'comunicacion', '0002_initial', '2026-11-21 21:56:56.595419'),
(34, 'cuentas', '0003_empresa_propietario_y_rol_usuario', '2026-11-21 21:56:57.689810'),
(35, 'dashboard', '0002_proyecto_rol_editor', '2026-11-21 21:56:58.496258'),
(36, 'socialaccount', '0001_initial', '2026-11-21 21:57:01.318740'),
(37, 'socialaccount', '0002_token_max_lengths', '2026-11-21 21:57:02.374068'),
(38, 'socialaccount', '0003_extra_data_default_dict', '2026-11-21 21:57:02.527995'),
(39, 'socialaccount', '0004_app_provider_id_settings', '2026-11-21 21:57:04.041277'),
(40, 'socialaccount', '0005_socialtoken_nullable_app', '2026-11-21 21:57:05.874749'),
(41, 'socialaccount', '0006_alter_socialaccount_extra_data', '2026-11-21 21:57:06.496481');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `django_session`
--

CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `django_session`
--

INSERT INTO `django_session` (`session_key`, `session_data`, `expire_date`) VALUES
('8uxle8kr45bda113382onyqb487qhzbu', '.eJxVjMsKwjAQRf8lawmZZGofS_f9hjCTDDYqiTQtKOK_a6Gbbu85536Ur1JrKtnL65nmtxrMSXlal8mvVWafohoUqMPGFO6SNxBvlK9Fh5KXObHeFL3TqscS5XHZ3cPBRHX6143pIwK0Ebqm4T5yB4zSgnOWLYYzokHojTUkrXWOyQWwbIQIOiQT1PcH2nM-GQ:1xUtCw:wyM1TB8ES26xmEc8ttILdOGgsNz_2lUzY6IsIS6Lgsk', '2026-12-05 22:05:18.985309');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `empresa`
--

CREATE TABLE `empresa` (
  `id_empresa` bigint(20) NOT NULL,
  `nombre` varchar(200) NOT NULL,
  `nit` varchar(30) DEFAULT NULL,
  `email` varchar(150) NOT NULL,
  `telefono` varchar(20) NOT NULL,
  `direccion` varchar(300) NOT NULL,
  `sector` varchar(20) NOT NULL,
  `num_empleados` varchar(10) NOT NULL,
  `fecha_creacion` datetime(6) NOT NULL,
  `fecha_actualizacion` datetime(6) NOT NULL,
  `id_propietario` bigint(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `empresa`
--

INSERT INTO `empresa` (`id_empresa`, `nombre`, `nit`, `email`, `telefono`, `direccion`, `sector`, `num_empleados`, `fecha_creacion`, `fecha_actualizacion`, `id_propietario`) VALUES
(1, 'Empresa demo', NULL, 'cuellaryohan100@gmail.com', '', '', '', '', '2026-11-21 19:22:30.726000', '2026-11-21 19:22:30.726000', 1),
(2, 'Nekros', NULL, 'cuellaryohan777@gmail.com', '', '', '', '', '2026-11-21 19:23:28.610000', '2026-11-21 19:23:28.610000', 2);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `equipos`
--

CREATE TABLE `equipos` (
  `id_equipo` bigint(20) NOT NULL,
  `nombre` varchar(150) NOT NULL,
  `descripcion` longtext NOT NULL,
  `fecha_creacion` datetime(6) NOT NULL,
  `id_empresa` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `equipos`
--

INSERT INTO `equipos` (`id_equipo`, `nombre`, `descripcion`, `fecha_creacion`, `id_empresa`) VALUES
(1, 'Equipo de producto', '', '2026-11-21 19:22:30.888000', 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `ia_conversaciones`
--

CREATE TABLE `ia_conversaciones` (
  `id_conversacion` bigint(20) NOT NULL,
  `titulo` varchar(200) NOT NULL,
  `fecha_inicio` datetime(6) NOT NULL,
  `fecha_ultima` datetime(6) NOT NULL,
  `activa` tinyint(1) NOT NULL,
  `id_usuario` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `ia_mensajes`
--

CREATE TABLE `ia_mensajes` (
  `id_ia_mensaje` bigint(20) NOT NULL,
  `rol` varchar(10) NOT NULL,
  `contenido` longtext NOT NULL,
  `tokens_usados` int(10) UNSIGNED DEFAULT NULL CHECK (`tokens_usados` >= 0),
  `modelo` varchar(60) NOT NULL,
  `fecha_envio` datetime(6) NOT NULL,
  `id_conversacion` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `ideas`
--

CREATE TABLE `ideas` (
  `id_idea` bigint(20) NOT NULL,
  `titulo` varchar(120) NOT NULL,
  `descripcion` longtext NOT NULL,
  `categoria` varchar(15) NOT NULL,
  `estado` varchar(15) NOT NULL,
  `color` varchar(10) NOT NULL,
  `fecha_creacion` datetime(6) NOT NULL,
  `id_empresa` bigint(20) NOT NULL,
  `id_usuario` bigint(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `ideas_votos`
--

CREATE TABLE `ideas_votos` (
  `id` bigint(20) NOT NULL,
  `id_idea` bigint(20) NOT NULL,
  `id_usuario` bigint(20) NOT NULL,
  `fecha` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `lienzos`
--

CREATE TABLE `lienzos` (
  `id_lienzo` bigint(20) NOT NULL,
  `nombre` varchar(60) NOT NULL,
  `contenido` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`contenido`)),
  `version` int(10) UNSIGNED NOT NULL CHECK (`version` >= 0),
  `compartido_con_empresa` tinyint(1) NOT NULL,
  `fecha_creacion` datetime(6) NOT NULL,
  `fecha_actualizacion` datetime(6) NOT NULL,
  `id_empresa` bigint(20) NOT NULL,
  `id_proyecto` bigint(20) DEFAULT NULL,
  `id_equipo` bigint(20) DEFAULT NULL,
  `id_creador` bigint(20) DEFAULT NULL,
  `id_ultimo_editor` bigint(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `lienzo_colaboradores`
--

CREATE TABLE `lienzo_colaboradores` (
  `id` bigint(20) NOT NULL,
  `id_lienzo` bigint(20) NOT NULL,
  `id_usuario` bigint(20) NOT NULL,
  `permiso` varchar(10) NOT NULL,
  `fecha_ingreso` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `mensajes`
--

CREATE TABLE `mensajes` (
  `id_mensajes` bigint(20) NOT NULL,
  `contenido` longtext NOT NULL,
  `fecha_envio` datetime(6) NOT NULL,
  `leido` tinyint(1) NOT NULL,
  `id_destinatario` bigint(20) DEFAULT NULL,
  `id_equipo` bigint(20) DEFAULT NULL,
  `id_usuario` bigint(20) NOT NULL
) ;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `metrica_rendimiento`
--

CREATE TABLE `metrica_rendimiento` (
  `id_metrica` bigint(20) NOT NULL,
  `tipo_metrica` varchar(100) NOT NULL,
  `valor` decimal(12,4) NOT NULL,
  `meta` decimal(12,4) DEFAULT NULL,
  `unidad` varchar(20) NOT NULL,
  `fecha_inicio_periodo` date NOT NULL,
  `fecha_fin_periodo` date NOT NULL,
  `id_empresa` bigint(20) NOT NULL,
  `id_usuario` bigint(20) DEFAULT NULL
) ;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `miembros_equipo`
--

CREATE TABLE `miembros_equipo` (
  `id` bigint(20) NOT NULL,
  `rol_en_equipo` varchar(10) NOT NULL,
  `fecha_ingreso` datetime(6) NOT NULL,
  `id_equipo` bigint(20) NOT NULL,
  `id_usuario` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `miembros_equipo`
--

INSERT INTO `miembros_equipo` (`id`, `rol_en_equipo`, `fecha_ingreso`, `id_equipo`, `id_usuario`) VALUES
(1, 'lider', '2026-11-21 19:22:30.947000', 1, 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `notificaciones`
--

CREATE TABLE `notificaciones` (
  `id_notificaciones` bigint(20) NOT NULL,
  `titulo` varchar(100) NOT NULL,
  `mensaje` longtext NOT NULL,
  `tipo` varchar(10) NOT NULL,
  `url` varchar(300) NOT NULL,
  `leida` tinyint(1) NOT NULL,
  `fecha_envio` datetime(6) NOT NULL,
  `id_usuario` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `proyecto`
--

CREATE TABLE `proyecto` (
  `id_proyecto` bigint(20) NOT NULL,
  `nombre` varchar(150) NOT NULL,
  `descripcion` longtext NOT NULL,
  `estado` varchar(15) NOT NULL,
  `nivel_importancia` smallint(5) UNSIGNED NOT NULL CHECK (`nivel_importancia` >= 0),
  `tipo_proyecto` varchar(15) NOT NULL,
  `fecha_inicio` date DEFAULT NULL,
  `fecha_fin` date DEFAULT NULL,
  `fecha_creacion` datetime(6) NOT NULL,
  `id_creador` bigint(20) DEFAULT NULL,
  `id_empresa` bigint(20) NOT NULL,
  `id_equipo` bigint(20) DEFAULT NULL
) ;

--
-- Volcado de datos para la tabla `proyecto`
--

INSERT INTO `proyecto` (`id_proyecto`, `nombre`, `descripcion`, `estado`, `nivel_importancia`, `tipo_proyecto`, `fecha_inicio`, `fecha_fin`, `fecha_creacion`, `id_creador`, `id_empresa`, `id_equipo`) VALUES
(1, 'Rediseño del sitio web', '', 'activo', 3, 'diseno', '2026-11-06', NULL, '2026-11-21 19:22:30.985000', 1, 1, 1),
(2, 'App de inventario', '', 'activo', 4, 'desarrollo', '2026-11-06', NULL, '2026-11-21 19:22:31.122000', 2, 1, 1),
(3, 'Campaña de lanzamiento', '', 'activo', 2, 'marketing', '2026-11-06', NULL, '2026-11-21 19:22:31.229000', 1, 1, 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `proyecto_miembros`
--

CREATE TABLE `proyecto_miembros` (
  `id` bigint(20) NOT NULL,
  `rol` varchar(15) NOT NULL,
  `fecha_ingreso` datetime(6) NOT NULL,
  `id_usuario` bigint(20) NOT NULL,
  `id_proyecto` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `reuniones`
--

CREATE TABLE `reuniones` (
  `id_reunion` bigint(20) NOT NULL,
  `nombre` varchar(150) NOT NULL,
  `enlace` varchar(300) NOT NULL,
  `fecha` datetime(6) NOT NULL,
  `estado` varchar(12) NOT NULL,
  `grabacion_url` varchar(500) NOT NULL,
  `id_equipo` bigint(20) DEFAULT NULL,
  `id_usuario` bigint(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `roles`
--

CREATE TABLE `roles` (
  `id_roles` int(11) NOT NULL,
  `codigo` varchar(30) NOT NULL,
  `nombre` varchar(80) NOT NULL,
  `descripcion` longtext NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `roles`
--

INSERT INTO `roles` (`id_roles`, `codigo`, `nombre`, `descripcion`) VALUES
(1, 'admin', 'Administrador', 'Gestiona todos los proyectos de su empresa. Solo el superadministrador puede dar este rol.'),
(4, 'usuario', 'Usuario', 'Usuario normal: crea su empresa, sus proyectos y trabaja en los proyectos donde lo agregan.');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `socialaccount_socialaccount`
--

CREATE TABLE `socialaccount_socialaccount` (
  `id` int(11) NOT NULL,
  `provider` varchar(200) NOT NULL,
  `uid` varchar(191) NOT NULL,
  `last_login` datetime(6) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `extra_data` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`extra_data`)),
  `user_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `socialaccount_socialapp`
--

CREATE TABLE `socialaccount_socialapp` (
  `id` int(11) NOT NULL,
  `provider` varchar(30) NOT NULL,
  `name` varchar(40) NOT NULL,
  `client_id` varchar(191) NOT NULL,
  `secret` varchar(191) NOT NULL,
  `key` varchar(191) NOT NULL,
  `provider_id` varchar(200) NOT NULL,
  `settings` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`settings`))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `socialaccount_socialtoken`
--

CREATE TABLE `socialaccount_socialtoken` (
  `id` int(11) NOT NULL,
  `token` longtext NOT NULL,
  `token_secret` longtext NOT NULL,
  `expires_at` datetime(6) DEFAULT NULL,
  `account_id` int(11) NOT NULL,
  `app_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tareas`
--

CREATE TABLE `tareas` (
  `id_tarea` bigint(20) NOT NULL,
  `titulo` varchar(200) NOT NULL,
  `descripcion` longtext NOT NULL,
  `estado` varchar(15) NOT NULL,
  `prioridad` varchar(10) NOT NULL,
  `fecha_creacion` datetime(6) NOT NULL,
  `fecha_vencimiento` date DEFAULT NULL,
  `fecha_completada` datetime(6) DEFAULT NULL,
  `id_usuario` bigint(20) DEFAULT NULL,
  `id_creador` bigint(20) DEFAULT NULL,
  `id_proyecto` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `tareas`
--

INSERT INTO `tareas` (`id_tarea`, `titulo`, `descripcion`, `estado`, `prioridad`, `fecha_creacion`, `fecha_vencimiento`, `fecha_completada`, `id_usuario`, `id_creador`, `id_proyecto`) VALUES
(1, 'Definir paleta de colores', '', 'completada', 'media', '2026-11-21 19:22:31.009000', '2026-11-15', '2026-11-21 19:22:31.007000', 1, 1, 1),
(2, 'Maquetar página de inicio', '', 'completada', 'alta', '2026-11-21 19:22:31.051000', '2026-11-19', '2026-11-21 19:22:31.050000', 1, 1, 1),
(3, 'Adaptar a móviles', '', 'en_progreso', 'alta', '2026-11-21 19:22:31.072000', '2026-11-24', NULL, 1, 1, 1),
(4, 'Revisar accesibilidad', '', 'por_hacer', 'media', '2026-11-21 19:22:31.092000', '2026-11-29', NULL, NULL, 1, 1),
(5, 'Modelo de datos', '', 'completada', 'alta', '2026-11-21 19:22:31.155000', '2026-11-11', '2026-11-21 19:22:31.153000', NULL, 1, 2),
(6, 'Pantalla de productos', '', 'en_revision', 'urgente', '2026-11-21 19:22:31.174000', '2026-11-20', NULL, 1, 1, 2),
(7, 'Reportes en PDF', '', 'por_hacer', 'baja', '2026-11-21 19:22:31.199000', '2026-12-03', NULL, 1, 1, 2),
(8, 'Guion del video', '', 'por_hacer', 'media', '2026-11-21 19:22:31.250000', '2026-11-26', NULL, NULL, 1, 3),
(9, 'Publicaciones en redes', '', 'por_hacer', 'baja', '2026-11-21 19:22:31.267000', NULL, NULL, 1, 1, 3);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tickets_soporte`
--

CREATE TABLE `tickets_soporte` (
  `id_ticket` bigint(20) NOT NULL,
  `asunto` varchar(200) NOT NULL,
  `descripcion` longtext NOT NULL,
  `prioridad` varchar(10) NOT NULL,
  `estado` varchar(12) NOT NULL,
  `fecha_creacion` datetime(6) NOT NULL,
  `fecha_cierre` datetime(6) DEFAULT NULL,
  `id_usuario` bigint(20) DEFAULT NULL,
  `id_empresa` bigint(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `id_usuario` bigint(20) NOT NULL,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `nombres` varchar(100) NOT NULL,
  `apellidos` varchar(100) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `estado` tinyint(1) NOT NULL,
  `fecha_creacion` datetime(6) NOT NULL,
  `email` varchar(150) NOT NULL,
  `cargo` varchar(80) NOT NULL,
  `telefono` varchar(20) NOT NULL,
  `avatar` varchar(100) NOT NULL,
  `id_empresa` bigint(20) DEFAULT NULL,
  `id_roles` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`id_usuario`, `password`, `last_login`, `is_superuser`, `nombres`, `apellidos`, `is_staff`, `estado`, `fecha_creacion`, `email`, `cargo`, `telefono`, `avatar`, `id_empresa`, `id_roles`) VALUES
(1, 'pbkdf2_sha256$1000000$r7u2CD7wovuQsQn5VorOtF$w91UIrjZFOxglb+i19pr8ZJ7j/auCqXPPxFpoQyx/9o=', '2026-11-21 22:05:18.976218', 1, '', '', 1, 1, '2026-11-21 19:21:45.982000', 'cuellaryohan100@gmail.com', '', '', '', 1, 1),
(2, 'pbkdf2_sha256$1000000$VcJ2urmdcjhUvdvlfZ5Ltf$JNurVmtFgW2EAuVsx6EOM+kNOlw7TIDYuH1DzLpOhZQ=', '2026-11-21 22:05:01.164279', 0, 'Yohan', 'Cuellar', 0, 1, '2026-11-21 19:23:28.617000', 'cuellaryohan777@gmail.com', '', '', '', 2, 4),
(3, 'pbkdf2_sha256$1000000$k2VrpDCW6gSr3NiOACzHZt$LIWabKGVC45vuUq0Mmsh8Ksnlw6Wtnlayvhjj76Z828=', NULL, 0, '', '', 0, 1, '2026-11-21 21:46:03.377963', 'cuellaryohan177@gmail.com', '', '', '', NULL, 4);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios_groups`
--

CREATE TABLE `usuarios_groups` (
  `id` bigint(20) NOT NULL,
  `usuario_id` bigint(20) NOT NULL,
  `group_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios_user_permissions`
--

CREATE TABLE `usuarios_user_permissions` (
  `id` bigint(20) NOT NULL,
  `usuario_id` bigint(20) NOT NULL,
  `permission_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `account_emailaddress`
--
ALTER TABLE `account_emailaddress`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `account_emailaddress_user_id_email_987c8728_uniq` (`user_id`,`email`),
  ADD KEY `account_emailaddress_email_03be32b2` (`email`);

--
-- Indices de la tabla `account_emailconfirmation`
--
ALTER TABLE `account_emailconfirmation`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `key` (`key`),
  ADD KEY `account_emailconfirm_email_address_id_5b7f8c58_fk_account_e` (`email_address_id`);

--
-- Indices de la tabla `actividad`
--
ALTER TABLE `actividad`
  ADD PRIMARY KEY (`id_actividad`),
  ADD KEY `idx_actividad_empresa_fecha` (`id_empresa`,`fecha` DESC),
  ADD KEY `actividad_id_usuario_c4865489_fk_usuarios_id_usuario` (`id_usuario`),
  ADD KEY `actividad_id_proyecto_7d1043e6_fk_proyecto_id_proyecto` (`id_proyecto`);

--
-- Indices de la tabla `auth_group`
--
ALTER TABLE `auth_group`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Indices de la tabla `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  ADD KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`);

--
-- Indices de la tabla `auth_permission`
--
ALTER TABLE `auth_permission`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`);

--
-- Indices de la tabla `calendario`
--
ALTER TABLE `calendario`
  ADD PRIMARY KEY (`id_calendario`),
  ADD KEY `calendario_id_usuario_ff213115_fk_usuarios_id_usuario` (`id_usuario`);

--
-- Indices de la tabla `django_admin_log`
--
ALTER TABLE `django_admin_log`
  ADD PRIMARY KEY (`id`),
  ADD KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  ADD KEY `django_admin_log_user_id_c564eba6_fk_cuentas_usuario_id` (`user_id`);

--
-- Indices de la tabla `django_content_type`
--
ALTER TABLE `django_content_type`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`);

--
-- Indices de la tabla `django_migrations`
--
ALTER TABLE `django_migrations`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `django_session`
--
ALTER TABLE `django_session`
  ADD PRIMARY KEY (`session_key`),
  ADD KEY `django_session_expire_date_a5c62663` (`expire_date`);

--
-- Indices de la tabla `empresa`
--
ALTER TABLE `empresa`
  ADD PRIMARY KEY (`id_empresa`),
  ADD UNIQUE KEY `nit` (`nit`),
  ADD KEY `empresa_id_propietario_0db51e50_fk_usuarios_id_usuario` (`id_propietario`);

--
-- Indices de la tabla `equipos`
--
ALTER TABLE `equipos`
  ADD PRIMARY KEY (`id_equipo`),
  ADD UNIQUE KEY `uq_equipo_nombre_por_empresa` (`id_empresa`,`nombre`);

--
-- Indices de la tabla `ia_conversaciones`
--
ALTER TABLE `ia_conversaciones`
  ADD PRIMARY KEY (`id_conversacion`),
  ADD KEY `ia_conversaciones_id_usuario_120f7335_fk_usuarios_id_usuario` (`id_usuario`);

--
-- Indices de la tabla `ia_mensajes`
--
ALTER TABLE `ia_mensajes`
  ADD PRIMARY KEY (`id_ia_mensaje`),
  ADD KEY `ia_mensajes_id_conversacion_0c0469da_fk_ia_conver` (`id_conversacion`);

--
-- Indices de la tabla `ideas`
--
ALTER TABLE `ideas`
  ADD PRIMARY KEY (`id_idea`),
  ADD KEY `ideas_id_empresa_c6705dce_fk_empresa_id_empresa` (`id_empresa`),
  ADD KEY `ideas_id_usuario_b9821647_fk_usuarios_id_usuario` (`id_usuario`);

--
-- Indices de la tabla `ideas_votos`
--
ALTER TABLE `ideas_votos`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_voto_idea` (`id_idea`,`id_usuario`),
  ADD KEY `ideas_votos_id_usuario_d5545740_fk_usuarios_id_usuario` (`id_usuario`);

--
-- Indices de la tabla `lienzos`
--
ALTER TABLE `lienzos`
  ADD PRIMARY KEY (`id_lienzo`),
  ADD KEY `lienzos_id_empresa_f12a263e_fk_empresa_id_empresa` (`id_empresa`),
  ADD KEY `lienzos_id_proyecto_8bab6206_fk_proyecto_id_proyecto` (`id_proyecto`),
  ADD KEY `lienzos_id_equipo_80c40d5b_fk_equipos_id_equipo` (`id_equipo`),
  ADD KEY `lienzos_id_creador_fcc1321a_fk_usuarios_id_usuario` (`id_creador`),
  ADD KEY `lienzos_id_ultimo_editor_9d497136_fk_usuarios_id_usuario` (`id_ultimo_editor`);

--
-- Indices de la tabla `lienzo_colaboradores`
--
ALTER TABLE `lienzo_colaboradores`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_lienzo_colaborador` (`id_lienzo`,`id_usuario`),
  ADD KEY `lienzo_colaboradores_id_usuario_83fdc601_fk_usuarios_id_usuario` (`id_usuario`);

--
-- Indices de la tabla `mensajes`
--
ALTER TABLE `mensajes`
  ADD PRIMARY KEY (`id_mensajes`),
  ADD KEY `mensajes_id_destinatario_7cf3d1ea_fk_usuarios_id_usuario` (`id_destinatario`),
  ADD KEY `mensajes_id_equipo_8b22db85_fk_equipos_id_equipo` (`id_equipo`),
  ADD KEY `idx_mensajes_conversacion` (`id_usuario`,`id_destinatario`,`fecha_envio`);

--
-- Indices de la tabla `metrica_rendimiento`
--
ALTER TABLE `metrica_rendimiento`
  ADD PRIMARY KEY (`id_metrica`),
  ADD KEY `metrica_rendimiento_id_empresa_98350754_fk_empresa_id_empresa` (`id_empresa`),
  ADD KEY `metrica_rendimiento_id_usuario_7c72a6f4_fk_usuarios_id_usuario` (`id_usuario`),
  ADD KEY `idx_metrica_tipo_periodo` (`tipo_metrica`,`fecha_inicio_periodo`,`fecha_fin_periodo`);

--
-- Indices de la tabla `miembros_equipo`
--
ALTER TABLE `miembros_equipo`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_miembro` (`id_equipo`,`id_usuario`),
  ADD KEY `miembros_equipo_id_usuario_7ddc7b77_fk_usuarios_id_usuario` (`id_usuario`);

--
-- Indices de la tabla `notificaciones`
--
ALTER TABLE `notificaciones`
  ADD PRIMARY KEY (`id_notificaciones`),
  ADD KEY `idx_notificaciones_usuario` (`id_usuario`,`leida`);

--
-- Indices de la tabla `proyecto`
--
ALTER TABLE `proyecto`
  ADD PRIMARY KEY (`id_proyecto`),
  ADD KEY `idx_proyecto_empresa_estado` (`id_empresa`,`estado`),
  ADD KEY `proyecto_id_creador_207002a5_fk_usuarios_id_usuario` (`id_creador`),
  ADD KEY `proyecto_id_equipo_776f7660_fk_equipos_id_equipo` (`id_equipo`);

--
-- Indices de la tabla `proyecto_miembros`
--
ALTER TABLE `proyecto_miembros`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_proyecto_miembro` (`id_proyecto`,`id_usuario`),
  ADD KEY `proyecto_miembros_id_usuario_8668de52_fk_usuarios_id_usuario` (`id_usuario`);

--
-- Indices de la tabla `reuniones`
--
ALTER TABLE `reuniones`
  ADD PRIMARY KEY (`id_reunion`),
  ADD KEY `reuniones_id_equipo_4fcd4e25_fk_equipos_id_equipo` (`id_equipo`),
  ADD KEY `reuniones_id_usuario_6371ab90_fk_usuarios_id_usuario` (`id_usuario`);

--
-- Indices de la tabla `roles`
--
ALTER TABLE `roles`
  ADD PRIMARY KEY (`id_roles`),
  ADD UNIQUE KEY `codigo` (`codigo`),
  ADD UNIQUE KEY `nombre` (`nombre`);

--
-- Indices de la tabla `socialaccount_socialaccount`
--
ALTER TABLE `socialaccount_socialaccount`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `socialaccount_socialaccount_provider_uid_fc810c6e_uniq` (`provider`,`uid`),
  ADD KEY `socialaccount_social_user_id_8146e70c_fk_usuarios_` (`user_id`);

--
-- Indices de la tabla `socialaccount_socialapp`
--
ALTER TABLE `socialaccount_socialapp`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `socialaccount_socialtoken`
--
ALTER TABLE `socialaccount_socialtoken`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `socialaccount_socialtoken_app_id_account_id_fca4e0ac_uniq` (`app_id`,`account_id`),
  ADD KEY `socialaccount_social_account_id_951f210e_fk_socialacc` (`account_id`);

--
-- Indices de la tabla `tareas`
--
ALTER TABLE `tareas`
  ADD PRIMARY KEY (`id_tarea`),
  ADD KEY `idx_tareas_proyecto_estado` (`id_proyecto`,`estado`),
  ADD KEY `tareas_id_usuario_01308f1b_fk_usuarios_id_usuario` (`id_usuario`),
  ADD KEY `tareas_id_creador_32b68b50_fk_usuarios_id_usuario` (`id_creador`);

--
-- Indices de la tabla `tickets_soporte`
--
ALTER TABLE `tickets_soporte`
  ADD PRIMARY KEY (`id_ticket`),
  ADD KEY `tickets_soporte_id_usuario_ee201afd_fk_usuarios_id_usuario` (`id_usuario`),
  ADD KEY `tickets_soporte_id_empresa_203cbbc2_fk_empresa_id_empresa` (`id_empresa`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`id_usuario`),
  ADD UNIQUE KEY `email` (`email`),
  ADD KEY `cuentas_usuario_id_empresa_07edfb00_fk_empresa_id_empresa` (`id_empresa`),
  ADD KEY `cuentas_usuario_id_roles_b5d94c34_fk_roles_id_roles` (`id_roles`);

--
-- Indices de la tabla `usuarios_groups`
--
ALTER TABLE `usuarios_groups`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `cuentas_usuario_groups_usuario_id_group_id_f5ef6c73_uniq` (`usuario_id`,`group_id`),
  ADD KEY `cuentas_usuario_groups_group_id_e6725cc8_fk_auth_group_id` (`group_id`);

--
-- Indices de la tabla `usuarios_user_permissions`
--
ALTER TABLE `usuarios_user_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `cuentas_usuario_user_per_usuario_id_permission_id_26c0acea_uniq` (`usuario_id`,`permission_id`),
  ADD KEY `cuentas_usuario_user_permission_id_1753ad79_fk_auth_perm` (`permission_id`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `account_emailaddress`
--
ALTER TABLE `account_emailaddress`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `account_emailconfirmation`
--
ALTER TABLE `account_emailconfirmation`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `actividad`
--
ALTER TABLE `actividad`
  MODIFY `id_actividad` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT de la tabla `auth_group`
--
ALTER TABLE `auth_group`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `auth_permission`
--
ALTER TABLE `auth_permission`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=137;

--
-- AUTO_INCREMENT de la tabla `calendario`
--
ALTER TABLE `calendario`
  MODIFY `id_calendario` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `django_admin_log`
--
ALTER TABLE `django_admin_log`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `django_content_type`
--
ALTER TABLE `django_content_type`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=35;

--
-- AUTO_INCREMENT de la tabla `django_migrations`
--
ALTER TABLE `django_migrations`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=42;

--
-- AUTO_INCREMENT de la tabla `empresa`
--
ALTER TABLE `empresa`
  MODIFY `id_empresa` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `equipos`
--
ALTER TABLE `equipos`
  MODIFY `id_equipo` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `ia_conversaciones`
--
ALTER TABLE `ia_conversaciones`
  MODIFY `id_conversacion` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `ia_mensajes`
--
ALTER TABLE `ia_mensajes`
  MODIFY `id_ia_mensaje` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `ideas`
--
ALTER TABLE `ideas`
  MODIFY `id_idea` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `ideas_votos`
--
ALTER TABLE `ideas_votos`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `lienzos`
--
ALTER TABLE `lienzos`
  MODIFY `id_lienzo` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `lienzo_colaboradores`
--
ALTER TABLE `lienzo_colaboradores`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `mensajes`
--
ALTER TABLE `mensajes`
  MODIFY `id_mensajes` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `metrica_rendimiento`
--
ALTER TABLE `metrica_rendimiento`
  MODIFY `id_metrica` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `miembros_equipo`
--
ALTER TABLE `miembros_equipo`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `notificaciones`
--
ALTER TABLE `notificaciones`
  MODIFY `id_notificaciones` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `proyecto`
--
ALTER TABLE `proyecto`
  MODIFY `id_proyecto` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `proyecto_miembros`
--
ALTER TABLE `proyecto_miembros`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `reuniones`
--
ALTER TABLE `reuniones`
  MODIFY `id_reunion` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `roles`
--
ALTER TABLE `roles`
  MODIFY `id_roles` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `socialaccount_socialaccount`
--
ALTER TABLE `socialaccount_socialaccount`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `socialaccount_socialapp`
--
ALTER TABLE `socialaccount_socialapp`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `socialaccount_socialtoken`
--
ALTER TABLE `socialaccount_socialtoken`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `tareas`
--
ALTER TABLE `tareas`
  MODIFY `id_tarea` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT de la tabla `tickets_soporte`
--
ALTER TABLE `tickets_soporte`
  MODIFY `id_ticket` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `id_usuario` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `usuarios_groups`
--
ALTER TABLE `usuarios_groups`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `usuarios_user_permissions`
--
ALTER TABLE `usuarios_user_permissions`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `account_emailaddress`
--
ALTER TABLE `account_emailaddress`
  ADD CONSTRAINT `account_emailaddress_user_id_2c513194_fk_usuarios_id_usuario` FOREIGN KEY (`user_id`) REFERENCES `usuarios` (`id_usuario`);

--
-- Filtros para la tabla `account_emailconfirmation`
--
ALTER TABLE `account_emailconfirmation`
  ADD CONSTRAINT `account_emailconfirm_email_address_id_5b7f8c58_fk_account_e` FOREIGN KEY (`email_address_id`) REFERENCES `account_emailaddress` (`id`);

--
-- Filtros para la tabla `actividad`
--
ALTER TABLE `actividad`
  ADD CONSTRAINT `actividad_id_empresa_cb1d3dc0_fk_empresa_id_empresa` FOREIGN KEY (`id_empresa`) REFERENCES `empresa` (`id_empresa`),
  ADD CONSTRAINT `actividad_id_proyecto_7d1043e6_fk_proyecto_id_proyecto` FOREIGN KEY (`id_proyecto`) REFERENCES `proyecto` (`id_proyecto`),
  ADD CONSTRAINT `actividad_id_usuario_c4865489_fk_usuarios_id_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`);

--
-- Filtros para la tabla `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  ADD CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  ADD CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`);

--
-- Filtros para la tabla `auth_permission`
--
ALTER TABLE `auth_permission`
  ADD CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`);

--
-- Filtros para la tabla `calendario`
--
ALTER TABLE `calendario`
  ADD CONSTRAINT `calendario_id_usuario_ff213115_fk_usuarios_id_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`);

--
-- Filtros para la tabla `django_admin_log`
--
ALTER TABLE `django_admin_log`
  ADD CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  ADD CONSTRAINT `django_admin_log_user_id_c564eba6_fk_cuentas_usuario_id` FOREIGN KEY (`user_id`) REFERENCES `usuarios` (`id_usuario`);

--
-- Filtros para la tabla `empresa`
--
ALTER TABLE `empresa`
  ADD CONSTRAINT `empresa_id_propietario_0db51e50_fk_usuarios_id_usuario` FOREIGN KEY (`id_propietario`) REFERENCES `usuarios` (`id_usuario`);

--
-- Filtros para la tabla `equipos`
--
ALTER TABLE `equipos`
  ADD CONSTRAINT `equipos_id_empresa_4e715381_fk_empresa_id_empresa` FOREIGN KEY (`id_empresa`) REFERENCES `empresa` (`id_empresa`);

--
-- Filtros para la tabla `ia_conversaciones`
--
ALTER TABLE `ia_conversaciones`
  ADD CONSTRAINT `ia_conversaciones_id_usuario_120f7335_fk_usuarios_id_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`);

--
-- Filtros para la tabla `ia_mensajes`
--
ALTER TABLE `ia_mensajes`
  ADD CONSTRAINT `ia_mensajes_id_conversacion_0c0469da_fk_ia_conver` FOREIGN KEY (`id_conversacion`) REFERENCES `ia_conversaciones` (`id_conversacion`);

--
-- Filtros para la tabla `ideas`
--
ALTER TABLE `ideas`
  ADD CONSTRAINT `ideas_id_empresa_c6705dce_fk_empresa_id_empresa` FOREIGN KEY (`id_empresa`) REFERENCES `empresa` (`id_empresa`),
  ADD CONSTRAINT `ideas_id_usuario_b9821647_fk_usuarios_id_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`);

--
-- Filtros para la tabla `ideas_votos`
--
ALTER TABLE `ideas_votos`
  ADD CONSTRAINT `ideas_votos_id_idea_fcec1227_fk_ideas_id_idea` FOREIGN KEY (`id_idea`) REFERENCES `ideas` (`id_idea`),
  ADD CONSTRAINT `ideas_votos_id_usuario_d5545740_fk_usuarios_id_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`);

--
-- Filtros para la tabla `lienzos`
--
ALTER TABLE `lienzos`
  ADD CONSTRAINT `lienzos_id_creador_fcc1321a_fk_usuarios_id_usuario` FOREIGN KEY (`id_creador`) REFERENCES `usuarios` (`id_usuario`),
  ADD CONSTRAINT `lienzos_id_empresa_f12a263e_fk_empresa_id_empresa` FOREIGN KEY (`id_empresa`) REFERENCES `empresa` (`id_empresa`),
  ADD CONSTRAINT `lienzos_id_equipo_80c40d5b_fk_equipos_id_equipo` FOREIGN KEY (`id_equipo`) REFERENCES `equipos` (`id_equipo`),
  ADD CONSTRAINT `lienzos_id_proyecto_8bab6206_fk_proyecto_id_proyecto` FOREIGN KEY (`id_proyecto`) REFERENCES `proyecto` (`id_proyecto`),
  ADD CONSTRAINT `lienzos_id_ultimo_editor_9d497136_fk_usuarios_id_usuario` FOREIGN KEY (`id_ultimo_editor`) REFERENCES `usuarios` (`id_usuario`);

--
-- Filtros para la tabla `lienzo_colaboradores`
--
ALTER TABLE `lienzo_colaboradores`
  ADD CONSTRAINT `lienzo_colaboradores_id_lienzo_88aaa20a_fk_lienzos_id_lienzo` FOREIGN KEY (`id_lienzo`) REFERENCES `lienzos` (`id_lienzo`),
  ADD CONSTRAINT `lienzo_colaboradores_id_usuario_83fdc601_fk_usuarios_id_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`);

--
-- Filtros para la tabla `mensajes`
--
ALTER TABLE `mensajes`
  ADD CONSTRAINT `mensajes_id_destinatario_7cf3d1ea_fk_usuarios_id_usuario` FOREIGN KEY (`id_destinatario`) REFERENCES `usuarios` (`id_usuario`),
  ADD CONSTRAINT `mensajes_id_equipo_8b22db85_fk_equipos_id_equipo` FOREIGN KEY (`id_equipo`) REFERENCES `equipos` (`id_equipo`),
  ADD CONSTRAINT `mensajes_id_usuario_64c6f5cf_fk_usuarios_id_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`);

--
-- Filtros para la tabla `metrica_rendimiento`
--
ALTER TABLE `metrica_rendimiento`
  ADD CONSTRAINT `metrica_rendimiento_id_empresa_98350754_fk_empresa_id_empresa` FOREIGN KEY (`id_empresa`) REFERENCES `empresa` (`id_empresa`),
  ADD CONSTRAINT `metrica_rendimiento_id_usuario_7c72a6f4_fk_usuarios_id_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`);

--
-- Filtros para la tabla `miembros_equipo`
--
ALTER TABLE `miembros_equipo`
  ADD CONSTRAINT `miembros_equipo_id_equipo_e2dfab96_fk_equipos_id_equipo` FOREIGN KEY (`id_equipo`) REFERENCES `equipos` (`id_equipo`),
  ADD CONSTRAINT `miembros_equipo_id_usuario_7ddc7b77_fk_usuarios_id_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`);

--
-- Filtros para la tabla `notificaciones`
--
ALTER TABLE `notificaciones`
  ADD CONSTRAINT `notificaciones_id_usuario_7a6362fb_fk_usuarios_id_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`);

--
-- Filtros para la tabla `proyecto`
--
ALTER TABLE `proyecto`
  ADD CONSTRAINT `proyecto_id_creador_207002a5_fk_usuarios_id_usuario` FOREIGN KEY (`id_creador`) REFERENCES `usuarios` (`id_usuario`),
  ADD CONSTRAINT `proyecto_id_empresa_6fd929e7_fk_empresa_id_empresa` FOREIGN KEY (`id_empresa`) REFERENCES `empresa` (`id_empresa`),
  ADD CONSTRAINT `proyecto_id_equipo_776f7660_fk_equipos_id_equipo` FOREIGN KEY (`id_equipo`) REFERENCES `equipos` (`id_equipo`);

--
-- Filtros para la tabla `proyecto_miembros`
--
ALTER TABLE `proyecto_miembros`
  ADD CONSTRAINT `proyecto_miembros_id_proyecto_4e187d3f_fk_proyecto_id_proyecto` FOREIGN KEY (`id_proyecto`) REFERENCES `proyecto` (`id_proyecto`),
  ADD CONSTRAINT `proyecto_miembros_id_usuario_8668de52_fk_usuarios_id_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`);

--
-- Filtros para la tabla `reuniones`
--
ALTER TABLE `reuniones`
  ADD CONSTRAINT `reuniones_id_equipo_4fcd4e25_fk_equipos_id_equipo` FOREIGN KEY (`id_equipo`) REFERENCES `equipos` (`id_equipo`),
  ADD CONSTRAINT `reuniones_id_usuario_6371ab90_fk_usuarios_id_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`);

--
-- Filtros para la tabla `socialaccount_socialaccount`
--
ALTER TABLE `socialaccount_socialaccount`
  ADD CONSTRAINT `socialaccount_social_user_id_8146e70c_fk_usuarios_` FOREIGN KEY (`user_id`) REFERENCES `usuarios` (`id_usuario`);

--
-- Filtros para la tabla `socialaccount_socialtoken`
--
ALTER TABLE `socialaccount_socialtoken`
  ADD CONSTRAINT `socialaccount_social_account_id_951f210e_fk_socialacc` FOREIGN KEY (`account_id`) REFERENCES `socialaccount_socialaccount` (`id`),
  ADD CONSTRAINT `socialaccount_social_app_id_636a42d7_fk_socialacc` FOREIGN KEY (`app_id`) REFERENCES `socialaccount_socialapp` (`id`);

--
-- Filtros para la tabla `tareas`
--
ALTER TABLE `tareas`
  ADD CONSTRAINT `tareas_id_creador_32b68b50_fk_usuarios_id_usuario` FOREIGN KEY (`id_creador`) REFERENCES `usuarios` (`id_usuario`),
  ADD CONSTRAINT `tareas_id_proyecto_3f503a90_fk_proyecto_id_proyecto` FOREIGN KEY (`id_proyecto`) REFERENCES `proyecto` (`id_proyecto`),
  ADD CONSTRAINT `tareas_id_usuario_01308f1b_fk_usuarios_id_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`);

--
-- Filtros para la tabla `tickets_soporte`
--
ALTER TABLE `tickets_soporte`
  ADD CONSTRAINT `tickets_soporte_id_empresa_203cbbc2_fk_empresa_id_empresa` FOREIGN KEY (`id_empresa`) REFERENCES `empresa` (`id_empresa`),
  ADD CONSTRAINT `tickets_soporte_id_usuario_ee201afd_fk_usuarios_id_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`);

--
-- Filtros para la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD CONSTRAINT `cuentas_usuario_id_empresa_07edfb00_fk_empresa_id_empresa` FOREIGN KEY (`id_empresa`) REFERENCES `empresa` (`id_empresa`),
  ADD CONSTRAINT `cuentas_usuario_id_roles_b5d94c34_fk_roles_id_roles` FOREIGN KEY (`id_roles`) REFERENCES `roles` (`id_roles`);

--
-- Filtros para la tabla `usuarios_groups`
--
ALTER TABLE `usuarios_groups`
  ADD CONSTRAINT `cuentas_usuario_groups_group_id_e6725cc8_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  ADD CONSTRAINT `cuentas_usuario_groups_usuario_id_251ff583_fk_cuentas_usuario_id` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id_usuario`);

--
-- Filtros para la tabla `usuarios_user_permissions`
--
ALTER TABLE `usuarios_user_permissions`
  ADD CONSTRAINT `cuentas_usuario_user_permission_id_1753ad79_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  ADD CONSTRAINT `cuentas_usuario_user_usuario_id_5a9718f1_fk_cuentas_u` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id_usuario`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
