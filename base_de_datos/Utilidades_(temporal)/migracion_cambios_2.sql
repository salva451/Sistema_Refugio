-- =====================================================================
-- CAMBIO: nuevo tipo de comida "Té" en Raciones.
-- Ejecutar UNA SOLA VEZ sobre la base albergue_solidario (despues de migracion_final.sql).
-- =====================================================================
USE albergue_solidario;

ALTER TABLE raciones
    MODIFY tipo_comida ENUM('DESAYUNO', 'ALMUERZO', 'TE', 'CENA', 'OTRA') NOT NULL DEFAULT 'OTRA';
