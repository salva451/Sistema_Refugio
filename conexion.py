import mysql.connector
from mysql.connector import Error

def conectar():
    try:
        conexion = mysql.connector.connect(
            host="localhost",
            port=3306,
            user="root",
            password="",
            database="refugio_solidario"
        )
        return conexion

    except Error as error:
        print(f"Error de conexión: {error}")
        return None

if __name__ == "__main__":
    conexion = conectar()

    if conexion is not None:
        print("Conexión exitosa con MySQL")
        conexion.close()
    else:
        print("No se pudo conectar")