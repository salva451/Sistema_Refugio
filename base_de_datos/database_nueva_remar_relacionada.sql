-- ================================================================
-- BASE DE DATOS NUEVA - SISTEMA DE GESTION DEL ALBERGUE REMAR
-- Compatible con MySQL 8.0.16 o superior.
--
-- IMPORTANTE:
-- Este script ELIMINA la base albergue_solidario si ya existe.
-- Se perderan todos sus datos. Exporta una copia antes de ejecutarlo
-- si necesitas conservar beneficiarios, usuarios, ingresos o historial.
--
-- Instalacion:
-- 1. Abrir este archivo en MySQL Workbench / DBeaver.
-- 2. Ejecutar el script completo.
-- 3. Crear el usuario administrador desde crear_admin.py.
-- 4. No ejecutar migracion_final.sql, migracion_cambios_2.sql
--    ni migrar_beneficiarios.py en una instalacion nueva.
-- ================================================================

CREATE DATABASE albergue_solidario
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE albergue_solidario;

CREATE TABLE albergue (
    id_albergue INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    direccion VARCHAR(200) NOT NULL,
    telefono VARCHAR(25),
    capacidad_maxima INT NOT NULL DEFAULT 0,
    CONSTRAINT chk_albergue_capacidad CHECK (capacidad_maxima >= 0)
) ENGINE = InnoDB;


-- ================================================================
-- 1. ALBERGUE, USUARIOS Y REGISTRO DE ACCESOS
-- ================================================================

CREATE TABLE usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre_usuario VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    rol ENUM('ADMINISTRADOR', 'ENCARGADO') NOT NULL DEFAULT 'ENCARGADO',
    intentos_fallidos INT NOT NULL DEFAULT 0,
    bloqueado_hasta DATETIME NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    id_albergue INT NOT NULL DEFAULT 1,
    CONSTRAINT chk_usuarios_intentos CHECK (intentos_fallidos >= 0),
    INDEX idx_usuarios_albergue (id_albergue),
    CONSTRAINT fk_usuarios_albergue
        FOREIGN KEY (id_albergue)
        REFERENCES albergue (id_albergue)
        ON DELETE RESTRICT
) ENGINE = InnoDB;

CREATE TABLE accesos (
    id_acceso INT AUTO_INCREMENT PRIMARY KEY,
    -- NULL solo si se intenta ingresar con un usuario inexistente.
    id_usuario INT NULL,
    nombre_usuario VARCHAR(50) NOT NULL,
    fecha_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resultado ENUM('EXITOSO', 'FALLIDO', 'BLOQUEADO') NOT NULL,
    INDEX idx_accesos_fecha (fecha_hora),
    INDEX idx_accesos_usuario (id_usuario),
    CONSTRAINT fk_accesos_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES usuarios (id_usuario)
        ON DELETE SET NULL
) ENGINE = InnoDB;

-- ================================================================
-- 2. ALBERGUE, HABITACIONES Y CAMAS
-- ================================================================

CREATE TABLE habitaciones (
    id_habitacion INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    id_albergue INT NOT NULL,
    numero VARCHAR(20) NOT NULL,
    descripcion VARCHAR(150),
    UNIQUE KEY uq_habitacion_albergue (id_albergue, numero),
    CONSTRAINT fk_habitaciones_albergue
        FOREIGN KEY (id_albergue)
        REFERENCES albergue (id_albergue)
        ON DELETE RESTRICT
) ENGINE = InnoDB;

CREATE TABLE camas (
    id_cama INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    id_habitacion INT NOT NULL,
    estado ENUM('HABILITADA', 'MANTENIMIENTO', 'INACTIVA')
        NOT NULL DEFAULT 'HABILITADA',
    INDEX idx_camas_habitacion_estado (id_habitacion, estado),
    CONSTRAINT fk_camas_habitacion
        FOREIGN KEY (id_habitacion)
        REFERENCES habitaciones (id_habitacion)
        ON DELETE RESTRICT
) ENGINE = InnoDB;

-- ================================================================
-- 3. BENEFICIARIOS Y OCUPACIONES
-- ================================================================

CREATE TABLE beneficiarios (
    id_beneficiario INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    nombres VARCHAR(80) NOT NULL,
    apellido_paterno VARCHAR(60) NOT NULL,
    apellido_materno VARCHAR(60),
    tipo_documento VARCHAR(30) NOT NULL DEFAULT 'CARNET DE IDENTIDAD',
    numero_documento VARCHAR(40) NOT NULL UNIQUE,
    fecha_nacimiento DATE,
    tipo_beneficiario ENUM('ALOJADO', 'EXTERNO') NOT NULL DEFAULT 'EXTERNO',
    telefono VARCHAR(25),
    direccion VARCHAR(200),
    fecha_registro DATE NOT NULL DEFAULT (CURRENT_DATE),
    estado ENUM('ACTIVO', 'RETIRADO') NOT NULL DEFAULT 'ACTIVO',
    observaciones VARCHAR(200),
    INDEX idx_beneficiarios_estado_tipo (estado, tipo_beneficiario)
) ENGINE = InnoDB;

