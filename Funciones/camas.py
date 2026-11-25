from mysql.connector import Error

from conexion import conectar


def obtener_camas(id_habitacion):
    conexion = conectar()
    cursor = None
    if conexion is None:
        return False, "No se pudo conectar con MySQL."
    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT c.id_cama, c.codigo, c.estado,
                   o.id_beneficiario
            FROM camas c
            LEFT JOIN ocupaciones o
              ON o.id_cama = c.id_cama
             AND o.fecha_salida IS NULL
            WHERE c.id_habitacion = %s
            ORDER BY c.codigo
        """, (id_habitacion,))
        filas = cursor.fetchall()
        resultado = []
        for id_cama, codigo, estado, id_beneficiario in filas:
            estado_visible = "OCUPADA" if id_beneficiario is not None else estado
            resultado.append((id_cama, codigo, estado_visible))
        return True, resultado
    except Error as error:
        return False, str(error)
    finally:
        if cursor is not None:
            cursor.close()
        conexion.close()


def crear_cama(id_habitacion):
    conexion = conectar()
    cursor = None
    if conexion is None:
        return False, "No se pudo conectar con MySQL."
    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT h.numero
            FROM habitaciones h
            WHERE h.id_habitacion = %s
        """, (id_habitacion,))
        habitacion = cursor.fetchone()
        if habitacion is None:
            return False, "Habitación no encontrada."

        cursor.execute("""
            SELECT COUNT(*)
            FROM camas
            WHERE id_habitacion = %s
        """, (id_habitacion,))
        siguiente = int(cursor.fetchone()[0]) + 1
        numero_habitacion = habitacion[0]
        codigo = f"C-{numero_habitacion}-{siguiente:02d}"
        cursor.execute("""
            INSERT INTO camas (codigo, id_habitacion, estado)
            VALUES (%s, %s, 'HABILITADA')
        """, (codigo, id_habitacion))
        conexion.commit()
        return True, codigo
    except Error as error:
        conexion.rollback()
        return False, str(error)
    finally:
        if cursor is not None:
            cursor.close()
        conexion.close()


def cambiar_estado_cama(id_cama, nuevo_estado):
    conexion = conectar()
    cursor = None
    if conexion is None:
        return False, "No se pudo conectar con MySQL."
    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT COUNT(*)
            FROM ocupaciones
            WHERE id_cama = %s AND fecha_salida IS NULL
        """, (id_cama,))
        if cursor.fetchone()[0] > 0:
            return False, "No puedes cambiar una cama ocupada. Registra primero su salida."

        if nuevo_estado not in ("HABILITADA", "MANTENIMIENTO", "INACTIVA"):
            return False, "Estado de cama no válido."

        cursor.execute("""
            UPDATE camas SET estado = %s
            WHERE id_cama = %s
        """, (nuevo_estado, id_cama))
        conexion.commit()
        return True, None
    except Error as error:
        conexion.rollback()
        return False, str(error)
    finally:
        if cursor is not None:
            cursor.close()
        conexion.close()


def resumen_habitacion(id_habitacion):
    conexion = conectar()
    cursor = None
    if conexion is None:
        return False, "No se pudo conectar con MySQL."
    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT
                COUNT(*) AS total,
                SUM(c.estado = 'HABILITADA' AND o.id_ocupacion IS NULL) AS disponibles,
                SUM(o.id_ocupacion IS NOT NULL) AS ocupadas,
                SUM(c.estado = 'MANTENIMIENTO') AS mantenimiento,
                SUM(c.estado = 'INACTIVA') AS inactivas
            FROM camas c
            LEFT JOIN ocupaciones o
              ON o.id_cama = c.id_cama
             AND o.fecha_salida IS NULL
            WHERE c.id_habitacion = %s
        """, (id_habitacion,))
        fila = cursor.fetchone()
        return True, {
            "total": fila[0] or 0,
            "disponibles": fila[1] or 0,
            "ocupadas": fila[2] or 0,
            "mantenimiento": fila[3] or 0,
            "inactivas": fila[4] or 0,
        }
    except Error as error:
        return False, str(error)
    finally:
        if cursor is not None:
            cursor.close()
        conexion.close()