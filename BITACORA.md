## 10 de noviembre de 2026 — Creación de la base de datos y ordenamiento de archivos posibles a utilizar

### Base de Datos y Organización Inicial
- **Diseño inicial de la base de datos:** Se creó el script inicial con la estructura de tablas en MySQL 8.0 para gestionar refugios, personas e inventario.
- **Ordenamiento de archivos:** Se clasificaron y organizaron en local los archivos base y recursos que se utilizarían para levantar el proyecto.

---

## 11 de noviembre de 2026 — Inicio de proyecto en GitHub y conexión a MySQL

### Configuración del Entorno y Repositorio
- **Inicio de proyecto (`salva541`):** Se inicializó el repositorio en GitHub subiendo la estructura base para el trabajo colaborativo del equipo.
- **Conexión a MySQL:** Se configuró e implementó el enlace entre Python y la base de datos local en MySQL mediante el conector correspondiente, verificando la comunicación exitosa.

---

## 12 de noviembre de 2026 — Carga inicial de archivos al repositorio

### Documentación y Estructura
- **Subida de archivos iniciales:** Se cargaron los primeros archivos de documentación y base al repositorio del proyecto.

---

## 13 de noviembre de 2026 — Cambios en la Base de Datos y el Archivo README *(Cesar Sumi / Pedro Efrain Rada / Ailin Cabaza)*

### Cambios en los nombres de la Base de Datos
- **Unificación del nombre "Albergue" :** Se actualizaron las tablas y se corrigieron plurales en `database.sql` para que tengan coherencia en todo el proyecto:
  * La base de datos ahora se llama `albergue_solidario`.
  * La tabla `refugio` pasó a llamarse `albergue` (agregando `capacidad_maxima`) y `personas` pasó a ser `beneficiarios`.
  * Se cambiaron las referencias viejas en columnas y vistas (`id_albergue`, `id_beneficiario`, `beneficiario_activo`, `vista_ocupacion_albergue`).
- **Nueva estructura de comedores y limpieza:**
  * Se agregó la tabla `comedores`, por lo que ahora el inventario, las raciones y las donaciones dependen del comedor y ya no del albergue.
  * Se quitó la tabla `movimientos_inventario` porque no era necesaria (había datos repetidos).
- **Nuevos datos para usuarios y alimentos:**
  * En la tabla `usuarios` se sumaron campos para el inicio de sesión y bloqueo (`rol`, `intentos_fallidos`, `bloqueado_hasta`).
  * En la tabla `alimentos` se agregó `raciones_por_unidad`.
- **Control de raciones entregadas (`detalle_raciones`):**
  * Se volvió a poner la tabla `detalle_raciones`, ya que es necesaria para que el inventario no solo suba con las donaciones, sino que baje bien cuando se entrega comida. Sin ella se pierde el control de los lotes y no se pueden cumplir los objetivos de evitar desperdicios ni respaldar los reportes de consumo.

### Adaptación e Interfaz
- **Ajustes y adaptación:** Se realizaron ajustes en los nombres de archivos y se adaptó la estructura inicial de la interfaz del refugio a los cambios de la base de datos.

### Actualización de Documentación
- **`README.md` *(Ailin Cabaza)*:** Se subió y depuró el formato del archivo principal eliminando contenido duplicado e incluyendo la tabla con los nombres de los integrantes, sus usuarios de GitHub y los roles de cada uno en el grupo.

---

## 14 de noviembre de 2026 — Prototipo: Funciones y Visualizador del login y menu principal (base)

### Prototipo
- **Definición del diseño y arquitectura:** Se estructuró la base visual y organizativa del proyecto:
  * Se definió el mockup con todas las pantallas y sus reglas, para tener una base del mockup en Canvas.
  * Se definió y actualizó la estructura de carpetas del proyecto (`Funciones/`, `Vistas/`, `conexion.py` y `main.py`), sincronizando los cambios con la rama `pedro` y aplicando pequeños ajustes a la base de datos.
- **Interfaces desarrolladas en Tkinter:** Se implementaron las vistas iniciales del sistema:
  * Login en Tkinter con bloqueo de 3 minutos tras 3 intentos fallidos (código listo, en pruebas).
  * Menú principal en Tkinter con las camas (total, ocupadas y disponibles) en un solo recuadro (por ahora los datos muestran 0).
- **Configuración y seguridad local:** Se aseguraron los accesos de prueba a la base de datos:
  * Contraseña de MySQL protegida con `config_local.py`, y script `crear_admin.py` para crear el usuario de prueba (que obviamente no forma parte del repositorio).

### Pendiente
- **Tareas del equipo y diseño:** Siguientes pasos para continuar con el desarrollo:
  * Que el equipo termine las demás pantallas y las registre en `main.py`.
  * Corregir detalles del mockup en Canva debido a mejoras vistas en grupo por llamada.

---

## 15 de noviembre de 2026 — Prototipo: Integración de vista y función `beneficiarios.py` al menú principal base

### Módulo de Beneficiarios (Funciones y Vistas)
- **Desarrollo y pruebas de `Beneficiarios` *(Cesar Sumi)*:** Se implementaron y probaron las funciones y vistas para ingresar, consultar y revisar registros de beneficiarios directamente en la base de datos.
- **Adaptación visual *(Cesar Sumi)*:** Se actualizó la vista de `Beneficiarios` adaptándola al diseño de las ventanas principales (`Login` y `Panel`), dejando funcional el subprograma de registro y revisión.

