INSERT INTO roles (nombre, descripcion)
SELECT 'SUPERADMIN', 'Administrador global'
WHERE NOT EXISTS (SELECT 1 FROM roles WHERE nombre = 'SUPERADMIN');
