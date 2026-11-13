CREATE DATABASE IF NOT EXISTS refugio_solidario
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE refugio_solidario;

CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre_usuario VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS refugio (
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
        REFERENCES refugio (id_refugio)
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

CREATE TABLE IF NOT EXISTS personas (
    id_persona INT AUTO_INCREMENT PRIMARY KEY,
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
    estado ENUM('ACTIVA', 'RETIRADA') NOT NULL DEFAULT 'ACTIVA',
    observaciones VARCHAR(200)
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS ocupaciones (
    id_ocupacion INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    id_cama INT NOT NULL,
    id_persona INT NOT NULL,
    fecha_ingreso DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_salida DATETIME NULL,
    cama_activa INT GENERATED ALWAYS AS (
        CASE WHEN fecha_salida IS NULL THEN id_cama ELSE NULL END
    ) STORED,
    persona_activa INT GENERATED ALWAYS AS (
        CASE WHEN fecha_salida IS NULL THEN id_persona ELSE NULL END
    ) STORED,
    UNIQUE KEY uq_cama_activa (cama_activa),
    UNIQUE KEY uq_persona_activa (persona_activa),
    CHECK (fecha_salida IS NULL OR fecha_salida >= fecha_ingreso),
    FOREIGN KEY (id_cama)
        REFERENCES camas (id_cama)
        ON DELETE RESTRICT,
    FOREIGN KEY (id_persona)
        REFERENCES personas (id_persona)
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
    id_refugio INT NOT NULL,
    id_alimento INT NOT NULL,
    lote VARCHAR(50) NOT NULL,
    cantidad DECIMAL(10, 2) NOT NULL DEFAULT 0,
    fecha_vencimiento DATE NULL,
    UNIQUE KEY uq_lote_refugio_alimento (id_refugio, id_alimento, lote),
    CHECK (cantidad >= 0),
    FOREIGN KEY (id_refugio)
        REFERENCES refugio (id_refugio)
        ON DELETE RESTRICT,
    FOREIGN KEY (id_alimento)
        REFERENCES alimentos (id_alimento)
        ON DELETE RESTRICT
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS movimientos_inventario (
    id_movimiento INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    id_inventario INT NOT NULL,
    tipo_movimiento ENUM(
        'ENTRADA_DONACION',
        'SALIDA_RACION',
        'AJUSTE_ENTRADA',
        'AJUSTE_SALIDA'
    ) NOT NULL,
    cantidad DECIMAL(10, 2) NOT NULL,
    fecha_movimiento DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    motivo VARCHAR(200),
    CHECK (cantidad > 0),
    FOREIGN KEY (id_inventario)
        REFERENCES inventarios (id_inventario)
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
    id_refugio INT NOT NULL,
    fecha_donacion DATE NOT NULL,
    observaciones VARCHAR(200),
    FOREIGN KEY (id_donante)
        REFERENCES donantes (id_donante)
        ON DELETE RESTRICT,
    FOREIGN KEY (id_refugio)
        REFERENCES refugio (id_refugio)
        ON DELETE RESTRICT
) ENGINE = InnoDB;

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

CREATE TABLE IF NOT EXISTS raciones (
    id_racion INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    id_refugio INT NOT NULL,
    fecha_entrega DATE NOT NULL,
    tipo_comida ENUM('DESAYUNO', 'ALMUERZO', 'CENA', 'OTRA')
        NOT NULL DEFAULT 'OTRA',
    cantidad INT NOT NULL,
    observaciones VARCHAR(200),
    CHECK (cantidad > 0),
    FOREIGN KEY (id_refugio)
        REFERENCES refugio (id_refugio)
        ON DELETE RESTRICT
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS detalle_raciones (
    id_detalle_racion INT AUTO_INCREMENT PRIMARY KEY,
    id_racion INT NOT NULL,
    id_inventario INT NOT NULL,
    cantidad_consumida DECIMAL(10, 2) NOT NULL,
    CHECK (cantidad_consumida > 0),
    FOREIGN KEY (id_racion)
        REFERENCES raciones (id_racion)
        ON DELETE RESTRICT,
    FOREIGN KEY (id_inventario)
        REFERENCES inventarios (id_inventario)
        ON DELETE RESTRICT
) ENGINE = InnoDB;

CREATE OR REPLACE VIEW vista_ocupacion_refugio AS
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
FROM refugio r
LEFT JOIN habitaciones h
    ON h.id_refugio = r.id_refugio
LEFT JOIN camas c
    ON c.id_habitacion = h.id_habitacion
LEFT JOIN ocupaciones o
    ON o.id_cama = c.id_cama
    AND o.fecha_salida IS NULL
GROUP BY r.id_refugio, r.nombre;
