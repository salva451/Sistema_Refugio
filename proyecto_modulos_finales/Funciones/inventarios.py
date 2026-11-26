"""Inventario por lotes: existencias, alertas de vencimiento y reparto FEFO
(FEFO = primero vence, primero sale)."""
from decimal import Decimal

from Funciones.utilidades import ErrorNegocio, bd

DIAS_ALERTA = 30     # desde cuantos dias antes se avisa "por vencer"
DIAS_URGENTE = 7

ESTADO_AGOTADO = "AGOTADO"
ESTADO_VENCIDO = "VENCIDO"
ESTADO_URGENTE = "VENCE EN 7 DÍAS O MENOS"
ESTADO_POR_VENCER = "POR VENCER"
ESTADO_VIGENTE = "VIGENTE"
ESTADOS_RIESGO = (ESTADO_VENCIDO, ESTADO_URGENTE, ESTADO_POR_VENCER)

FILTROS = {
    "Todos": None,
    "Por vencer": (ESTADO_URGENTE, ESTADO_POR_VENCER),
    "Vencidos": (ESTADO_VENCIDO,),
    "Agotados": (ESTADO_AGOTADO,),
    "Vigentes": (ESTADO_VIGENTE,),
}


def estado_lote(cantidad, dias):
    """dias = dias que faltan para vencer (negativo si ya vencio, None si no vence)."""
    if cantidad <= 0:
        return ESTADO_AGOTADO
    if dias is None:
        return ESTADO_VIGENTE
    if dias < 0:
        return ESTADO_VENCIDO
    if dias <= DIAS_URGENTE:
        return ESTADO_URGENTE
    if dias <= DIAS_ALERTA:
        return ESTADO_POR_VENCER
    return ESTADO_VIGENTE


def repartir_fefo(lotes, cantidad):
    """lotes: lista de dicts YA ordenada (los que vencen antes, primero).
    Devuelve [(lote, cantidad_a_usar), ...]. Lanza ErrorNegocio si no alcanza."""
    restante = Decimal(cantidad)
    disponible = sum((Decimal(l["cantidad"]) for l in lotes), Decimal("0"))
    if disponible < restante:
        raise ErrorNegocio(f"Stock insuficiente: hay {disponible:.2f} disponibles y "
                           f"se necesitan {restante:.2f}.")
    resultado = []
    for lote in lotes:
        if restante <= 0:
            break
        usar = min(Decimal(lote["cantidad"]), restante)
        if usar > 0:
            resultado.append((lote, usar))
            restante -= usar
    return resultado


# ---------------- consultas ----------------
@bd
def listar_lotes(cur, busqueda="", estado="Todos"):
    texto = f"%{(busqueda or '').strip()}%"
    cur.execute(
        "SELECT i.id_inventario, i.codigo, a.nombre AS alimento, i.lote, i.cantidad, a.unidad, "
        "i.fecha_vencimiento, DATEDIFF(i.fecha_vencimiento, CURDATE()) AS dias "
        "FROM inventarios i JOIN alimentos a ON a.id_alimento = i.id_alimento "
        "WHERE a.nombre LIKE %s OR i.lote LIKE %s "
        "ORDER BY (i.fecha_vencimiento IS NULL), i.fecha_vencimiento, a.nombre",
        (texto, texto))
    filas = cur.fetchall()
    for fila in filas:
        fila["estado"] = estado_lote(fila["cantidad"], fila["dias"])
    permitidos = FILTROS.get(estado)
    if permitidos:
        filas = [f for f in filas if f["estado"] in permitidos]
    return filas


@bd
def contar_por_vencer(cur, dias=DIAS_ALERTA):
    """Lotes con stock que vencen dentro de 'dias' (o que ya vencieron)."""
    cur.execute(
        "SELECT COUNT(*) AS total FROM inventarios "
        "WHERE cantidad > 0 AND fecha_vencimiento IS NOT NULL "
        "AND fecha_vencimiento <= DATE_ADD(CURDATE(), INTERVAL %s DAY)", (dias,))
    return int(cur.fetchone()["total"])


def calcular_raciones_disponibles(cur):
    """Suma de (cantidad x raciones por unidad) de los lotes NO vencidos."""
    cur.execute(
        "SELECT COALESCE(SUM(i.cantidad * a.raciones_por_unidad), 0) AS total "
        "FROM inventarios i JOIN alimentos a ON a.id_alimento = i.id_alimento "
        "WHERE i.cantidad > 0 AND (i.fecha_vencimiento IS NULL OR i.fecha_vencimiento >= CURDATE())")
    return int(cur.fetchone()["total"])


raciones_disponibles = bd(calcular_raciones_disponibles)


@bd
def stock_por_alimento(cur):
    """Stock utilizable (sin lotes vencidos) de cada alimento del catalogo."""
    cur.execute(
        "SELECT a.id_alimento, a.nombre, a.unidad, "
        "COALESCE(SUM(CASE WHEN i.fecha_vencimiento IS NULL OR i.fecha_vencimiento >= CURDATE() "
        "THEN i.cantidad ELSE 0 END), 0) AS stock "
        "FROM alimentos a LEFT JOIN inventarios i ON i.id_alimento = a.id_alimento "
        "GROUP BY a.id_alimento, a.nombre, a.unidad ORDER BY a.nombre")
    return cur.fetchall()


def _lotes_fefo(cur, id_alimento):
    cur.execute(
        "SELECT id_inventario, codigo, lote, cantidad, fecha_vencimiento FROM inventarios "
        "WHERE id_alimento = %s AND cantidad > 0 "
        "AND (fecha_vencimiento IS NULL OR fecha_vencimiento >= CURDATE()) "
        "ORDER BY (fecha_vencimiento IS NULL), fecha_vencimiento, id_inventario", (id_alimento,))
    return cur.fetchall()


lotes_alimento = bd(_lotes_fefo)


@bd
def sugerir_lotes(cur, id_alimento, cantidad, reservado=None):
    """Propone de que lotes sacar 'cantidad' (FEFO).
    reservado = {id_inventario: cantidad} ya agregada a la lista en pantalla."""
    reservado = reservado or {}
    lotes = _lotes_fefo(cur, id_alimento)
    for lote in lotes:
        lote["cantidad"] = Decimal(lote["cantidad"]) - Decimal(reservado.get(lote["id_inventario"], 0))
    lotes = [l for l in lotes if l["cantidad"] > 0]
    return repartir_fefo(lotes, cantidad)
