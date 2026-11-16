"""Logica de usuarios y login. Aqui NO hay ventanas, solo consultas y reglas."""
import hashlib
import hmac
import math
import os
from datetime import datetime, timedelta

from conexion import conectar

MAX_INTENTOS = 3
MINUTOS_BLOQUEO = 3


# ---------- contrasenas (nunca se guardan en texto plano) ----------
def hashear_password(password):
    sal = os.urandom(16)
    h = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), sal, 100_000)
    return sal.hex() + "$" + h.hex()


def verificar_password(password, almacenado):
    try:
        sal_hex, hash_hex = almacenado.split("$")
        h = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"),
                                bytes.fromhex(sal_hex), 100_000)
    except ValueError:
        return False
    return hmac.compare_digest(h.hex(), hash_hex)


def crear_usuario(nombre_usuario, password, rol="ENCARGADO"):
    con = conectar()
    try:
        cur = con.cursor()
        cur.execute(
            "INSERT INTO usuarios (nombre_usuario, password_hash, rol) VALUES (%s, %s, %s)",
            (nombre_usuario, hashear_password(password), rol),
        )
        con.commit()
    finally:
        con.close()


# ---------- login con bloqueo ----------
def _respuesta(ok, mensaje, bloqueado=False, segundos=0, usuario=None):
    return {"ok": ok, "mensaje": mensaje, "bloqueado": bloqueado,
            "segundos": segundos, "usuario": usuario}


def autenticar(nombre_usuario, password):
    """Devuelve un diccionario con:
       ok (bool), mensaje (str), bloqueado (bool), segundos (int), usuario (dict o None).
    Regla: 3 intentos fallidos -> bloqueo de 3 minutos (se guarda en la base,
    asi que cerrar y abrir el programa no salta el bloqueo)."""
    con = conectar()
    try:
        cur = con.cursor(dictionary=True)
        cur.execute("SELECT * FROM usuarios WHERE nombre_usuario = %s", (nombre_usuario,))
        u = cur.fetchone()

        # Mismo mensaje si no existe o esta inactivo: no revelar que usuarios existen.
        if u is None or not u["activo"]:
            return _respuesta(False, "Credenciales incorrectas.")

        ahora = datetime.now()
        if u["bloqueado_hasta"] and u["bloqueado_hasta"] > ahora:
            seg = math.ceil((u["bloqueado_hasta"] - ahora).total_seconds())
            return _respuesta(False, "Acceso bloqueado temporalmente.", True, seg)

        if verificar_password(password, u["password_hash"]):
            cur.execute(
                "UPDATE usuarios SET intentos_fallidos = 0, bloqueado_hasta = NULL "
                "WHERE id_usuario = %s", (u["id_usuario"],))
            con.commit()
            return _respuesta(True, "Bienvenido", usuario={
                "id": u["id_usuario"], "nombre": u["nombre_usuario"], "rol": u["rol"]})

        intentos = u["intentos_fallidos"] + 1
        if intentos >= MAX_INTENTOS:
            hasta = ahora + timedelta(minutes=MINUTOS_BLOQUEO)
            cur.execute(
                "UPDATE usuarios SET intentos_fallidos = 0, bloqueado_hasta = %s "
                "WHERE id_usuario = %s", (hasta, u["id_usuario"]))
            con.commit()
            return _respuesta(False, f"Acceso bloqueado por {MINUTOS_BLOQUEO} minutos.",
                              True, MINUTOS_BLOQUEO * 60)

        cur.execute("UPDATE usuarios SET intentos_fallidos = %s WHERE id_usuario = %s",
                    (intentos, u["id_usuario"]))
        con.commit()
        return _respuesta(False, f"Credenciales incorrectas. Intento {intentos} de {MAX_INTENTOS}.")
    finally:
        con.close()