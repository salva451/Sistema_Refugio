"""Pantalla Ingreso de alimentos (menu: Donaciones). Un ingreso puede ser DONACION o COMPRA;
en los dos casos los alimentos se suman al inventario."""
import tkinter as tk
from tkinter import messagebox, ttk

from Funciones import alimentos, donaciones, donantes
from Funciones.validaciones import fecha_a_texto, validar_cantidad, validar_fecha
from Vistas.componentes import barra_superior, crear_tabla, fecha_texto, formato_fecha, vaciar_tabla
from datetime import date

TIPOS = ("Donación", "Compra")


class Donaciones(tk.Frame):
    def __init__(self, padre, controlador):
        super().__init__(padre, bg="white")
        self.controlador = controlador
        self.items = []             # productos agregados a la lista antes de registrar
        self.mapa_alimentos = {}    # texto del combo -> datos del alimento
        self.mapa_origenes = {}     # texto del combo -> id del donante/proveedor

        marco = tk.Frame(self, bg="white", padx=30, pady=25)
        marco.pack(fill="both", expand=True)
        barra_superior(marco, controlador, "Ingreso de alimentos (donación o compra)").pack(fill="x", pady=(0, 15))

        pestanas = ttk.Notebook(marco)
        pestanas.pack(fill="both", expand=True)
        self.tab_nuevo = tk.Frame(pestanas, bg="white", padx=15, pady=15)
        self.tab_historial = tk.Frame(pestanas, bg="white", padx=15, pady=15)
        pestanas.add(self.tab_nuevo, text="Nuevo ingreso")
        pestanas.add(self.tab_historial, text="Historial")
        self.crear_nuevo()
        self.crear_historial()

    # ================= pestana 1: nuevo ingreso =================
    def crear_nuevo(self):
        t = self.tab_nuevo
        cabecera = tk.Frame(t, bg="white")
        cabecera.pack(fill="x")

        tk.Label(cabecera, text="Tipo de ingreso*", bg="white").grid(row=0, column=0, sticky="w")
        self.tipo = ttk.Combobox(cabecera, values=TIPOS, state="readonly", width=14)
        self.tipo.set("Donación")
        self.tipo.grid(row=1, column=0, sticky="w", padx=(0, 20), pady=(2, 10))
        self.tipo.bind("<<ComboboxSelected>>", self.cambio_tipo)

        self.lbl_origen = tk.Label(cabecera, text="Donante*", bg="white")
        self.lbl_origen.grid(row=0, column=1, sticky="w")
        fila_origen = tk.Frame(cabecera, bg="white")
        fila_origen.grid(row=1, column=1, sticky="w", padx=(0, 20), pady=(2, 10))
        self.origen = ttk.Combobox(fila_origen, state="readonly", width=30)
        self.origen.pack(side="left")
        tk.Button(fila_origen, text="Nuevo...", command=self.nuevo_origen).pack(side="left", padx=6)

        tk.Label(cabecera, text="Fecha*", bg="white").grid(row=0, column=2, sticky="w")
        self.fecha = formato_fecha(tk.Entry(cabecera, width=14))
        self.fecha.insert(0, fecha_a_texto(date.today()))
        self.fecha.grid(row=1, column=2, sticky="w", padx=(0, 20), pady=(2, 10))

        tk.Label(cabecera, text="Costo total (Bs.) - solo compras", bg="white").grid(row=0, column=3, sticky="w")
        self.costo = tk.Entry(cabecera, width=16, state="disabled")
        self.costo.grid(row=1, column=3, sticky="w", padx=(0, 20), pady=(2, 10))

        tk.Label(cabecera, text="Observaciones", bg="white").grid(row=0, column=4, sticky="w")
        self.observaciones = tk.Entry(cabecera, width=30)
        self.observaciones.grid(row=1, column=4, sticky="w", pady=(2, 10))

        tk.Label(t, text="Productos del ingreso", bg="white", font=("Arial", 12, "bold")).pack(anchor="w", pady=(8, 4))
        producto = tk.Frame(t, bg="white")
        producto.pack(fill="x")
        for col, texto in enumerate(("Alimento*", "Lote*", "Cantidad*", "Vencimiento (dd/mm/aaaa)")):
            tk.Label(producto, text=texto, bg="white").grid(row=0, column=col, sticky="w")
        self.alimento = ttk.Combobox(producto, state="readonly", width=32)
        self.alimento.grid(row=1, column=0, sticky="w", padx=(0, 15), pady=(2, 8))
        self.alimento.bind("<<ComboboxSelected>>", self.cambio_alimento)
        self.lote = tk.Entry(producto, width=16)
        self.lote.grid(row=1, column=1, sticky="w", padx=(0, 15), pady=(2, 8))
        self.cantidad = tk.Entry(producto, width=12)
        self.cantidad.grid(row=1, column=2, sticky="w", padx=(0, 5), pady=(2, 8))
        self.lbl_unidad = tk.Label(producto, text="", bg="white", width=8, anchor="w")
        self.lbl_unidad.grid(row=1, column=3, sticky="w")
        self.vencimiento = formato_fecha(tk.Entry(producto, width=16))
        self.vencimiento.grid(row=1, column=4, sticky="w", padx=(0, 15), pady=(2, 8))
        tk.Button(producto, text="Agregar a la lista", command=self.agregar_item).grid(row=1, column=5, pady=(2, 8))

        marco_tabla, self.tabla_items = crear_tabla(t, [
            ("alimento", "Alimento", 220), ("lote", "Lote", 120), ("cantidad", "Cantidad", 100),
            ("unidad", "Unidad", 80), ("vence", "Vencimiento", 130)], altura=8)
        marco_tabla.pack(fill="both", expand=True, pady=(5, 8))

        acciones = tk.Frame(t, bg="white")
        acciones.pack(fill="x")
        tk.Button(acciones, text="Quitar fila", command=self.quitar_item, padx=14, pady=6).pack(side="left")
        tk.Button(acciones, text="Limpiar todo", command=self.limpiar_todo, padx=14, pady=6).pack(side="left", padx=10)
        tk.Button(acciones, text="Registrar ingreso", command=self.registrar, padx=24, pady=8).pack(side="right")

    def cambio_tipo(self, evento=None):
        es_compra = self.tipo.get() == "Compra"
        self.lbl_origen.config(text="Proveedor*" if es_compra else "Donante*")
        self.costo.config(state="normal" if es_compra else "disabled")
        if not es_compra:
            self.costo.config(state="normal")
            self.costo.delete(0, tk.END)
            self.costo.config(state="disabled")
        self.cargar_origenes()

    def cambio_alimento(self, evento=None):
        datos = self.mapa_alimentos.get(self.alimento.get())
        self.lbl_unidad.config(text=datos["unidad"] if datos else "")

    def cargar_alimentos(self):
        correcto, filas = alimentos.listar_alimentos()
        if not correcto:
            messagebox.showerror("Error", filas)
            return
        self.mapa_alimentos = {f"{f['codigo']} - {f['nombre']}": f for f in filas}
        self.alimento["values"] = tuple(self.mapa_alimentos)

    def cargar_origenes(self, seleccionar=None):
        tipos = ["PROVEEDOR"] if self.tipo.get() == "Compra" else ["PERSONA", "ORGANIZACION"]
        correcto, filas = donantes.listar_donantes(tipos)
        if not correcto:
            messagebox.showerror("Error", filas)
            return
        self.mapa_origenes = {f"{f['nombre']} ({f['codigo']})": f["id_donante"] for f in filas}
        self.origen["values"] = tuple(self.mapa_origenes)
        self.origen.set("")
        if seleccionar is not None:
            for texto, id_donante in self.mapa_origenes.items():
                if id_donante == seleccionar:
                    self.origen.set(texto)

    # ---------- ventanita para crear un donante o proveedor ----------
    def nuevo_origen(self):
        es_compra = self.tipo.get() == "Compra"
        ventana = tk.Toplevel(self)
        ventana.title("Nuevo proveedor" if es_compra else "Nuevo donante")
        ventana.configure(bg="white", padx=20, pady=15)
        ventana.grab_set()

        tk.Label(ventana, text="Nombre*", bg="white").grid(row=0, column=0, sticky="w")
        nombre = tk.Entry(ventana, width=34)
        nombre.grid(row=1, column=0, sticky="ew", pady=(2, 8))
        tk.Label(ventana, text="Tipo", bg="white").grid(row=2, column=0, sticky="w")
        if es_compra:
            tipo = ttk.Combobox(ventana, values=("PROVEEDOR",), state="readonly")
            tipo.set("PROVEEDOR")
        else:
            tipo = ttk.Combobox(ventana, values=("PERSONA", "ORGANIZACION"), state="readonly")
            tipo.set("PERSONA")
        tipo.grid(row=3, column=0, sticky="ew", pady=(2, 8))
        tk.Label(ventana, text="Teléfono", bg="white").grid(row=4, column=0, sticky="w")
        telefono = tk.Entry(ventana)
        telefono.grid(row=5, column=0, sticky="ew", pady=(2, 12))

        def guardar():
            correcto, resultado = donantes.crear_donante(nombre.get(), tipo.get(), telefono.get())
            if correcto:
                self.cargar_origenes(seleccionar=resultado)
                ventana.destroy()
            else:
                messagebox.showerror("Error", resultado, parent=ventana)

        botones = tk.Frame(ventana, bg="white")
        botones.grid(row=6, column=0, sticky="e")
        tk.Button(botones, text="Guardar", command=guardar, padx=14).pack(side="left", padx=(0, 8))
        tk.Button(botones, text="Cancelar", command=ventana.destroy, padx=14).pack(side="left")

    # ---------- lista de productos ----------
    def agregar_item(self):
        datos = self.mapa_alimentos.get(self.alimento.get())
        if datos is None:
            messagebox.showwarning("Campo vacío", "Seleccione un alimento.")
            return
        lote = self.lote.get().strip()
        if not lote:
            messagebox.showwarning("Campo vacío", "Complete el campo: Lote")
            return
        correcto, cantidad = validar_cantidad(self.cantidad.get(), "La cantidad")
        if not correcto:
            messagebox.showwarning("Dato inválido", cantidad)
            return
        correcto, vence = validar_fecha(self.vencimiento.get(), "El vencimiento", obligatoria=False)
        if not correcto:
            messagebox.showwarning("Dato inválido", vence)
            return
        if vence is not None and vence < date.today():
            messagebox.showwarning("Producto vencido", "No se puede ingresar un producto ya vencido.")
            return
        self.items.append({"id_alimento": datos["id_alimento"], "alimento": datos["nombre"],
                           "unidad": datos["unidad"], "lote": lote, "cantidad": cantidad, "vencimiento": vence})
        self.dibujar_items()
        self.lote.delete(0, tk.END)
        self.cantidad.delete(0, tk.END)
        self.vencimiento.delete(0, tk.END)

    def dibujar_items(self):
        vaciar_tabla(self.tabla_items)
        for i, it in enumerate(self.items):
            self.tabla_items.insert("", tk.END, iid=str(i), values=(
                it["alimento"], it["lote"], f"{it['cantidad']:.2f}", it["unidad"],
                fecha_texto(it["vencimiento"], "Sin vencimiento")))

    def quitar_item(self):
        seleccion = self.tabla_items.selection()
        if not seleccion:
            messagebox.showwarning("Selección necesaria", "Seleccione una fila de la lista.")
            return
        del self.items[int(seleccion[0])]
        self.dibujar_items()

    def limpiar_todo(self):
        self.items = []
        self.dibujar_items()
        for campo in (self.lote, self.cantidad, self.vencimiento, self.observaciones):
            campo.delete(0, tk.END)
        self.alimento.set("")
        self.lbl_unidad.config(text="")
        self.origen.set("")
        self.tipo.set("Donación")
        self.cambio_tipo()
        self.fecha.delete(0, tk.END)
        self.fecha.insert(0, fecha_a_texto(date.today()))

    def registrar(self):
        id_donante = self.mapa_origenes.get(self.origen.get())
        if id_donante is None:
            messagebox.showwarning("Campo vacío", "Seleccione el donante o proveedor.")
            return
        correcto, fecha = validar_fecha(self.fecha.get(), "La fecha", permitir_futura=False)
        if not correcto:
            messagebox.showwarning("Dato inválido", fecha)
            return
        costo = None
        if self.tipo.get() == "Compra" and self.costo.get().strip():
            correcto, costo = validar_cantidad(self.costo.get(), "El costo total", permitir_cero=True)
            if not correcto:
                messagebox.showwarning("Dato inválido", costo)
                return
        if not self.items:
            messagebox.showwarning("Lista vacía", "Agregue al menos un producto a la lista.")
            return

        tipo = "COMPRA" if self.tipo.get() == "Compra" else "DONACION"
        lista = [{"id_alimento": i["id_alimento"], "lote": i["lote"], "cantidad": i["cantidad"],
                  "vencimiento": i["vencimiento"]} for i in self.items]
        correcto, resultado = donaciones.registrar_ingreso(
            tipo, id_donante, fecha, costo, self.observaciones.get(), lista)
        if correcto:
            self.limpiar_todo()
            self.cargar_historial()
        else:
            messagebox.showerror("Error", resultado)

    # ================= pestana 2: historial =================
    def crear_historial(self):
        t = self.tab_historial
        filtros = tk.Frame(t, bg="white")
        filtros.pack(fill="x", pady=(0, 8))
        tk.Label(filtros, text="Buscar por código o nombre", bg="white").pack(side="left")
        self.busqueda = tk.Entry(filtros, width=28)
        self.busqueda.pack(side="left", padx=(8, 20))
        self.busqueda.bind("<KeyRelease>", lambda e: self.cargar_historial())
        tk.Label(filtros, text="Tipo", bg="white").pack(side="left")
        self.filtro_tipo = ttk.Combobox(filtros, values=("Todos",) + TIPOS, state="readonly", width=12)
        self.filtro_tipo.set("Todos")
        self.filtro_tipo.pack(side="left", padx=8)
        self.filtro_tipo.bind("<<ComboboxSelected>>", lambda e: self.cargar_historial())

        marco_tabla, self.tabla_historial = crear_tabla(t, [
            ("codigo", "Código", 100), ("fecha", "Fecha", 100), ("tipo", "Tipo", 100),
            ("origen", "Donante / Proveedor", 240), ("productos", "Productos", 90),
            ("costo", "Costo (Bs.)", 100)], altura=9)
        marco_tabla.pack(fill="both", expand=True)
        self.tabla_historial.bind("<<TreeviewSelect>>", self.mostrar_detalle)

        tk.Label(t, text="Detalle del ingreso seleccionado", bg="white", font=("Arial", 11, "bold")).pack(anchor="w", pady=(10, 4))
        marco_detalle, self.tabla_detalle = crear_tabla(t, [
            ("alimento", "Alimento", 220), ("lote", "Lote", 120), ("cantidad", "Cantidad", 100),
            ("unidad", "Unidad", 80), ("vence", "Vencimiento", 130)], altura=5)
        marco_detalle.pack(fill="both", expand=True)

    def cargar_historial(self):
        tipo = {"Donación": "DONACION", "Compra": "COMPRA"}.get(self.filtro_tipo.get())
        correcto, filas = donaciones.listar_ingresos(tipo, self.busqueda.get())
        if not correcto:
            messagebox.showerror("Error", filas)
            return
        vaciar_tabla(self.tabla_historial)
        vaciar_tabla(self.tabla_detalle)
        for f in filas:
            self.tabla_historial.insert("", tk.END, iid=str(f["id_donacion"]), values=(
                f["codigo"], fecha_texto(f["fecha"]), "Donación" if f["tipo"] == "DONACION" else "Compra",
                f["origen"], f["productos"], "" if f["costo"] is None else f"{f['costo']:.2f}"))

    def mostrar_detalle(self, evento=None):
        seleccion = self.tabla_historial.selection()
        if not seleccion:
            return
        correcto, filas = donaciones.detalle_ingreso(int(seleccion[0]))
        if not correcto:
            messagebox.showerror("Error", filas)
            return
        vaciar_tabla(self.tabla_detalle)
        for i, f in enumerate(filas):
            self.tabla_detalle.insert("", tk.END, iid=str(i), values=(
                f["alimento"], f["lote"], f"{f['cantidad']:.2f}", f["unidad"],
                fecha_texto(f["fecha_vencimiento"], "Sin vencimiento")))

    def al_mostrar(self):
        self.cargar_alimentos()
        self.cargar_origenes()
        self.cargar_historial()
