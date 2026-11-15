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

# Ejecuta la ventana principal de beneficiarios
def vista_beneficiarios():
    # Ventana secundaria que se abre desde el panel principal
    ventana = tk.Toplevel()
    ventana.title("Beneficiarios")
    ventana.state("zoomed")

    # Contenedor general de las dos mitades de la pantalla
    contenido = tk.Frame(ventana, padx=30, pady=25)
    contenido.pack(fill="both", expand=True)

    # Mitad izquierda: formulario para crear o editar
    formulario = tk.Frame(contenido, padx=10, pady=10)
    formulario.pack(side="left", fill="both", expand=True)

    # Mitad derecha: busqueda y tabla de beneficiarios
    lista = tk.Frame(contenido, padx=10, pady=10)
    lista.pack(side="left", fill="both", expand=True)

    # Titulo y campos del formulario parte de lleando de datos
    tk.Label(
        formulario,
        text="Nuevo beneficiario",
        font=("Arial", 20, "bold")
    ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 25))

    tk.Label(formulario, text="Código").grid(
        row=1, column=0, sticky="w", padx=(0, 15)
    )
    tk.Label(formulario, text="Nombres*").grid(
        row=1, column=1, sticky="w"
    )

    codigo = tk.Entry(formulario)
    codigo.grid(row=2, column=0, sticky="ew", padx=(0, 15), pady=(5, 15))

    nombres = tk.Entry(formulario)
    nombres.grid(row=2, column=1, sticky="ew", pady=(5, 15))

    tk.Label(formulario, text="Apellido paterno*").grid(
        row=3, column=0, sticky="w", padx=(0, 15)
    )
    tk.Label(formulario, text="Apellido materno").grid(
        row=3, column=1, sticky="w"
    )

    apellido_paterno = tk.Entry(formulario)
    apellido_paterno.grid(
        row=4, column=0, sticky="ew", padx=(0, 15), pady=(5, 15)
    )

    apellido_materno = tk.Entry(formulario)
    apellido_materno.grid(
        row=4, column=1, sticky="ew", pady=(5, 15)
    )

    tk.Label(formulario, text="Tipo de documento").grid(
        row=5, column=0, sticky="w", padx=(0, 15)
    )
    tk.Label(formulario, text="Número de documento*").grid(
        row=5, column=1, sticky="w"
    )

    tipo_documento = ttk.Combobox(
        formulario,
        values=("Carnet de identidad", "Pasaporte", "Otro"),
        state="readonly"
    )
    tipo_documento.set("Carnet de identidad")
    tipo_documento.grid(
        row=6, column=0, sticky="ew", padx=(0, 15), pady=(5, 15)
    )

    numero_documento = tk.Entry(formulario)
    numero_documento.grid(
        row=6, column=1, sticky="ew", pady=(5, 15)
    )

    tk.Label(formulario, text="Fecha de nacimiento").grid(
        row=7, column=0, sticky="w", padx=(0, 15)
    )
    tk.Label(formulario, text="Teléfono").grid(
        row=7, column=1, sticky="w"
    )

    fecha_nacimiento = tk.Entry(formulario)
    fecha_nacimiento.insert(0, "dd/mm/aaaa")
    fecha_nacimiento.grid(
        row=8, column=0, sticky="ew", padx=(0, 15), pady=(5, 15)
    )

    telefono = tk.Entry(formulario)
    telefono.grid(row=8, column=1, sticky="ew", pady=(5, 15))

    tk.Label(formulario, text="Dirección").grid(
        row=9, column=0, columnspan=2, sticky="w"
    )
    direccion = tk.Entry(formulario)
    direccion.grid(
        row=10, column=0, columnspan=2, sticky="ew", pady=(5, 15)
    )

    tk.Label(formulario, text="Observaciones").grid(
        row=11, column=0, columnspan=2, sticky="w"
    )
    observaciones = tk.Text(formulario, height=4)
    observaciones.grid(
        row=12, column=0, columnspan=2, sticky="nsew", pady=(5, 20)
    )

    # Guarda el id cuando se esta editando un beneficiario
    beneficiario_editando = {"id": None}

    # Obtiene el contenido actual de todas las cajas del formulario
    def obtener_datos_formulario():
        return (
            codigo.get().strip(),
            nombres.get().strip(),
            apellido_paterno.get().strip(),
            apellido_materno.get().strip(),
            tipo_documento.get().strip(),
            numero_documento.get().strip(),
            fecha_nacimiento.get().strip(),
            telefono.get().strip(),
            direccion.get().strip(),
            observaciones.get("1.0", tk.END).strip()
        )

    # Todos los campos son obligatorios excepto observaciones
    def formulario_valido(datos):
        return all(datos[:-1]) and datos[6] != "dd/mm/aaaa"

    # Limpia el formulario y lo prepara para un nuevo registro
    def limpiar_formulario():
        for campo in (
            codigo,
            nombres,
            apellido_paterno,
            apellido_materno,
            numero_documento,
            telefono,
            direccion
        ):
            campo.delete(0, tk.END)

        tipo_documento.set("Carnet de identidad")
        fecha_nacimiento.delete(0, tk.END)
        fecha_nacimiento.insert(0, "dd/mm/aaaa")
        observaciones.delete("1.0", tk.END)
        beneficiario_editando["id"] = None
        boton_guardar.config(text="Guardar")

    # Consulta la base y actualiza las filas visibles de la tabla
    def cargar_lista(event=None):
        correcto, resultado = obtener_beneficiarios(busqueda.get().strip())

        if not correcto:
            messagebox.showerror("Error", resultado)
            return

        for fila in tabla.get_children():
            tabla.delete(fila)

        for beneficiario in resultado:
            id_beneficiario, codigo_fila, nombre_completo, documento, estado = (
                beneficiario
            )
            tabla.insert(
                "",
                tk.END,
                iid=str(id_beneficiario),
                values=(codigo_fila, nombre_completo, documento, estado)
            )

    # Carga en el formulario los datos de la fila seleccionada
    def editar_seleccionado():
        seleccion = tabla.selection()

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

        limpiar_formulario()
        beneficiario_editando["id"] = id_beneficiario
        codigo.insert(0, valor_codigo)
        nombres.insert(0, valor_nombres)
        apellido_paterno.insert(0, valor_apellido_paterno)
        apellido_materno.insert(0, valor_apellido_materno or "")
        tipo_documento.set(valor_tipo_documento)
        numero_documento.insert(0, valor_numero_documento)
        fecha_nacimiento.delete(0, tk.END)
        fecha_nacimiento.insert(
            0,
            valor_fecha_nacimiento.strftime("%d/%m/%Y")
            if valor_fecha_nacimiento
            else ""
        )
        telefono.insert(0, valor_telefono or "")
        direccion.insert(0, valor_direccion or "")
        observaciones.insert("1.0", valor_observaciones or "")
        boton_guardar.config(text="Actualizar")

    # Cambia el registro seleccionado a estado RETIRADO
    def eliminar_seleccionado():
        seleccion = tabla.selection()

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
            cargar_lista()
        else:
            messagebox.showerror("Error", error)

    # Guarda un registro nuevo o actualiza el registro en edicion
    def guardar_desde_formulario():
        datos = obtener_datos_formulario()

        if not formulario_valido(datos):
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

        if beneficiario_editando["id"] is None:
            guardado, error = guardar_registro(*datos)
        else:
            guardado, error = actualizar_beneficiario(
                beneficiario_editando["id"],
                *datos
            )

        if guardado:
            messagebox.showinfo("Éxito", "Datos guardados correctamente.")
            limpiar_formulario()
            cargar_lista()
        else:
            messagebox.showerror(
                "Error",
                f"No se pudieron guardar los datos: {error}"
            )

    # Elementos de la mitad derecha: busqueda y tabla
    tk.Label(
        lista,
        text="Beneficiarios",
        font=("Arial", 20, "bold")
    ).pack(anchor="w", pady=(0, 25))

    tk.Label(
        lista,
        text="Buscar por nombre o documento",
        font=("Arial", 12, "bold")
    ).pack(anchor="w")

    busqueda = tk.Entry(lista)
    busqueda.pack(fill="x", pady=(5, 15))
    # Actualiza la tabla cada vez que cambia el texto de busqueda
    busqueda.bind("<KeyRelease>", cargar_lista)

    # Tabla que muestra solo codigo, nombre, documento y estado
    tabla = ttk.Treeview(
        lista,
        columns=("codigo", "nombre", "documento", "estado"),
        show="headings",
        selectmode="browse"
    )
    tabla.heading("codigo", text="Código")
    tabla.heading("nombre", text="Nombre completo")
    tabla.heading("documento", text="Documento")
    tabla.heading("estado", text="Estado")
    tabla.column("codigo", width=110)
    tabla.column("nombre", width=220)
    tabla.column("documento", width=130)
    tabla.column("estado", width=100)
    tabla.pack(fill="both", expand=True)

    # Botones que actuan sobre la fila seleccionada de la tabla
    botones_lista = tk.Frame(lista)
    botones_lista.pack(anchor="w", pady=(15, 0))

    tk.Button(
        botones_lista,
        text="Editar",
        command=editar_seleccionado,
        padx=20,
        pady=8
    ).grid(row=0, column=0)

    tk.Button(
        botones_lista,
        text="Eliminar",
        command=eliminar_seleccionado,
        padx=20,
        pady=8
    ).grid(row=0, column=1, padx=(15, 0))

    # Boton del formulario: guarda o actualiza segun el modo actual
    boton_guardar = tk.Button(
        formulario,
        text="Guardar",
        bg="#222222",
        fg="white",
        command=guardar_desde_formulario,
        padx=20,
        pady=8
    )
    boton_guardar.grid(row=13, column=0, sticky="w")

    # Boton que limpia el formulario cuando el usuario lo solicita
    tk.Button(
        formulario,
        text="Limpiar",
        command=limpiar_formulario,
        padx=20,
        pady=8
    ).grid(row=13, column=0, sticky="w", padx=(145, 0))

    # Permite que las dos columnas y el campo de observaciones se expandan
    formulario.columnconfigure(0, weight=1)
    formulario.columnconfigure(1, weight=1)
    formulario.rowconfigure(12, weight=1)
    lista.rowconfigure(3, weight=1)

    # Carga todos los beneficiarios al abrir la ventana
    cargar_lista()


# Permite probar esta vista directamente sin ejecutar aun el panel principal
if __name__ == "__main__":
    ventana_principal = tk.Tk()
    ventana_principal.title("Sistema de refugio")
    tk.Button(
        ventana_principal,
        text="Abrir beneficiarios",
        command=vista_beneficiarios
    ).pack(pady=40)
    ventana_principal.mainloop()
