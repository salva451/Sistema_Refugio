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

- **Sistema Operativo:** Windows 10 o Windows 11.
- **Python:** Versión 3.12 (durante la instalación, marcar la casilla **"Add python.exe to PATH"**; incluye `tkinter` por defecto).
- **Librería de conexión a MySQL:** `mysql-connector-python` (versión 9.1.0 o superior).
- **Servidor local de base de datos:** XAMPP para Windows, versión 8.2.12 (incluye el motor MySQL).
- **Herramienta visual de base de datos:** MySQL Workbench 8.0 CE.
- **Control de versiones (opcional):** Git para Windows, versión 2.47.0.

---

## Instalación paso a paso (Windows + XAMPP)

### 1. Descargar el proyecto

Puedes descargar el proyecto de dos maneras:

- **Opción A (Directa desde GitHub, sin instalar Git):**
  1. Entra al repositorio del proyecto en GitHub.
  2. Haz clic en el botón verde **Code** y selecciona **Download ZIP**.
  3. Haz clic derecho sobre el archivo `.zip` descargado y selecciona **Extraer todo...** en una ubicación fácil de encontrar (por ejemplo, el Escritorio o `Documentos`).

- **Opción B (Usando Git):**
  1. Si no tienes Git, descárgalo desde [git-scm.com](https://git-scm.com/) e instálalo dejando las opciones por defecto.
  2. Abre la terminal (CMD o PowerShell), ubícate en la carpeta donde guardarás el proyecto y ejecuta:
     ```bash
     git clone https://github.com/salva541/Sistema_Refugio
     ```
  3. Entra a la carpeta del proyecto:
     ```bash
     cd Sistema_Refugio
     ```

### 2. Instalar la dependencia de Python

1. Abre la carpeta del proyecto en el Explorador de archivos de Windows.
2. Haz clic en la barra de dirección superior de la carpeta, escribe `cmd` y presiona **Enter** (esto abrirá la terminal ubicada exactamente dentro del proyecto).
3. Instala el conector de MySQL para Python ejecutando:
   ```bash
   pip install mysql-connector-python
   ```

### 3. Iniciar el servidor de base de datos en XAMPP

1. Abre el programa **XAMPP Control Panel** desde el menú Inicio de Windows.
2. Ubica la fila **MySQL** y haz clic en el botón **Start**.
3. Verifica que el nombre **MySQL** quede sombreado en color **verde** y muestre un número en la columna *Port(s)* (por defecto `3306`). No cierres esta ventana mientras uses el sistema.

### 4. Importar la base de datos en MySQL Workbench

1. Abre **MySQL Workbench**.
2. Si es la primera vez que lo abres y no aparece ninguna conexión guardada:
   - Haz clic en el símbolo **`+`** junto a **MySQL Connections**.
   - En *Connection Name* escribe `Local XAMPP` (deja *Hostname* en `127.0.0.1`, *Port* en `3306` y *Username* en `root`) y haz clic en **OK**.
3. Haz clic sobre la conexión **Local XAMPP** para entrar al entorno de base de datos.
4. En el menú superior, selecciona **File > Open SQL Script...**, busca la carpeta del proyecto y abre el archivo `database.sql`.
5. Haz clic en el icono del **rayo amarillo** (**Execute**, ubicado encima del código) para crear la base de datos y todas sus tablas.
6. En el panel izquierdo (**Schemas**), haz clic en el botón de actualizar (icono de dos flechas circulares) para comprobar que aparece la base de datos `albergue_solidario`.

### 5. Configurar la conexión del sistema

1. Dentro de la carpeta principal del proyecto, busca el archivo `config_ejemplo.py`.
2. Haz una copia de ese archivo en la misma carpeta y cámbiale el nombre a `config_local.py`.
3. Abre `config_local.py` con el Bloc de notas o tu editor de código y verifica que la configuración coincida con tu instalación de XAMPP (por defecto en XAMPP la contraseña de `root` va vacía `""`):
   ```python
   DB_CONFIG = {
       "host": "localhost",
       "user": "root",
       "password": "",
       "database": "albergue_solidario",
   }
   ```
4. Guarda el archivo y ciérralo.

### 6. Crear el usuario administrador inicial

Como la base de datos se crea vacía, crea un primer usuario administrador ejecutando este comando en la terminal (dentro de la carpeta del proyecto), si desea puede cambiar los valores tanto para el usuario como la contraseña:

```bash
python -c "from Funciones.usuarios import crear_usuario; crear_usuario('admin', '1234', 'ADMINISTRADOR'); print('Usuario creado')"
```
Nota: Los valores 'admin' y '1234' son solo de ejemplo; puedes reemplazarlos dentro de las comillas por el nombre de usuario y la contraseña que prefieras antes de ejecutar el comando.

### 7. Ejecutar el programa

1. En la misma terminal (ubicada dentro de la carpeta del proyecto), inicia la aplicación con:
   ```bash
   python main.py
   ```
2. En la ventana de inicio de sesión, ingresa el usuario `admin` y la contraseña `1234` o con los datos si es que los edito previamente.
