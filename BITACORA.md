## 13 de noviembre de 2026 — Cambios en la Base de Datos y el Archivo README

### Cambios en los nombres de la Base de Datos
* **Unificación del nombre "Albergue":** Se cambiaron varios nombres para que tengan sentido en todo el proyecto:
  * La base de datos ahora se llama `albergue_solidario`.
  * La tabla `refugio` pasó a llamarse `albergue` (agregando `capacidad_maxima`) y `personas` pasó a ser `beneficiarios`.
  * Se cambiaron las referencias viejas en columnas y vistas (`id_albergue`, `id_beneficiario`, `beneficiario_activo`, `vista_ocupacion_albergue`).
* **Nueva estructura de comedores y limpieza:**
  * Se agregó la tabla `comedores`, por lo que ahora el inventario, las raciones y las donaciones dependen del comedor y ya no del albergue.
  * Se quitó la tabla `movimientos_inventario` porque no era necesaria (había datos repetidos).
* **Nuevos datos para usuarios y alimentos:**
  * En la tabla `usuarios` se sumaron campos para el inicio de sesión y bloqueo (`rol`, `intentos_fallidos`, `bloqueado_hasta`).
  * En la tabla `alimentos` se agregó `raciones_por_unidad`.
* **Control de raciones entregadas (`detalle_raciones`):**
  * Se volvió a poner la tabla `detalle_raciones`, ya que es necesaria para que el inventario no solo suba con las donaciones, sino que baje bien cuando se entrega comida. Sin ella se pierde el control de los lotes y no se pueden cumplir los objetivos de evitar desperdicios ni respaldar los reportes de consumo.

### Actualización de Documentación
* **`README.md`:** Se agregó una tabla con los nombres de los integrantes, sus usuarios de GitHub y los roles que cumple cada uno en el grupo.
