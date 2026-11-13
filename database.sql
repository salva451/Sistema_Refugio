CREATE DATABASE IF NOT EXISTS albergue_solidario
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE albergue_solidario;


-- ACCESO AL SISTEMA
CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre_usuario VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    rol ENUM('ADMINISTRADOR', 'ENCARGADO') NOT NULL DEFAULT 'ENCARGADO',
    intentos_fallidos INT NOT NULL DEFAULT 0,
    bloqueado_hasta DATETIME NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    CHECK (intentos_fallidos >= 0)
) ENGINE = InnoDB;


-- ALOJAMIENTO
CREATE TABLE IF NOT EXISTS albergues (
    id_albergue INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    direccion VARCHAR(200) NOT NULL,
    telefono VARCHAR(25),
    capacidad_maxima INT NOT NULL DEFAULT 0,
    CHECK (capacidad_maxima >= 0)
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS habitaciones (
    id_habitacion INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    id_albergue INT NOT NULL,
    numero VARCHAR(20) NOT NULL,
    descripcion VARCHAR(150),
    UNIQUE KEY uq_habitacion_albergue (id_albergue, numero),
    FOREIGN KEY (id_albergue)
        REFERENCES albergues (id_albergue)
        ON DELETE RESTRICT
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS camas (
    id_cama INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    id_habitacion INT NOT NULL,
    estado ENUM('HABILITADA', 'MANTENIMIENTO', 'INACTIVA')
        NOT NULL DEFAULT 'HABILITADA',
    FOREIGN KEY (id_habitacion)
        REFERENCES habitaciones (id_habitacion)
        ON DELETE RESTRICT
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS beneficiarios (
    id_beneficiario INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    nombres VARCHAR(80) NOT NULL,
    apellido_paterno VARCHAR(60) NOT NULL,
    apellido_materno VARCHAR(60),
    tipo_documento VARCHAR(30) NOT NULL DEFAULT 'CARNET DE IDENTIDAD',
    numero_documento VARCHAR(40) NOT NULL UNIQUE,
    fecha_nacimiento DATE,
    telefono VARCHAR(25),
    direccion VARCHAR(200),
    fecha_registro DATE NOT NULL DEFAULT (CURRENT_DATE),
    estado ENUM('ACTIVO', 'RETIRADO') NOT NULL DEFAULT 'ACTIVO',
    observaciones VARCHAR(200)
) ENGINE = InnoDB;

-- Tabla intermedia (camas N:M beneficiarios).
-- cama_activa y beneficiario_activo son columnas generadas: valen NULL cuando
-- la persona ya salio, y asi los UNIQUE impiden dos ocupaciones activas a la vez.
CREATE TABLE IF NOT EXISTS ocupaciones (
    id_ocupacion INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    id_cama INT NOT NULL,
    id_beneficiario INT NOT NULL,
    fecha_ingreso DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_salida DATETIME NULL,
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

-- ---------------------------------------------------------------------
-- COMEDORES E INVENTARIO
-- ---------------------------------------------------------------------
-- id_albergue es opcional: un comedor puede funcionar sin albergue.
CREATE TABLE IF NOT EXISTS comedores (
    id_comedor INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    direccion VARCHAR(200),
    id_albergue INT NULL,
    FOREIGN KEY (id_albergue)
        REFERENCES albergues (id_albergue)
        ON DELETE RESTRICT
) ENGINE = InnoDB;

-- raciones_por_unidad: cuantas raciones rinde una unidad (p. ej. 1 kg = 10).
CREATE TABLE IF NOT EXISTS alimentos (
    id_alimento INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    unidad ENUM('kg', 'litros', 'unidades') NOT NULL,
    raciones_por_unidad DECIMAL(10, 2) NOT NULL DEFAULT 1,
    CHECK (raciones_por_unidad > 0)
) ENGINE = InnoDB;

-- Tabla intermedia (comedores N:M alimentos), uno por lote.
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

CREATE TABLE IF NOT EXISTS raciones (
    id_racion INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    id_comedor INT NOT NULL,
    fecha_entrega DATE NOT NULL,
    tipo_comida ENUM('DESAYUNO', 'ALMUERZO', 'CENA', 'OTRA')
        NOT NULL DEFAULT 'OTRA',
    cantidad INT NOT NULL,
    observaciones VARCHAR(200),
    CHECK (cantidad > 0),
    FOREIGN KEY (id_comedor)
        REFERENCES comedores (id_comedor)
        ON DELETE RESTRICT
) ENGINE = InnoDB;


-- DONACIONES
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

-- Tabla intermedia (donaciones N:M alimentos).
CREATE TABLE IF NOT EXISTS detalle_donaciones (
    id_detalle INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    id_donacion INT NOT NULL,
    id_alimento INT NOT NULL,
    lote VARCHAR(50) NOT NULL,
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


-- VISTA: ocupacion del albergue (cupos disponibles)
CREATE OR REPLACE VIEW vista_ocupacion_albergue AS
SELECT
    a.id_albergue,
    a.nombre,
    a.capacidad_maxima,
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
FROM albergues a
LEFT JOIN habitaciones h
    ON h.id_albergue = a.id_albergue
LEFT JOIN camas c
    ON c.id_habitacion = h.id_habitacion
LEFT JOIN ocupaciones o
    ON o.id_cama = c.id_cama
    AND o.fecha_salida IS NULL
GROUP BY a.id_albergue, a.nombre, a.capacidad_maxima;


-- DATO INICIAL: el unico albergue del prototipo (ajustar capacidad real)
INSERT INTO albergues (codigo, nombre, direccion, capacidad_maxima)
VALUES ('ALB-001', 'Albergue Municipal Transitorio', 'Terminal de Buses, La Paz', 40)
ON DUPLICATE KEY UPDATE nombre = VALUES(nombre);