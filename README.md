# Proyecto: SISTEMA DE GESTIÓN PARA ALBERGUES, CENTROS DE ACOGIDA Y COMEDORES

## Integrantes:

| Integrante | Usuario de GitHub | Rol / Función |
| :--- | :--- | :--- |
| Rada Saramani Pedro Efrain | radaefrain02-cd | Scrum Master |
| López Chino Nicolás Sebastián | nicmax06 | Product Owner |
| Cabaza Mayta Ailin Melani | cabazaailin | Líder de documentación |
| Sumi Urbina Cesar Nayib Luis | salva541 | Developer |
| Torrez Calle Claudio Yamil | ClaudioYamil | Developer |

## Descripción del Proyecto

Este proyecto estudia cómo operan los albergues transitorios, centros de acogida y comedores comunitarios en La Paz que brindan apoyo a migrantes y personas en situación de calle, donde gran parte del control diario —como el registro de beneficiarios, la disponibilidad de camas, el inventario por lotes y la entrega de raciones— aún se lleva a mano y por separado. Para evitar sobrecupos, desorden en los datos y pérdidas de alimentos por vencimiento, desarrollamos un sistema de escritorio conectado a una base de datos centralizada que organiza estos procesos en un solo lugar, facilitando la administración diaria y permitiendo ayudar de forma más eficiente a quienes lo necesitan.

---

## Requisitos

Para ejecutar el sistema en Windows se necesitan los siguientes programas instalados (se indican las versiones utilizadas en el desarrollo del proyecto):

* **Sistema Operativo:** Windows 10 o Windows 11.
* **Python:** Versión 3.12 (incluye `tkinter` por defecto).
* **Librería de conexión a MySQL:** `mysql-connector-python` (versión 9.1.0 o superior).
* **Servidor local de base de datos:** XAMPP para Windows, versión 8.2.12 (incluye Apache y MariaDB/MySQL).
* **Herramienta visual de base de datos (opcional):** MySQL Workbench 8.0 CE.
* **Control de versiones (opcional para descargar):** Git para Windows, versión 2.47.0.

---

## Instalación paso a paso (Windows + XAMPP)

### 1. Descargar el proyecto

Puedes descargar el proyecto de dos maneras:

* **Opción A (Directa desde GitHub, sin instalar Git):**
  1. Entra al repositorio del proyecto en GitHub.
  2. Haz clic en el botón verde **Code** y selecciona **Download ZIP**.
  3. Descomprime el archivo descargado en una carpeta de tu computadora (por ejemplo, en el Escritorio o en `Documentos`).

* **Opción B (Usando Git):**
  1. Si no tienes Git, descárgalo desde [git-scm.com](https://git-scm.com/) e instálalo dejando las opciones por defecto.
  2. Abre la terminal (CMD o PowerShell), ubícate en la carpeta donde guardarás el proyecto y ejecuta:
     ```bash
     git clone <URL_DEL_REPOSITORIO>
     ```
  3. Entra a la carpeta del proyecto:
     ```bash
     cd <NOMBRE_DE_LA_CARPETA>
     ```

### 2. Iniciar XAMPP

1. Abre el programa **XAMPP Control Panel** desde el menú Inicio de Windows.
2. En la fila **Apache**, haz clic en el botón **Start**.
3. En la fila **MySQL**, haz clic en el botón **Start**.
4. Verifica que ambos nombres queden marcados en verde antes de continuar.

### 3. Importar la base de datos

Existen dos formas de cargar la base de datos `albergue_solidario`:

* **Opción A: Desde phpMyAdmin (usando solo XAMPP)**
  1. En el panel de XAMPP, haz clic en el botón **Admin** de la fila **MySQL** (o abre tu navegador y entra a `http://localhost/phpmyadmin`).
  2. En el menú superior, haz clic en la pestaña **Importar**.
  3. Haz clic en **Seleccionar archivo** y busca el archivo `database.sql` dentro de la carpeta del proyecto.
  4. Baja hasta el final de la página y haz clic en el botón **Importar** (o **Continuar**).
  5. Al finalizar, aparecerá la base de datos `albergue_solidario` en el panel izquierdo.

* **Opción B: Desde MySQL Workbench**
  1. Abre **MySQL Workbench** e inicia sesión en tu conexión local (`Local instance MySQL`, usuario `root`).
  2. En el menú superior, haz clic en **File > Open SQL Script...** y selecciona el archivo `database.sql` del proyecto.
  3. Haz clic en el icono del rayo amarillo (**Execute**) para ejecutar todo el script.
  4. Actualiza el panel de esquemas (**Schemas**) para comprobar que se creó `albergue_solidario`.

### 4. Configurar la conexión del sistema

1. Dentro de la carpeta principal del proyecto, busca el archivo `config_ejemplo.py`.
2. Haz una copia de ese archivo y cámbiale el nombre a `config_local.py`.
3. Abre `config_local.py` con el Bloc de notas o tu editor de código y ajusta la contraseña según tu instalación de XAMPP (en XAMPP por defecto la contraseña de `root` va vacía `""`):
   ```python
   DB_CONFIG = {
       "host": "localhost",
       "user": "root",
       "password": "",
       "database": "albergue_solidario",
   }
   ```
4. Guarda los cambios.

### 5. Instalar dependencias y ejecutar el programa

1. Abre la terminal (CMD o PowerShell) dentro de la carpeta del proyecto.
2. Instala el conector de MySQL para Python ejecutando:
   ```bash
   pip install mysql-connector-python
   ```
3. Inicia la aplicación con:
   ```bash
   python main.py
   ```