-- Una persona no puede tener dos ocupaciones activas y una cama
-- no puede estar asignada a dos personas al mismo tiempo.
-- Las columnas generadas quedan en NULL cuando existe fecha_salida.
CREATE TABLE ocupaciones (
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
    INDEX idx_ocupaciones_fechas (fecha_ingreso, fecha_salida),

    CONSTRAINT chk_ocupaciones_fechas
        CHECK (fecha_salida IS NULL OR fecha_salida >= fecha_ingreso),

    CONSTRAINT fk_ocupaciones_cama
        FOREIGN KEY (id_cama)
        REFERENCES camas (id_cama)
        ON DELETE RESTRICT,

    CONSTRAINT fk_ocupaciones_beneficiario
        FOREIGN KEY (id_beneficiario)
        REFERENCES beneficiarios (id_beneficiario)
        ON DELETE RESTRICT
) ENGINE = InnoDB;

-- ================================================================
-- 4. COMEDORES, CATALOGO DE ALIMENTOS E INVENTARIO
-- ================================================================

CREATE TABLE comedores (
    id_comedor INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    direccion VARCHAR(200),
    id_albergue INT NULL,
    CONSTRAINT fk_comedores_albergue
        FOREIGN KEY (id_albergue)
        REFERENCES albergue (id_albergue)
        ON DELETE RESTRICT
) ENGINE = InnoDB;

CREATE TABLE alimentos (
    id_alimento INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    categoria VARCHAR(30) NOT NULL DEFAULT 'Otros',
    unidad ENUM('kg', 'litros', 'unidades') NOT NULL,
    raciones_por_unidad DECIMAL(10, 2) NOT NULL DEFAULT 1,
    CONSTRAINT chk_alimentos_raciones CHECK (raciones_por_unidad > 0)
) ENGINE = InnoDB;

-- Cada registro representa un lote de un alimento en un comedor.
CREATE TABLE inventarios (
    id_inventario INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    id_comedor INT NOT NULL,
    id_alimento INT NOT NULL,
    lote VARCHAR(50) NOT NULL,
    cantidad DECIMAL(10, 2) NOT NULL DEFAULT 0,
    fecha_vencimiento DATE NULL,

    UNIQUE KEY uq_lote_comedor_alimento (id_comedor, id_alimento, lote),
    INDEX idx_inventario_fefo (id_alimento, fecha_vencimiento),
    INDEX idx_inventario_comedor (id_comedor),

    CONSTRAINT chk_inventario_cantidad CHECK (cantidad >= 0),

    CONSTRAINT fk_inventarios_comedor
        FOREIGN KEY (id_comedor)
        REFERENCES comedores (id_comedor)
        ON DELETE RESTRICT,

    CONSTRAINT fk_inventarios_alimento
        FOREIGN KEY (id_alimento)
        REFERENCES alimentos (id_alimento)
        ON DELETE RESTRICT
) ENGINE = InnoDB;

-- ================================================================
-- 5. RACIONES Y CONSUMO DE INVENTARIO
-- ================================================================

CREATE TABLE raciones (
    id_racion INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    id_comedor INT NOT NULL,
    fecha_entrega DATE NOT NULL,
    tipo_comida ENUM('DESAYUNO', 'ALMUERZO', 'TE', 'CENA', 'OTRA')
        NOT NULL DEFAULT 'OTRA',
    cantidad INT NOT NULL,
    cantidad_alojados INT NOT NULL DEFAULT 0,
    cantidad_externos INT NOT NULL DEFAULT 0,
    observaciones VARCHAR(200),

    INDEX idx_raciones_fecha (fecha_entrega),
    INDEX idx_raciones_comida_fecha (tipo_comida, fecha_entrega),

    CONSTRAINT chk_raciones_cantidad CHECK (cantidad > 0),
    CONSTRAINT chk_raciones_division CHECK (
        cantidad_alojados >= 0
        AND cantidad_externos >= 0
        AND cantidad = cantidad_alojados + cantidad_externos
    ),

    CONSTRAINT fk_raciones_comedor
        FOREIGN KEY (id_comedor)
        REFERENCES comedores (id_comedor)
        ON DELETE RESTRICT
) ENGINE = InnoDB;

