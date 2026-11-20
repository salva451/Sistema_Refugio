import tkinter as tk
from tkinter import messagebox, ttk

from Funciones.habitaciones import crear_habitacion, obtener_habitaciones
from Funciones.camas import (
    cambiar_estado_cama,
    crear_cama,
    obtener_camas,
    resumen_habitacion,
)


class HabitacionesCamas(tk.Frame):
    def __init__(self, padre, controlador):
        super().__init__(padre, bg="white")
        self.controlador = controlador

        marco = tk.Frame(self, bg="white", padx=30, pady=25)
        marco.pack(fill="both", expand=True)

        izquierda = tk.Frame(marco, bg="white")
        izquierda.pack(side="left", fill="both", expand=True, padx=(0, 15))
        derecha = tk.Frame(marco, bg="white")
        derecha.pack(side="left", fill="both", expand=True, padx=(15, 0))

        tk.Button(
            derecha,
            text="← Menú principal",
            command=lambda: controlador.mostrar("Principal")
        ).pack(anchor="e")

        tk.Label(
            izquierda,
            text="Habitaciones y camas",
            bg="white",
            font=("Arial", 20, "bold")
        ).pack(anchor="w", pady=(0, 15))

        tk.Label(izquierda, text="Número de habitación*", bg="white").pack(anchor="w")
        self.numero_habitacion = tk.Entry(izquierda)
        self.numero_habitacion.pack(fill="x", pady=(5, 10))

        tk.Label(izquierda, text="Descripción", bg="white").pack(anchor="w")
        self.descripcion_habitacion = tk.Entry(izquierda)
        self.descripcion_habitacion.pack(fill="x", pady=(5, 10))

        tk.Button(
            izquierda,
            text="Crear habitación",
            command=self.crear_habitacion,
            padx=20,
            pady=8
        ).pack(anchor="w", pady=(0, 15))

        tk.Label(
            izquierda,
            text="Habitaciones",
            bg="white",
            font=("Arial", 12, "bold")
        ).pack(anchor="w")
        self.lista_habitaciones = ttk.Treeview(
            izquierda,
            columns=("codigo", "numero", "camas"),
            show="headings",
            selectmode="browse",
            height=8
        )
        self.lista_habitaciones.heading("codigo", text="Código")
        self.lista_habitaciones.heading("numero", text="Número")
        self.lista_habitaciones.heading("camas", text="N.º de camas")
        self.lista_habitaciones.column("codigo", width=90)
        self.lista_habitaciones.column("numero", width=140)
        self.lista_habitaciones.column("camas", width=100)
        self.lista_habitaciones.pack(fill="both", expand=True)
        self.lista_habitaciones.bind("<<TreeviewSelect>>", self.seleccionar_habitacion)

        tk.Label(
            derecha,
            text="Camas",
            bg="white",
            font=("Arial", 20, "bold")
        ).pack(anchor="w", pady=(45, 15))

        self.resumen = tk.Label(
            derecha,
            text="Selecciona una habitación",
            bg="white",
            font=("Arial", 11, "bold")
        )
        self.resumen.pack(anchor="w", pady=(0, 10))

        tk.Button(
            derecha,
            text="Agregar cama",
            command=self.agregar_cama,
            padx=20,
            pady=8
        ).pack(anchor="w", pady=(0, 10))

        self.tabla_camas = ttk.Treeview(
            derecha,
            columns=("codigo", "estado"),
            show="headings",
            selectmode="browse",
            height=10
        )
        self.tabla_camas.heading("codigo", text="Código")
        self.tabla_camas.heading("estado", text="Estado")
        self.tabla_camas.column("codigo", width=120)
        self.tabla_camas.column("estado", width=180)
        self.tabla_camas.pack(fill="both", expand=True)

        controles = tk.Frame(derecha, bg="white")
        controles.pack(anchor="w", pady=(10, 0))
        tk.Button(
            controles,
            text="Disponible",
            command=lambda: self.cambiar_estado("HABILITADA")
        ).grid(row=0, column=0)
        tk.Button(
            controles,
            text="Mantenimiento",
            command=lambda: self.cambiar_estado("MANTENIMIENTO")
        ).grid(row=0, column=1, padx=5)
        tk.Button(
            controles,
            text="Inactiva",
            command=lambda: self.cambiar_estado("INACTIVA")
        ).grid(row=0, column=2)

        self.id_habitacion = None
        self.cargar_habitaciones()

    def al_mostrar(self):
        self.cargar_habitaciones()

    def cargar_habitaciones(self):
        correcto, resultado = obtener_habitaciones()
        if not correcto:
            messagebox.showerror("Error", resultado)
            return
        for fila in self.lista_habitaciones.get_children():
            self.lista_habitaciones.delete(fila)
        for id_habitacion, codigo, numero, descripcion, total_camas in resultado:
            self.lista_habitaciones.insert(
                "", tk.END, iid=str(id_habitacion),
                values=(codigo, numero, total_camas)
            )

    def crear_habitacion(self):
        numero = self.numero_habitacion.get().strip()
        descripcion = self.descripcion_habitacion.get().strip()
        if not numero:
            messagebox.showwarning("Dato necesario", "Ingresa el número de habitación.")
            return
        correcto, resultado = crear_habitacion(numero, descripcion)
        if correcto:
            messagebox.showinfo("Éxito", "Habitación creada correctamente.")
            self.numero_habitacion.delete(0, tk.END)
            self.descripcion_habitacion.delete(0, tk.END)
            self.cargar_habitaciones()
        else:
            messagebox.showerror("Error", resultado)

    def seleccionar_habitacion(self, event=None):
        seleccion = self.lista_habitaciones.selection()
        if seleccion:
            self.id_habitacion = int(seleccion[0])
            self.cargar_camas()

    def agregar_cama(self):
        if self.id_habitacion is None:
            messagebox.showwarning("Selección necesaria", "Selecciona una habitación.")
            return
        correcto, resultado = crear_cama(self.id_habitacion)
        if correcto:
            messagebox.showinfo("Éxito", f"Cama creada: {resultado}")
            self.cargar_camas()
            self.cargar_habitaciones()
            self.lista_habitaciones.selection_set(str(self.id_habitacion))
        else:
            messagebox.showerror("Error", resultado)

    def cargar_camas(self):
        if self.id_habitacion is None:
            return
        correcto, resultado = obtener_camas(self.id_habitacion)
        if not correcto:
            messagebox.showerror("Error", resultado)
            return
        for fila in self.tabla_camas.get_children():
            self.tabla_camas.delete(fila)
        for id_cama, codigo, estado in resultado:
            self.tabla_camas.insert(
                "", tk.END, iid=str(id_cama),
                values=(codigo, estado)
            )

        correcto_resumen, resumen = resumen_habitacion(self.id_habitacion)
        if correcto_resumen:
            self.resumen.config(
                text=(
                    f"Total: {resumen['total']} | "
                    f"Disponibles: {resumen['disponibles']} | "
                    f"Ocupadas: {resumen['ocupadas']} | "
                    f"Mantenimiento: {resumen['mantenimiento']} | "
                    f"Inactivas: {resumen['inactivas']}"
                )
            )

    def cambiar_estado(self, nuevo_estado):
        seleccion = self.tabla_camas.selection()
        if not seleccion:
            messagebox.showwarning("Selección necesaria", "Selecciona una cama.")
            return
        correcto, resultado = cambiar_estado_cama(int(seleccion[0]), nuevo_estado)
        if correcto:
            messagebox.showinfo("Éxito", "Estado actualizado.")
            self.cargar_camas()
        else:
            messagebox.showerror("Error", resultado)