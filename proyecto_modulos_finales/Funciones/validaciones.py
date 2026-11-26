"""Validaciones y calculos simples reutilizables (no usan la base de datos)."""
import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

# ---------------- documento de identidad ----------------
# Regla acordada: el CI se guarda como texto; los primeros caracteres deben ser
# numeros y el final debe tener letras (ej.: 1234567LP).
EXIGIR_LETRAS_EN_CI = True


def validar_documento(tipo, numero):
    """Devuelve (True, documento_normalizado) o (False, mensaje).
    Se guarda en MAYUSCULAS y sin espacios ni guiones."""
    numero = (numero or "").strip().upper().replace(" ", "").replace("-", "")
    if not numero:
        return False, "Ingrese el número de documento."
    tipo = (tipo or "").lower()
    if "carnet" in tipo:
        patron = r"\d{5,10}[A-Z]{1,3}" if EXIGIR_LETRAS_EN_CI else r"\d{5,10}[A-Z]{0,3}"
        if not re.fullmatch(patron, numero):
            return False, ("El carnet debe empezar con 5 a 10 números y terminar con "
                           "1 a 3 letras. Ejemplo: 1234567LP")
    elif "pasaporte" in tipo:
        if not re.fullmatch(r"[A-Z0-9]{5,15}", numero):
            return False, "El pasaporte debe tener de 5 a 15 letras o números, sin símbolos."
    else:
        if not re.fullmatch(r"[A-Z0-9]{3,20}", numero):
            return False, "El documento debe tener de 3 a 20 letras o números, sin símbolos."
    return True, numero


# ---------------- numeros ----------------
def validar_cantidad(texto, nombre="La cantidad", permitir_cero=False):
    """Acepta decimales con punto o coma. Devuelve (True, Decimal) o (False, mensaje)."""
    try:
        valor = Decimal(str(texto).strip().replace(",", "."))
    except (InvalidOperation, ValueError):
        return False, f"{nombre} debe ser un número."
    if not valor.is_finite():
        return False, f"{nombre} debe ser un número."
    if valor < 0 or (valor == 0 and not permitir_cero):
        return False, f"{nombre} debe ser mayor que 0."
    return True, valor.quantize(Decimal("0.01"))


def validar_entero(texto, nombre="El valor", minimo=0):
    texto = str(texto).strip()
    if texto == "":
        texto = "0"
    if not texto.isdigit():
        return False, f"{nombre} debe ser un número entero."
    valor = int(texto)
    if valor < minimo:
        return False, f"{nombre} debe ser como mínimo {minimo}."
    return True, valor


# ---------------- fechas ----------------
def texto_a_fecha(texto):
    """'25/11/2026' -> date. Lanza ValueError si no es una fecha real."""
    return datetime.strptime(texto.strip(), "%d/%m/%Y").date()


def fecha_a_texto(fecha):
    return fecha.strftime("%d/%m/%Y") if fecha else ""


def validar_fecha(texto, nombre="La fecha", obligatoria=True, permitir_futura=True):
    """Devuelve (True, date | None) o (False, mensaje)."""
    texto = (texto or "").strip()
    if not texto or texto.lower() == "dd/mm/aaaa":
        return (False, f"Complete el campo: {nombre}") if obligatoria else (True, None)
    try:
        fecha = texto_a_fecha(texto)
    except ValueError:
        return False, f"{nombre} no es una fecha válida. Use el formato dd/mm/aaaa."
    if not permitir_futura and fecha > date.today():
        return False, f"{nombre} no puede ser una fecha futura."
    return True, fecha


# ---------------- edad ----------------
RANGOS_EDAD = (
    ("Niñez (0-11)", 0, 11),
    ("Adolescencia (12-17)", 12, 17),
    ("Adultez (18-59)", 18, 59),
    ("Adulto mayor (60+)", 60, 200),
)


def calcular_edad(fecha_nacimiento, hoy=None):
    hoy = hoy or date.today()
    ya_cumplio = (hoy.month, hoy.day) >= (fecha_nacimiento.month, fecha_nacimiento.day)
    return hoy.year - fecha_nacimiento.year - (0 if ya_cumplio else 1)


def rango_edad(edad):
    for nombre, minimo, maximo in RANGOS_EDAD:
        if minimo <= edad <= maximo:
            return nombre
    return "Sin rango"
