from mysql.connector import Error

from conexion import conectar


def guardar_registro(codigo, nombre):
    conexion = conectar()
    cursor = None

    if conexion is None:
        return False, "No se pudo conectar con MySQL."

    try:
        cursor = conexion.cursor()
        query = """
            INSERT IGNORE INTO registros (codigo, nombre)
            VALUES (%s, %s)
        """
        cursor.execute(query, (codigo, nombre))
        conexion.commit()
        return True, None

    except Error as error:
        conexion.rollback()
        return False, str(error)

    finally:
        if cursor is not None:
            cursor.close()
        conexion.close()
