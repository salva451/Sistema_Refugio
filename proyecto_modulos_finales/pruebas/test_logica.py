"""Pruebas de la logica que NO usa la base de datos.
Ejecutar desde la carpeta raiz:   python -m unittest pruebas.test_logica -v"""
import csv
import os
import tempfile
import unittest
from datetime import date, datetime
from decimal import Decimal

from Funciones import inventarios, reportes
from Funciones.estadistica import porcentaje, promedio
from Funciones.utilidades import ErrorNegocio
from Funciones.validaciones import (calcular_edad, rango_edad, validar_cantidad,
                                    validar_documento, validar_entero, validar_fecha)


class TestValidaciones(unittest.TestCase):
    def test_ci_valido(self):
        self.assertEqual(validar_documento("Carnet de identidad", "1234567LP"), (True, "1234567LP"))
        self.assertEqual(validar_documento("Carnet de identidad", " 1234567 lp ")[1], "1234567LP")
        self.assertEqual(validar_documento("Carnet de identidad", "1234567-1A")[1], "12345671A")

    def test_ci_invalido(self):
        for malo in ("1234567", "LP1234567", "12AB34LP", "123LP", "12345678901LP", "1234567LPAB"):
            self.assertFalse(validar_documento("Carnet de identidad", malo)[0], malo)

    def test_otros_documentos(self):
        self.assertTrue(validar_documento("Pasaporte", "AB123456")[0])
        self.assertFalse(validar_documento("Pasaporte", "AB-12")[0])
        self.assertTrue(validar_documento("Otro", "XYZ99")[0])
        self.assertFalse(validar_documento("Otro", "")[0])

    def test_cantidad(self):
        self.assertEqual(validar_cantidad("2,5"), (True, Decimal("2.50")))
        for malo in ("", "abc", "0", "-3", "nan", "inf"):
            self.assertFalse(validar_cantidad(malo)[0], malo)
        self.assertTrue(validar_cantidad("0", permitir_cero=True)[0])

    def test_entero(self):
        self.assertEqual(validar_entero("12"), (True, 12))
        self.assertEqual(validar_entero(""), (True, 0))
        self.assertFalse(validar_entero("1.5")[0])
        self.assertFalse(validar_entero("-2")[0])

    def test_fecha(self):
        self.assertEqual(validar_fecha("25/11/2026"), (True, date(2026, 11, 25)))
        self.assertFalse(validar_fecha("31/02/2026")[0])
        self.assertFalse(validar_fecha("2026-11-25")[0])
        self.assertFalse(validar_fecha("01/01/2999", permitir_futura=False)[0])
        self.assertEqual(validar_fecha("", obligatoria=False), (True, None))

    def test_edad_y_rango(self):
        self.assertEqual(calcular_edad(date(2000, 6, 15), date(2026, 6, 14)), 25)
        self.assertEqual(calcular_edad(date(2000, 6, 15), date(2026, 6, 15)), 26)
        self.assertEqual([rango_edad(e) for e in (0, 11, 12, 17, 18, 59, 60, 90)],
                         ["Niñez (0-11)", "Niñez (0-11)", "Adolescencia (12-17)", "Adolescencia (12-17)",
                          "Adultez (18-59)", "Adultez (18-59)", "Adulto mayor (60+)", "Adulto mayor (60+)"])


class TestInventario(unittest.TestCase):
    def test_estados(self):
        e = inventarios.estado_lote
        self.assertEqual(e(Decimal("0"), 50), inventarios.ESTADO_AGOTADO)
        self.assertEqual(e(Decimal("5"), None), inventarios.ESTADO_VIGENTE)
        self.assertEqual(e(Decimal("5"), -1), inventarios.ESTADO_VENCIDO)
        self.assertEqual(e(Decimal("5"), 7), inventarios.ESTADO_URGENTE)
        self.assertEqual(e(Decimal("5"), 30), inventarios.ESTADO_POR_VENCER)
        self.assertEqual(e(Decimal("5"), 31), inventarios.ESTADO_VIGENTE)

    def test_fefo_reparte_primero_el_que_vence(self):
        lotes = [{"id_inventario": 1, "cantidad": Decimal("10")},
                 {"id_inventario": 2, "cantidad": Decimal("30")}]
        r = inventarios.repartir_fefo(lotes, Decimal("25"))
        self.assertEqual([(l["id_inventario"], u) for l, u in r], [(1, Decimal("10")), (2, Decimal("15"))])
        self.assertEqual(len(inventarios.repartir_fefo(lotes, Decimal("4"))), 1)

    def test_fefo_sin_stock(self):
        with self.assertRaises(ErrorNegocio):
            inventarios.repartir_fefo([{"id_inventario": 1, "cantidad": Decimal("3")}], Decimal("5"))


class TestEstadistica(unittest.TestCase):
    def test_formulas(self):
        self.assertAlmostEqual(porcentaje(28, 40), 70.0)
        self.assertEqual(porcentaje(1, 0), 0.0)
        self.assertAlmostEqual(promedio([2, 4, 6]), 4.0)
        self.assertEqual(promedio([]), 0.0)