-- Detalla los lotes de inventario consumidos en cada registro de raciones.
CREATE TABLE detalle_raciones (
    id_detalle_racion INT AUTO_INCREMENT PRIMARY KEY,
    id_racion INT NOT NULL,
    id_inventario INT NOT NULL,
    cantidad_consumida DECIMAL(10, 2) NOT NULL,

    UNIQUE KEY uq_racion_inventario (id_racion, id_inventario),

    CONSTRAINT chk_detalle_raciones_consumo CHECK (cantidad_consumida > 0),

    CONSTRAINT fk_detalle_raciones_racion
        FOREIGN KEY (id_racion)
        REFERENCES raciones (id_racion)
        ON DELETE RESTRICT,

    CONSTRAINT fk_detalle_raciones_inventario
        FOREIGN KEY (id_inventario)
        REFERENCES inventarios (id_inventario)
        ON DELETE RESTRICT
) ENGINE = InnoDB;

-- ================================================================
-- 6. DONANTES, PROVEEDORES, DONACIONES Y COMPRAS
-- ================================================================

CREATE TABLE donantes (
    id_donante INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    nombre VARCHAR(120) NOT NULL,
    tipo ENUM('PERSONA', 'ORGANIZACION', 'PROVEEDOR')
        NOT NULL DEFAULT 'PERSONA',
    telefono VARCHAR(25)
) ENGINE = InnoDB;

-- La tabla donaciones registra tanto DONACION como COMPRA.
CREATE TABLE donaciones (
    id_donacion INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    id_donante INT NOT NULL,
    id_comedor INT NOT NULL,
    fecha_donacion DATE NOT NULL,
    observaciones VARCHAR(200),
    tipo_ingreso ENUM('DONACION', 'COMPRA') NOT NULL DEFAULT 'DONACION',
    costo_total DECIMAL(10, 2) NULL,

    INDEX idx_donaciones_fecha (fecha_donacion),
    INDEX idx_donaciones_tipo_fecha (tipo_ingreso, fecha_donacion),

    CONSTRAINT chk_donaciones_costo
        CHECK (costo_total IS NULL OR costo_total >= 0),

    CONSTRAINT fk_donaciones_donante
        FOREIGN KEY (id_donante)
        REFERENCES donantes (id_donante)
        ON DELETE RESTRICT,

    CONSTRAINT fk_donaciones_comedor
        FOREIGN KEY (id_comedor)
        REFERENCES comedores (id_comedor)
        ON DELETE RESTRICT
) ENGINE = InnoDB;

-- Conserva el detalle histórico de los productos que ingresaron.
CREATE TABLE detalle_donaciones (
    id_detalle INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    id_donacion INT NOT NULL,
    id_alimento INT NOT NULL,
    lote VARCHAR(50) NOT NULL,
    cantidad DECIMAL(10, 2) NOT NULL,
    fecha_vencimiento DATE NULL,

    CONSTRAINT chk_detalle_donaciones_cantidad CHECK (cantidad > 0),

    CONSTRAINT fk_detalle_donaciones_donacion
        FOREIGN KEY (id_donacion)
        REFERENCES donaciones (id_donacion)
        ON DELETE RESTRICT,

    CONSTRAINT fk_detalle_donaciones_alimento
        FOREIGN KEY (id_alimento)
        REFERENCES alimentos (id_alimento)
        ON DELETE RESTRICT
) ENGINE = InnoDB;

-- ================================================================
-- 7. VISTA UTILIZADA POR EL MODULO DE OCUPACIONES Y REPORTES
-- ================================================================

CREATE VIEW vista_ocupacion_albergue AS
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
FROM albergue a
LEFT JOIN habitaciones h
    ON h.id_albergue = a.id_albergue
LEFT JOIN camas c
    ON c.id_habitacion = h.id_habitacion
LEFT JOIN ocupaciones o
    ON o.id_cama = c.id_cama
    AND o.fecha_salida IS NULL
GROUP BY a.id_albergue, a.nombre, a.capacidad_maxima;

-- ================================================================
-- 8. REGISTROS INICIALES NECESARIOS PARA QUE EL SISTEMA FUNCIONE
-- ================================================================

INSERT INTO albergue (
    codigo, nombre, direccion, capacidad_maxima
) VALUES (
    'ALB-001',
    'Albergue Municipal Transitorio',
    'Direccion pendiente de completar',
    40
);

INSERT INTO comedores (
    codigo, nombre, direccion, id_albergue
) VALUES (
    'COM-001',
    'Comedor del Albergue',
    NULL,
    1
);

-- Los usuarios se vinculan al albergue principal (id_albergue=1) por defecto.
-- No se insertan beneficiarios ni alimentos de demostracion.
-- El administrador se crea con crear_admin.py.
-- Los datos de prueba, si se necesitan, deben cargarse por separado.
