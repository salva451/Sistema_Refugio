import tkinter as tk
from tkinter import messagebox, ttk

from Funciones.beneficiarios import guardar_registro

#Ejecuta la ventana priuncipal de beneficiarios mostrandola
def vista_beneficiarios():
    #Ventana principal de beneficiarios
    ventana = tk.Toplevel()
    ventana.title("Beneficiarios")
    ventana.state("zoomed")
    #Pequeño organizador para los campos de lleanado de datos(Caja invisible)
    formulario = tk.Frame(ventana, padx=30, pady=25)
    formulario.pack(fill="both", expand=True)
    #Etiquetas de la ventana y cajas de beneficiarios
    tk.Label(
        formulario,
        text="Nuevo beneficiario",
        font=("Arial", 20, "bold")
    ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 25))

    tk.Label(formulario, text="Código").grid(
        row=1, column=0, sticky="w", padx=(0, 15)
    )
    tk.Label(formulario, text="Nombres").grid(
        row=1, column=1, sticky="w"
    )

    codigo = tk.Entry(formulario)
    codigo.grid(row=2, column=0, sticky="ew", padx=(0, 15), pady=(5, 15))

    nombres = tk.Entry(formulario)
    nombres.grid(row=2, column=1, sticky="ew", pady=(5, 15))

    tk.Label(formulario, text="Apellido paterno").grid(
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
    tk.Label(formulario, text="Número de documento").grid(
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

    # Funcion que guarda los datos ingresados en cada caja de la vista
    def guardar_desde_formulario():
        dato_codigo = codigo.get().strip()
        dato_nombres = nombres.get().strip()
        dato_apellido_paterno = apellido_paterno.get().strip()
        dato_apellido_materno = apellido_materno.get().strip()
        dato_tipo_documento = tipo_documento.get().strip()
        dato_numero_documento = numero_documento.get().strip()
        dato_fecha_nacimiento = fecha_nacimiento.get().strip()
        dato_telefono = telefono.get().strip()
        dato_direccion = direccion.get().strip()
        dato_observaciones = observaciones.get("1.0", tk.END).strip()

        if (
            not dato_codigo
            or not dato_nombres
            or not dato_apellido_paterno
            or not dato_apellido_materno
            or not dato_tipo_documento
            or not dato_numero_documento
            or not dato_fecha_nacimiento
            or dato_fecha_nacimiento == "dd/mm/aaaa"
            or not dato_telefono
            or not dato_direccion
        ):
            messagebox.showwarning(
                "Campos vacíos",
                "Completa todos los campos, es opcional llenar las observaciones."
            )
            return

        guardado, error = guardar_registro(
            dato_codigo,
            dato_nombres,
            dato_apellido_paterno,
            dato_apellido_materno,
            dato_tipo_documento,
            dato_numero_documento,
            dato_fecha_nacimiento,
            dato_telefono,
            dato_direccion,
            dato_observaciones
        )

        if guardado:
            messagebox.showinfo("Éxito", "Datos guardados correctamente.")
            limpiar_formulario()
        else:
            messagebox.showerror(
                "Error",
                f"No se pudieron guardar los datos: {error}"
            )
    # Boton opcional que limpia los datos para agregar datos nuevos
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

    boton_limpiar = tk.Button(
        formulario,
        text="Limpiar",
        command=limpiar_formulario,
        padx=20,
        pady=8
    )
    boton_limpiar.grid(row=13, column=0, sticky="w", padx=(145, 0))

    formulario.columnconfigure(0, weight=1)
    formulario.columnconfigure(1, weight=1)
    formulario.rowconfigure(12, weight=1)


if __name__ == "__main__":
    ventana_principal = tk.Tk()
    ventana_principal.title("Sistema de refugio")
    tk.Button(
        ventana_principal,
        text="Abrir beneficiarios",
        command=vista_beneficiarios
    ).pack(pady=40)
    ventana_principal.mainloop()
