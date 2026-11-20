"""Ejecutar (desde la carpeta raiz) con:  python main.py

=====================  COMO SE CONECTA TODO  =====================

main.py crea UNA sola ventana (clase App) y guarda dentro todas las pantallas.
Cada pantalla es una clase que hereda de tk.Frame (ver Vistas/login.py y
Vistas/principal.py). App cambia de pantalla con  mostrar("NombreDeLaPantalla").

    Login  --(entra bien)-->  Principal (menu)  --(clic en un boton)-->  modulo

--- COMO AGREGAR UNA PANTALLA NUEVA---
 1. Crear Vistas/mi_pantalla.py con una clase que reciba (padre, controlador):

        import tkinter as tk
        class Beneficiarios(tk.Frame):
            def __init__(self, padre, controlador):
                super().__init__(padre, bg="white")
                self.controlador = controlador
                tk.Button(self, text="← Menú principal",
                          command=lambda: controlador.mostrar("Principal")).pack()
            def al_mostrar(self):      # opcional: se ejecuta cada vez que se abre
                pass                   # aqui recargar la tabla desde la base

 2. Registrarla AQUI, en el diccionario MODULOS, con DOS lineas:

        from Vistas.beneficiarios import Beneficiarios
        MODULOS["Beneficiarios"] = Beneficiarios

    El texto entre comillas debe ser IGUAL al del boton del menu
    (ver la lista MODULOS en Vistas/principal.py: con tildes y mayusculas).
    Mientras un modulo no este registrado, su boton muestra "En construccion".

 3. Las consultas SQL NO van en la vista: van en Funciones/<tabla>.py, y la vista
    las llama (from Funciones import beneficiarios). Esas usan conexion.py.

 Desde cualquier pantalla:
    controlador.mostrar("Principal")   -> volver al menu
    controlador.usuario                -> {"id":..., "nombre":..., "rol":...} de quien inicio sesion

--- DATOS DEL MENU PRINCIPAL ---
 Los numeros del menu (camas, alimentos por vencer, raciones de hoy) estan en 0.
 Se conectan en Vistas/principal.py, metodo obtener_datos(): ahi hay comentado el
 codigo exacto y lo que debe devolver cada funcion de Funciones/. No hace falta
 tocar main.py para eso.
==================================================================
"""
import tkinter as tk
from tkinter import messagebox

from Vistas.login import Login
from Vistas.principal import Principal
from Vistas.beneficiarios import Beneficiarios
from Vistas.habitaciones import HabitacionesCamas
from Vistas.ocupaciones import Ocupaciones

# Pantallas de los modulos (nombre del boton -> clase). Ejemplo para registrar la suya:
#   from Vistas.beneficiarios import Beneficiarios
#   MODULOS["Beneficiarios"] = Beneficiarios
MODULOS = {
    "Beneficiarios": Beneficiarios,
    "Habitaciones y camas": HabitacionesCamas,
    "Ocupación": Ocupaciones,
}


class App(tk.Tk):
    ANCHO, ALTO = 1200, 800

    def __init__(self):
        super().__init__()
        self.title("Sistema de Gestión")
        self.resizable(True, True)
        x = (self.winfo_screenwidth() - self.ANCHO) // 2
        y = (self.winfo_screenheight() - self.ALTO) // 2
        self.geometry(f"{self.ANCHO}x{self.ALTO}+{x}+{y}")

        self.usuario = None  # diccionario del usuario que inicio sesion

        self.contenedor = tk.Frame(self, bg="white")
        self.contenedor.pack(fill="both", expand=True)
        self.contenedor.grid_rowconfigure(0, weight=1)
        self.contenedor.grid_columnconfigure(0, weight=1)

        self.pantallas = {}
        self._crear("Login", Login)
        self._crear("Principal", Principal)
        self.mostrar("Login")

    def _crear(self, nombre, clase):
        frame = clase(self.contenedor, self)
        frame.grid(row=0, column=0, sticky="nsew")
        self.pantallas[nombre] = frame

    def mostrar(self, nombre):
        """Trae al frente la pantalla pedida (y le avisa para que recargue sus datos)."""
        frame = self.pantallas[nombre]
        if hasattr(frame, "al_mostrar"):
            frame.al_mostrar()
        frame.tkraise()

    def iniciar_sesion(self, usuario):
        self.usuario = usuario
        self.mostrar("Principal")

    def cerrar_sesion(self):
        self.usuario = None
        self.mostrar("Login")

    def abrir_modulo(self, nombre):
        """Lo llaman los botones del menu. Crea la pantalla la primera vez que se abre."""
        if nombre not in MODULOS:
            messagebox.showinfo("En construcción", f"El módulo «{nombre}» todavía no está listo.")
            return
        if nombre not in self.pantallas:
            self._crear(nombre, MODULOS[nombre])
        self.mostrar(nombre)

# Pantalla Beneficiarios y otros
from Vistas.login import Login
from Vistas.principal import Principal
from Vistas.beneficiarios import Beneficiarios
from Vistas.habitaciones import HabitacionesCamas
from Vistas.ocupaciones import Ocupaciones

MODULOS = {}
MODULOS["Beneficiarios"] = Beneficiarios
MODULOS["Habitaciones y camas"] = HabitacionesCamas
MODULOS["Ocupación"] = Ocupaciones

if __name__ == "__main__":
    App().mainloop()
