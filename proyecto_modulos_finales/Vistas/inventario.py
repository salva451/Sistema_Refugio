"""Pantalla Inventario: existencias por lote (con alertas) y catalogo de alimentos."""
import tkinter as tk
from tkinter import messagebox, ttk

from Funciones import alimentos, inventarios
from Funciones.validaciones import validar_cantidad
from Vistas.componentes import barra_superior, crear_tabla, fecha_texto, vaciar_tabla


class Inventario(tk.Frame):
    def __init__(self, padre, controlador):
        super().__init__(padre, bg="white")
        self.controlador = controlador
        self.id_editando = None          # id del alimento que se esta editando

        marco = tk.Frame(self, bg="white", padx=30, pady=25)
        marco.pack(fill="both", expand=True)
        barra_superior(marco, controlador, "Inventario de alimentos").pack(fill="x", pady=(0, 15))

        pestanas = ttk.Notebook(marco)
        pestanas.pack(fill="both", expand=True)
        self.tab_stock = tk.Frame(pestanas, bg="white", padx=15, pady=15)
        self.tab_catalogo = tk.Frame(pestanas, bg="white", padx=15, pady=15)
        pestanas.add(self.tab_stock, text="Existencias")
        pestanas.add(self.tab_catalogo, text="Catálogo de alimentos")

        self.crear_existencias()
        self.crear_catalogo()

    # ================= pestana 1: existencias =================
    def crear_existencias(self):
        t = self.tab_stock
        resumen = tk.Frame(t, bg="white")
        resumen.pack(fill="x")
        self.lbl_raciones = tk.Label(resumen, text="Raciones disponibles según inventario: 0",
                                     bg="white", font=("Arial", 11, "bold"))
        self.lbl_raciones.pack(side="left")
        self.lbl_alerta = tk.Label(resumen, text="", bg="white", font=("Arial", 11, "bold"))
        self.lbl_alerta.pack(side="right")

        filtros = tk.Frame(t, bg="white")
        filtros.pack(fill="x", pady=(12, 8))
        tk.Label(filtros, text="Buscar alimento o lote", bg="white").pack(side="left")
        self.busqueda = tk.Entry(filtros, width=30)
        self.busqueda.pack(side="left", padx=(8, 20))
        self.busqueda.bind("<KeyRelease>", lambda e: self.cargar_lotes())
        tk.Label(filtros, text="Estado", bg="white").pack(side="left")
        self.filtro_estado = ttk.Combobox(filtros, values=tuple(inventarios.FILTROS), state="readonly", width=14)
        self.filtro_estado.set("Todos")
        self.filtro_estado.pack(side="left", padx=8)
        self.filtro_estado.bind("<<ComboboxSelected>>", lambda e: self.cargar_lotes())

        marco_tabla, self.tabla_lotes = crear_tabla(t, [
            ("alimento", "Alimento", 190), ("lote", "Lote", 110), ("cantidad", "Cantidad", 90),
            ("unidad", "Unidad", 80), ("vence", "Vencimiento", 120),
            ("dias", "Días restantes", 110), ("estado", "Estado", 210)], altura=14)
        marco_tabla.pack(fill="both", expand=True)
        self.tabla_lotes.tag_configure("alerta", font=("Arial", 10, "bold"))

    def cargar_lotes(self):
        correcto, filas = inventarios.listar_lotes(self.busqueda.get(), self.filtro_estado.get())
        if not correcto:
            messagebox.showerror("Error", filas)
            return
        vaciar_tabla(self.tabla_lotes)
        for f in filas:
            etiqueta = ("alerta",) if f["estado"] in inventarios.ESTADOS_RIESGO else ()
            self.tabla_lotes.insert(
                "", tk.END, iid=str(f["id_inventario"]), tags=etiqueta,
                values=(f["alimento"], f["lote"], f"{f['cantidad']:.2f}", f["unidad"],
                        fecha_texto(f["fecha_vencimiento"], "Sin vencimiento"),
                        "" if f["dias"] is None else f["dias"], f["estado"]))

        correcto, n = inventarios.contar_por_vencer(inventarios.DIAS_ALERTA)
        if correcto:
            self.lbl_alerta.config(text=f"⚠ {n} lote(s) por vencer o vencidos" if n else "Sin alertas de vencimiento")
        correcto, disponibles = inventarios.raciones_disponibles()
        if correcto:
            self.lbl_raciones.config(text=f"Raciones disponibles según inventario: {disponibles}")

    # ================= pestana 2: catalogo =================
    def crear_catalogo(self):
        t = self.tab_catalogo
        form = tk.Frame(t, bg="white")
        form.pack(side="left", fill="y", padx=(0, 30))

        self.lbl_form = tk.Label(form, text="Nuevo alimento", bg="white", font=("Arial", 14, "bold"))
        self.lbl_form.grid(row=0, column=0, sticky="w", pady=(0, 12))

        tk.Label(form, text="Código", bg="white").grid(row=1, column=0, sticky="w")
        self.var_codigo = tk.StringVar(value="Automático")
        tk.Entry(form, textvariable=self.var_codigo, state="readonly", width=32).grid(row=2, column=0, sticky="ew", pady=(2, 10))

        tk.Label(form, text="Nombre*", bg="white").grid(row=3, column=0, sticky="w")
        self.nombre = tk.Entry(form, width=32)
        self.nombre.grid(row=4, column=0, sticky="ew", pady=(2, 10))

        tk.Label(form, text="Categoría", bg="white").grid(row=5, column=0, sticky="w")
        self.categoria = ttk.Combobox(form, values=alimentos.CATEGORIAS, state="readonly")
        self.categoria.set("Otros")
        self.categoria.grid(row=6, column=0, sticky="ew", pady=(2, 10))

        tk.Label(form, text="Unidad*", bg="white").grid(row=7, column=0, sticky="w")
        self.unidad = ttk.Combobox(form, values=alimentos.UNIDADES, state="readonly")
        self.unidad.grid(row=8, column=0, sticky="ew", pady=(2, 10))

        tk.Label(form, text="Raciones por unidad* (ej.: 1 kg rinde 10)", bg="white").grid(row=9, column=0, sticky="w")
        self.raciones = tk.Entry(form)
        self.raciones.grid(row=10, column=0, sticky="ew", pady=(2, 16))

        botones = tk.Frame(form, bg="white")
        botones.grid(row=11, column=0, sticky="w")
        self.boton_guardar = tk.Button(botones, text="Guardar", command=self.guardar_alimento, padx=20, pady=6)
        self.boton_guardar.pack(side="left")
        tk.Button(botones, text="Limpiar", command=self.limpiar_formulario, padx=20, pady=6).pack(side="left", padx=10)

        lista = tk.Frame(t, bg="white")
        lista.pack(side="left", fill="both", expand=True)
        tk.Label(lista, text="Buscar por nombre o código", bg="white").pack(anchor="w")
        self.buscar_alimento = tk.Entry(lista)
        self.buscar_alimento.pack(fill="x", pady=(2, 10))
        self.buscar_alimento.bind("<KeyRelease>", lambda e: self.cargar_catalogo())
        marco_tabla, self.tabla_catalogo = crear_tabla(lista, [
            ("codigo", "Código", 90), ("nombre", "Nombre", 190), ("categoria", "Categoría", 150),
            ("unidad", "Unidad", 80), ("raciones", "Raciones/unidad", 120)], altura=12)
        marco_tabla.pack(fill="both", expand=True)
        tk.Button(lista, text="Editar", command=self.editar_seleccionado, padx=20, pady=6).pack(anchor="w", pady=(10, 0))

    def cargar_catalogo(self):
        correcto, filas = alimentos.listar_alimentos(self.buscar_alimento.get())
        if not correcto:
            messagebox.showerror("Error", filas)
            return
        vaciar_tabla(self.tabla_catalogo)
        for f in filas:
            self.tabla_catalogo.insert("", tk.END, iid=str(f["id_alimento"]),
                                       values=(f["codigo"], f["nombre"], f["categoria"], f["unidad"],
                                               f"{f['raciones_por_unidad']:.2f}"))

    def limpiar_formulario(self):
        self.id_editando = None
        self.var_codigo.set("Automático")
        self.nombre.delete(0, tk.END)
        self.categoria.set("Otros")
        self.unidad.set("")
        self.raciones.delete(0, tk.END)
        self.lbl_form.config(text="Nuevo alimento")
        self.boton_guardar.config(text="Guardar")

    def editar_seleccionado(self):
        seleccion = self.tabla_catalogo.selection()
        if not seleccion:
            messagebox.showwarning("Selección necesaria", "Seleccione un alimento de la tabla.")
            return
        correcto, a = alimentos.obtener_alimento(int(seleccion[0]))
        if not correcto:
            messagebox.showerror("Error", a)
            return
        self.limpiar_formulario()
        self.id_editando = a["id_alimento"]
        self.var_codigo.set(a["codigo"])
        self.nombre.insert(0, a["nombre"])
        self.categoria.set(a["categoria"])
        self.unidad.set(a["unidad"])
        self.raciones.insert(0, f"{a['raciones_por_unidad']:.2f}")
        self.lbl_form.config(text=f"Editando {a['codigo']}")
        self.boton_guardar.config(text="Guardar cambios")

    def guardar_alimento(self):
        nombre = self.nombre.get().strip()
        if not nombre:
            messagebox.showwarning("Campo vacío", "Complete el campo: Nombre")
            return
        if not self.unidad.get():
            messagebox.showwarning("Campo vacío", "Seleccione la unidad.")
            return
        correcto, raciones = validar_cantidad(self.raciones.get(), "Las raciones por unidad")
        if not correcto:
            messagebox.showwarning("Dato inválido", raciones)
            return

        if self.id_editando is None:
            correcto, resultado = alimentos.crear_alimento(nombre, self.categoria.get(), self.unidad.get(), raciones)
        else:
            correcto, resultado = alimentos.actualizar_alimento(
                self.id_editando, nombre, self.categoria.get(), self.unidad.get(), raciones)
        if correcto:
            messagebox.showinfo("Éxito", "Alimento guardado correctamente.")
            self.limpiar_formulario()
            self.cargar_catalogo()
            self.cargar_lotes()
        else:
            messagebox.showerror("Error", resultado)

    def al_mostrar(self):
        self.cargar_lotes()
        self.cargar_catalogo()
