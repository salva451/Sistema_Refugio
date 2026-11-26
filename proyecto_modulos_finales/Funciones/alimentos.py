"""Catalogo de alimentos."""
from Funciones.utilidades import ErrorNegocio, bd, siguiente_codigo
from Funciones.validaciones import validar_cantidad

UNIDADES = ("kg", "litros", "unidades")
CATEGORIAS = ("Cereales", "Lácteos", "Carnes", "Verduras y frutas", "Legumbres",
              "Panadería", "Bebidas", "Otros")


def _validar(nombre, categoria, unidad, raciones_por_unidad):
    nombre = (nombre or "").strip()
    if len(nombre) < 2:
        raise ErrorNegocio("El nombre del alimento debe tener al menos 2 caracteres.")
    if unidad not in UNIDADES:
        raise ErrorNegocio("Seleccione una unidad válida (kg, litros o unidades).")
    ok, raciones = validar_cantidad(raciones_por_unidad, "Las raciones por unidad")
    if not ok:
        raise ErrorNegocio(raciones)
    return nombre, (categoria or "Otros"), unidad, raciones


@bd
def listar_alimentos(cur, busqueda=""):
    texto = f"%{(busqueda or '').strip()}%"
    cur.execute(
        "SELECT id_alimento, codigo, nombre, categoria, unidad, raciones_por_unidad "
        "FROM alimentos WHERE nombre LIKE %s OR codigo LIKE %s ORDER BY nombre",
        (texto, texto))
    return cur.fetchall()


@bd
def obtener_alimento(cur, id_alimento):
    cur.execute(
        "SELECT id_alimento, codigo, nombre, categoria, unidad, raciones_por_unidad "
        "FROM alimentos WHERE id_alimento = %s", (id_alimento,))
    fila = cur.fetchone()
    if fila is None:
        raise ErrorNegocio("No se encontró el alimento seleccionado.")
    return fila


@bd
def crear_alimento(cur, nombre, categoria, unidad, raciones_por_unidad):
    nombre, categoria, unidad, raciones = _validar(nombre, categoria, unidad, raciones_por_unidad)
    cur.execute("SELECT 1 FROM alimentos WHERE nombre = %s", (nombre,))
    if cur.fetchone():
        raise ErrorNegocio("Ya existe un alimento con ese nombre.")
    codigo = siguiente_codigo(cur, "alimentos", "id_alimento", "ALI")
    cur.execute(
        "INSERT INTO alimentos (codigo, nombre, categoria, unidad, raciones_por_unidad) "
        "VALUES (%s, %s, %s, %s, %s)", (codigo, nombre, categoria, unidad, raciones))
    return codigo


@bd
def actualizar_alimento(cur, id_alimento, nombre, categoria, unidad, raciones_por_unidad):
    nombre, categoria, unidad, raciones = _validar(nombre, categoria, unidad, raciones_por_unidad)
    cur.execute("SELECT 1 FROM alimentos WHERE nombre = %s AND id_alimento <> %s",
                (nombre, id_alimento))
    if cur.fetchone():
        raise ErrorNegocio("Ya existe otro alimento con ese nombre.")
    cur.execute(
        "UPDATE alimentos SET nombre = %s, categoria = %s, unidad = %s, "
        "raciones_por_unidad = %s WHERE id_alimento = %s",
        (nombre, categoria, unidad, raciones, id_alimento))
    return None
