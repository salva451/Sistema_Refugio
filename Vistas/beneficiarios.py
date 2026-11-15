import tkinter as tk
from tkinter import messagebox

from Funciones.beneficiarios import guardar_registro

def formulario_beneficiarios():
    ventana = tk.Toplevel()
    ventana.title("Beneficiarios")
    ventana.geometry("600x400")

    tk.Label(ventana, text="Código").grid(
        row=0, column=0, padx=(20, 5), pady=(20, 0), sticky="w"
    )
    Codigo = tk.Entry(ventana)
    Codigo.grid(row=1, column=0, padx=(20, 5), pady=5)

    tk.Label(ventana, text="Nombre").grid(
        row=0, column=1, padx=5, pady=(20, 0), sticky="w"
    )
    Nombre = tk.Entry(ventana)
    Nombre.grid(row=1, column=1, padx=5, pady=5)

    def guardar_datos():
        codigo = Codigo.get()
        nombre = Nombre.get()

        if not codigo or not nombre:
            messagebox.showwarning(
                "Campos vacíos",
                "Intenta completar los datos antes de guardar."
            )
            return

        guardado, error = guardar_registro(codigo, nombre)

        if guardado:
            messagebox.showinfo("Éxito", "Datos guardados correctamente.")
            Codigo.delete(0, tk.END)
            Nombre.delete(0, tk.END)
        else:
            messagebox.showerror(
                "Error",
                f"No se pudieron guardar los datos: {error}"
            )

    boton_enviar = tk.Button(
        ventana,
        text="Guardar",
        command=guardar_datos
    )
    boton_enviar.grid(
        row=2, column=0, columnspan=2, padx=(20, 5), pady=15
    )


if __name__ == "__main__":
    ventana_principal = tk.Tk()
    ventana_principal.title("Sistema de refugio")
    tk.Button(
        ventana_principal,
        text="Abrir beneficiarios",
        command=formulario_beneficiarios
    ).pack(pady=40)
    ventana_principal.mainloop()