### Conexión en `main.py` y menú principal
- **Integración:** Se unió el código de la vista de beneficiarios realizado por Cesar Sumi con la interfaz principal desarrollada por Pedro Efrain Rada:
  * Se enlazó la pantalla de `Beneficiarios` con el menú de navegación en `Principal`.
  * Se actualizaron las importaciones en `main.py` (`Login`, `Principal`, `Beneficiarios`) y se registró la vista en el diccionario `MODULOS["Beneficiarios"] = Beneficiarios` para que el sistema pueda abrirlo y funcionar.

---

## 16 de noviembre de 2026 — Integración de ramas y pruebas funcionales de las primeras 3 pantallas

### Fusión y Pruebas del Sistema Base
- **Anexión de ramas:** Se integraron los avances de las ramas `pedro` y `cesar` unificando `Login`, `Panel` y `Beneficiarios` en un solo flujo funcional.
- **Prueba de conexión integral:** Se validó con éxito la comunicación entre el inicio de sesión, el panel principal y el módulo de beneficiarios con la base de datos activa, consolidando las primeras 3 pantallas funcionales.
- **Ajustes visuales:** Se realizaron mejoras menores en el menú de registro de beneficiarios y se estandarizó la configuración de tamaño general de las ventanas de la aplicación.

---

## 19 de noviembre de 2026 — Reorganización de la base de datos en el repositorio y guía en README

### Estructura y Documentación
- **Carpeta `base_de_datos/` *(Claudio Yamil)*:** Se creó el directorio `base_de_datos` en el repositorio y se movió allí el archivo SQL principal para mantener separado el código fuente de los scripts de datos.
- **Actualización de `README.md` *(Pedro Efrain Rada)*:** Se corrigió el nombre del proyecto y se añadió una guía de instalación detallada para facilitar la ejecución local.

---

## 20 de noviembre de 2026 — Módulo de Habitaciones y Camas, Ocupación, Conexión a BD y Validaciones

### Nuevas Funcionalidades e Integración
- **Habitaciones, Camas y Ocupación *(Cesar Sumi)*:** Se creó y dejó completamente funcional el contenido del botón `Habitaciones y Camas` junto con el control de `Ocupación`.
- **Integración de módulos y conexión a BD *(Cesar Sumi)*:** Se resolvió un error de integración entre los módulos para dejar operativos los botones de navegación hacia `Habitaciones y Camas` y `Ocupaciones`, verificando la conexión activa con la base de datos.
- **Corrección de errores y validaciones *(Cesar Sumi)*:** Se corrigieron observaciones y errores de validación en los formularios (como las restricciones de longitud mínima de caracteres en nombres y apellidos) y se aplicaron mejoras generales en `Beneficiarios`.
- **Documentación *(Pedro Efrain Rada)*:** Se hicieron ajustes adicionales en el `README.md` para mayor claridad.

---

## 22 de noviembre de 2026 — Ajustes finales en documentación

### Documentación
- **`README.md`:** Se realizaron pequeñas correcciones de formato y redacción en el archivo principal del repositorio.

---

## 25 de noviembre de 2026 — Mejora visual del menú principal y consolidación del programa preliminar

### Interfaz e Integración Final
- **Mejora estética en el menú principal *(Ailin Cabaza)*:** Se actualizaron los estilos y la presentación visual del panel/menú principal para lograr un mejor aspecto en la interfaz de usuario.
- **Fusión de cambios (`Merge branch 'cesar'`) *(Cesar Sumi)*:** Se integraron las últimas actualizaciones desarrolladas en la rama `cesar` hacia la rama principal.
- **Programa preliminar funcional *(Cesar Sumi)*:** Se realizaron pruebas del sistema de refugios a través de distintas ramas verificando que los módulos conectados funcionen de manera estable.
- **Soporte de base de datos *(Cesar Sumi)*:** Se incorporó un archivo temporal de prueba para agilizar la actualización y testeo de la base de datos.

---

## 27 de noviembre de 2026 — Validaciones, fechas automáticas, ajustes en raciones y alimentos, ajustes en la Base de Datos (E-R)
- **Restricción de registro en beneficiarios:** Se retiró la opción para registrar personas externas en el módulo de beneficiarios, enfocando el registro en quienes corresponden al flujo actual del albergue.
- **Validación de fecha de nacimiento:** Al registrar un beneficiario, se agregó validación sobre la fecha de nacimiento para rechazar valores imposibles (como años muy antiguos tipo `1000`), fechas futuras o fuera de un rango razonable, evitando errores en la base de datos y en los reportes.
- **Validación de carnet de identidad:** Se ajustó la regla del CI para que acepte dígitos numéricos al inicio y, de forma opcional, 2 letras al final correspondientes a la extensión departamental.
- **Formato automático en campos de fecha:** Se implementó formato automático mientras se escribe en los campos de fecha de Tkinter (`DD/MM/AAAA`): solo permite dígitos numéricos, limita la entrada a 8 números, inserta `/` automáticamente después del día y del mes, y permite borrar sin trabarse ni generar errores de formato.
- **Nuevo tipo de comida en raciones:** Se añadió `"Té"` dentro de las opciones de tipo de comida en el módulo de Raciones para cubrir la hora del té junto con el resto de turnos del comedor.
- **Eliminación de popup al crear registro o tabla:** Al crear el registro o tabla correspondiente en la vista, se quitó la ventana emergente (*popup*) de confirmación de éxito para que la interfaz se actualice directamente sin interrumpir el flujo.
- **Actualizacion de relaciones en la Base de datos:** Se arreglo las relaciones faltantes entre el usuario y el albergue.

### Pendiente
- Adaptacion y pequeños cambios a la base de datos
- Arreglar bug de estadisticas
