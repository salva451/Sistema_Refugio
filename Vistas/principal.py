"""Menu principal. Solo dibuja; los numeros vienen de obtener_datos()."""
import tkinter as tk
from Funciones.ocupaciones import cupos

MODULOS = ["Beneficiarios", "Habitaciones y camas", "Ocupación", "Inventario",
           "Donaciones", "Raciones", "Reportes"]


class Principal(tk.Frame):
    def __init__(self, padre, controlador):
        super().__init__(padre, bg="white")
        self.controlador = controlador

        # ---------- barra superior ----------
        barra = tk.Frame(self, bg="white")
        barra.pack(fill="x", padx=20, pady=10)
        for c in range(3):
            barra.columnconfigure(c, weight=1, uniform="barra")

        tk.Label(barra, text="Menú principal", bg="white",
                 font=("Arial", 13, "bold")).grid(row=0, column=1)

        derecha = tk.Frame(barra, bg="white")
        derecha.grid(row=0, column=2, sticky="e")
        self.lbl_usuario = tk.Label(derecha, text="", bg="white")
        self.lbl_usuario.pack(side="left", padx=(0, 10))
        tk.Button(derecha, text="Cerrar sesión", relief="solid", bd=1, bg="white",
                  command=self.controlador.cerrar_sesion).pack(side="left")

        tk.Frame(self, bg="black", height=1).pack(fill="x")

        # ---------- titulo ----------
        cuerpo = tk.Frame(self, bg="white")
        cuerpo.pack(fill="both", expand=True, padx=24, pady=(14, 10))

        tk.Label(cuerpo, text="Albergue Solidario", bg="white",
                 font=("Courier New", 20, "bold"), anchor="w").pack(fill="x")
        tk.Label(cuerpo, text="Sistema de Gestión de Albergues Transitorios y Comedores Comunitarios",
                 bg="white", fg="#555555", anchor="w").pack(fill="x", pady=(0, 10))

        # ---------- recuadro de CAMAS (3 datos en un solo cuadro) ----------
        camas = tk.Frame(cuerpo, bg="white", highlightbackground="black", highlightthickness=1)
        camas.pack(fill="x", padx=6, pady=6)

        cabecera = tk.Frame(camas, bg="white")
        cabecera.pack(fill="x", padx=12, pady=(8, 0))
        tk.Label(cabecera, text="Camas", bg="white", font=("Arial", 11, "bold")).pack(side="left")
        self.d_capacidad = tk.Label(cabecera, text="Capacidad máxima: 0", bg="white", fg="#555555")
        self.d_capacidad.pack(side="right")

        fila = tk.Frame(camas, bg="white")
        fila.pack(fill="x", padx=12, pady=(4, 12))
        for c in (0, 2, 4):
            fila.columnconfigure(c, weight=1, uniform="dato")
        self.v_total = self._dato(fila, 0, "Total de camas")
        tk.Frame(fila, bg="black", width=1).grid(row=0, column=1, sticky="ns")
        self.v_ocup = self._dato(fila, 2, "Ocupadas")
        tk.Frame(fila, bg="black", width=1).grid(row=0, column=3, sticky="ns")
        self.v_disp = self._dato(fila, 4, "Disponibles")

        # ---------- fila 2: alimentos y raciones ----------
        otras = tk.Frame(cuerpo, bg="white")
        otras.pack(fill="x")
        otras.columnconfigure(0, weight=1, uniform="tarjeta")
        otras.columnconfigure(1, weight=1, uniform="tarjeta")
        self.v_venc, self.d_venc = self._tarjeta(otras, "Alimentos por vencer (30 días)", 0)
        self.v_rac, self.d_rac = self._tarjeta(otras, "Raciones entregadas hoy", 1)

        # ---------- modulos ----------
        tk.Label(cuerpo, text="Módulos", bg="white", font=("Arial", 12, "bold"),
                 anchor="w").pack(fill="x", pady=(14, 6))
        grilla = tk.Frame(cuerpo, bg="white")
        grilla.pack(fill="x")
        for c in range(4):
            grilla.columnconfigure(c, weight=1, uniform="modulo")
        for i, nombre in enumerate(MODULOS):
            tk.Button(grilla, text=f"{nombre} →", anchor="w", padx=12, relief="solid", bd=1,
                      bg="white", activebackground="#eeeeee", font=("Arial", 10, "bold"),
                      command=lambda n=nombre: self.controlador.abrir_modulo(n)
                      ).grid(row=i // 4, column=i % 4, sticky="nsew", padx=6, pady=6, ipady=14)

    # ---------- piezas de dibujo ----------
    def _dato(self, padre, columna, titulo):
        """Un numero grande con su titulo, dentro del recuadro de camas."""
        marco = tk.Frame(padre, bg="white")
        marco.grid(row=0, column=columna, sticky="nsew", padx=10)
        valor = tk.Label(marco, text="0", bg="white", font=("Arial", 30, "bold"))
        valor.pack()
        tk.Label(marco, text=titulo, bg="white", fg="#333333").pack()
        return valor

    def _tarjeta(self, padre, titulo, columna):
        marco = tk.Frame(padre, bg="white", highlightbackground="black", highlightthickness=1)
        marco.grid(row=0, column=columna, sticky="nsew", padx=6, pady=6)
        tk.Label(marco, text=titulo, bg="white", fg="#333333", anchor="w"
                 ).pack(fill="x", padx=12, pady=(8, 0))
        valor = tk.Label(marco, text="0", bg="white", font=("Arial", 22, "bold"), anchor="w")
        valor.pack(fill="x", padx=12)
        detalle = tk.Label(marco, text="", bg="white", fg="#555555", anchor="w")
        detalle.pack(fill="x", padx=12, pady=(0, 8))
        return valor, detalle

    # ---------- datos del menu ----------
    def obtener_datos(self):
        """Devuelve los numeros que muestra el menu.

        POR AHORA TODO ES 0 (los companeros estan haciendo esas funciones).

        Cuando esten listas, reemplazar el 'return' de abajo por este bloque
        (y poner el import arriba del archivo):

            from Funciones import ocupaciones, inventarios, raciones

            cupos = ocupaciones.cupos()
            return {
                "capacidad_maxima":  cupos["capacidad_maxima"],
                "total_camas":       cupos["total_camas"],
                "camas_ocupadas":    cupos["camas_ocupadas"],
                "camas_disponibles": cupos["camas_disponibles"],
                "por_vencer":        inventarios.contar_por_vencer(30),
                "raciones_hoy":      raciones.entregadas_hoy(),
            }

        Lo que debe devolver cada funcion de la carpeta Funciones/:
            ocupaciones.cupos()               -> diccionario con las 4 claves de arriba
                                                 (se lee de la vista vista_ocupacion_albergue)
            inventarios.contar_por_vencer(30) -> numero entero: lotes con stock que vencen
                                                 dentro de 30 dias o menos
            raciones.entregadas_hoy()         -> numero entero: raciones entregadas hoy

        Si la base de datos falla, envolver el bloque en try/except mysql.connector.Error
        y mostrar los valores en 0 o un messagebox.
        """
        cupos_camas = cupos()
        return {
            "capacidad_maxima": cupos_camas["capacidad_maxima"],
            "total_camas": cupos_camas["total_camas"],
            "camas_ocupadas": cupos_camas["camas_ocupadas"],
            "camas_disponibles": cupos_camas["camas_disponibles"],
            "por_vencer": 0,
            "raciones_hoy": 0,
        }

    # ---------- se llama cada vez que se muestra el menu ----------
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