class TestReportes(unittest.TestCase):
    def test_periodos(self):
        hoy = date(2026, 11, 26)
        self.assertEqual(reportes.rango_periodo("Hoy", hoy), (hoy, hoy))
        self.assertEqual(reportes.rango_periodo("Últimos 7 días", hoy), (date(2026, 11, 20), hoy))
        self.assertIsNone(reportes.rango_periodo("Personalizado", hoy))
        self.assertEqual(len(reportes.dias_del_rango(date(2026, 11, 20), hoy)), 7)

    def test_ocupacion(self):
        filas = [
            {"codigo": "OCU-1", "persona": "Ana", "cama": "C-01",
             "fecha_ingreso": datetime(2026, 11, 1, 8), "fecha_salida": datetime(2026, 11, 3, 8)},
            {"codigo": "OCU-2", "persona": "Luis", "cama": "C-02",
             "fecha_ingreso": datetime(2026, 11, 1, 10), "fecha_salida": None},
        ]
        r = reportes.armar_reporte_ocupacion(filas, {"camas_ocupadas": 28, "camas_habilitadas": 40},
                                             ahora=datetime(2026, 11, 2, 10))
        ind = dict(r["indicadores"])
        self.assertTrue(ind["Tasa de ocupación actual"].startswith("70.0 %"))
        self.assertTrue(ind["Estadía promedio (estadías cerradas)"].startswith("2.0 días"))
        self.assertEqual(r["grafica"]["series"]["Ingresos"], [2])
        self.assertEqual(r["filas"][1][4], "En curso")

    def test_raciones(self):
        filas = [{"codigo": "R1", "fecha": date(2026, 11, 20), "comida": "ALMUERZO", "alojados": 30, "externos": 10, "total": 40},
                 {"codigo": "R2", "fecha": date(2026, 11, 22), "comida": "CENA", "alojados": 20, "externos": 20, "total": 40}]
        r = reportes.armar_reporte_raciones(filas, date(2026, 11, 20), date(2026, 11, 26))
        ind = dict(r["indicadores"])
        self.assertEqual(ind["Total de raciones entregadas"], "80")
        self.assertTrue(ind["Promedio diario"].startswith("11.4"))
        self.assertTrue(ind["% de alojados"].startswith("62.5"))
        self.assertEqual(len(r["grafica"]["x"]), 7)
        self.assertEqual(r["grafica"]["series"]["Total"][0], 40)

    def test_ingresos(self):
        filas = [{"codigo": "I1", "fecha": date(2026, 11, 1), "tipo": "DONACION", "origen": "Panadería",
                  "productos": 2, "cantidad": Decimal("30"), "costo": None},
                 {"codigo": "I2", "fecha": date(2026, 11, 1), "tipo": "COMPRA", "origen": "Mercado",
                  "productos": 1, "cantidad": Decimal("10"), "costo": Decimal("85.50")}]
        r = reportes.armar_reporte_ingresos(filas)
        ind = dict(r["indicadores"])
        self.assertEqual(ind["% de donaciones"], "50.0 %")
        self.assertEqual(ind["Gasto total en compras"], "Bs. 85.50")
        self.assertEqual(r["grafica"]["series"]["Donación"], [30.0])
        self.assertEqual(r["grafica"]["series"]["Compra"], [10.0])

    def test_inventario(self):
        filas = [{"alimento": "Arroz", "lote": "L1", "cantidad": Decimal("20"), "unidad": "kg",
                  "fecha_vencimiento": date(2026, 12, 1), "dias": 5},
                 {"alimento": "Arroz", "lote": "L2", "cantidad": Decimal("30"), "unidad": "kg",
                  "fecha_vencimiento": date(2027, 6, 1), "dias": 180},
                 {"alimento": "Sal", "lote": "S1", "cantidad": Decimal("2"), "unidad": "kg",
                  "fecha_vencimiento": None, "dias": None}]
        r = reportes.armar_reporte_inventario(filas)
        ind = dict(r["indicadores"])
        self.assertEqual(ind["Lotes por vencer o vencidos"], "1")
        self.assertTrue(ind["% de lotes por vencer o vencidos"].startswith("33.3"))
        self.assertEqual(r["grafica"]["series"]["Stock"], [50.0, 2.0])

    def test_edades(self):
        filas = [{"codigo": "B1", "nombre": "Ana", "fecha_nacimiento": date(2020, 1, 1)},
                 {"codigo": "B2", "nombre": "Luis", "fecha_nacimiento": date(1990, 1, 1)},
                 {"codigo": "B3", "nombre": "Eva", "fecha_nacimiento": date(1950, 1, 1)},
                 {"codigo": "B4", "nombre": "Sin fecha", "fecha_nacimiento": None}]
        r = reportes.armar_reporte_edades(filas, hoy=date(2026, 6, 1))
        ind = dict(r["indicadores"])
        self.assertEqual(ind["Personas incluidas"], "3")
        self.assertEqual(ind["Sin fecha de nacimiento (no incluidas)"], "1")
        self.assertEqual(r["grafica"]["series"]["Personas"], [1, 0, 1, 1])

    def test_exportar_csv(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = os.path.join(carpeta, "r.csv")
            self.assertTrue(reportes.exportar_csv(["A", "B"], [[1, "ñandú"], [2, "x"]], ruta)[0])
            with open(ruta, encoding="utf-8-sig", newline="") as f:
                self.assertEqual(list(csv.reader(f, delimiter=";")), [["A", "B"], ["1", "ñandú"], ["2", "x"]])
            self.assertFalse(reportes.exportar_csv(["A"], [], os.path.join(carpeta, "no", "r.csv"))[0])


if __name__ == "__main__":
    unittest.main()
