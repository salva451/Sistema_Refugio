"""Pantalla Raciones: Seccion A (entrega de raciones) + Seccion B (alimentos usados).
Un solo boton confirma las dos cosas: guarda la entrega y descuenta el inventario."""
import tkinter as tk
from datetime import date
from decimal import Decimal
from tkinter import messagebox, ttk

from Funciones import inventarios, raciones
from Funciones.validaciones import fecha_a_texto, validar_cantidad, validar_entero, validar_fecha
from Vistas.componentes import barra_superior, crear_tabla, fecha_texto, formato_fecha, vaciar_tabla


class Raciones(tk.Frame):
    def __init__(self, padre, controlador):
        super().__init__(padre, bg="white")
        self.controlador = controlador
        self.lineas = []             # alimentos usados (cada uno con el lote sugerido)
        self.mapa_alimentos = {}     # texto del combo -> datos del alimento
        self.alojados_lista = []     # personas alojadas que se muestran para marcar

        marco = tk.Frame(self, bg="white", padx=30, pady=20)
        marco.pack(fill="both", expand=True)
        barra_superior(marco, controlador, "Raciones").pack(fill="x", pady=(0, 10))

        # ---------- planificacion (promedio historico) ----------
        plan = tk.LabelFrame(marco, text="PLANIFICACIÓN DE RACIONES · promedio histórico (7 días)",
                             bg="white", padx=10, pady=8, font=("Arial", 10, "bold"))
        plan.pack(fill="x", pady=(0, 10))
        self.lbl_plan = {}
        for columna, (clave, texto) in enumerate((("DESAYUNO", "Desayuno"), ("ALMUERZO", "Almuerzo"),
                                                  ("TE", "Té"), ("CENA", "Cena"),
                                                  ("TOTAL", "Total diario (promedio)"))):
            plan.columnconfigure(columna, weight=1)
            tarjeta = tk.Frame(plan, bg="white", highlightbackground="black", highlightthickness=1)
            tarjeta.grid(row=0, column=columna, sticky="ew", padx=6)
            tk.Label(tarjeta, text=texto, bg="white").pack(side="left", padx=10, pady=6)
            self.lbl_plan[clave] = tk.Label(tarjeta, text="0", bg="white", font=("Arial", 12, "bold"))
            self.lbl_plan[clave].pack(side="right", padx=10)

        cuerpo = tk.Frame(marco, bg="white")
        cuerpo.pack(fill="both", expand=True)
        cuerpo.columnconfigure(0, weight=1, uniform="seccion")
        cuerpo.columnconfigure(1, weight=1, uniform="seccion")
        cuerpo.rowconfigure(0, weight=1)

        self.seccion_a = tk.LabelFrame(cuerpo, text="SECCIÓN A: Entrega de raciones", bg="white",
                                       padx=12, pady=8, font=("Arial", 10, "bold"))
        self.seccion_a.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self.seccion_b = tk.LabelFrame(cuerpo, text="SECCIÓN B: Alimentos usados en preparación", bg="white",
                                       padx=12, pady=8, font=("Arial", 10, "bold"))
        self.seccion_b.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        self.crear_seccion_a()
        self.crear_seccion_b()

        pie = tk.Frame(marco, bg="white")
        pie.pack(fill="x", pady=(10, 0))
        self.lbl_disponibles = tk.Label(pie, text="Raciones disponibles según inventario: 0",
                                        bg="white", font=("Arial", 10, "bold"))
        self.lbl_disponibles.pack(side="left")
        tk.Button(pie, text="Confirmar registro de raciones y consumo", command=self.confirmar_registro,
                  padx=24, pady=8).pack(side="right")

    # ================= SECCION A =================
    def crear_seccion_a(self):
        a = self.seccion_a
        a.columnconfigure(0, weight=1)
        a.columnconfigure(1, weight=1)

        tk.Label(a, text="Fecha de atención (dd/mm/aaaa)", bg="white").grid(row=0, column=0, sticky="w")
        self.fecha = formato_fecha(tk.Entry(a))
        self.fecha.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=(2, 8))
        tk.Label(a, text="Tipo de comida", bg="white").grid(row=0, column=1, sticky="w")
        self.tipo_comida = ttk.Combobox(a, values=raciones.COMIDAS, state="readonly")
        self.tipo_comida.grid(row=1, column=1, sticky="ew", pady=(2, 8))

        tk.Label(a, text="Conteo de raciones", bg="white", font=("Arial", 10, "bold")).grid(row=2, column=0, columnspan=2, sticky="w")
        tk.Label(a, text="Alojados (registrados individualmente)", bg="white").grid(row=3, column=0, sticky="w")
        tk.Label(a, text="Externos (servicios anónimos)", bg="white").grid(row=3, column=1, sticky="w")
        self.var_alojados = tk.StringVar(value="0")
        self.var_externos = tk.StringVar(value="0")
        self.var_total = tk.StringVar(value="0")
        tk.Entry(a, textvariable=self.var_alojados).grid(row=4, column=0, sticky="ew", padx=(0, 10), pady=(2, 8))
        tk.Entry(a, textvariable=self.var_externos).grid(row=4, column=1, sticky="ew", pady=(2, 8))
        self.var_alojados.trace_add("write", self.actualizar_total)
        self.var_externos.trace_add("write", self.actualizar_total)

        tk.Label(a, text="Total entregado", bg="white").grid(row=5, column=0, sticky="w")
        tk.Entry(a, textvariable=self.var_total, state="readonly").grid(row=6, column=0, columnspan=2, sticky="ew", pady=(2, 8))

        tk.Button(a, text="Registrar asistencia de alojados", command=self.marcar_asistencia
                  ).grid(row=7, column=0, columnspan=2, sticky="ew", pady=(0, 8))

        tk.Label(a, text="Beneficiarios alojados para marcar (seleccione quienes comieron)",
                 bg="white").grid(row=8, column=0, columnspan=2, sticky="w")
        self.buscar_alojado = tk.Entry(a)
        self.buscar_alojado.grid(row=9, column=0, columnspan=2, sticky="ew", pady=(2, 4))
        self.buscar_alojado.bind("<KeyRelease>", lambda e: self.cargar_alojados())
        marco_tabla, self.tabla_alojados = crear_tabla(a, [("codigo", "Código", 90), ("nombre", "Beneficiario", 260)],
                                                       altura=5, seleccion="extended")
        marco_tabla.grid(row=10, column=0, columnspan=2, sticky="nsew")
        a.rowconfigure(10, weight=1)

        tk.Label(a, text="Observaciones", bg="white").grid(row=11, column=0, columnspan=2, sticky="w", pady=(8, 0))
        self.observaciones = tk.Entry(a)
        self.observaciones.grid(row=12, column=0, columnspan=2, sticky="ew", pady=(2, 0))

    def actualizar_total(self, *args):
        ok1, alojados = validar_entero(self.var_alojados.get(), "Alojados")
        ok2, externos = validar_entero(self.var_externos.get(), "Externos")
        self.var_total.set(str(alojados + externos) if ok1 and ok2 else "—")

    def cargar_alojados(self):
        correcto, filas = raciones.alojados_activos(self.buscar_alojado.get())
        if not correcto:
            messagebox.showerror("Error", filas)
            return
        vaciar_tabla(self.tabla_alojados)
        for f in filas:
            self.tabla_alojados.insert("", tk.END, iid=str(f["id_beneficiario"]), values=(f["codigo"], f["nombre"]))

    def marcar_asistencia(self):
        marcados = len(self.tabla_alojados.selection())
        if marcados == 0:
            messagebox.showwarning("Selección necesaria", "Seleccione en la lista a los alojados que recibieron su ración.")
            return
        self.var_alojados.set(str(marcados))

    # ================= SECCION B =================
    def crear_seccion_b(self):
        b = self.seccion_b
        b.columnconfigure(0, weight=1)
        tk.Label(b, text="Alimentos para lote de raciones actuales", bg="white", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w")

        fila = tk.Frame(b, bg="white")
        fila.grid(row=1, column=0, sticky="ew", pady=(6, 8))
        tk.Label(fila, text="Alimento", bg="white").grid(row=0, column=0, sticky="w")
        tk.Label(fila, text="Cantidad usada", bg="white").grid(row=0, column=1, sticky="w")
        tk.Label(fila, text="Unidad", bg="white").grid(row=0, column=2, sticky="w")
        self.alimento = ttk.Combobox(fila, state="readonly", width=34)
        self.alimento.grid(row=1, column=0, padx=(0, 10))
        self.alimento.bind("<<ComboboxSelected>>", self.cambio_alimento)
        self.cantidad = tk.Entry(fila, width=10)
        self.cantidad.grid(row=1, column=1, padx=(0, 10))
        self.lbl_unidad = tk.Label(fila, text="", bg="white", width=8, anchor="w")
        self.lbl_unidad.grid(row=1, column=2, padx=(0, 10))
        tk.Button(fila, text="Agregar a la lista", command=self.agregar_a_lista).grid(row=1, column=3)

        tk.Label(b, text="Lista de ingredientes y lotes SUGERIDOS (FEFO: primero vence, primero sale)",
                 bg="white").grid(row=2, column=0, sticky="w")
        marco_tabla, self.tabla_lineas = crear_tabla(b, [
            ("alimento", "Alimento", 130), ("cantidad", "Cantidad", 70), ("unidad", "Unidad", 60),
            ("lote", "Lote sugerido", 190), ("estado", "Estado", 90)], altura=8)
        marco_tabla.grid(row=3, column=0, sticky="nsew", pady=(4, 6))
        b.rowconfigure(3, weight=1)

        botones = tk.Frame(b, bg="white")
        botones.grid(row=4, column=0, sticky="w")
        tk.Button(botones, text="Confirmar lote", command=self.confirmar_lote, padx=10).pack(side="left")
        tk.Button(botones, text="Cambiar lote", command=self.cambiar_lote, padx=10).pack(side="left", padx=8)
        tk.Button(botones, text="Eliminar", command=self.quitar_linea, padx=10).pack(side="left")
        self.lbl_total_lineas = tk.Label(b, text="Total de alimentos en lista: 0", bg="white", font=("Arial", 9, "bold"))
        self.lbl_total_lineas.grid(row=5, column=0, sticky="w", pady=(6, 0))

    def cargar_alimentos(self):
        correcto, filas = inventarios.stock_por_alimento()
        if not correcto:
            messagebox.showerror("Error", filas)
            return
        self.mapa_alimentos = {f"{f['nombre']} - stock {f['stock']:.2f} {f['unidad']}": f for f in filas}
        self.alimento["values"] = tuple(self.mapa_alimentos)
        self.alimento.set("")
        self.lbl_unidad.config(text="")

    def cambio_alimento(self, evento=None):
        datos = self.mapa_alimentos.get(self.alimento.get())
        self.lbl_unidad.config(text=datos["unidad"] if datos else "")

    def reservado(self):
        """Cantidad ya usada de cada lote por las lineas de la lista."""
        total = {}
        for linea in self.lineas:
            total[linea["id_inventario"]] = total.get(linea["id_inventario"], Decimal("0")) + linea["cantidad"]
        return total

    def agregar_a_lista(self):
        datos = self.mapa_alimentos.get(self.alimento.get())
        if datos is None:
            messagebox.showwarning("Campo vacío", "Seleccione un alimento.")
            return
        correcto, cantidad = validar_cantidad(self.cantidad.get(), "La cantidad usada")
        if not correcto:
            messagebox.showwarning("Dato inválido", cantidad)
            return
        correcto, propuesta = inventarios.sugerir_lotes(datos["id_alimento"], cantidad, self.reservado())
        if not correcto:
            messagebox.showwarning("Stock insuficiente", propuesta)
            return
        for lote, usar in propuesta:
            self.lineas.append({
                "id_inventario": lote["id_inventario"], "id_alimento": datos["id_alimento"],
                "alimento": datos["nombre"], "unidad": datos["unidad"], "cantidad": usar,
                "lote": lote["lote"], "vence": lote["fecha_vencimiento"], "confirmado": False})
        self.cantidad.delete(0, tk.END)
        self.dibujar_lineas()

    def dibujar_lineas(self):
        vaciar_tabla(self.tabla_lineas)
        for i, l in enumerate(self.lineas):
            lote = f"{l['lote']} · vence {fecha_texto(l['vence'], 'sin vencimiento')}"
            self.tabla_lineas.insert("", tk.END, iid=str(i), values=(
                l["alimento"], f"{l['cantidad']:.2f}", l["unidad"], lote,
                "Confirmado" if l["confirmado"] else "Sugerido"))
        self.lbl_total_lineas.config(text=f"Total de alimentos en lista: {len(self.lineas)}")

    def linea_seleccionada(self):
        seleccion = self.tabla_lineas.selection()
        if not seleccion:
            messagebox.showwarning("Selección necesaria", "Seleccione una fila de la lista.")
            return None
        return int(seleccion[0])

    def confirmar_lote(self):
        indice = self.linea_seleccionada()
        if indice is not None:
            self.lineas[indice]["confirmado"] = True
            self.dibujar_lineas()

    def quitar_linea(self):
        indice = self.linea_seleccionada()
        if indice is not None:
            del self.lineas[indice]
            self.dibujar_lineas()

    def cambiar_lote(self):
        indice = self.linea_seleccionada()
        if indice is None:
            return
        linea = self.lineas[indice]
        correcto, lotes = inventarios.lotes_alimento(linea["id_alimento"])
        if not correcto:
            messagebox.showerror("Error", lotes)
            return
        # lo que ya usan las OTRAS lineas de cada lote
        otras = {}
        for i, l in enumerate(self.lineas):
            if i != indice:
                otras[l["id_inventario"]] = otras.get(l["id_inventario"], Decimal("0")) + l["cantidad"]
        opciones = {}
        for lote in lotes:
            libre = Decimal(lote["cantidad"]) - otras.get(lote["id_inventario"], Decimal("0"))
            if libre >= linea["cantidad"]:
                texto = f"{lote['lote']} · vence {fecha_texto(lote['fecha_vencimiento'], 'sin vencimiento')} · disponible {libre:.2f}"
                opciones[texto] = lote
        if not opciones:
            messagebox.showwarning("Sin lotes", "Ningún otro lote tiene stock suficiente para esta cantidad.")
            return

        ventana = tk.Toplevel(self)
        ventana.title("Cambiar lote")
        ventana.configure(bg="white", padx=20, pady=15)
        ventana.grab_set()
        tk.Label(ventana, text=f"{linea['alimento']} - {linea['cantidad']:.2f} {linea['unidad']}",
                 bg="white", font=("Arial", 10, "bold")).pack(anchor="w")
        tk.Label(ventana, text="Lote realmente utilizado", bg="white").pack(anchor="w", pady=(8, 2))
        combo = ttk.Combobox(ventana, values=tuple(opciones), state="readonly", width=60)
        combo.pack()

        def aceptar():
            lote = opciones.get(combo.get())
            if lote is None:
                messagebox.showwarning("Campo vacío", "Seleccione un lote.", parent=ventana)
                return
            linea.update({"id_inventario": lote["id_inventario"], "lote": lote["lote"],
                          "vence": lote["fecha_vencimiento"], "confirmado": True})
            ventana.destroy()
            self.dibujar_lineas()

        botones = tk.Frame(ventana, bg="white")
        botones.pack(anchor="e", pady=(12, 0))
        tk.Button(botones, text="Aceptar", command=aceptar, padx=14).pack(side="left", padx=(0, 8))
        tk.Button(botones, text="Cancelar", command=ventana.destroy, padx=14).pack(side="left")

    # ================= confirmar todo =================
    def confirmar_registro(self):
        correcto, fecha = validar_fecha(self.fecha.get(), "La fecha de atención", permitir_futura=False)
        if not correcto:
            messagebox.showwarning("Dato inválido", fecha)
            return
        if not self.tipo_comida.get():
            messagebox.showwarning("Campo vacío", "Seleccione el tipo de comida.")
            return
        ok1, alojados = validar_entero(self.var_alojados.get(), "Alojados")
        ok2, externos = validar_entero(self.var_externos.get(), "Externos")
        if not ok1 or not ok2:
            messagebox.showwarning("Dato inválido", alojados if not ok1 else externos)
            return
        if alojados + externos == 0:
            messagebox.showwarning("Sin raciones", "Ingrese la cantidad de raciones entregadas.")
            return
        if not self.lineas:
            messagebox.showwarning("Lista vacía", "Agregue los alimentos usados en la preparación.")
            return
        sin_confirmar = [l for l in self.lineas if not l["confirmado"]]
        if sin_confirmar and not messagebox.askyesno(
                "Lotes sin confirmar",
                f"Hay {len(sin_confirmar)} lote(s) solo sugeridos. ¿Usar los lotes sugeridos?"):
            return

        consumo = [(l["id_inventario"], l["cantidad"]) for l in self.lineas]
        correcto, resultado = raciones.registrar_raciones(
            fecha, self.tipo_comida.get(), alojados, externos, self.observaciones.get(), consumo)
        if correcto:
            self.limpiar()
            self.al_mostrar()
        else:
            messagebox.showerror("No se pudo registrar", resultado)

    def limpiar(self):
        self.lineas = []
        self.dibujar_lineas()
        self.var_alojados.set("0")
        self.var_externos.set("0")
        self.observaciones.delete(0, tk.END)
        self.cantidad.delete(0, tk.END)
        self.tabla_alojados.selection_remove(self.tabla_alojados.selection())

    # ================= datos de cabecera =================
    def cargar_planificacion(self):
        correcto, p = raciones.promedio_historico(7)
        if correcto:
            for clave, etiqueta in self.lbl_plan.items():
                etiqueta.config(text=str(p.get(clave, 0)))

    def al_mostrar(self):
        if not self.fecha.get().strip():
            self.fecha.insert(0, fecha_a_texto(date.today()))
        if not self.tipo_comida.get():
            self.tipo_comida.set(raciones.COMIDAS[1])
        self.cargar_planificacion()
        self.cargar_alimentos()
        self.cargar_alojados()
        correcto, disponibles = inventarios.raciones_disponibles()
        if correcto:
            self.lbl_disponibles.config(text=f"Raciones disponibles según inventario: {disponibles}")
