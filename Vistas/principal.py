"""Menu principal. Solo dibuja; los numeros vienen de obtener_datos()."""
import tkinter as tk
from Funciones.ocupaciones import cupos

MODULOS = ["Beneficiarios", "Habitaciones y camas", "Ocupación", "Inventario",
           "Donaciones", "Raciones", "Reportes"]

COLORES = {
    "fondo": "#FAF8F5",
    "tarjeta": "#FFFFFF",
    "borde": "#D6CFC7",
    "titulo": "#3B5249",
    "subtitulo": "#6E6A63",
    "acento": "#5B8E7D",
    "acento_suave": "#EBF3F0",
    "ambar": "#C87D55",
    "boton": "#FFFFFF",
    "boton_hover": "#F0EBE3",
    "salir_hover": "#FDECEC",
    "salir_texto": "#B84A4A",
}


class Principal(tk.Frame):
    def __init__(self, padre, controlador):
        super().__init__(padre, bg=COLORES["fondo"])
        self.controlador = controlador

        barra = tk.Frame(self, bg=COLORES["fondo"])
        barra.pack(fill="x", padx=20, pady=10)
        for c in range(3):
            barra.columnconfigure(c, weight=1, uniform="barra")

        tk.Label(barra, text="Menú principal", bg=COLORES["fondo"], fg=COLORES["titulo"],
                 font=("Arial", 13, "bold")).grid(row=0, column=1)

        derecha = tk.Frame(barra, bg=COLORES["fondo"])
        derecha.grid(row=0, column=2, sticky="e")
        self.lbl_usuario = tk.Label(derecha, text="", bg=COLORES["fondo"], fg=COLORES["subtitulo"])
        self.lbl_usuario.pack(side="left", padx=(0, 10))

        btn_salir = tk.Button(
            derecha,
            text="Cerrar sesión",
            relief="solid",
            bd=1,
            bg=COLORES["tarjeta"],
            fg=COLORES["salir_texto"],
            activebackground=COLORES["salir_hover"],
            cursor="hand2",
            padx=8,
            pady=2,
            command=self.controlador.cerrar_sesion,
        )
        btn_salir.pack(side="left")
        btn_salir.bind("<Enter>", lambda e: btn_salir.config(bg=COLORES["salir_hover"]))
        btn_salir.bind("<Leave>", lambda e: btn_salir.config(bg=COLORES["tarjeta"]))

        tk.Frame(self, bg=COLORES["borde"], height=1).pack(fill="x")

        cuerpo = tk.Frame(self, bg=COLORES["fondo"])
        cuerpo.pack(fill="both", expand=True, padx=24, pady=(14, 10))

        tk.Label(cuerpo, text="Albergue Solidario", bg=COLORES["fondo"], fg=COLORES["titulo"],
                 font=("Courier New", 20, "bold"), anchor="w").pack(fill="x")
        tk.Label(cuerpo, text="Sistema de Gestión de Albergues Transitorios y Comedores Comunitarios",
                 bg=COLORES["fondo"], fg=COLORES["subtitulo"], anchor="w").pack(fill="x", pady=(0, 10))

        camas = tk.Frame(cuerpo, bg=COLORES["tarjeta"], highlightbackground=COLORES["borde"], highlightthickness=1)
        camas.pack(fill="x", padx=6, pady=6)

        cabecera = tk.Frame(camas, bg=COLORES["tarjeta"])
        cabecera.pack(fill="x", padx=12, pady=(8, 0))
        tk.Label(cabecera, text="Camas", bg=COLORES["tarjeta"], fg=COLORES["titulo"],
                 font=("Arial", 11, "bold")).pack(side="left")
        self.d_capacidad = tk.Label(cabecera, text="Capacidad máxima: 0",
                                    bg=COLORES["acento_suave"], fg=COLORES["acento"],
                                    font=("Arial", 9, "bold"), padx=8, pady=2)
        self.d_capacidad.pack(side="right")

        fila = tk.Frame(camas, bg=COLORES["tarjeta"])
        fila.pack(fill="x", padx=12, pady=(4, 12))
        for c in (0, 2, 4):
            fila.columnconfigure(c, weight=1, uniform="dato")
        self.v_total = self._dato(fila, 0, "Total de camas", COLORES["titulo"])
        tk.Frame(fila, bg=COLORES["borde"], width=1).grid(row=0, column=1, sticky="ns")
        self.v_ocup = self._dato(fila, 2, "Ocupadas", COLORES["ambar"])
        tk.Frame(fila, bg=COLORES["borde"], width=1).grid(row=0, column=3, sticky="ns")
        self.v_disp = self._dato(fila, 4, "Disponibles", COLORES["acento"])

        otras = tk.Frame(cuerpo, bg=COLORES["fondo"])
        otras.pack(fill="x")
        otras.columnconfigure(0, weight=1, uniform="tarjeta")
        otras.columnconfigure(1, weight=1, uniform="tarjeta")
        self.v_venc, self.d_venc = self._tarjeta(otras, "Alimentos por vencer (30 días)", 0, COLORES["ambar"])
        self.v_rac, self.d_rac = self._tarjeta(otras, "Raciones entregadas hoy", 1, COLORES["acento"])

        tk.Label(cuerpo, text="Módulos", bg=COLORES["fondo"], fg=COLORES["titulo"],
                 font=("Arial", 12, "bold"), anchor="w").pack(fill="x", pady=(14, 6))
        grilla = tk.Frame(cuerpo, bg=COLORES["fondo"])
        grilla.pack(fill="x")
        for c in range(4):
            grilla.columnconfigure(c, weight=1, uniform="modulo")
        for i, nombre in enumerate(MODULOS):
            btn = tk.Button(
                grilla,
                text=f"{nombre} →",
                anchor="w",
                padx=12,
                relief="solid",
                bd=1,
                bg=COLORES["boton"],
                fg=COLORES["titulo"],
                activebackground=COLORES["boton_hover"],
                activeforeground=COLORES["titulo"],
                font=("Arial", 10, "bold"),
                cursor="hand2",
                command=lambda n=nombre: self.controlador.abrir_modulo(n),
            )
            btn.grid(row=i // 4, column=i % 4, sticky="nsew", padx=6, pady=6, ipady=14)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=COLORES["boton_hover"]))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=COLORES["boton"]))

    def _dato(self, padre, columna, titulo, color_valor):
        marco = tk.Frame(padre, bg=COLORES["tarjeta"])
        marco.grid(row=0, column=columna, sticky="nsew", padx=10)
        valor = tk.Label(marco, text="0", bg=COLORES["tarjeta"], fg=color_valor,
                         font=("Arial", 30, "bold"))
        valor.pack()
        tk.Label(marco, text=titulo, bg=COLORES["tarjeta"], fg=COLORES["subtitulo"]).pack()
        return valor

    def _tarjeta(self, padre, titulo, columna, color_valor):
        marco = tk.Frame(padre, bg=COLORES["tarjeta"], highlightbackground=COLORES["borde"], highlightthickness=1)
        marco.grid(row=0, column=columna, sticky="nsew", padx=6, pady=6)
        tk.Label(marco, text=titulo, bg=COLORES["tarjeta"], fg=COLORES["titulo"], anchor="w"
                 ).pack(fill="x", padx=12, pady=(8, 0))
        valor = tk.Label(marco, text="0", bg=COLORES["tarjeta"], fg=color_valor,
                         font=("Arial", 22, "bold"), anchor="w")
        valor.pack(fill="x", padx=12)
        detalle = tk.Label(marco, text="", bg=COLORES["tarjeta"], fg=COLORES["subtitulo"], anchor="w")
        detalle.pack(fill="x", padx=12, pady=(0, 8))
        return valor, detalle

    def obtener_datos(self):
        cupos_camas = cupos()
        return {
            "capacidad_maxima": cupos_camas["capacidad_maxima"],
            "total_camas": cupos_camas["total_camas"],
            "camas_ocupadas": cupos_camas["camas_ocupadas"],
            "camas_disponibles": cupos_camas["camas_disponibles"],
            "por_vencer": 0,
            "raciones_hoy": 0,
        }

    def al_mostrar(self):
        usuario = self.controlador.usuario
        self.lbl_usuario.config(text=f"Usuario: {usuario['nombre']}" if usuario else "")
        self.actualizar_datos()

    def actualizar_datos(self):
        d = self.obtener_datos()
        self.d_capacidad.config(text=f"Capacidad máxima: {d['capacidad_maxima']}")
        self.v_total.config(text=str(d["total_camas"]))
        self.v_ocup.config(text=str(d["camas_ocupadas"]))
        self.v_disp.config(text=str(d["camas_disponibles"]))
        self.v_venc.config(text=str(d["por_vencer"]))
        self.d_venc.config(text="lotes por vencer o vencidos")
        self.v_rac.config(text=str(d["raciones_hoy"]))
        self.d_rac.config(text="Comedor del Albergue")
