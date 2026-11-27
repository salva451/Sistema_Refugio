"""Herramientas comunes de la carpeta Funciones.

@bd convierte una funcion normal en una operacion segura con la base de datos:
  - abre la conexion y le pasa el cursor como PRIMER parametro,
  - si todo sale bien hace commit y devuelve (True, resultado),
  - si algo falla hace rollback y devuelve (False, "mensaje para el usuario").
Asi todas las funciones responden igual que las de beneficiarios: (correcto, dato_o_error).
"""
import functools

from mysql.connector import Error

from conexion import conectar


class ErrorNegocio(Exception):
    """Error de una regla del sistema. Su mensaje se muestra tal cual al usuario."""


def traducir_error(error):
    """Convierte errores tecnicos de MySQL/MariaDB en mensajes entendibles."""
    codigo = getattr(error, "errno", None)
    if codigo == 1062:
        return "Ya existe un registro con esos datos (valor repetido)."
    if codigo in (1451, 1452):
        return "El registro está relacionado con otros datos o apunta a algo que no existe."
    if codigo in (3819, 4025):
        return "Alguno de los valores no es válido (fuera de rango)."
    if codigo in (1054, 1146):
        return ("La base de datos no está actualizada. Ejecute migracion_final.sql. "
                f"Detalle: {error}")
    return str(error)


def bd(funcion):
    """Decorador: ver la explicacion al inicio del archivo."""
    @functools.wraps(funcion)
    def envoltura(*args, **kwargs):
        try:
            con = conectar()
        except Error as error:
            return False, f"No se pudo conectar con la base de datos: {error}"
        if con is None:
            return False, "No se pudo conectar con MySQL."
        try:
            cur = con.cursor(dictionary=True)
            resultado = funcion(cur, *args, **kwargs)
            con.commit()
            return True, resultado
        except ErrorNegocio as error:
            con.rollback()
            return False, str(error)
        except Error as error:
            con.rollback()
            return False, traducir_error(error)
        finally:
            con.close()
    return envoltura


def siguiente_codigo(cur, tabla, columna_id, prefijo):
    """Genera codigos legibles como ALI-0007 a partir del mayor id existente."""
    cur.execute(f"SELECT COALESCE(MAX({columna_id}), 0) + 1 AS n FROM {tabla}")
    return f"{prefijo}-{int(cur.fetchone()['n']):04d}"


def obtener_id_comedor(cur):
    """El prototipo trabaja con un solo comedor: se usa el primero registrado."""
    cur.execute("SELECT id_comedor FROM comedores ORDER BY id_comedor LIMIT 1")
    fila = cur.fetchone()
    if fila is None:
        raise ErrorNegocio("No hay un comedor registrado. Ejecute migracion_final.sql.")
    return fila["id_comedor"]
