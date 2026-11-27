"""Los 5 reportes del sistema. Cada funcion reporte_*() consulta la base y devuelve
(True, datos) con esta forma:
    {"columnas": [...], "filas": [[...], ...],
     "indicadores": [("Nombre", "valor"), ...],
     "grafica": {"tipo": "barras" | "lineas", "titulo": ..., "x": [...], "y": "...",
                 "series": {"Nombre": [valores]}}}
Los calculos estadisticos estan en las funciones armar_*(), que no usan la base de datos.
"""
import csv
from collections import Counter, OrderedDict
from datetime import date, datetime, timedelta

from Funciones.estadistica import porcentaje, promedio
from Funciones.inventarios import ESTADOS_RIESGO, estado_lote
from Funciones.utilidades import bd
from Funciones.validaciones import RANGOS_EDAD, calcular_edad, rango_edad

PERIODOS = ("Hoy", "Últimos 7 días", "Últimos 30 días", "Todo el historial", "Personalizado")
TIPOS_REPORTE = ("Ocupación", "Inventario y vencimientos", "Ingresos de alimentos",
                 "Raciones entregadas", "Edades")


def rango_periodo(nombre, hoy=None):
    """Devuelve (desde, hasta) del periodo elegido; None si es 'Personalizado'."""
    hoy = hoy or date.today()
    if nombre == "Hoy":
        return hoy, hoy
    if nombre == "Últimos 7 días":
        return hoy - timedelta(days=6), hoy
    if nombre == "Últimos 30 días":
        return hoy - timedelta(days=29), hoy
    if nombre == "Todo el historial":
        return date(2000, 1, 1), hoy
    return None


def dias_del_rango(desde, hasta):
    return [desde + timedelta(days=i) for i in range((hasta - desde).days + 1)]


def _dia(fecha):
    return fecha.strftime("%d/%m/%Y") if fecha else ""


def _grafica(tipo, titulo, x, y, series):
    return {"tipo": tipo, "titulo": titulo, "x": x, "y": y, "series": series}


# =====================================================================
# 1) OCUPACION
# =====================================================================
def armar_reporte_ocupacion(filas, vista, ahora=None):
    """Tasa de ocupacion = ocupadas / habilitadas x 100.
    Estadia promedio = suma de dias de las estadias cerradas / numero de estadias cerradas."""
    ahora = ahora or datetime.now()
    tabla, estadias = [], []
    for f in filas:
        ingreso, salida = f["fecha_ingreso"], f["fecha_salida"]
        if salida:
            dias = (salida - ingreso).total_seconds() / 86400
            estadias.append(dias)
        else:
            dias = (ahora - ingreso).total_seconds() / 86400
        tabla.append([f["codigo"], f["persona"], f["cama"], ingreso.strftime("%d/%m/%Y %H:%M"),
                      salida.strftime("%d/%m/%Y %H:%M") if salida else "En curso", f"{dias:.1f}"])
    ocupadas, habilitadas = int(vista["camas_ocupadas"]), int(vista["camas_habilitadas"])
    por_dia = Counter(f["fecha_ingreso"].date() for f in filas)
    fechas = sorted(por_dia)
    return {
        "columnas": ["Código", "Persona", "Cama", "Ingreso", "Salida", "Días de estadía"],
        "filas": tabla,
        "indicadores": [
            ("Tasa de ocupación actual",
             f"{porcentaje(ocupadas, habilitadas):.1f} %  ({ocupadas} de {habilitadas} camas habilitadas)"),
            ("Estadía promedio (estadías cerradas)", f"{promedio(estadias):.1f} días  ({len(estadias)} estadías)"),
            ("Ingresos en el periodo", str(len(filas))),
        ],
        "grafica": _grafica("barras", "Ingresos por día", [d.strftime("%d/%m") for d in fechas],
                            "Personas ingresadas", {"Ingresos": [por_dia[d] for d in fechas]}),
    }


@bd
def reporte_ocupacion(cur, desde, hasta):
    cur.execute(
        "SELECT o.codigo, CONCAT_WS(' ', b.nombres, b.apellido_paterno, b.apellido_materno) AS persona, "
        "c.codigo AS cama, o.fecha_ingreso, o.fecha_salida "
        "FROM ocupaciones o JOIN beneficiarios b ON b.id_beneficiario = o.id_beneficiario "
        "JOIN camas c ON c.id_cama = o.id_cama "
        "WHERE DATE(o.fecha_ingreso) BETWEEN %s AND %s ORDER BY o.fecha_ingreso", (desde, hasta))
    filas = cur.fetchall()
    cur.execute("SELECT camas_ocupadas, camas_habilitadas FROM vista_ocupacion_albergue LIMIT 1")
    vista = cur.fetchone() or {"camas_ocupadas": 0, "camas_habilitadas": 0}
    return armar_reporte_ocupacion(filas, vista)


