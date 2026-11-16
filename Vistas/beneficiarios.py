from datetime import datetime

import tkinter as tk
from tkinter import messagebox, ttk

# Importa las funciones necesarias para que la vista trabaje con MySQL
from Funciones.beneficiarios import (
    actualizar_beneficiario,
    guardar_registro,
    obtener_beneficiario,
    obtener_beneficiarios,
    retirar_beneficiario,
)


# Pantalla de beneficiarios dentro de la aplicacion principal
class Beneficiarios(tk.Frame):
    def __init__(self, padre, controlador):
        super().__init__(padre, bg="white")
        self.controlador = controlador

        # Guarda el id cuando se esta editando un beneficiario
        self.beneficiario_editando = {"id": None}

        # Contenedor general de las dos mitades de la pantalla
        contenido = tk.Frame(self, bg="white", padx=30, pady=25)
        contenido.pack(fill="both", expand=True)

        # Mitad izquierda: formulario para crear o editar
        self.formulario = tk.Frame(contenido, bg="white", padx=10, pady=10)
        self.formulario.pack(side="left", fill="both", expand=True)

        # Mitad derecha: busqueda y tabla de beneficiarios
        self.lista = tk.Frame(contenido, bg="white", padx=10, pady=10)
        self.lista.pack(side="left", fill="both", expand=True)

        self.crear_formulario()
        self.crear_lista()

        # Permite que las dos columnas y observaciones se expandan
        self.formulario.columnconfigure(0, weight=1)
        self.formulario.columnconfigure(1, weight=1)
        self.formulario.rowconfigure(12, weight=1)

        # Carga todos los beneficiarios al abrir la pantalla
        self.cargar_lista()

    def crear_formulario(self):
        # Titulo y campos del formulario
        tk.Label(
            self.formulario,
            text="Nuevo beneficiario",
            bg="white",
            font=("Arial", 20, "bold")
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 25))

        tk.Label(self.formulario, text="Código", bg="white").grid(
            row=1, column=0, sticky="w", padx=(0, 15)
        )
        tk.Label(self.formulario, text="Nombres*", bg="white").grid(
            row=1, column=1, sticky="w"
        )

        self.codigo = tk.Entry(self.formulario)
        self.codigo.grid(
            row=2, column=0, sticky="ew", padx=(0, 15), pady=(5, 15)
        )

        self.nombres = tk.Entry(self.formulario)
        self.nombres.grid(row=2, column=1, sticky="ew", pady=(5, 15))

        tk.Label(self.formulario, text="Apellido paterno*", bg="white").grid(
            row=3, column=0, sticky="w", padx=(0, 15)
        )
        tk.Label(self.formulario, text="Apellido materno", bg="white").grid(
            row=3, column=1, sticky="w"
        )

        self.apellido_paterno = tk.Entry(self.formulario)
        self.apellido_paterno.grid(
            row=4, column=0, sticky="ew", padx=(0, 15), pady=(5, 15)
        )

        self.apellido_materno = tk.Entry(self.formulario)
        self.apellido_materno.grid(
            row=4, column=1, sticky="ew", pady=(5, 15)
        )

        tk.Label(self.formulario, text="Tipo de documento", bg="white").grid(
            row=5, column=0, sticky="w", padx=(0, 15)
        )
        tk.Label(
            self.formulario,
            text="Número de documento*",
            bg="white"
        ).grid(row=5, column=1, sticky="w")

        self.tipo_documento = ttk.Combobox(
            self.formulario,
            values=("Carnet de identidad", "Pasaporte", "Otro"),
            state="readonly"
        )
        self.tipo_documento.set("Carnet de identidad")
        self.tipo_documento.grid(
            row=6, column=0, sticky="ew", padx=(0, 15), pady=(5, 15)
        )

        self.numero_documento = tk.Entry(self.formulario)
        self.numero_documento.grid(
            row=6, column=1, sticky="ew", pady=(5, 15)
        )

        tk.Label(
            self.formulario,
            text="Fecha de nacimiento (dd/mm/aaaa)",
            bg="white"
        ).grid(row=7, column=0, sticky="w", padx=(0, 15))
        tk.Label(self.formulario, text="Teléfono", bg="white").grid(
            row=7, column=1, sticky="w"
        )

        self.fecha_nacimiento = tk.Entry(self.formulario)
        self.fecha_nacimiento.grid(
            row=8, column=0, sticky="ew", padx=(0, 15), pady=(5, 15)
        )

        self.telefono = tk.Entry(self.formulario)
        self.telefono.grid(row=8, column=1, sticky="ew", pady=(5, 15))

        tk.Label(self.formulario, text="Dirección", bg="white").grid(
            row=9, column=0, columnspan=2, sticky="w"
        )
        self.direccion = tk.Entry(self.formulario)
        self.direccion.grid(
            row=10, column=0, columnspan=2, sticky="ew", pady=(5, 15)
        )

        tk.Label(self.formulario, text="Observaciones", bg="white").grid(
            row=11, column=0, columnspan=2, sticky="w"
        )
        self.observaciones = tk.Text(self.formulario, height=4)
        self.observaciones.grid(
            row=12, column=0, columnspan=2, sticky="nsew", pady=(5, 20)
        )

        # Boton para guardar o actualizar segun el modo actual
        self.boton_guardar = tk.Button(
            self.formulario,
            text="Guardar",
            bg="#222222",
            fg="white",
            command=self.guardar_desde_formulario,
            padx=20,
            pady=8
        )
        self.boton_guardar.grid(row=13, column=0, sticky="w")

        # Boton que limpia el formulario cuando el usuario lo solicita
        tk.Button(
            self.formulario,
            text="Limpiar",
            command=self.limpiar_formulario,
            padx=20,
            pady=8
        ).grid(row=13, column=0, sticky="w", padx=(145, 0))

    def crear_lista(self):
        # Boton para volver al panel principal
        tk.Button(
            self.lista,
            text="← Menú principal",
            command=self.volver_principal
        ).pack(anchor="e", pady=(0, 10))

        tk.Label(
            self.lista,
            text="Beneficiarios",
            bg="white",
            font=("Arial", 20, "bold")
        ).pack(anchor="w", pady=(0, 25))

        tk.Label(
            self.lista,
            text="Buscar por nombre o documento",
            bg="white",
            font=("Arial", 12, "bold")
        ).pack(anchor="w")

        self.busqueda = tk.Entry(self.lista)
        self.busqueda.pack(fill="x", pady=(5, 15))
        self.busqueda.bind("<KeyRelease>", self.cargar_lista)

        # Tabla que muestra solo codigo, nombre, documento y estado
        self.tabla = ttk.Treeview(
            self.lista,
            columns=("codigo", "nombre", "documento", "estado"),
            show="headings",
            selectmode="browse"
        )
        self.tabla.heading("codigo", text="Código")
        self.tabla.heading("nombre", text="Nombre completo")
        self.tabla.heading("documento", text="Documento")
        self.tabla.heading("estado", text="Estado")
        self.tabla.column("codigo", width=110)
        self.tabla.column("nombre", width=220)
        self.tabla.column("documento", width=130)
        self.tabla.column("estado", width=100)
        self.tabla.pack(fill="both", expand=True)

        # Botones que actuan sobre la fila seleccionada
        botones_lista = tk.Frame(self.lista, bg="white")
        botones_lista.pack(anchor="w", pady=(15, 0))

        tk.Button(
            botones_lista,
            text="Editar",
            command=self.editar_seleccionado,
            padx=20,
            pady=8
        ).grid(row=0, column=0)

        tk.Button(
            botones_lista,
            text="Eliminar",
            command=self.eliminar_seleccionado,
            padx=20,
            pady=8
        ).grid(row=0, column=1, padx=(15, 0))

    # Se llama cada vez que App muestra esta pantalla
    def al_mostrar(self):
        self.cargar_lista()

    # Regresa al panel principal cuando existe un controlador
    def volver_principal(self):
        if hasattr(self.controlador, "mostrar"):
            self.controlador.mostrar("Principal")
        else:
            self.master.destroy()

    # Obtiene el contenido actual de todas las cajas del formulario
    def obtener_datos_formulario(self):
        return (
            self.codigo.get().strip(),
            self.nombres.get().strip(),
            self.apellido_paterno.get().strip(),
            self.apellido_materno.get().strip(),
            self.tipo_documento.get().strip(),
            self.numero_documento.get().strip(),
            self.fecha_nacimiento.get().strip(),
            self.telefono.get().strip(),
            self.direccion.get().strip(),
            self.observaciones.get("1.0", tk.END).strip()
        )

    # Todos los campos son obligatorios excepto observaciones
    def formulario_valido(self, datos):
        return all(datos[:-1]) and datos[6] != "dd/mm/aaaa"

    # Limpia el formulario y lo prepara para un nuevo registro
    def limpiar_formulario(self):
        for campo in (
            self.codigo,
            self.nombres,
            self.apellido_paterno,
            self.apellido_materno,
            self.numero_documento,
            self.telefono,
            self.direccion
        ):
            campo.delete(0, tk.END)

        self.tipo_documento.set("Carnet de identidad")
        self.fecha_nacimiento.delete(0, tk.END)
        self.observaciones.delete("1.0", tk.END)
        self.beneficiario_editando["id"] = None
        self.boton_guardar.config(text="Guardar")

    # Consulta la base y actualiza las filas visibles de la tabla
    def cargar_lista(self, event=None):
        correcto, resultado = obtener_beneficiarios(
            self.busqueda.get().strip()
        )

        if not correcto:
            messagebox.showerror("Error", resultado)
            return

        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        for beneficiario in resultado:
            (
                id_beneficiario,
                codigo_fila,
                nombre_completo,
                documento,
                estado
            ) = beneficiario
            self.tabla.insert(
                "",
                tk.END,
                iid=str(id_beneficiario),
                values=(codigo_fila, nombre_completo, documento, estado)
            )

    # Carga en el formulario los datos de la fila seleccionada
    def editar_seleccionado(self):
        seleccion = self.tabla.selection()

        if not seleccion:
            messagebox.showwarning(
                "Selección necesaria",
                "Selecciona un beneficiario de la tabla."
            )
            return

        correcto, resultado = obtener_beneficiario(int(seleccion[0]))

        if not correcto:
            messagebox.showerror("Error", resultado)
            return

        (
            id_beneficiario,
            valor_codigo,
            valor_nombres,
            valor_apellido_paterno,
            valor_apellido_materno,
            valor_tipo_documento,
            valor_numero_documento,
            valor_fecha_nacimiento,
            valor_telefono,
            valor_direccion,
            valor_observaciones
        ) = resultado

        self.limpiar_formulario()
        self.beneficiario_editando["id"] = id_beneficiario
        self.codigo.insert(0, valor_codigo)
        self.nombres.insert(0, valor_nombres)
        self.apellido_paterno.insert(0, valor_apellido_paterno)
        self.apellido_materno.insert(0, valor_apellido_materno or "")
        self.tipo_documento.set(valor_tipo_documento)
        self.numero_documento.insert(0, valor_numero_documento)
        self.fecha_nacimiento.delete(0, tk.END)
        self.fecha_nacimiento.insert(
            0,
            valor_fecha_nacimiento.strftime("%d/%m/%Y")
            if valor_fecha_nacimiento
            else ""
        )
        self.telefono.insert(0, valor_telefono or "")
        self.direccion.insert(0, valor_direccion or "")
        self.observaciones.insert("1.0", valor_observaciones or "")
        self.boton_guardar.config(text="Actualizar")

    # Cambia el registro seleccionado a estado RETIRADO
    def eliminar_seleccionado(self):
        seleccion = self.tabla.selection()

        if not seleccion:
            messagebox.showwarning(
                "Selección necesaria",
                "Selecciona un beneficiario de la tabla."
            )
            return

        confirmar = messagebox.askyesno(
            "Confirmar retiro",
            "¿Quieres marcar este beneficiario como retirado?"
        )

        if not confirmar:
            return

        correcto, error = retirar_beneficiario(int(seleccion[0]))

        if correcto:
            messagebox.showinfo("Éxito", "Beneficiario marcado como retirado.")
            self.cargar_lista()
        else:
            messagebox.showerror("Error", error)

    # Guarda un registro nuevo o actualiza el registro en edicion
    def guardar_desde_formulario(self):
        datos = self.obtener_datos_formulario()

        if not self.formulario_valido(datos):
            messagebox.showwarning(
                "Campos vacíos",
                "Completa todos los campos excepto observaciones."
            )
            return

        try:
            fecha = datetime.strptime(datos[6], "%d/%m/%Y").date()
        except ValueError:
            messagebox.showwarning(
                "Fecha inválida",
                "Usa el formato dd/mm/aaaa."
            )
            return

        datos = datos[:6] + (fecha,) + datos[7:]

        if self.beneficiario_editando["id"] is None:
            guardado, error = guardar_registro(*datos)
        else:
            guardado, error = actualizar_beneficiario(
                self.beneficiario_editando["id"],
                *datos
            )

        if guardado:
            messagebox.showinfo("Éxito", "Datos guardados correctamente.")
            self.limpiar_formulario()
            self.cargar_lista()
        else:
            messagebox.showerror(
                "Error",
                f"No se pudieron guardar los datos: {error}"
            )
