"""Piezas de interfaz que se repiten en varias pantallas."""
import tkinter as tk
from tkinter import ttk

from Funciones.validaciones import formatear_fecha


def barra_superior(padre, controlador, titulo):
    """Fila con el titulo a la izquierda y el boton '← Menú principal' a la derecha."""
    barra = tk.Frame(padre, bg="white")
    tk.Label(barra, text=titulo, bg="white", font=("Arial", 20, "bold")).pack(side="left")
    tk.Button(barra, text="← Menú principal",
              command=lambda: controlador.mostrar("Principal")).pack(side="right")
    return barra


def crear_tabla(padre, columnas, altura=10, seleccion="browse"):
    """columnas = [(clave, titulo, ancho), ...]. Devuelve (marco, tabla): hay que hacer
    marco.pack(...) y usar 'tabla' para llenarla."""
    marco = tk.Frame(padre, bg="white")
    tabla = ttk.Treeview(marco, columns=[c[0] for c in columnas], show="headings",
                         selectmode=seleccion, height=altura)
    for clave, titulo, ancho in columnas:
        tabla.heading(clave, text=titulo)
        tabla.column(clave, width=ancho, anchor="w")
    barra = ttk.Scrollbar(marco, orient="vertical", command=tabla.yview)
    tabla.configure(yscrollcommand=barra.set)
    tabla.pack(side="left", fill="both", expand=True)
    barra.pack(side="right", fill="y")
    return marco, tabla


def vaciar_tabla(tabla):
    for fila in tabla.get_children():
        tabla.delete(fila)


def fecha_texto(fecha, vacio=""):
    return fecha.strftime("%d/%m/%Y") if fecha else vacio


def formato_fecha(entrada):
    """Hace que un Entry de fecha se formatee solo mientras se escribe: dd/mm/aaaa.
    Solo acepta digitos (maximo 8), pone las '/' despues del dia y del mes y permite borrar
    sin trabarse. Llamarlo justo despues de crear el Entry (antes de insertarle texto)."""
    variable = tk.StringVar(master=entrada)
    estado = {"previo": "", "ocupado": False}

    def al_cambiar(*_):
        if estado["ocupado"]:
            return
        texto = variable.get()
        nuevo = formatear_fecha(texto, estado["previo"])
        estado["previo"] = nuevo
        if nuevo != texto:
            estado["ocupado"] = True
            variable.set(nuevo)
            entrada.icursor(tk.END)
            estado["ocupado"] = False

    variable.trace_add("write", al_cambiar)
    entrada.config(textvariable=variable)
    entrada._variable_fecha = variable      # se guarda para que Python no la elimine
    return entrada
