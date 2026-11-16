from mysql.connector import Error

from conexion import conectar


# Funcion que guarda un nuevo beneficiario enviado desde la vista
def guardar_registro(
    codigo,
    nombres,
    apellido_paterno,
    apellido_materno,
    tipo_documento,
    numero_documento,
    fecha_nacimiento,
    telefono,
    direccion,
    observaciones
):
    # Se solicita la conexion definida en conexion.py
    conexion = conectar()
    # Se inicializa para poder cerrarlo de forma segura al final
    cursor = None

    # Si conectar() devolvio None, no se puede continuar
    if conexion is None:
        return False, "No se pudo conectar con MySQL."

    # Intenta ejecutar el INSERT en la base de datos
    try:
        cursor = conexion.cursor()
        query = """
            INSERT IGNORE INTO beneficiarios (
                codigo,
                nombres,
                apellido_paterno,
                apellido_materno,
                tipo_documento,
                numero_documento,
                fecha_nacimiento,
                telefono,
                direccion,
                observaciones
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(
            query,
            (
                codigo,
                nombres,
                apellido_paterno,
                apellido_materno,
                tipo_documento,
                numero_documento,
                fecha_nacimiento,
                telefono,
                direccion,
                observaciones
            )
        )
        conexion.commit()
        return True, None

    # Avisa si MySQL produjo un error
    except Error as error:
        conexion.rollback()
        return False, str(error)

    # Siempre cierra el cursor y la conexion
    finally:
        if cursor is not None:
            cursor.close()
        conexion.close()


# Funcion que consulta los beneficiarios para llenar la tabla de la vista
def obtener_beneficiarios(busqueda=""):
    conexion = conectar()
    cursor = None

    if conexion is None:
        return False, "No se pudo conectar con MySQL."

    # Ejecuta la busqueda por nombre, apellido o documento
    try:
        cursor = conexion.cursor()
        query = """
            SELECT
                id_beneficiario,
                codigo,
                CONCAT_WS(
                    ' ',
                    nombres,
                    apellido_paterno,
                    apellido_materno
                ) AS nombre_completo,
                numero_documento,
                estado
            FROM beneficiarios
            WHERE nombres LIKE %s
               OR apellido_paterno LIKE %s
               OR apellido_materno LIKE %s
               OR numero_documento LIKE %s
            ORDER BY id_beneficiario DESC
        """
        texto = f"%{busqueda}%"
        cursor.execute(query, (texto, texto, texto, texto))
        return True, cursor.fetchall()

    # Devuelve el error para que la vista pueda informarlo
    except Error as error:
        return False, str(error)

    # Cierra los recursos despues de consultar
    finally:
        if cursor is not None:
            cursor.close()
        conexion.close()


# Funcion que obtiene todos los datos de un beneficiario seleccionado
def obtener_beneficiario(id_beneficiario):
    conexion = conectar()
    cursor = None

    if conexion is None:
        return False, "No se pudo conectar con MySQL."

    # Busca una sola fila usando el id interno de la tabla
    try:
        cursor = conexion.cursor()
        query = """
            SELECT
                id_beneficiario,
                codigo,
                nombres,
                apellido_paterno,
                apellido_materno,
                tipo_documento,
                numero_documento,
                fecha_nacimiento,
                telefono,
                direccion,
                observaciones
            FROM beneficiarios
            WHERE id_beneficiario = %s
        """
        cursor.execute(query, (id_beneficiario,))
        beneficiario = cursor.fetchone()

        if beneficiario is None:
            return False, "No se encontró el beneficiario seleccionado."

        return True, beneficiario

    # Devuelve el error para que la vista pueda informarlo
    except Error as error:
        return False, str(error)

    # Cierra los recursos despues de consultar
    finally:
        if cursor is not None:
            cursor.close()
        conexion.close()


# Funcion que actualiza los datos del beneficiario seleccionado
def actualizar_beneficiario(
    id_beneficiario,
    codigo,
    nombres,
    apellido_paterno,
    apellido_materno,
    tipo_documento,
    numero_documento,
    fecha_nacimiento,
    telefono,
    direccion,
    observaciones
):
    conexion = conectar()
    cursor = None

    if conexion is None:
        return False, "No se pudo conectar con MySQL."

    # Ejecuta el UPDATE usando el id del beneficiario
    try:
        cursor = conexion.cursor()
        query = """
            UPDATE beneficiarios
            SET codigo = %s,
                nombres = %s,
                apellido_paterno = %s,
                apellido_materno = %s,
                tipo_documento = %s,
                numero_documento = %s,
                fecha_nacimiento = %s,
                telefono = %s,
                direccion = %s,
                observaciones = %s
            WHERE id_beneficiario = %s
        """
        cursor.execute(
            query,
            (
                codigo,
                nombres,
                apellido_paterno,
                apellido_materno,
                tipo_documento,
                numero_documento,
                fecha_nacimiento,
                telefono,
                direccion,
                observaciones,
                id_beneficiario
            )
        )
        conexion.commit()
        return True, None

    # Deshace la operacion si MySQL produce un error
    except Error as error:
        conexion.rollback()
        return False, str(error)

    # Cierra los recursos despues de actualizar
    finally:
        if cursor is not None:
            cursor.close()
        conexion.close()


# Funcion que cambia el estado del beneficiario a RETIRADO
def retirar_beneficiario(id_beneficiario):
    conexion = conectar()
    cursor = None

    if conexion is None:
        return False, "No se pudo conectar con MySQL."

    # No elimina la fila: conserva el historial y cambia su estado
    try:
        cursor = conexion.cursor()
        query = """
            UPDATE beneficiarios
            SET estado = 'RETIRADO'
            WHERE id_beneficiario = %s
        """
        cursor.execute(query, (id_beneficiario,))
        conexion.commit()
        return True, None

    # Deshace la operacion si MySQL produce un error
    except Error as error:
        conexion.rollback()
        return False, str(error)

    # Cierra los recursos despues de actualizar
    finally:
        if cursor is not None:
            cursor.close()
        conexion.close()