"""Donantes y proveedores."""
from Funciones.utilidades import ErrorNegocio, bd, siguiente_codigo

TIPOS = ("PERSONA", "ORGANIZACION", "PROVEEDOR")


@bd
def listar_donantes(cur, tipos=None):
    """tipos = lista de tipos a mostrar (por ejemplo ['PROVEEDOR']); None = todos."""
    if tipos:
        marcas = ", ".join(["%s"] * len(tipos))
        cur.execute(f"SELECT id_donante, codigo, nombre, tipo, telefono FROM donantes "
                    f"WHERE tipo IN ({marcas}) ORDER BY nombre", tuple(tipos))
    else:
        cur.execute("SELECT id_donante, codigo, nombre, tipo, telefono FROM donantes ORDER BY nombre")
    return cur.fetchall()


@bd
def crear_donante(cur, nombre, tipo, telefono=""):
    nombre = (nombre or "").strip()
    if len(nombre) < 2:
        raise ErrorNegocio("El nombre debe tener al menos 2 caracteres.")
    if tipo not in TIPOS:
        raise ErrorNegocio("Seleccione un tipo válido.")
    telefono = (telefono or "").strip()
    if telefono and not telefono.replace(" ", "").replace("+", "").isdigit():
        raise ErrorNegocio("El teléfono solo puede tener números.")
    codigo = siguiente_codigo(cur, "donantes", "id_donante", "DON")
    cur.execute("INSERT INTO donantes (codigo, nombre, tipo, telefono) VALUES (%s, %s, %s, %s)",
                (codigo, nombre, tipo, telefono or None))
    return cur.lastrowid
