-- ============================================================
-- Xincronix: verificación de datos (SOLO CONSULTAS, no modifica nada)
-- Ejecutar en phpMyAdmin (pestaña SQL) o en el cliente mysql,
-- con la base xincronix_bd seleccionada.
-- ============================================================

-- 1. ¿Cuántas filas tiene cada tabla?
SELECT 'empresa' AS tabla, COUNT(*) AS filas FROM empresa
UNION ALL SELECT 'roles', COUNT(*) FROM roles
UNION ALL SELECT 'usuarios', COUNT(*) FROM usuarios
UNION ALL SELECT 'equipos', COUNT(*) FROM equipos
UNION ALL SELECT 'miembros_equipo', COUNT(*) FROM miembros_equipo
UNION ALL SELECT 'proyecto', COUNT(*) FROM proyecto
UNION ALL SELECT 'proyecto_miembros', COUNT(*) FROM proyecto_miembros
UNION ALL SELECT 'tareas', COUNT(*) FROM tareas
UNION ALL SELECT 'actividad', COUNT(*) FROM actividad;

-- 2. Proyectos cuyo creador es de OTRA empresa (debe dar 0 filas)
SELECT p.id_proyecto, p.nombre, p.id_empresa AS empresa_proyecto,
       u.email AS creador, u.id_empresa AS empresa_creador
FROM proyecto p
JOIN usuarios u ON u.id_usuario = p.id_creador
WHERE u.id_empresa <> p.id_empresa;

-- 3. Tareas asignadas a alguien de otra empresa (debe dar 0 filas)
SELECT t.id_tarea, t.titulo, u.email
FROM tareas t
JOIN proyecto p ON p.id_proyecto = t.id_proyecto
JOIN usuarios u ON u.id_usuario = t.id_usuario
WHERE u.id_empresa <> p.id_empresa;

-- 4. Equipos con miembros de otra empresa (debe dar 0 filas)
SELECT e.nombre AS equipo, u.email
FROM miembros_equipo m
JOIN equipos e ON e.id_equipo = m.id_equipo
JOIN usuarios u ON u.id_usuario = m.id_usuario
WHERE u.id_empresa <> e.id_empresa;

-- 5. Empresas sin equipos ni proyectos
SELECT em.id_empresa, em.nombre
FROM empresa em
WHERE NOT EXISTS (SELECT 1 FROM equipos e WHERE e.id_empresa = em.id_empresa)
  AND NOT EXISTS (SELECT 1 FROM proyecto p WHERE p.id_empresa = em.id_empresa);

-- 6. Usuarios sin nombre
SELECT id_usuario, email, is_superuser FROM usuarios
WHERE nombres = '' OR apellidos = '';

-- 7. Tareas sin responsable
SELECT id_tarea, titulo, estado FROM tareas WHERE id_usuario IS NULL;

-- 8. Tareas vencidas que no están completadas
SELECT id_tarea, titulo, estado, fecha_vencimiento FROM tareas
WHERE fecha_vencimiento < CURDATE() AND estado <> 'completada';

-- 9. Fechas imposibles: tareas completadas antes de crearse,
--    o actividad registrada antes de que existiera su proyecto
SELECT 'tarea' AS que, id_tarea AS id, titulo AS detalle
FROM tareas WHERE fecha_completada < fecha_creacion
UNION ALL
SELECT 'actividad', a.id_actividad, a.descripcion
FROM actividad a JOIN proyecto p ON p.id_proyecto = a.id_proyecto
WHERE a.fecha < p.fecha_creacion;

-- 10. Proyectos que no tienen miembros directos (proyecto_miembros vacío)
SELECT p.id_proyecto, p.nombre, p.id_equipo
FROM proyecto p
WHERE NOT EXISTS (SELECT 1 FROM proyecto_miembros pm WHERE pm.id_proyecto = p.id_proyecto);

-- 11. Sesiones abiertas (si alguna sigue vigente, NO compartas el volcado)
SELECT COUNT(*) AS sesiones_vigentes FROM django_session WHERE expire_date > NOW();

-- 12. Reglas CHECK que tiene la tabla proyecto
--     (si solo aparece la de nivel_importancia >= 0, se perdieron
--      las reglas de fechas e importancia 1-4: ver la guía, sección 6)
SELECT constraint_name, check_clause
FROM information_schema.check_constraints
WHERE constraint_schema = DATABASE() AND table_name = 'proyecto';