# =====================================================================
# 2) INVENTARIO Y VENCIMIENTOS
# =====================================================================
def armar_reporte_inventario(filas):
    """% de lotes por vencer = lotes por vencer o vencidos / lotes con stock x 100."""
    tabla, riesgo, stock = [], 0, OrderedDict()
    for f in filas:
        estado = estado_lote(f["cantidad"], f["dias"])
        if estado in ESTADOS_RIESGO:
            riesgo += 1
        tabla.append([f["alimento"], f["lote"], f"{f['cantidad']:.2f}", f["unidad"],
                      _dia(f["fecha_vencimiento"]) or "Sin vencimiento",
                      "" if f["dias"] is None else f["dias"], estado])
        nombre = f"{f['alimento']} ({f['unidad']})"
        stock[nombre] = stock.get(nombre, 0) + float(f["cantidad"])
    total = len(filas)
    return {
        "columnas": ["Alimento", "Lote", "Cantidad", "Unidad", "Vencimiento", "Días restantes", "Estado"],
        "filas": tabla,
        "indicadores": [
            ("Lotes con stock", str(total)),
            ("Lotes por vencer o vencidos", str(riesgo)),
            ("% de lotes por vencer o vencidos", f"{porcentaje(riesgo, total):.1f} %"),
        ],
        "grafica": _grafica("barras", "Stock actual por alimento", list(stock.keys()),
                            "Cantidad (según unidad)", {"Stock": list(stock.values())}),
    }


@bd
def reporte_inventario(cur):
    cur.execute(
        "SELECT a.nombre AS alimento, i.lote, i.cantidad, a.unidad, i.fecha_vencimiento, "
        "DATEDIFF(i.fecha_vencimiento, CURDATE()) AS dias "
        "FROM inventarios i JOIN alimentos a ON a.id_alimento = i.id_alimento WHERE i.cantidad > 0 "
        "ORDER BY (i.fecha_vencimiento IS NULL), i.fecha_vencimiento, a.nombre")
    return armar_reporte_inventario(cur.fetchall())


# =====================================================================
# 3) INGRESOS DE ALIMENTOS (donaciones y compras)
# =====================================================================
def armar_reporte_ingresos(filas):
    """Promedio por ingreso = cantidad total ingresada / numero de ingresos.
    % de donaciones = donaciones / total de ingresos x 100."""
    n = len(filas)
    donaciones = sum(1 for f in filas if f["tipo"] == "DONACION")
    cantidad_total = sum(float(f["cantidad"]) for f in filas)
    gasto = sum(float(f["costo"]) for f in filas if f["costo"] is not None)
    tabla = [[f["codigo"], _dia(f["fecha"]), "Donación" if f["tipo"] == "DONACION" else "Compra",
              f["origen"], f["productos"], f"{float(f['cantidad']):.2f}",
              "" if f["costo"] is None else f"{float(f['costo']):.2f}"] for f in filas]
    fechas = sorted({f["fecha"] for f in filas})
    serie = {"Donación": [], "Compra": []}
    for d in fechas:
        serie["Donación"].append(sum(float(f["cantidad"]) for f in filas if f["fecha"] == d and f["tipo"] == "DONACION"))
        serie["Compra"].append(sum(float(f["cantidad"]) for f in filas if f["fecha"] == d and f["tipo"] == "COMPRA"))
    return {
        "columnas": ["Código", "Fecha", "Tipo", "Donante / Proveedor", "Productos", "Cantidad total", "Costo (Bs.)"],
        "filas": tabla,
        "indicadores": [
            ("Ingresos en el periodo", f"{n}  ({donaciones} donaciones y {n - donaciones} compras)"),
            ("Promedio de cantidad por ingreso", f"{promedio([float(f['cantidad']) for f in filas]):.1f}"),
            ("% de donaciones", f"{porcentaje(donaciones, n):.1f} %"),
            ("Gasto total en compras", f"Bs. {gasto:.2f}"),
        ],
        "grafica": _grafica("barras", "Cantidad ingresada por fecha", [d.strftime("%d/%m") for d in fechas],
                            "Cantidad ingresada", serie),
    }


@bd
def reporte_ingresos(cur, desde, hasta):
    cur.execute(
        "SELECT d.codigo, d.fecha_donacion AS fecha, d.tipo_ingreso AS tipo, dn.nombre AS origen, "
        "COUNT(dd.id_detalle) AS productos, COALESCE(SUM(dd.cantidad), 0) AS cantidad, d.costo_total AS costo "
        "FROM donaciones d JOIN donantes dn ON dn.id_donante = d.id_donante "
        "JOIN detalle_donaciones dd ON dd.id_donacion = d.id_donacion "
        "WHERE d.fecha_donacion BETWEEN %s AND %s "
        "GROUP BY d.id_donacion, d.codigo, d.fecha_donacion, d.tipo_ingreso, dn.nombre, d.costo_total "
        "ORDER BY d.fecha_donacion, d.id_donacion", (desde, hasta))
    return armar_reporte_ingresos(cur.fetchall())


