"""Pantalla Usuarios (solo administrador): crear usuarios, activarlos/desactivarlos
y consultar el registro de accesos."""
import tkinter as tk
from datetime import date, timedelta
from tkinter import messagebox, ttk

from Funciones import usuarios
from Funciones.validaciones import fecha_a_texto, validar_fecha
from Vistas.componentes import barra_superior, crear_tabla, formato_fecha, vaciar_tabla


class Usuarios(tk.Frame):
    def __init__(self, padre, controlador):
        super().__init__(padre, bg="white")
        self.controlador = controlador

        marco = tk.Frame(self, bg="white", padx=30, pady=25)
        marco.pack(fill="both", expand=True)
        barra_superior(marco, controlador, "Usuarios y accesos").pack(fill="x", pady=(0, 15))

        pestanas = ttk.Notebook(marco)
        pestanas.pack(fill="both", expand=True)
        self.tab_usuarios = tk.Frame(pestanas, bg="white", padx=15, pady=15)
        self.tab_accesos = tk.Frame(pestanas, bg="white", padx=15, pady=15)
        pestanas.add(self.tab_usuarios, text="Usuarios")
        pestanas.add(self.tab_accesos, text="Registro de accesos")
        self.crear_usuarios()
        self.crear_accesos()

    # ================= pestana 1: usuarios =================
    def crear_usuarios(self):
        t = self.tab_usuarios
        form = tk.Frame(t, bg="white")
        form.pack(side="left", fill="y", padx=(0, 30))
        tk.Label(form, text="Nuevo usuario", bg="white", font=("Arial", 14, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 12))

        tk.Label(form, text="Usuario*", bg="white").grid(row=1, column=0, sticky="w")
        self.usuario = tk.Entry(form, width=30)
        self.usuario.grid(row=2, column=0, sticky="ew", pady=(2, 8))
        tk.Label(form, text="Contraseña*", bg="white").grid(row=3, column=0, sticky="w")
        self.clave = tk.Entry(form, show="*")
        self.clave.grid(row=4, column=0, sticky="ew", pady=(2, 8))
        tk.Label(form, text="Repetir contraseña*", bg="white").grid(row=5, column=0, sticky="w")
        self.clave2 = tk.Entry(form, show="*")
        self.clave2.grid(row=6, column=0, sticky="ew", pady=(2, 8))
        tk.Label(form, text="Rol*", bg="white").grid(row=7, column=0, sticky="w")
        self.rol = ttk.Combobox(form, values=usuarios.ROLES, state="readonly")
        self.rol.set("ENCARGADO")
        self.rol.grid(row=8, column=0, sticky="ew", pady=(2, 14))
        tk.Button(form, text="Crear usuario", command=self.crear_usuario, padx=18, pady=6).grid(row=9, column=0, sticky="w")

        lista = tk.Frame(t, bg="white")
        lista.pack(side="left", fill="both", expand=True)
        marco_tabla, self.tabla_usuarios = crear_tabla(lista, [
            ("usuario", "Usuario", 200), ("rol", "Rol", 160), ("estado", "Estado", 110)], altura=12)
        marco_tabla.pack(fill="both", expand=True)
        botones = tk.Frame(lista, bg="white")
        botones.pack(anchor="w", pady=(10, 0))
        tk.Button(botones, text="Activar", command=lambda: self.cambiar_estado(True), padx=16, pady=6).pack(side="left")
        tk.Button(botones, text="Desactivar", command=lambda: self.cambiar_estado(False), padx=16, pady=6).pack(side="left", padx=10)

    def cargar_usuarios(self):
        correcto, filas = usuarios.listar_usuarios()
        if not correcto:
            messagebox.showerror("Error", filas)
            return
        vaciar_tabla(self.tabla_usuarios)
        for f in filas:
            self.tabla_usuarios.insert("", tk.END, iid=str(f["id_usuario"]), values=(
                f["nombre_usuario"], f["rol"], "Activo" if f["activo"] else "Inactivo"))

    def crear_usuario(self):
        if not self.usuario.get().strip():
            messagebox.showwarning("Campo vacío", "Complete el campo: Usuario")
            return
        if self.clave.get() != self.clave2.get():
            messagebox.showwarning("Dato inválido", "Las contraseñas no coinciden.")
            return
        correcto, resultado = usuarios.registrar_usuario(self.usuario.get(), self.clave.get(), self.rol.get())
        if correcto:
            for campo in (self.usuario, self.clave, self.clave2):
                campo.delete(0, tk.END)
            self.cargar_usuarios()
        else:
            messagebox.showerror("Error", resultado)

    def cambiar_estado(self, activo):
        seleccion = self.tabla_usuarios.selection()
        if not seleccion:
            messagebox.showwarning("Selección necesaria", "Seleccione un usuario de la tabla.")
            return
        actual = (self.controlador.usuario or {}).get("id")
        correcto, resultado = usuarios.cambiar_estado_usuario(int(seleccion[0]), activo, actual)
        if correcto:
            self.cargar_usuarios()
        else:
            messagebox.showerror("Error", resultado)

    # ================= pestana 2: accesos =================
    def crear_accesos(self):
        t = self.tab_accesos
        filtros = tk.Frame(t, bg="white")
        filtros.pack(fill="x", pady=(0, 8))
        tk.Label(filtros, text="Desde (dd/mm/aaaa)", bg="white").pack(side="left")
        self.desde = formato_fecha(tk.Entry(filtros, width=14))
        self.desde.pack(side="left", padx=(8, 15))
        tk.Label(filtros, text="Hasta (dd/mm/aaaa)", bg="white").pack(side="left")
        self.hasta = formato_fecha(tk.Entry(filtros, width=14))
        self.hasta.pack(side="left", padx=(8, 15))
        tk.Button(filtros, text="Consultar", command=self.cargar_accesos, padx=14).pack(side="left")
        self.desde.insert(0, fecha_a_texto(date.today() - timedelta(days=6)))
        self.hasta.insert(0, fecha_a_texto(date.today()))

        marco_tabla, self.tabla_accesos = crear_tabla(t, [
            ("fecha", "Fecha y hora", 190), ("usuario", "Usuario", 200), ("resultado", "Resultado", 140)], altura=14)
        marco_tabla.pack(fill="both", expand=True)

    def cargar_accesos(self):
        correcto, desde = validar_fecha(self.desde.get(), "La fecha «Desde»")
        if not correcto:
            messagebox.showwarning("Dato inválido", desde)
            return
        correcto, hasta = validar_fecha(self.hasta.get(), "La fecha «Hasta»")
        if not correcto:
            messagebox.showwarning("Dato inválido", hasta)
            return
        if desde > hasta:
            messagebox.showwarning("Dato inválido", "La fecha «Desde» no puede ser mayor que «Hasta».")
            return
        correcto, filas = usuarios.listar_accesos(desde, hasta)
        if not correcto:
            messagebox.showerror("Error", filas)
            return
        vaciar_tabla(self.tabla_accesos)
        for i, f in enumerate(filas):
            self.tabla_accesos.insert("", tk.END, iid=str(i), values=(
                f["fecha_hora"].strftime("%d/%m/%Y %H:%M:%S"), f["nombre_usuario"], f["resultado"]))

    def al_mostrar(self):
        self.cargar_usuarios()
        self.cargar_accesos()
