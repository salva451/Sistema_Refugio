"""Ejecutar UNA sola vez por computadora:  python crear_admin.py
Crea el usuario de prueba  admin / 1234  en la tabla usuarios."""
import mysql.connector
from Funciones.usuarios import crear_usuario

try:
    crear_usuario("admin", "1234", "ADMINISTRADOR")
    print("Usuario creado -> usuario: admin | contrasena: 1234")
except mysql.connector.IntegrityError:
    print("El usuario admin ya existe. No se hizo ningun cambio.")
except mysql.connector.Error as error:
    print("No se pudo conectar o escribir en la base de datos:", error)