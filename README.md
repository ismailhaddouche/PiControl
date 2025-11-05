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
# PiControl

**Autor:** hismardev

## Resumen

PiControl es una aplicación ligera pensada para ejecutar en una Raspberry Pi y gestionar fichajes de entrada/salida
de personal mediante lectores RFID. Proporciona una API de administración (FastAPI), una interfaz web para el administrador,
un simulador para probar fichajes sin hardware y utilidades para instalación y recuperación en un dispositivo físico.

Este repositorio contiene la lógica del servidor, los modelos de datos, plantillas HTML y scripts de instalación pensados
para desplegar PiControl en una Raspberry Pi o en un entorno de desarrollo local.

## Tecnologías y stack utilizado

- **Lenguaje:** Python 3.10+ / 3.11+
- **Web framework:** FastAPI (endpoints REST, plantillas Jinja2)
- **Servidor ASGI:** Uvicorn
- **ORM / modelos:** SQLModel (SQLAlchemy)
- **Base de datos:** SQLite (archivo `pi_control.db`)
- **Autenticación:** sesiones Starlette + hashing de contraseñas (passlib pbkdf2_sha256)
- **Plantillas:** Jinja2
- **Frontend ligero:** HTML/CSS y JavaScript para llamadas AJAX
- **Tests:** pytest + httpx TestClient

El proyecto evita dependencias pesadas para facilitar la instalación en Raspberry Pi y entornos con recursos limitados.

## Requisitos

- Raspberry Pi (opcional para despliegue real) o cualquier Linux para desarrollo.
- Python 3.10+ instalado.
- Acceso con privilegios root para instalar servicios systemd (si procede).

## Instalación (local / desarrollo)

1. Clona el repositorio y entra en la carpeta:

```bash
git clone https://github.com/ismailhaddouche/PiControl.git
cd PiControl
```

2. Crea y activa un entorno virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Instala dependencias:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4. Inicializa y arranca la API (en desarrollo puedes usar el reload):

```bash
uvicorn app.main:app --reload
```

5. Abre el navegador en `http://127.0.0.1:8000/admin` para acceder a la UI de administración.

## Instalación en Raspberry Pi (automática desde GitHub)

El repositorio incluye utilidades para instalar directamente desde GitHub y preparar la Pi:

- `install/install_from_github.sh`: clona (o actualiza) el repo en `/opt/picontrol`, crea un virtualenv, instala dependencias y ejecuta el instalador local.
- `install/pi_installer.sh`: instalador que guarda el `machine-id`, instala scripts en `/usr/local/bin`, crea un servicio systemd `picontrol-firstboot.service` y crea un acceso `.desktop` para el usuario de escritorio.

Ejemplo de uso en la Raspberry Pi (ejecutar como root):

```bash
sudo bash install/install_from_github.sh https://github.com/ismailhaddouche/PiControl.git main --user pi
```

Notas importantes:
- Revisa los scripts antes de ejecutarlos como root. El instalador coloca archivos en `/opt`, `/usr/local/bin` y crea/activa servicios systemd.
- El instalador guarda `/etc/machine-id` en `/var/lib/picontrol/machine-id` para permitir que el script de reseteo de administrador sólo se ejecute en la misma máquina.

## Configuración

- **Primer arranque / setup:** el proyecto incluye una pantalla de setup (`/admin/setup`) que permite crear el primer usuario administrador si no existe uno.
- **Cambio de contraseña admin:** desde la UI de `Configuración` puedes cambiar la contraseña del admin.
- **Zona horaria:** la UI de configuración permite seleccionar una zona horaria y el servidor intenta aplicar `timedatectl` (requiere privilegios).
- **Exportar/importar BD:** desde la configuración puedes descargar el archivo `pi_control.db` o subir una copia para reemplazar la base de datos (se recomienda reiniciar tras importar).

Seguridad y recuperación:
- Se incluye `tools/picontrol-reset-admin.sh` y `tools/reset_admin.py` para recuperar el acceso admin en la misma Raspberry Pi. El flujo verifica el `machine-id` guardado para evitar restablecimientos desde otro equipo.
- El script de reset genera una contraseña segura y la guarda en `/var/lib/picontrol/reset_password.txt` con permisos 600. Se recomienda rotarla o eliminarla tras su uso.

## Uso básico

- Añadir empleados, asignar RFID y gestionar fichajes se realiza desde la UI de administración (`/admin`).
- Para simular fichajes sin lector RFID físico, ejecuta `python simulador.py` en una terminal y escribe el `rfid_uid` que desees simular.

Endpoints habituales:

- `GET /admin` — panel principal (requiere login)
- `POST /admin/empleados` — crear/actualizar empleado
- `POST /admin/fichajes/manual` — crear fichaje manual
- `GET /admin/fichajes` — ver histórico

## Estructura del proyecto

Raíz del proyecto y propósito de los archivos/directorios más relevantes:

- `app/` — código principal de la aplicación
  - `main.py` — punto de entrada FastAPI y configuración middleware
  - `models.py` — modelos SQLModel (Empleado, Fichaje, Usuario, Config)
  - `crud.py` — funciones de acceso a datos y lógica (crear empleado, fichajes, archive/restore, config)
  - `db.py` — utilidades de conexión/engine de SQLite
  - `routers/` — rutas web/API organizadas (empleados, fichajes, web)
  - `templates/` — plantillas Jinja2 para interfaz web
  - `static/` — CSS/JS estático para la UI

- `simulador.py` — script que simula la lectura de tarjetas RFID (modo desarrollo)
- `pi_control.db` — archivo SQLite (generado en ejecución)
- `install/` — scripts de instalación y servicio systemd
  - `install_from_github.sh` — clonador/instalador desde GitHub
  - `pi_installer.sh` — instalador local que configura servicio / scripts
  - `picontrol-firstboot.service` — unidad systemd de primer arranque
- `tools/` — scripts de utilidad
  - `picontrol-reset-admin.sh` — wrapper que valida machine-id y lanza el reset
  - `reset_admin.py` — script Python que crea o resetea la cuenta admin

- `tests/` — pruebas automatizadas (pytest)
- `requirements.txt` — dependencias Python
- `README.md` — este fichero

## Tests

Ejecuta las pruebas con:

```bash
source .venv/bin/activate
pytest -q
```

## Contribuir

Si quieres contribuir, abre un issue o un pull request. Revisa las convenciones de estilo y añade pruebas para cambios relevantes.

## Licencia

Revisa el fichero `LICENSE` incluido en el repositorio para detalles de la licencia.

---

Si quieres que añada una sección con comandos rápidos de administración (p. ej. cómo reiniciar el servicio, ver logs o forzar migraciones), dímelo y la incluyo.
