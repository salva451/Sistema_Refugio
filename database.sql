CREATE DATABASE IF NOT EXISTS refugio_solidario
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE refugio_solidario;

CREATE TABLE IF NOT EXISTS refugios (
    id_refugio INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    direccion VARCHAR(200) NOT NULL,
    telefono VARCHAR(25),
    capacidad_planificada INT NOT NULL DEFAULT 0,
    CHECK (capacidad_planificada >= 0)
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS habitaciones (
    id_habitacion INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    id_refugio INT NOT NULL,
    numero VARCHAR(20) NOT NULL,
    descripcion VARCHAR(150),
    UNIQUE KEY uq_habitacion_refugio (id_refugio, numero),
    FOREIGN KEY (id_refugio)
        REFERENCES refugios (id_refugio)
        ON DELETE RESTRICT
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS camas (
    id_cama INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    id_habitacion INT NOT NULL,
    estado ENUM('HABILITADA', 'MANTENIMIENTO', 'INACTIVA')
        NOT NULL DEFAULT 'HABILITADA',
    UNIQUE KEY uq_cama_habitacion (id_habitacion, codigo),
    FOREIGN KEY (id_habitacion)
        REFERENCES habitaciones (id_habitacion)
        ON DELETE RESTRICT
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS beneficiarios (
    id_beneficiario INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    fecha_registro DATE NOT NULL,
    observaciones VARCHAR(200)
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS ocupaciones (
    id_ocupacion INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    id_cama INT NOT NULL,
    id_beneficiario INT NOT NULL,
    fecha_ingreso DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_salida DATETIME NULL,
    -- UNIQUE permite varios NULL: solo una ocupacion activa por cama/beneficiario.
    cama_activa INT GENERATED ALWAYS AS (
        CASE WHEN fecha_salida IS NULL THEN id_cama ELSE NULL END
    ) STORED,
    beneficiario_activo INT GENERATED ALWAYS AS (
        CASE WHEN fecha_salida IS NULL THEN id_beneficiario ELSE NULL END
    ) STORED,
    UNIQUE KEY uq_cama_activa (cama_activa),
    UNIQUE KEY uq_beneficiario_activo (beneficiario_activo),
    CHECK (fecha_salida IS NULL OR fecha_salida >= fecha_ingreso),
    FOREIGN KEY (id_cama)
        REFERENCES camas (id_cama)
        ON DELETE RESTRICT,
    FOREIGN KEY (id_beneficiario)
        REFERENCES beneficiarios (id_beneficiario)
        ON DELETE RESTRICT
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS comedores (
    id_comedor INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    direccion VARCHAR(200) NOT NULL,
    id_refugio INT NULL,
    FOREIGN KEY (id_refugio)
        REFERENCES refugios (id_refugio)
        ON DELETE RESTRICT
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS alimentos (
    id_alimento INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    unidad ENUM('kg', 'litros', 'unidades') NOT NULL
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS inventarios (
    id_inventario INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    id_comedor INT NOT NULL,
    id_alimento INT NOT NULL,
    lote VARCHAR(50) NOT NULL,
    cantidad DECIMAL(10, 2) NOT NULL DEFAULT 0,
    fecha_vencimiento DATE NULL,
    UNIQUE KEY uq_lote_comedor_alimento (id_comedor, id_alimento, lote),
    CHECK (cantidad >= 0),
    FOREIGN KEY (id_comedor)
        REFERENCES comedores (id_comedor)
        ON DELETE RESTRICT,
    FOREIGN KEY (id_alimento)
        REFERENCES alimentos (id_alimento)
        ON DELETE RESTRICT
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS donantes (
    id_donante INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    nombre VARCHAR(120) NOT NULL,
    tipo ENUM('PERSONA', 'ORGANIZACION') NOT NULL DEFAULT 'PERSONA',
    telefono VARCHAR(25)
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS donaciones (
    id_donacion INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    id_donante INT NOT NULL,
    id_comedor INT NOT NULL,
    fecha_donacion DATE NOT NULL,
    observaciones VARCHAR(200),
    FOREIGN KEY (id_donante)
        REFERENCES donantes (id_donante)
        ON DELETE RESTRICT,
    FOREIGN KEY (id_comedor)
        REFERENCES comedores (id_comedor)
        ON DELETE RESTRICT
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS detalle_donaciones (
    id_detalle INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    id_donacion INT NOT NULL,
    id_alimento INT NOT NULL,
    cantidad DECIMAL(10, 2) NOT NULL,
    fecha_vencimiento DATE NULL,
    CHECK (cantidad > 0),
    FOREIGN KEY (id_donacion)
        REFERENCES donaciones (id_donacion)
        ON DELETE RESTRICT,
    FOREIGN KEY (id_alimento)
        REFERENCES alimentos (id_alimento)
        ON DELETE RESTRICT
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS raciones (
    id_racion INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    id_comedor INT NOT NULL,
    fecha_entrega DATE NOT NULL,
    cantidad INT NOT NULL,
    observaciones VARCHAR(200),
    CHECK (cantidad > 0),
    FOREIGN KEY (id_comedor)
        REFERENCES comedores (id_comedor)
        ON DELETE RESTRICT
) ENGINE = InnoDB;

-- Vista para el panel de ocupacion. No cuenta como tabla.
CREATE OR REPLACE VIEW vista_ocupacion_refugios AS
SELECT
    r.id_refugio,
    r.nombre,
    COUNT(c.id_cama) AS total_camas,
    COUNT(CASE WHEN c.estado = 'HABILITADA' THEN 1 END) AS camas_habilitadas,
    COUNT(
        CASE
            WHEN c.estado = 'HABILITADA'
                AND o.id_ocupacion IS NOT NULL
            THEN 1
        END
    ) AS camas_ocupadas,
    COUNT(
        CASE
            WHEN c.estado = 'HABILITADA'
                AND o.id_ocupacion IS NULL
            THEN 1
        END
    ) AS camas_disponibles
FROM refugios r
LEFT JOIN habitaciones h
    ON h.id_refugio = r.id_refugio
LEFT JOIN camas c
    ON c.id_habitacion = h.id_habitacion
LEFT JOIN ocupaciones o
    ON o.id_cama = c.id_cama
    AND o.fecha_salida IS NULL
GROUP BY r.id_refugio, r.nombre;

INSERT INTO refugios (
    codigo,
    nombre,
    direccion,
    telefono,
    capacidad_planificada
) VALUES
    ('REF-001', 'Refugio Esperanza', 'Zona Central, La Paz', '70000001', 20),
    ('REF-002', 'Centro Nueva Vida', 'Zona Sur, La Paz', '70000002', 15);

INSERT INTO habitaciones (
    codigo,
    id_refugio,
    numero,
    descripcion
) VALUES
    ('HAB-001', 1, 'H-01', 'Habitacion principal'),
    ('HAB-002', 1, 'H-02', 'Habitacion secundaria'),
    ('HAB-003', 2, 'H-01', 'Habitacion principal');

INSERT INTO camas (
    codigo,
    id_habitacion,
    estado
) VALUES
    ('CAM-001', 1, 'HABILITADA'),
    ('CAM-002', 1, 'HABILITADA'),
    ('CAM-003', 2, 'MANTENIMIENTO'),
    ('CAM-004', 3, 'HABILITADA');

INSERT INTO beneficiarios (
    codigo,
    fecha_registro,
    observaciones
) VALUES
    ('BEN-001', '2026-11-01', 'Registro de demostracion'),
    ('BEN-002', '2026-11-02', NULL);

INSERT INTO ocupaciones (
    codigo,
    id_cama,
    id_beneficiario,
    fecha_ingreso
) VALUES
    ('OCU-001', 1, 1, '2026-11-05 10:00:00');

INSERT INTO comedores (
    codigo,
    nombre,
    direccion,
    id_refugio
) VALUES
    ('COM-001', 'Comedor Esperanza', 'Zona Central, La Paz', 1),
    ('COM-002', 'Comedor Solidario', 'Zona Sur, La Paz', 2);

INSERT INTO alimentos (
    codigo,
    nombre,
    unidad
) VALUES
    ('ALI-001', 'Arroz', 'kg'),
    ('ALI-002', 'Aceite', 'litros'),
    ('ALI-003', 'Fideo', 'kg');

INSERT INTO inventarios (
    codigo,
    id_comedor,
    id_alimento,
    lote,
    cantidad,
    fecha_vencimiento
) VALUES
    ('INV-001', 1, 1, 'ARR-001', 50.00, '2027-05-01'),
    ('INV-002', 1, 2, 'ACE-001', 20.00, '2027-06-01');

INSERT INTO donantes (
    codigo,
    nombre,
    tipo,
    telefono
) VALUES
    ('DON-001', 'Donante Ejemplo', 'PERSONA', NULL),
    ('DON-002', 'Fundacion Ejemplo', 'ORGANIZACION', NULL);

INSERT INTO donaciones (
    codigo,
    id_donante,
    id_comedor,
    fecha_donacion,
    observaciones
) VALUES
    ('DNA-001', 1, 1, '2026-11-06', 'Donacion de prueba');

INSERT INTO detalle_donaciones (
    codigo,
    id_donacion,
    id_alimento,
    cantidad,
    fecha_vencimiento
) VALUES
    ('DET-001', 1, 1, 10.00, '2027-05-01'),
    ('DET-002', 1, 2, 5.00, '2027-06-01');

INSERT INTO raciones (
    codigo,
    id_comedor,
    fecha_entrega,
    cantidad,
    observaciones
) VALUES
    ('RAC-001', 1, '2026-11-07', 80, 'Entrega de prueba'),
    ('RAC-002', 2, '2026-11-07', 40, 'Entrega de prueba');
