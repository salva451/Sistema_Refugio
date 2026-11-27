"""Pantalla Reportes: 5 reportes con indicadores, grafica (Matplotlib) y tabla; exporta a CSV."""
import tkinter as tk
from datetime import date
from tkinter import filedialog, messagebox, ttk

from Funciones import reportes
from Funciones.validaciones import fecha_a_texto, validar_fecha
from Vistas.componentes import barra_superior, crear_tabla, formato_fecha, vaciar_tabla

try:
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    HAY_MATPLOTLIB = True
except ImportError:          # falta instalar la libreria: pip install matplotlib
    HAY_MATPLOTLIB = False

FUNCIONES_CON_FECHAS = {
    "Ocupación": reportes.reporte_ocupacion,
    "Ingresos de alimentos": reportes.reporte_ingresos,
    "Raciones entregadas": reportes.reporte_raciones,
    "Edades": reportes.reporte_edades,
}
TONOS = ("0.25", "0.65", "0.45")      # grises: los colores los pone el grupo despues


class Reportes(tk.Frame):
    def __init__(self, padre, controlador):
        super().__init__(padre, bg="white")
        self.controlador = controlador
        self.ultimo = None            # (columnas, filas) del ultimo reporte generado

        marco = tk.Frame(self, bg="white", padx=30, pady=20)
        marco.pack(fill="both", expand=True)
        barra_superior(marco, controlador, "Reportes").pack(fill="x", pady=(0, 10))

        # ---------- controles ----------
        controles = tk.Frame(marco, bg="white")
        controles.pack(fill="x", pady=(0, 10))
        tk.Label(controles, text="Reporte", bg="white").grid(row=0, column=0, sticky="w")
        self.tipo = ttk.Combobox(controles, values=reportes.TIPOS_REPORTE, state="readonly", width=26)
        self.tipo.set(reportes.TIPOS_REPORTE[0])
        self.tipo.grid(row=1, column=0, padx=(0, 15))
        self.tipo.bind("<<ComboboxSelected>>", self.cambio_controles)

        tk.Label(controles, text="Periodo", bg="white").grid(row=0, column=1, sticky="w")
        self.periodo = ttk.Combobox(controles, values=reportes.PERIODOS, state="readonly", width=18)
        self.periodo.set("Últimos 30 días")
        self.periodo.grid(row=1, column=1, padx=(0, 15))
        self.periodo.bind("<<ComboboxSelected>>", self.cambio_controles)

        tk.Label(controles, text="Desde (dd/mm/aaaa)", bg="white").grid(row=0, column=2, sticky="w")
        self.desde = formato_fecha(tk.Entry(controles, width=14))
        self.desde.grid(row=1, column=2, padx=(0, 10))
        tk.Label(controles, text="Hasta (dd/mm/aaaa)", bg="white").grid(row=0, column=3, sticky="w")
        self.hasta = formato_fecha(tk.Entry(controles, width=14))
        self.hasta.grid(row=1, column=3, padx=(0, 20))

        tk.Button(controles, text="Generar", command=self.generar, padx=18, pady=4).grid(row=1, column=4, padx=(0, 8))
        tk.Button(controles, text="Exportar a CSV", command=self.exportar, padx=12, pady=4).grid(row=1, column=5)
        self.cambio_controles()

        # ---------- indicadores + grafica ----------
        medio = tk.Frame(marco, bg="white")
        medio.pack(fill="both", expand=True)
        self.marco_indicadores = tk.LabelFrame(medio, text="Indicadores", bg="white", padx=10, pady=8,
                                               width=330, font=("Arial", 10, "bold"))
        self.marco_indicadores.pack(side="left", fill="y", padx=(0, 10))
        self.marco_indicadores.pack_propagate(False)
        self.marco_grafica = tk.LabelFrame(medio, text="Gráfica", bg="white", padx=6, pady=6,
                                           font=("Arial", 10, "bold"))
        self.marco_grafica.pack(side="left", fill="both", expand=True)
        tk.Label(self.marco_grafica, text="Elija un reporte y pulse «Generar».", bg="white").pack(expand=True)

        # ---------- tabla ----------
        marco_tabla = tk.Frame(marco, bg="white")
        marco_tabla.pack(fill="both", expand=True, pady=(10, 0))
        contenedor, self.tabla = crear_tabla(marco_tabla, [("a", "", 100)], altura=7)
        contenedor.pack(fill="both", expand=True)

    # ---------- controles ----------
    def cambio_controles(self, evento=None):
        usa_fechas = self.tipo.get() in FUNCIONES_CON_FECHAS
        self.periodo.config(state="readonly" if usa_fechas else "disabled")
        personalizado = usa_fechas and self.periodo.get() == "Personalizado"
        for campo in (self.desde, self.hasta):
            campo.config(state="normal" if personalizado else "disabled")

    def leer_rango(self):
        rango = reportes.rango_periodo(self.periodo.get())
        if rango is not None:
            return rango
        correcto, desde = validar_fecha(self.desde.get(), "La fecha «Desde»")
        if not correcto:
            messagebox.showwarning("Dato inválido", desde)
            return None
        correcto, hasta = validar_fecha(self.hasta.get(), "La fecha «Hasta»")
        if not correcto:
            messagebox.showwarning("Dato inválido", hasta)
            return None
        if desde > hasta:
            messagebox.showwarning("Dato inválido", "La fecha «Desde» no puede ser mayor que «Hasta».")
            return None
        return desde, hasta

    # ---------- generar ----------
    def generar(self):
        tipo = self.tipo.get()
        if tipo in FUNCIONES_CON_FECHAS:
            rango = self.leer_rango()
            if rango is None:
                return
            if self.periodo.get() != "Personalizado":
                for campo, valor in zip((self.desde, self.hasta), rango):
                    campo.config(state="normal")
                    campo.delete(0, tk.END)
                    campo.insert(0, fecha_a_texto(valor))
                    campo.config(state="disabled")
            correcto, datos = FUNCIONES_CON_FECHAS[tipo](*rango)
        else:
            correcto, datos = reportes.reporte_inventario()
        if not correcto:
            messagebox.showerror("Error", datos)
            return
        self.ultimo = (datos["columnas"], datos["filas"])
        self.mostrar_indicadores(datos["indicadores"])
        self.mostrar_tabla(datos["columnas"], datos["filas"])
        self.dibujar_grafica(datos["grafica"])

    def mostrar_indicadores(self, indicadores):
        for w in self.marco_indicadores.winfo_children():
            w.destroy()
        for nombre, valor in indicadores:
            tk.Label(self.marco_indicadores, text=nombre, bg="white", anchor="w").pack(fill="x")
            tk.Label(self.marco_indicadores, text=valor, bg="white", anchor="w", wraplength=300,
                     justify="left", font=("Arial", 11, "bold")).pack(fill="x", pady=(0, 6))

    def mostrar_tabla(self, columnas, filas):
        self.tabla["columns"] = columnas
        ancho = max(90, int(1000 / len(columnas)))
        for c in columnas:
            self.tabla.heading(c, text=c)
            self.tabla.column(c, width=ancho, anchor="w")
        vaciar_tabla(self.tabla)
        for i, fila in enumerate(filas):
            self.tabla.insert("", tk.END, iid=str(i), values=fila)

    def dibujar_grafica(self, g):
        for w in self.marco_grafica.winfo_children():
            w.destroy()
        if not HAY_MATPLOTLIB:
            tk.Label(self.marco_grafica, bg="white", justify="center",
                     text="Para ver la gráfica instale Matplotlib:\npip install matplotlib").pack(expand=True)
            return
        if not g["x"]:
            tk.Label(self.marco_grafica, text="No hay datos para graficar en este periodo.", bg="white").pack(expand=True)
            return
        figura = Figure(figsize=(6.4, 3.3), dpi=100)
        ejes = figura.add_subplot(111)
        x = list(range(len(g["x"])))
        series = g["series"]
        if g["tipo"] == "lineas":
            for i, (nombre, valores) in enumerate(series.items()):
                ejes.plot(x, valores, marker="o", color=TONOS[i % 3], label=nombre)
        else:
            ancho = 0.8 / len(series)
            for i, (nombre, valores) in enumerate(series.items()):
                ejes.bar([p - 0.4 + ancho * (i + 0.5) for p in x], valores, width=ancho,
                         color=TONOS[i % 3], label=nombre)
        ejes.set_xticks(x)
        ejes.set_xticklabels(g["x"], rotation=30, ha="right", fontsize=8)
        ejes.set_title(g["titulo"], fontsize=10)
        ejes.set_ylabel(g["y"], fontsize=9)
        if len(series) > 1:
            ejes.legend(fontsize=8)
        figura.tight_layout()
        lienzo = FigureCanvasTkAgg(figura, master=self.marco_grafica)
        lienzo.draw()
        lienzo.get_tk_widget().pack(fill="both", expand=True)

    # ---------- exportar ----------
    def exportar(self):
        if self.ultimo is None or not self.ultimo[1]:
            messagebox.showwarning("Sin datos", "Primero genere un reporte con datos.")
            return
        ruta = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("Archivo CSV", "*.csv")],
            initialfile=f"reporte_{date.today():%Y%m%d}.csv")
        if not ruta:
            return
        correcto, resultado = reportes.exportar_csv(self.ultimo[0], self.ultimo[1], ruta)
        if correcto:
            messagebox.showinfo("Éxito", f"Archivo exportado:\n{resultado}")
        else:
            messagebox.showerror("Error", resultado)

    def al_mostrar(self):
        self.cambio_controles()
