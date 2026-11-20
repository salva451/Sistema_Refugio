"""Ejecutar una vez para adaptar una base creada antes de tipo_beneficiario."""
from mysql.connector import Error

from conexion import conectar


conexion = None
cursor = None

try:
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = 'albergue_solidario'
          AND TABLE_NAME = 'beneficiarios'
          AND COLUMN_NAME = 'tipo_beneficiario'
    """)
    existe = cursor.fetchone()[0] > 0

    if not existe:
        cursor.execute("""
            ALTER TABLE beneficiarios
            ADD COLUMN tipo_beneficiario
            ENUM('ALOJADO', 'EXTERNO')
            NOT NULL DEFAULT 'EXTERNO'
            AFTER fecha_nacimiento
        """)
        conexion.commit()
        print("Migracion completada: se agrego tipo_beneficiario.")
    else:
        print("La tabla beneficiarios ya tiene tipo_beneficiario.")

except Error as error:
    print("No se pudo realizar la migracion:", error)
finally:
    if cursor is not None:
        cursor.close()
    if conexion is not None:
        conexion.close()
