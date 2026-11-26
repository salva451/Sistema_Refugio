"""Ingresos de alimentos: donaciones y compras (los dos suman al inventario)."""
from datetime import date
from decimal import Decimal

from Funciones.utilidades import ErrorNegocio, bd, obtener_id_comedor, siguiente_codigo

TIPOS_INGRESO = ("DONACION", "COMPRA")


@bd
def registrar_ingreso(cur, tipo_ingreso, id_donante, fecha, costo_total, observaciones, items):
    """items = [{"id_alimento", "lote", "cantidad" (Decimal), "vencimiento" (date o None)}].
    Todo se guarda en una transaccion: si algo falla, no queda nada a medias."""
    if tipo_ingreso not in TIPOS_INGRESO:
        raise ErrorNegocio("El tipo de ingreso debe ser donación o compra.")
    if not id_donante:
        raise ErrorNegocio("Seleccione el donante o proveedor.")
    if fecha is None or fecha > date.today():
        raise ErrorNegocio("La fecha del ingreso no puede ser futura.")
    if not items:
        raise ErrorNegocio("Agregue al menos un producto a la lista.")
    if tipo_ingreso == "DONACION":
        costo_total = None
    elif costo_total is not None and costo_total < 0:
        raise ErrorNegocio("El costo total no puede ser negativo.")

    id_comedor = obtener_id_comedor(cur)
    codigo = siguiente_codigo(cur, "donaciones", "id_donacion", "ING")
    cur.execute(
        "INSERT INTO donaciones (codigo, id_donante, id_comedor, fecha_donacion, observaciones, "
        "tipo_ingreso, costo_total) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (codigo, id_donante, id_comedor, fecha, (observaciones or "").strip() or None,
         tipo_ingreso, costo_total))
    id_donacion = cur.lastrowid

    for item in items:
        cantidad = Decimal(item["cantidad"])
        lote = (item["lote"] or "").strip()
        vence = item["vencimiento"]
        if cantidad <= 0:
            raise ErrorNegocio("Todas las cantidades deben ser mayores que 0.")
        if not lote:
            raise ErrorNegocio("Todos los productos necesitan un lote.")
        if vence is not None and vence < date.today():
            raise ErrorNegocio(f"El lote {lote} ya está vencido: no se puede ingresar.")

        cur.execute(
            "SELECT id_inventario, fecha_vencimiento FROM inventarios "
            "WHERE id_comedor = %s AND id_alimento = %s AND lote = %s FOR UPDATE",
            (id_comedor, item["id_alimento"], lote))
        existente = cur.fetchone()
        if existente:
            if existente["fecha_vencimiento"] != vence:
                raise ErrorNegocio(f"El lote {lote} ya existe con otra fecha de vencimiento. "
                                   "Use un código de lote distinto.")
            cur.execute("UPDATE inventarios SET cantidad = cantidad + %s WHERE id_inventario = %s",
                        (cantidad, existente["id_inventario"]))
        else:
            cur.execute(
                "INSERT INTO inventarios (codigo, id_comedor, id_alimento, lote, cantidad, "
                "fecha_vencimiento) VALUES (%s, %s, %s, %s, %s, %s)",
                (siguiente_codigo(cur, "inventarios", "id_inventario", "INV"),
                 id_comedor, item["id_alimento"], lote, cantidad, vence))
        cur.execute(
            "INSERT INTO detalle_donaciones (codigo, id_donacion, id_alimento, lote, cantidad, "
            "fecha_vencimiento) VALUES (%s, %s, %s, %s, %s, %s)",
            (siguiente_codigo(cur, "detalle_donaciones", "id_detalle", "DET"),
             id_donacion, item["id_alimento"], lote, cantidad, vence))
    return codigo


@bd
def listar_ingresos(cur, tipo=None, busqueda=""):
    texto = f"%{(busqueda or '').strip()}%"
    condicion = "AND d.tipo_ingreso = %s" if tipo else ""
    parametros = [texto, texto] + ([tipo] if tipo else [])
    cur.execute(
        "SELECT d.id_donacion, d.codigo, d.fecha_donacion AS fecha, d.tipo_ingreso AS tipo, "
        "dn.nombre AS origen, COUNT(dd.id_detalle) AS productos, d.costo_total AS costo "
        "FROM donaciones d JOIN donantes dn ON dn.id_donante = d.id_donante "
        "LEFT JOIN detalle_donaciones dd ON dd.id_donacion = d.id_donacion "
        f"WHERE (d.codigo LIKE %s OR dn.nombre LIKE %s) {condicion} "
        "GROUP BY d.id_donacion, d.codigo, d.fecha_donacion, d.tipo_ingreso, dn.nombre, d.costo_total "
        "ORDER BY d.fecha_donacion DESC, d.id_donacion DESC", tuple(parametros))
    return cur.fetchall()


@bd
def detalle_ingreso(cur, id_donacion):
    cur.execute(
        "SELECT a.nombre AS alimento, dd.lote, dd.cantidad, a.unidad, dd.fecha_vencimiento "
        "FROM detalle_donaciones dd JOIN alimentos a ON a.id_alimento = dd.id_alimento "
        "WHERE dd.id_donacion = %s ORDER BY dd.id_detalle", (id_donacion,))
    return cur.fetchall()
