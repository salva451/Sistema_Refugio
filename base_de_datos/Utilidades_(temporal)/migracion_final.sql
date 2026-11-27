-- =====================================================================
-- MIGRACION FINAL (ejecutar UNA SOLA VEZ sobre la base albergue_solidario)
-- Agrega lo que necesitan Inventario, Ingresos, Raciones, Reportes y Accesos.
-- Funciona en MySQL 8 y en MariaDB (XAMPP). Si falla porque una columna "ya existe",
-- esa parte ya estaba aplicada: salten esa sentencia y sigan con la siguiente.
-- Si su tabla del albergue se llama "albergues" (plural), cambien "albergue" en el
-- punto 5.
-- =====================================================================
USE albergue_solidario;

-- 1) Alimentos: categoria
ALTER TABLE alimentos
    ADD COLUMN categoria VARCHAR(30) NOT NULL DEFAULT 'Otros' AFTER nombre;

-- 2) Ingresos de alimentos: donacion o compra (+ costo de la compra)
ALTER TABLE donaciones
    ADD COLUMN tipo_ingreso ENUM('DONACION', 'COMPRA') NOT NULL DEFAULT 'DONACION',
    ADD COLUMN costo_total DECIMAL(10, 2) NULL,
    ADD CONSTRAINT chk_donaciones_costo CHECK (costo_total IS NULL OR costo_total >= 0);

-- Los proveedores se guardan en la misma tabla que los donantes
ALTER TABLE donantes
    MODIFY tipo ENUM('PERSONA', 'ORGANIZACION', 'PROVEEDOR') NOT NULL DEFAULT 'PERSONA';

-- 3) Raciones: cuantas fueron para alojados y cuantas para externos
ALTER TABLE raciones
    ADD COLUMN cantidad_alojados INT NOT NULL DEFAULT 0,
    ADD COLUMN cantidad_externos INT NOT NULL DEFAULT 0,
    ADD CONSTRAINT chk_raciones_split CHECK (cantidad_alojados >= 0 AND cantidad_externos >= 0);

-- 4) Registro de accesos (fecha y hora de cada ingreso al sistema)
CREATE TABLE IF NOT EXISTS accesos (
    id_acceso INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NULL,
    nombre_usuario VARCHAR(50) NOT NULL,
    fecha_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resultado ENUM('EXITOSO', 'FALLIDO', 'BLOQUEADO') NOT NULL,
    FOREIGN KEY (id_usuario)
        REFERENCES usuarios (id_usuario)
        ON DELETE SET NULL
) ENGINE = InnoDB;

-- 5) El prototipo trabaja con UN solo comedor: se crea si todavia no existe ninguno
INSERT INTO comedores (codigo, nombre, direccion, id_albergue)
SELECT 'COM-001', 'Comedor del Albergue', NULL, a.id_albergue
FROM albergue a
WHERE NOT EXISTS (SELECT 1 FROM comedores)
ORDER BY a.id_albergue
LIMIT 1;
