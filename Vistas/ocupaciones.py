import tkinter as tk
from tkinter import messagebox, ttk

from Funciones.habitaciones import obtener_habitaciones
from Funciones.camas import resumen_habitacion
from Funciones.ocupaciones import (
    asignar,
    obtener_beneficiarios_alojados,
    obtener_camas_disponibles,
    obtener_ocupaciones_activas,
    registrar_salida,
)


class Ocupaciones(tk.Frame):
    def __init__(self, padre, controlador):
        super().__init__(padre, bg="white")
        self.controlador = controlador

        marco = tk.Frame(self, bg="white", padx=30, pady=25)
        marco.pack(fill="both", expand=True)

        tk.Button(
            marco,
            text="← Menú principal",
            command=lambda: controlador.mostrar("Principal")
        ).pack(anchor="e")
        tk.Label(
            marco,
            text="Ocupaciones",
            bg="white",
            font=("Arial", 20, "bold")
        ).pack(anchor="w", pady=(0, 15))

        asignacion = tk.Frame(marco, bg="white")
        asignacion.pack(fill="x", pady=(0, 15))

        tk.Label(asignacion, text="Beneficiario alojado", bg="white").grid(
            row=0, column=0, sticky="w"
        )
        tk.Label(asignacion, text="Habitación", bg="white").grid(
            row=0, column=1, sticky="w", padx=(15, 0)
        )
        tk.Label(asignacion, text="Cama disponible", bg="white").grid(
            row=0, column=2, sticky="w", padx=(15, 0)
        )

        self.beneficiarios = ttk.Combobox(asignacion, state="readonly", width=35)
        self.beneficiarios.grid(row=1, column=0, sticky="ew", pady=(5, 0))
        self.habitaciones = ttk.Combobox(asignacion, state="readonly", width=18)
        self.habitaciones.grid(row=1, column=1, sticky="ew", padx=(15, 0), pady=(5, 0))
        self.habitaciones.bind("<<ComboboxSelected>>", self.habitacion_seleccionada)
        self.camas = ttk.Combobox(asignacion, state="readonly", width=35)
        self.camas.grid(row=1, column=2, sticky="ew", padx=(15, 0), pady=(5, 0))
        asignacion.columnconfigure(0, weight=1)
        asignacion.columnconfigure(1, weight=1)
        asignacion.columnconfigure(2, weight=1)

        self.resumen_habitacion = tk.Label(
            asignacion,
            text="Selecciona una habitación",
            bg="white",
            font=("Arial", 11, "bold"),
            fg="#1f4e78"
        )
        self.resumen_habitacion.grid(
            row=2, column=0, columnspan=3, sticky="w", pady=(12, 0)
        )

        tk.Button(
            asignacion,
            text="Asignar cama",
            command=self.asignar_cama,
            padx=20,
            pady=8
        ).grid(row=3, column=0, sticky="w", pady=(10, 0))

        tk.Label(
            marco,
            text="Ocupaciones activas",
            bg="white",
            font=("Arial", 12, "bold")
        ).pack(anchor="w")

        self.tabla = ttk.Treeview(
            marco,
            columns=("codigo", "cama", "habitacion", "beneficiario", "ingreso"),
            show="headings",
            selectmode="browse"
        )
        for nombre, texto in (
            ("codigo", "Código"),
            ("cama", "Cama"),
            ("habitacion", "Habitación"),
            ("beneficiario", "Beneficiario"),
            ("ingreso", "Ingreso"),
        ):
            self.tabla.heading(nombre, text=texto)
        self.tabla.column("codigo", width=90)
        self.tabla.column("cama", width=90)
        self.tabla.column("habitacion", width=100)
        self.tabla.column("beneficiario", width=220)
        self.tabla.column("ingreso", width=180)
        self.tabla.pack(fill="both", expand=True, pady=(5, 10))

        tk.Button(
            marco,
            text="Registrar salida",
            command=self.registrar_salida,
            padx=20,
            pady=8
        ).pack(anchor="w")

        self.beneficiarios_datos = {}
        self.camas_datos = {}
        self.habitaciones_datos = {}
        self.cargar()

    def al_mostrar(self):
        self.cargar()

    def cargar(self):
        correcto, resultado = obtener_beneficiarios_alojados()
        if not correcto:
            messagebox.showerror("Error", resultado)
            return
        self.beneficiarios_datos = {}
        etiquetas = []
        for id_persona, codigo, nombre in resultado:
            etiqueta = f"{codigo} - {nombre}"
            etiquetas.append(etiqueta)
            self.beneficiarios_datos[etiqueta] = id_persona
        self.beneficiarios["values"] = etiquetas
        if etiquetas:
            self.beneficiarios.set(etiquetas[0])
        else:
            self.beneficiarios.set("")

        correcto, resultado = obtener_habitaciones()
        if not correcto:
            messagebox.showerror("Error", resultado)
            return
        self.habitaciones_datos = {}
        etiquetas_habitaciones = []
        for id_habitacion, codigo, numero, descripcion, total_camas in resultado:
            etiqueta = f"{numero} - {codigo} ({total_camas} camas)"
            etiquetas_habitaciones.append(etiqueta)
            self.habitaciones_datos[etiqueta] = id_habitacion
        self.habitaciones["values"] = etiquetas_habitaciones
        if etiquetas_habitaciones:
            self.habitaciones.set(etiquetas_habitaciones[0])
            self.cargar_camas_habitacion()
        else:
            self.habitaciones.set("")
            self.camas.set("")
            self.camas["values"] = ()

        correcto, resultado = obtener_ocupaciones_activas()
        if not correcto:
            messagebox.showerror("Error", resultado)
            return
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)
        for id_ocupacion, codigo, cama, habitacion, beneficiario, ingreso in resultado:
            self.tabla.insert(
                "", tk.END, iid=str(id_ocupacion),
                values=(codigo, cama, habitacion, beneficiario, ingreso)
            )

    def cargar_camas_habitacion(self):
        etiqueta = self.habitaciones.get()
        if not etiqueta:
            self.camas.set("")
            self.camas["values"] = ()
            self.resumen_habitacion.config(text="Selecciona una habitación")
            return

        id_habitacion = self.habitaciones_datos[etiqueta]
        correcto, resultado = obtener_camas_disponibles(id_habitacion)
        if not correcto:
            messagebox.showerror("Error", resultado)
            return
        self.camas_datos = {}
        etiquetas = []
        for id_cama, codigo, numero_habitacion in resultado:
            etiqueta_cama = f"{codigo}"
            etiquetas.append(etiqueta_cama)
            self.camas_datos[etiqueta_cama] = id_cama
        self.camas["values"] = etiquetas
        if etiquetas:
            self.camas.set(etiquetas[0])
        else:
            self.camas.set("")

        correcto, resumen = resumen_habitacion(id_habitacion)
        if correcto:
            self.resumen_habitacion.config(
                text=(
                    f"Total: {resumen['total']} | "
                    f"Disponibles: {resumen['disponibles']} | "
                    f"Ocupadas: {resumen['ocupadas']} | "
                    f"Mantenimiento: {resumen['mantenimiento']} | "
                    f"Inactivas: {resumen['inactivas']}"
                )
            )

    def habitacion_seleccionada(self, event=None):
        self.cargar_camas_habitacion()

    def asignar_cama(self):
        etiqueta_persona = self.beneficiarios.get()
        etiqueta_cama = self.camas.get()
        if not etiqueta_persona or not etiqueta_cama:
            messagebox.showwarning(
                "Datos necesarios",
                "Selecciona un beneficiario alojado y una cama disponible."
            )
            return
        correcto, resultado = asignar(
            self.beneficiarios_datos[etiqueta_persona],
            self.camas_datos[etiqueta_cama]
        )
        if correcto:
            self.cargar()
        else:
            messagebox.showerror("Error", resultado)

    def registrar_salida(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Selección necesaria", "Selecciona una ocupación activa.")
            return
        confirmar = messagebox.askyesno(
            "Confirmar salida",
            "¿Registrar la salida y liberar la cama?"
        )
        if not confirmar:
            return
        correcto, resultado = registrar_salida(int(seleccion[0]))
        if correcto:
            messagebox.showinfo("Éxito", "Salida registrada y cama liberada.")
            self.cargar()
        else:
            messagebox.showerror("Error", resultado)
