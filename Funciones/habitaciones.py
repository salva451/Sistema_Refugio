from mysql.connector import Error

from conexion import conectar


def obtener_habitaciones():
    conexion = conectar()
    cursor = None
    if conexion is None:
        return False, "No se pudo conectar con MySQL."
    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT h.id_habitacion,
                   h.codigo,
                   h.numero,
                   h.descripcion,
                   COUNT(c.id_cama)
            FROM habitaciones h
            LEFT JOIN camas c ON c.id_habitacion = h.id_habitacion
            GROUP BY h.id_habitacion, h.codigo, h.numero, h.descripcion
            ORDER BY h.numero
        """)
        return True, cursor.fetchall()
    except Error as error:
        return False, str(error)
    finally:
        if cursor is not None:
            cursor.close()
        conexion.close()


def crear_habitacion(numero, descripcion):
    conexion = conectar()
    cursor = None
    if conexion is None:
        return False, "No se pudo conectar con MySQL."
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT id_albergue FROM albergue ORDER BY id_albergue LIMIT 1")
        albergue = cursor.fetchone()
        if albergue is None:
            return False, "Primero debe existir un albergue."

        cursor.execute("""
            SELECT COALESCE(MAX(CAST(SUBSTRING(codigo, 3) AS UNSIGNED)), 0)
            FROM habitaciones
            WHERE codigo LIKE 'H-%'
        """)
        siguiente = int(cursor.fetchone()[0]) + 1
        codigo = f"H-{siguiente:03d}"

        cursor.execute("""
            INSERT INTO habitaciones (codigo, id_albergue, numero, descripcion)
            VALUES (%s, %s, %s, %s)
        """, (codigo, albergue[0], numero, descripcion))
        conexion.commit()
        return True, None
    except Error as error:
        conexion.rollback()
        return False, str(error)
    finally:
        if cursor is not None:
            cursor.close()
        conexion.close()