# =====================================================================
# 4) RACIONES ENTREGADAS
# =====================================================================
def armar_reporte_raciones(filas, desde, hasta):
    """Promedio diario = suma de raciones / numero de dias del periodo.
    % de alojados = raciones a alojados / total de raciones x 100."""
    dias = dias_del_rango(desde, hasta)
    total = sum(f["total"] for f in filas)
    alojados = sum(f["alojados"] for f in filas)
    por_dia = Counter()
    for f in filas:
        por_dia[f["fecha"]] += f["total"]
    mayor = max(por_dia.items(), key=lambda par: par[1]) if por_dia else None
    ejes = dias if len(dias) <= 62 else sorted(por_dia)
    nombres = {"DESAYUNO": "Desayuno", "ALMUERZO": "Almuerzo", "TE": "Té", "CENA": "Cena", "OTRA": "Otra"}
    return {
        "columnas": ["Código", "Fecha", "Comida", "Alojados", "Externos", "Total"],
        "filas": [[f["codigo"], _dia(f["fecha"]), nombres.get(f["comida"], f["comida"]),
                   f["alojados"], f["externos"], f["total"]] for f in filas],
        "indicadores": [
            ("Total de raciones entregadas", str(total)),
            ("Promedio diario", f"{total / len(dias):.1f} raciones por día  ({len(dias)} días)"),
            ("% de alojados", f"{porcentaje(alojados, total):.1f} %"),
            ("Día de mayor entrega", f"{_dia(mayor[0])} ({mayor[1]} raciones)" if mayor else "Sin datos"),
        ],
        "grafica": _grafica("lineas", "Raciones entregadas por día", [d.strftime("%d/%m") for d in ejes],
                            "Raciones", {"Total": [por_dia.get(d, 0) for d in ejes]}),
    }


@bd
def reporte_raciones(cur, desde, hasta):
    cur.execute(
        "SELECT codigo, fecha_entrega AS fecha, tipo_comida AS comida, cantidad_alojados AS alojados, "
        "cantidad_externos AS externos, cantidad AS total FROM raciones "
        "WHERE fecha_entrega BETWEEN %s AND %s ORDER BY fecha_entrega, id_racion", (desde, hasta))
    return armar_reporte_raciones(cur.fetchall(), desde, hasta)


# =====================================================================
# 5) EDADES
# =====================================================================
def armar_reporte_edades(filas, hoy=None):
    """% por rango = personas del rango / personas con fecha de nacimiento x 100.
    Edad promedio = suma de edades / numero de personas."""
    con_fecha = [f for f in filas if f["fecha_nacimiento"]]
    sin_fecha = len(filas) - len(con_fecha)
    tabla, edades, conteo = [], [], OrderedDict((r[0], 0) for r in RANGOS_EDAD)
    for f in con_fecha:
        edad = calcular_edad(f["fecha_nacimiento"], hoy)
        rango = rango_edad(edad)
        edades.append(edad)
        conteo[rango] = conteo.get(rango, 0) + 1
        tabla.append([f["codigo"], f["nombre"], _dia(f["fecha_nacimiento"]), edad, rango])
    n = len(con_fecha)
    indicadores = [("Personas incluidas", f"{n}"), ("Edad promedio", f"{promedio(edades):.1f} años")]
    indicadores += [(f"% {rango}", f"{porcentaje(c, n):.1f} %  ({c})") for rango, c in conteo.items()]
    indicadores.append(("Sin fecha de nacimiento (no incluidas)", str(sin_fecha)))
    return {
        "columnas": ["Código", "Persona", "Fecha de nacimiento", "Edad", "Rango"],
        "filas": tabla,
        "indicadores": indicadores,
        "grafica": _grafica("barras", "Personas por rango de edad", list(conteo.keys()),
                            "Personas", {"Personas": list(conteo.values())}),
    }


@bd
def reporte_edades(cur, desde, hasta):
    cur.execute(
        "SELECT codigo, CONCAT_WS(' ', nombres, apellido_paterno, apellido_materno) AS nombre, "
        "fecha_nacimiento FROM beneficiarios "
        "WHERE estado = 'ACTIVO' AND fecha_registro BETWEEN %s AND %s ORDER BY apellido_paterno, nombres",
        (desde, hasta))
    return armar_reporte_edades(cur.fetchall())


# =====================================================================
# EXPORTAR
# =====================================================================
def exportar_csv(columnas, filas, ruta):
    """Guarda la tabla del reporte en un CSV (separado por ';' para que Excel lo abra bien)."""
    try:
        with open(ruta, "w", newline="", encoding="utf-8-sig") as archivo:
            escritor = csv.writer(archivo, delimiter=";")
            escritor.writerow(columnas)
            escritor.writerows(filas)
        return True, ruta
    except OSError as error:
        return False, f"No se pudo guardar el archivo: {error}"
