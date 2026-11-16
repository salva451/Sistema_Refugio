"""Unica puerta de entrada a MySQL.
Todos los archivos de la carpeta Funciones usan conectar() de aqui.

Cada integrante tiene su propia contrasena de MySQL, por eso los datos reales
van en config_local.py (que NO se sube a Git). Ver config_ejemplo.py.
"""
import mysql.connector

try:
    from config_local import DB_CONFIG
except ImportError:
    DB_CONFIG = {
        "host": "localhost",
        "user": "root",
        "password": "",
        "database": "albergue_solidario",
    }


def conectar():
    """Abre y devuelve una conexion nueva. Quien la pide debe cerrarla (con.close())."""
    return mysql.connector.connect(**DB_CONFIG)
