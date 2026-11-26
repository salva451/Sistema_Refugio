-- =====================================================================
-- DATOS DE PRUEBA (OPCIONAL). Ejecutar DESPUES de migracion_final.sql.
-- Sirve para ver Inventario, Raciones y Reportes con datos desde el primer momento.
-- =====================================================================
USE albergue_solidario;

INSERT IGNORE INTO alimentos (codigo, nombre, categoria, unidad, raciones_por_unidad) VALUES
('ALI-0001', 'Arroz',    'Cereales',  'kg',     10),
('ALI-0002', 'Fideo',    'Cereales',  'kg',     10),
('ALI-0003', 'Lentejas', 'Legumbres', 'kg',     12),
('ALI-0004', 'Aceite',   'Otros',     'litros', 40),
('ALI-0005', 'Azúcar',   'Otros',     'kg',     20),
('ALI-0006', 'Leche',    'Lácteos',   'litros',  5);

INSERT IGNORE INTO donantes (codigo, nombre, tipo, telefono) VALUES
('DON-0001', 'Panadería Sol',      'ORGANIZACION', '70000001'),
('DON-0002', 'Pedro Rojas',        'PERSONA',      NULL),
('DON-0003', 'Mercado Rodríguez',  'PROVEEDOR',    NULL);

-- Lotes de ejemplo (uno vencido y uno por vencer, para ver las alertas y el orden FEFO)
INSERT IGNORE INTO inventarios (codigo, id_comedor, id_alimento, lote, cantidad, fecha_vencimiento)
SELECT x.codigo,
       (SELECT id_comedor FROM comedores ORDER BY id_comedor LIMIT 1),
       (SELECT id_alimento FROM alimentos WHERE nombre = x.alimento),
       x.lote, x.cantidad, DATE_ADD(CURDATE(), INTERVAL x.dias DAY)
FROM (
    SELECT 'INV-0001' AS codigo, 'Arroz'    AS alimento, 'L-001' AS lote, 20 AS cantidad,    5 AS dias
    UNION ALL SELECT 'INV-0002', 'Arroz',    'L-002', 30, 180
    UNION ALL SELECT 'INV-0003', 'Fideo',    'L-001', 15,  20
    UNION ALL SELECT 'INV-0004', 'Lentejas', 'L-001', 12,  90
    UNION ALL SELECT 'INV-0005', 'Aceite',   'L-001',  5,  60
    UNION ALL SELECT 'INV-0006', 'Leche',    'L-001', 40,  45
    UNION ALL SELECT 'INV-0007', 'Azúcar',   'L-001', 10,  -3
) x;
