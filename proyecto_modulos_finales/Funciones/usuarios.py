"""Logica de usuarios, login con bloqueo y registro de accesos.
Aqui NO hay ventanas, solo consultas y reglas."""
import hashlib
import hmac
import math
import os
import re
from datetime import datetime, timedelta

from mysql.connector import Error

from conexion import conectar
from Funciones.utilidades import ErrorNegocio, bd

MAX_INTENTOS = 3
MINUTOS_BLOQUEO = 3
ROLES = ("ADMINISTRADOR", "ENCARGADO")


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
    """Usada por crear_admin.py (sin validaciones de pantalla)."""
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


# ---------- registro de accesos ----------
def _registrar_acceso(con, id_usuario, nombre_usuario, resultado):
    """Guarda fecha y hora de cada intento de ingreso. Si la tabla accesos todavia no existe,
    el login sigue funcionando (simplemente no se registra)."""
    try:
        cur = con.cursor()
        cur.execute("INSERT INTO accesos (id_usuario, nombre_usuario, resultado) VALUES (%s, %s, %s)",
                    (id_usuario, nombre_usuario[:50], resultado))
        con.commit()
    except Error:
        con.rollback()


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
            _registrar_acceso(con, u["id_usuario"] if u else None, nombre_usuario, "FALLIDO")
            return _respuesta(False, "Credenciales incorrectas.")

        ahora = datetime.now()
        if u["bloqueado_hasta"] and u["bloqueado_hasta"] > ahora:
            seg = math.ceil((u["bloqueado_hasta"] - ahora).total_seconds())
            _registrar_acceso(con, u["id_usuario"], nombre_usuario, "BLOQUEADO")
            return _respuesta(False, "Acceso bloqueado temporalmente.", True, seg)

        if verificar_password(password, u["password_hash"]):
            cur.execute(
                "UPDATE usuarios SET intentos_fallidos = 0, bloqueado_hasta = NULL "
                "WHERE id_usuario = %s", (u["id_usuario"],))
            con.commit()
            _registrar_acceso(con, u["id_usuario"], nombre_usuario, "EXITOSO")
            return _respuesta(True, "Bienvenido", usuario={
                "id": u["id_usuario"], "nombre": u["nombre_usuario"], "rol": u["rol"]})

        intentos = u["intentos_fallidos"] + 1
        _registrar_acceso(con, u["id_usuario"], nombre_usuario, "FALLIDO")
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


# ---------- administracion de usuarios (solo administrador) ----------
@bd
def listar_usuarios(cur):
    cur.execute("SELECT id_usuario, nombre_usuario, rol, activo FROM usuarios ORDER BY nombre_usuario")
    return cur.fetchall()


@bd
def registrar_usuario(cur, nombre_usuario, password, rol):
    nombre_usuario = (nombre_usuario or "").strip()
    if not re.fullmatch(r"[A-Za-z0-9_.]{3,30}", nombre_usuario):
        raise ErrorNegocio("El usuario debe tener de 3 a 30 letras, números, punto o guion bajo.")
    if len(password or "") < 4:
        raise ErrorNegocio("La contraseña debe tener al menos 4 caracteres.")
    if rol not in ROLES:
        raise ErrorNegocio("Seleccione un rol válido.")
    cur.execute("SELECT 1 FROM usuarios WHERE nombre_usuario = %s", (nombre_usuario,))
    if cur.fetchone():
        raise ErrorNegocio("Ese nombre de usuario ya existe.")
    cur.execute("INSERT INTO usuarios (nombre_usuario, password_hash, rol) VALUES (%s, %s, %s)",
                (nombre_usuario, hashear_password(password), rol))
    return None


@bd
def cambiar_estado_usuario(cur, id_usuario, activo, id_usuario_actual):
    if id_usuario == id_usuario_actual and not activo:
        raise ErrorNegocio("No puedes desactivar tu propio usuario.")
    cur.execute("UPDATE usuarios SET activo = %s WHERE id_usuario = %s", (1 if activo else 0, id_usuario))
    return None


@bd
def listar_accesos(cur, desde, hasta):
    cur.execute(
        "SELECT fecha_hora, nombre_usuario, resultado FROM accesos "
        "WHERE DATE(fecha_hora) BETWEEN %s AND %s ORDER BY fecha_hora DESC LIMIT 500", (desde, hasta))
    return cur.fetchall()
