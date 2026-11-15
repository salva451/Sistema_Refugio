"""Pantalla de Login. Solo dibuja la ventana; la logica esta en Funciones/usuarios.py"""
import tkinter as tk

import mysql.connector

from Funciones import usuarios


class Login(tk.Frame):
    def __init__(self, padre, controlador):
        super().__init__(padre, bg="white")
        self.controlador = controlador
        self.segundos_restantes = 0

        caja = tk.Frame(self, bg="white")
        caja.place(relx=0.5, rely=0.45, anchor="center")

        tk.Label(caja, text="Albergue Solidario", bg="white",
                 font=("Courier New", 16, "bold")).pack(pady=(0, 25))

        tk.Label(caja, text="Usuario", bg="white", anchor="w").pack(fill="x")
        self.entry_usuario = tk.Entry(caja, width=38, relief="solid", bd=1)
        self.entry_usuario.pack(pady=(2, 12), ipady=4)

        tk.Label(caja, text="Contraseña", bg="white", anchor="w").pack(fill="x")
        self.entry_password = tk.Entry(caja, width=38, relief="solid", bd=1, show="*")
        self.entry_password.pack(pady=(2, 18), ipady=4)

        self.boton = tk.Button(caja, text="Ingresar", width=14, relief="solid", bd=1,
                               bg="white", activebackground="#eeeeee", command=self.ingresar)
        self.boton.pack()

        self.lbl_mensaje = tk.Label(caja, text="", bg="white", fg="black",
                                    font=("Arial", 10, "bold"), wraplength=320, justify="center")
        self.lbl_mensaje.pack(pady=(18, 0))

        # Enter en cualquier campo = Ingresar
        self.entry_usuario.bind("<Return>", self.ingresar)
        self.entry_password.bind("<Return>", self.ingresar)

    # ---------- se llama cada vez que se muestra esta pantalla ----------
    def al_mostrar(self):
        if self.segundos_restantes == 0:
            self.entry_usuario.delete(0, "end")
            self.entry_password.delete(0, "end")
            self.lbl_mensaje.config(text="")
            self.entry_usuario.focus_set()

    # ---------- boton Ingresar ----------
    def ingresar(self, evento=None):
        if self.segundos_restantes > 0:
            return
        usuario = self.entry_usuario.get().strip()
        password = self.entry_password.get()

        if not usuario:
            self._mensaje("Complete el campo: Usuario")
            return
        if not password:
            self._mensaje("Complete el campo: Contraseña")
            return

        try:
            r = usuarios.autenticar(usuario, password)
        except mysql.connector.Error:
            self._mensaje("No se pudo conectar a la base de datos.\n"
                          "Verifique que MySQL esté encendido y revise config_local.py")
            return

        if r["ok"]:
            self.entry_password.delete(0, "end")
            self._mensaje("")
            self.controlador.iniciar_sesion(r["usuario"])
        elif r["bloqueado"]:
            self._bloquear(r["segundos"])
        else:
            self._mensaje(r["mensaje"])
            self.entry_password.delete(0, "end")
            self.entry_password.focus_set()

    # ---------- bloqueo con cuenta regresiva ----------
    def _bloquear(self, segundos):
        self.segundos_restantes = segundos
        self._habilitar(False)
        self._tic()

    def _tic(self):
        if self.segundos_restantes <= 0:
            self.segundos_restantes = 0
            self._habilitar(True)
            self._mensaje("Ya puede intentar nuevamente.")
            return
        minutos, seg = divmod(self.segundos_restantes, 60)
        self._mensaje(f"Acceso bloqueado por intentos fallidos.\n"
                      f"Intente de nuevo en {minutos}:{seg:02d}")
        self.segundos_restantes -= 1
        self.after(1000, self._tic)

    def _habilitar(self, activo):
        estado = "normal" if activo else "disabled"
        for w in (self.entry_usuario, self.entry_password, self.boton):
            w.config(state=estado)
        if activo:
            self.entry_password.delete(0, "end")
            self.entry_usuario.focus_set()

    def _mensaje(self, texto):
        self.lbl_mensaje.config(text=("⚠ " + texto) if texto else "")
