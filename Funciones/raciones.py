"""Entrega de raciones y consumo de alimentos (descuento del inventario)."""
from collections import OrderedDict
from datetime import date
from decimal import Decimal

from Funciones.inventarios import calcular_raciones_disponibles
from Funciones.utilidades import ErrorNegocio, bd, obtener_id_comedor, siguiente_codigo

COMIDAS = ("Desayuno", "Almuerzo", "Té", "Cena", "Otra")
# texto de la pantalla -> valor guardado en la columna tipo_comida de la base
MAPA_COMIDAS = {"Desayuno": "DESAYUNO", "Almuerzo": "ALMUERZO", "Té": "TE", "Cena": "CENA", "Otra": "OTRA"}


@bd
def entregadas_hoy(cur):
    cur.execute("SELECT COALESCE(SUM(cantidad), 0) AS total FROM raciones WHERE fecha_entrega = CURDATE()")
    return int(cur.fetchone()["total"])


@bd
def promedio_historico(cur, dias=7):
    """Promedio diario de raciones por tipo de comida en los ultimos 'dias' dias (incluye hoy)."""
    cur.execute(
        "SELECT tipo_comida, COALESCE(SUM(cantidad), 0) AS total FROM raciones "
        "WHERE fecha_entrega BETWEEN DATE_SUB(CURDATE(), INTERVAL %s DAY) AND CURDATE() "
        "GROUP BY tipo_comida", (dias - 1,))
    sumas = {f["tipo_comida"]: int(f["total"]) for f in cur.fetchall()}
    promedios = {t: round(sumas.get(t, 0) / dias) for t in ("DESAYUNO", "ALMUERZO", "TE", "CENA", "OTRA")}
    promedios["TOTAL"] = sum(promedios.values())
    return promedios


@bd
def alojados_activos(cur, busqueda=""):
    """Personas con una cama asignada ahora (ocupacion sin fecha de salida)."""
    texto = f"%{(busqueda or '').strip()}%"
    cur.execute(
        "SELECT b.id_beneficiario, b.codigo, "
        "CONCAT_WS(' ', b.nombres, b.apellido_paterno, b.apellido_materno) AS nombre "
        "FROM ocupaciones o JOIN beneficiarios b ON b.id_beneficiario = o.id_beneficiario "
        "WHERE o.fecha_salida IS NULL "
        "AND (b.nombres LIKE %s OR b.apellido_paterno LIKE %s OR b.codigo LIKE %s) "
        "ORDER BY nombre", (texto, texto, texto))
    return cur.fetchall()


@bd
def registrar_raciones(cur, fecha, tipo_comida, alojados, externos, observaciones, consumo):
    """Guarda la entrega y descuenta del inventario los lotes usados, todo en una transaccion.
    consumo = [(id_inventario, cantidad Decimal), ...]"""
    tipo_bd = MAPA_COMIDAS.get(tipo_comida)
    if tipo_bd is None:
        raise ErrorNegocio("Seleccione el tipo de comida.")
    if fecha is None or fecha > date.today():
        raise ErrorNegocio("La fecha de atención no puede ser futura.")
    if alojados < 0 or externos < 0:
        raise ErrorNegocio("Las cantidades no pueden ser negativas.")
    total = alojados + externos
    if total <= 0:
        raise ErrorNegocio("Ingrese al menos una ración entregada.")
    if not consumo:
        raise ErrorNegocio("Agregue los alimentos usados en la preparación.")

    # Regla: no entregar mas raciones de las que permite el inventario.
    disponibles = calcular_raciones_disponibles(cur)
    if total > disponibles:
        raise ErrorNegocio(f"No hay raciones suficientes: se intentan entregar {total} y el "
                           f"inventario permite {disponibles}.")

    # Si un lote aparece varias veces en la lista, se suman sus cantidades.
    por_lote = OrderedDict()
    for id_inventario, cantidad in consumo:
        por_lote[id_inventario] = por_lote.get(id_inventario, Decimal("0")) + Decimal(cantidad)

    for id_inventario, cantidad in por_lote.items():
        cur.execute("SELECT lote, cantidad, fecha_vencimiento FROM inventarios "
                    "WHERE id_inventario = %s FOR UPDATE", (id_inventario,))
        lote = cur.fetchone()
        if lote is None:
            raise ErrorNegocio("Uno de los lotes ya no existe.")
        if lote["fecha_vencimiento"] is not None and lote["fecha_vencimiento"] < date.today():
            raise ErrorNegocio(f"El lote {lote['lote']} está vencido y no se puede usar.")
        if Decimal(lote["cantidad"]) < cantidad:
            raise ErrorNegocio(f"Stock insuficiente en el lote {lote['lote']}: hay "
                               f"{Decimal(lote['cantidad']):.2f} y se usarían {cantidad:.2f}.")

    id_comedor = obtener_id_comedor(cur)
    codigo = siguiente_codigo(cur, "raciones", "id_racion", "RAC")
    cur.execute(
        "INSERT INTO raciones (codigo, id_comedor, fecha_entrega, tipo_comida, cantidad, "
        "cantidad_alojados, cantidad_externos, observaciones) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        (codigo, id_comedor, fecha, tipo_bd, total, alojados, externos,
         (observaciones or "").strip() or None))
    id_racion = cur.lastrowid

    for id_inventario, cantidad in por_lote.items():
        cur.execute("INSERT INTO detalle_raciones (id_racion, id_inventario, cantidad_consumida) "
                    "VALUES (%s, %s, %s)", (id_racion, id_inventario, cantidad))
        cur.execute("UPDATE inventarios SET cantidad = cantidad - %s WHERE id_inventario = %s",
                    (cantidad, id_inventario))
    return codigo
