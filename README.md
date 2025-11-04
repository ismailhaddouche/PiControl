# PiControl
A tailored Raspberry Pi app for worker clock-in/out registration using RFID.

# 🚀 PiControl: Sistema de Fichaje RFID

Este repositorio contiene el "cerebro" del software para **PiControl**, un sistema de registro de jornadas laborales basado en Raspberry Pi.

Esta es la **Fase 1 (Software y Simulación)**. El proyecto se desarrolla 100% en un entorno simulado, sin necesidad de hardware.

Utiliza **FastAPI** para una API de administración moderna y un script de Python independiente para **simular la lectura de tarjetas RFID** desde la terminal.

## Funcionalidades
**Panel de administracióm:** permite acceder mediante contrasela y usuario a la gestion de la aplicación y permite 
   -Añadir quitar empleados.
   -Asociar o disociar un usario de un llavero RFID
   -Ver informes de entrada y salida de un trabajador en concreto.
   -Ver informes de entrada y salida de un día concreto.
   -Ver horas trabajadas de un trabajador concreto durante un periodo concreto.
   -Sincronizar hora de la máquina.

**Script en guardia:** Un script que esta atento a los cambios aplicados por el administrador y el lectro de rfid:
    -Si es la entrada del usuario comprueba y registrada entrada de usuario. Dando un mensaje de bienvenida.
    -Si es la salida del usuario comprueba y registra salida del usuario. Dando un mensaje de despedida.
    -Si falla la salida o entrada lo indica con un mensaje.

## ⚙️ Tecnologías Utilizadas

* **Python 3.10+**
* **FastAPI:** Para construir la API de administración (ver fichajes, añadir empleados).
* **Uvicorn:** Servidor ASGI para ejecutar FastAPI.
* **SQLite:** Base de datos ligera basada en archivos, perfecta para este proyecto.


## 🔧 Instalación y Configuración

Sigue estos pasos para poner en marcha el proyecto:

1.  **Clona o crea tu repositorio** y navega hasta él.

2.  **Crea los archivos** (ver la sección "Código Fuente" más abajo) con el contenido proporcionado.

3.  **Crea un entorno virtual:**
    ```bash
    python -m venv .venv
    ```

4.  **Activa el entorno virtual:**
    * En macOS/Linux: `source .venv/bin/activate`
    * En Windows (PowerShell): `.\.venv\Scripts\Activate.ps1`

5.  **Instala las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

6.  **Inicializa la Base de Datos:**
    La API lo hará automáticamente cuando arranque, ¡así que no necesitas un paso manual!

---

## ⚡️ Cómo Ejecutar el Proyecto

Necesitarás **dos terminales** abiertas al mismo tiempo (ambas con el entorno virtual activado).

### Terminal 1: Iniciar la API de Administración

1.  Ejecuta el servidor Uvicorn desde la raíz del proyecto:
    ```bash
    uvicorn app.main:app --reload
    ```
    * `app.main`: Se refiere al archivo `main.py` dentro del directorio `app`.
    * `app`: Se refiere al objeto `app = FastAPI()` dentro de ese archivo.
    * `--reload`: Reinicia el servidor automáticamente cada vez que guardas cambios.

2.  ¡La API ya está funcionando! Puedes ver la documentación interactiva (Swagger UI) en tu navegador:
    **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

3.  Desde esta interfaz `/docs`, ya puedes:
    * Usar el endpoint `POST /empleados/` para añadir nuevos empleados (ej: "Ismail", "rfid-001").
    * Usar el endpoint `GET /fichajes/` para ver la lista de todos los fichajes.

### Terminal 2: Ejecutar el Simulador RFID

1.  En una **segunda terminal** (con el entorno virtual activado), ejecuta el script simulador:
    ```bash
    python simulador.py
    ```

2.  El script te pedirá que "pases una tarjeta". Escribe el `rfid_uid` que registraste en la API (ej: "rfid-001") y pulsa Enter.

3.  Verás la respuesta en la terminal (`ÉXITO: Fichaje de Entrada...`).

4.  Vuelve a tu navegador y refresca el endpoint `GET /fichajes/` en la API. Verás cómo el nuevo fichaje aparece instantáneamente.

---

## 📋 Código Fuente de los Archivos

Copia y pega este contenido en los archivos correspondientes.
