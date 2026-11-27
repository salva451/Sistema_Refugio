"""Validaciones y calculos simples reutilizables (no usan la base de datos)."""
import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

# ---------------- documento de identidad ----------------
# Regla acordada: el documento se guarda como texto.
#   Carnet de identidad: de 5 a 10 numeros al inicio y, OPCIONALMENTE, 2 letras al final
#   (extension departamental). Ejemplos: 1234567  o  1234567LP
def validar_documento(tipo, numero):
    """Devuelve (True, documento_normalizado) o (False, mensaje).
    Se guarda en MAYUSCULAS y sin espacios ni guiones."""
    numero = (numero or "").strip().upper().replace(" ", "").replace("-", "")
    if not numero:
        return False, "Ingrese el número de documento."
    tipo = (tipo or "").lower()
    if "carnet" in tipo:
        if not re.fullmatch(r"\d{5,10}([A-Z]{2})?", numero):
            return False, ("El carnet debe tener de 5 a 10 números y, si corresponde, 2 letras al "
                           "final (extensión). Ejemplos: 1234567 o 1234567LP")
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


EDAD_MAXIMA = 120      # una fecha de nacimiento mas antigua que esto no es razonable


def validar_fecha_nacimiento(texto):
    """Fecha de nacimiento OPCIONAL. Devuelve (True, date | None) o (False, mensaje).
    Rechaza fechas inexistentes, futuras o de mas de EDAD_MAXIMA anios (ej. el anio 1000)."""
    texto = (texto or "").strip()
    if not texto:
        return True, None
    if len(texto) != 10:
        return False, "La fecha debe tener el formato dd/mm/aaaa (ejemplo: 05/03/1990)."
    correcto, fecha = validar_fecha(texto, "La fecha de nacimiento", permitir_futura=False)
    if not correcto:
        return False, fecha
    if calcular_edad(fecha) > EDAD_MAXIMA:
        return False, f"La fecha de nacimiento no es razonable (más de {EDAD_MAXIMA} años)."
    return True, fecha


def formatear_fecha(texto, previo=""):
    """Da formato dd/mm/aaaa a lo que el usuario escribio: solo digitos, maximo 8,
    y una '/' despues del dia y del mes. 'previo' es el texto anterior; sirve para que
    al borrar una '/' tambien se borre el digito que la precede (si no, quedaria trabado)."""
    digitos = "".join(c for c in texto if c.isdigit())
    if len(texto) < len(previo):
        previos = "".join(c for c in previo if c.isdigit())
        if digitos and digitos == previos:      # solo se borro una "/"
            digitos = digitos[:-1]
    digitos = digitos[:8]
    resultado = digitos[:2]
    if len(digitos) >= 2:
        resultado += "/"
    resultado += digitos[2:4]
    if len(digitos) >= 4:
        resultado += "/"
    resultado += digitos[4:8]
    return resultado


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
