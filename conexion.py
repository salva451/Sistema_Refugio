import mysql.connector
from mysql.connector import Error
#Conecta la base de datos al programa python
def conectar():
    #Intenta conectarse a la base de datos
    try:
        conexion = mysql.connector.connect(
            host="localhost",
            port=3306,
            user="root",
            password="",
            database="Sistema_Refugio"
        )
        #Devuelve la variable conexion como verdadero o falso si es que se pudo conectar a la base de datos
        return conexion
#Revisa que no haya errores en la conexion
    except Error as error:
        print(f"Error de conexión: {error}")
        return None
#avisa si se pudo conectar a la base de datos o no
if __name__ == "__main__":
    conexion = conectar()

    if conexion is not None:
        print("Conexión exitosa con MySQL")
        conexion.close()
    else:
        print("No se pudo conectar")