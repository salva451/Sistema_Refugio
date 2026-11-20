from mysql.connector import Error

from conexion import conectar


def obtener_beneficiarios_alojados():
    conexion = conectar()
    cursor = None
    if conexion is None:
        return False, "No se pudo conectar con MySQL."
    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT b.id_beneficiario,
                   b.codigo,
                   CONCAT_WS(' ', b.nombres, b.apellido_paterno, b.apellido_materno)
            FROM beneficiarios b
            LEFT JOIN ocupaciones o
              ON o.id_beneficiario = b.id_beneficiario
             AND o.fecha_salida IS NULL
            WHERE b.tipo_beneficiario = 'ALOJADO'
              AND b.estado = 'ACTIVO'
              AND o.id_ocupacion IS NULL
            ORDER BY b.nombres
        """)
        return True, cursor.fetchall()
    except Error as error:
        return False, str(error)
    finally:
        if cursor is not None:
            cursor.close()
        conexion.close()


def obtener_camas_disponibles(id_habitacion=None):
    conexion = conectar()
    cursor = None
    if conexion is None:
        return False, "No se pudo conectar con MySQL."
    try:
        cursor = conexion.cursor()
        parametros = ()
        filtro_habitacion = ""
        if id_habitacion is not None:
            filtro_habitacion = "AND c.id_habitacion = %s"
            parametros = (id_habitacion,)

        cursor.execute("""
            SELECT c.id_cama, c.codigo, h.numero
            FROM camas c
            JOIN habitaciones h ON h.id_habitacion = c.id_habitacion
            LEFT JOIN ocupaciones o
              ON o.id_cama = c.id_cama
             AND o.fecha_salida IS NULL
            WHERE c.estado = 'HABILITADA'
              AND o.id_ocupacion IS NULL
              """ + filtro_habitacion + """
            ORDER BY h.numero, c.codigo
        """, parametros)
        return True, cursor.fetchall()
    except Error as error:
        return False, str(error)
    finally:
        if cursor is not None:
            cursor.close()
        conexion.close()


def asignar(id_beneficiario, id_cama):
    conexion = conectar()
    cursor = None
    if conexion is None:
        return False, "No se pudo conectar con MySQL."
    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT tipo_beneficiario, estado
            FROM beneficiarios
            WHERE id_beneficiario = %s
        """, (id_beneficiario,))
        persona = cursor.fetchone()
        if persona is None:
            return False, "Beneficiario no encontrado."
        if persona[0] != "ALOJADO":
            return False, "Solo los beneficiarios alojados pueden ocupar camas."
        if persona[1] != "ACTIVO":
            return False, "El beneficiario está retirado."

        cursor.execute("""
            SELECT estado
            FROM camas
            WHERE id_cama = %s
        """, (id_cama,))
        cama = cursor.fetchone()
        if cama is None:
            return False, "Cama no encontrada."
        if cama[0] != "HABILITADA":
            return False, "La cama no está disponible."

        cursor.execute("""
            SELECT COUNT(*)
            FROM ocupaciones
            WHERE id_cama = %s AND fecha_salida IS NULL
        """, (id_cama,))
        if cursor.fetchone()[0] > 0:
            return False, "La cama ya está ocupada."

        cursor.execute("""
            SELECT COUNT(*)
            FROM ocupaciones
            WHERE id_beneficiario = %s AND fecha_salida IS NULL
        """, (id_beneficiario,))
        if cursor.fetchone()[0] > 0:
            return False, "El beneficiario ya tiene una ocupación activa."

        cursor.execute("SELECT COALESCE(MAX(id_ocupacion), 0) + 1 FROM ocupaciones")
        numero = int(cursor.fetchone()[0])
        cursor.execute("""
            INSERT INTO ocupaciones (codigo, id_cama, id_beneficiario)
            VALUES (%s, %s, %s)
        """, (f"O-{numero:05d}", id_cama, id_beneficiario))
        conexion.commit()
        return True, None
    except Error as error:
        conexion.rollback()
        return False, str(error)
    finally:
        if cursor is not None:
            cursor.close()
        conexion.close()


def obtener_ocupaciones_activas():
    conexion = conectar()
    cursor = None
    if conexion is None:
        return False, "No se pudo conectar con MySQL."
    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT o.id_ocupacion, o.codigo, c.codigo, h.numero,
                   CONCAT_WS(' ', b.nombres, b.apellido_paterno, b.apellido_materno),
                   o.fecha_ingreso
            FROM ocupaciones o
            JOIN camas c ON c.id_cama = o.id_cama
            JOIN habitaciones h ON h.id_habitacion = c.id_habitacion
            JOIN beneficiarios b ON b.id_beneficiario = o.id_beneficiario
            WHERE o.fecha_salida IS NULL
            ORDER BY o.fecha_ingreso DESC
        """)
        return True, cursor.fetchall()
    except Error as error:
        return False, str(error)
    finally:
        if cursor is not None:
            cursor.close()
        conexion.close()


def cupos():
    conexion = conectar()
    cursor = None
    if conexion is None:
        return {
            "capacidad_maxima": 0,
            "total_camas": 0,
            "camas_ocupadas": 0,
            "camas_disponibles": 0,
        }
    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT capacidad_maxima,
                   total_camas,
                   camas_ocupadas,
                   camas_disponibles
            FROM vista_ocupacion_albergue
            LIMIT 1
        """)
        fila = cursor.fetchone()
        if fila is None:
            return {
                "capacidad_maxima": 0,
                "total_camas": 0,
                "camas_ocupadas": 0,
                "camas_disponibles": 0,
            }
        return {
            "capacidad_maxima": fila[0],
            "total_camas": fila[1],
            "camas_ocupadas": fila[2],
            "camas_disponibles": fila[3],
        }
    except Error:
        return {
            "capacidad_maxima": 0,
            "total_camas": 0,
            "camas_ocupadas": 0,
            "camas_disponibles": 0,
        }
    finally:
        if cursor is not None:
            cursor.close()
        conexion.close()


def registrar_salida(id_ocupacion):
    conexion = conectar()
    cursor = None
    if conexion is None:
        return False, "No se pudo conectar con MySQL."
    try:
        cursor = conexion.cursor()
        cursor.execute("""
            UPDATE ocupaciones
            SET fecha_salida = CURRENT_TIMESTAMP
            WHERE id_ocupacion = %s AND fecha_salida IS NULL
        """, (id_ocupacion,))
        conexion.commit()
        return True, None
    except Error as error:
        conexion.rollback()
        return False, str(error)
    finally:
        if cursor is not None:
            cursor.close()
        conexion.close()