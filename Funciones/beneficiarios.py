from mysql.connector import Error

from conexion import conectar

# Funcion que guarda los datos mandados desde la vista
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
    conexion = conectar()
    cursor = None
    # Aviso si no se pudo conectar a la base de datos
    if conexion is None:
        return False, "No se pudo conectar con MySQL."

    # Intenta guardar los datos que vienen de la vista
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

    # Avisa si ocurrio algun error
    except Error as error:
        conexion.rollback()
        return False, str(error)

    # Por ultimo se cierra la conexion a la base de datos
    finally:
        if cursor is not None:
            cursor.close()
        conexion.close()
