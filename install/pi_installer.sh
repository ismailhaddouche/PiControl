#!/usr/bin/env bash
# Instalador para Raspberry Pi - configura servicio de primer arranque y script de reseteo local
# Debe ejecutarse como root en la Raspberry Pi destino.

set -euo pipefail

TARGET_LIB_DIR="/var/lib/picontrol"
INSTALL_PREFIX="/opt/picontrol"
REPO_DIR="$INSTALL_PREFIX"
RESET_BIN="/usr/local/bin/picontrol-reset-admin.sh"
FIRSTBOOT_BIN="/usr/local/bin/picontrol-firstboot.sh"
SERVICE_FILE="/etc/systemd/system/picontrol-firstboot.service"

# Adjust paths for local (non-root) installs
if [ "${INSTALL_MODE:-system}" = "local" ]; then
  INSTALL_PREFIX="$HOME/.local/picontrol"
  REPO_DIR="$INSTALL_PREFIX"
  TARGET_LIB_DIR="$HOME/.local/share/picontrol"
  RESET_BIN="$HOME/.local/bin/picontrol-reset-admin.sh"
  FIRSTBOOT_BIN="$HOME/.local/bin/picontrol-firstboot.sh"
  SERVICE_FILE=""
fi

usage() {
  cat <<EOF
Usage: $0 [--user USER] [--github-repo REPO]

  --user USER, -u USER         Crear accesos .desktop para el usuario USER (opcional).
  --github-repo REPO, -g REPO  Clonar el repositorio desde REPO a /opt/picontrol antes de instalar.
  --reinstall, -r              Forzar re-ejecución de pip install -r requirements.txt en el venv.
  --system                     Forzar instalación a nivel sistema (requiere root).
  --local                      Forzar instalación en modo usuario (~/.local, no requiere root).
EOF
  exit 1
}

GITHUB_REPO=""
USER_ARG=""
REINSTALL_REQ="no"
FORCE_SYSTEM="no"
FORCE_LOCAL="no"
while [ "$#" -gt 0 ]; do
  case "$1" in
    --user|-u)
      shift
      USER_ARG="$1"
      shift
      ;;
    --system)
      FORCE_SYSTEM="yes"
      shift
      ;;
    --local)
      FORCE_LOCAL="yes"
      shift
      ;;
    --github-repo|--github|-g)
      shift
      GITHUB_REPO="$1"
      shift
      ;;
    --reinstall|-r)
      REINSTALL_REQ="yes"
      shift
      ;;
    --help|-h)
      usage
      ;;
    *)
      echo "Argumento desconocido: $1"
      usage
      ;;
  esac
done

# Detect simple GUI session early (used to decide whether to attempt graphical elevation)
GUI_SESSION="no"
if [ -n "${DISPLAY:-}" ] || [ -n "${WAYLAND_DISPLAY:-}" ]; then
  GUI_SESSION="yes"
fi
PKEXEC_AVAILABLE="no"
if command -v pkexec >/dev/null 2>&1; then
  PKEXEC_AVAILABLE="yes"
fi

# Decide install mode: system or local (user)
INSTALL_MODE="system"
if [ "$FORCE_LOCAL" = "yes" ]; then
  INSTALL_MODE="local"
elif [ "$FORCE_SYSTEM" = "yes" ]; then
  INSTALL_MODE="system"
else
  if [ "$EUID" -ne 0 ]; then
    # Default to local install when not root
    INSTALL_MODE="local"
  else
    INSTALL_MODE="system"
  fi
fi

# If system install requested but not root, attempt graphical elevation; otherwise fail
if [ "$INSTALL_MODE" = "system" ] && [ "$EUID" -ne 0 ]; then
  if [ "$GUI_SESSION" = "yes" ] && [ "$PKEXEC_AVAILABLE" = "yes" ]; then
    echo "Solicitando elevación gráfica con pkexec para instalación a nivel sistema..."
    exec pkexec env DISPLAY="$DISPLAY" XAUTHORITY="${XAUTHORITY:-}" XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-}" PATH="$PATH" bash -c "exec \"$0\" \"\$@\"" _ "$0" "$@"
  fi
  echo "Instalación a nivel sistema requiere root. Ejecuta: sudo bash $0 --system"
  exit 1
fi


# GUI mode detection and zenity support
GUI_AVAILABLE="no"
ZENITY_CMD=""
if [ -n "${DISPLAY:-}" ] || [ -n "${WAYLAND_DISPLAY:-}" ]; then
  # We are in a graphical session (likely). Ensure zenity is installed.
  if command -v zenity >/dev/null 2>&1; then
    GUI_AVAILABLE="yes"
    ZENITY_CMD=zenity
  else
    # Auto-install zenity if apt-get is available (non-interactive)
    if command -v apt-get >/dev/null 2>&1; then
      echo "Entorno gráfico detectado y 'zenity' no está instalado. Instalando zenity automáticamente..."
      export DEBIAN_FRONTEND=noninteractive
      apt-get update -y
      apt-get install -y zenity || true
      if command -v zenity >/dev/null 2>&1; then
        GUI_AVAILABLE="yes"
        ZENITY_CMD=zenity
      else
        echo "No se pudo instalar 'zenity'. Continuando en modo texto."
      fi
    else
      echo "Entorno gráfico detectado pero no hay apt-get: no se puede instalar 'zenity' automáticamente. Continuando en modo texto."
    fi
  fi
fi

use_gui() {
  [ "$GUI_AVAILABLE" = "yes" ]
}

prompt_gui_options() {
  # Use zenity to collect GITHUB_REPO, USER_ARG and re-install flag
  GITHUB_REPO=$(zenity --entry --title="PiControl Installer" --text="GitHub repo to clone (leave empty to use local repo):" --entry-text "$GITHUB_REPO" 2>/dev/null || echo "$GITHUB_REPO")
  USER_ARG=$(zenity --entry --title="PiControl Installer" --text="Desktop user (leave empty to detect e.g. 'pi'):" --entry-text "$USER_ARG" 2>/dev/null || echo "$USER_ARG")
  if zenity --question --title="PiControl Installer" --text="Force reinstall Python requirements?" 2>/dev/null; then
    REINSTALL_REQ="yes"
  else
    REINSTALL_REQ="no"
  fi
}

start_progress() {
  # Start a background zenity progress if GUI available
  if use_gui; then
    exec 3> >(zenity --progress --title="Instalando PiControl" --percentage=0 --auto-close)
  fi
}

progress_update() {
  # progress_update <percent> <message>
  if use_gui; then
    local pct=${1:-0}
    local msg=${2:-""}
    echo "$pct"
    echo "# $msg"
  else
    echo "$2"
  fi
}

# Detectar e instalar dependencias de sistema necesarias (Debian/Ubuntu/Raspbian)
check_and_install_deps() {
  echo "Comprobando dependencias de sistema..."
  missing=()

  # Comprobar comandos básicos
  command -v python3 >/dev/null 2>&1 || missing+=(python3)
  command -v git >/dev/null 2>&1 || missing+=(git)

  # Paquetes Debian/apt
  dpkg -s python3-venv >/dev/null 2>&1 || missing+=(python3-venv)
  dpkg -s python3-pip >/dev/null 2>&1 || missing+=(python3-pip)
  dpkg -s build-essential >/dev/null 2>&1 || missing+=(build-essential)
  dpkg -s libssl-dev >/dev/null 2>&1 || missing+=(libssl-dev)
  dpkg -s libffi-dev >/dev/null 2>&1 || missing+=(libffi-dev)
  dpkg -s python3-dev >/dev/null 2>&1 || missing+=(python3-dev)
  # GUI dialogs (zenity) can be useful on RPi Desktop
  dpkg -s zenity >/dev/null 2>&1 || missing+=(zenity)

  if [ ${#missing[@]} -eq 0 ]; then
    echo "Todas las dependencias del sistema están presentes."
    return 0
  fi

  echo "Faltan paquetes: ${missing[*]}"
  if command -v apt-get >/dev/null 2>&1; then
    echo "Instalando dependencias con apt-get... (esto puede tardar)"
    export DEBIAN_FRONTEND=noninteractive
    apt-get update -y
    apt-get install -y "${missing[@]}"
    apt-get clean
    return 0
  else
    echo "No se encontró apt-get. Instala manualmente: ${missing[*]}"
    exit 1
  fi
}

check_and_install_deps

# If GUI is available prompt for options
if use_gui; then
  prompt_gui_options
fi

start_progress

echo "Creando directorio $TARGET_LIB_DIR ..."
mkdir -p "$TARGET_LIB_DIR"
if [ "${INSTALL_MODE:-system}" = "system" ]; then
  chown root:root "$TARGET_LIB_DIR" || true
  chmod 0755 "$TARGET_LIB_DIR" || true
else
  chown "$USER" "$TARGET_LIB_DIR" || true
  chmod 0755 "$TARGET_LIB_DIR" || true
fi

echo "Guardando machine-id en $TARGET_LIB_DIR/machine-id ..."
if [ -f /etc/machine-id ]; then
  cat /etc/machine-id > "$TARGET_LIB_DIR/machine-id"
else
  hostnamectl --no-pager status | head -n 1 > "$TARGET_LIB_DIR/machine-id" || true
fi

echo "Preparando repositorio en $REPO_DIR ..."
if [ -n "$GITHUB_REPO" ] && [ ! -d "$REPO_DIR" ]; then
  echo "Clonando $GITHUB_REPO en $REPO_DIR ..."
  if [ "${INSTALL_MODE:-system}" = "system" ]; then
    git clone --depth 1 "$GITHUB_REPO" "$REPO_DIR"
  else
    # local mode: clone into user-owned dir
    mkdir -p "$REPO_DIR"
    git clone --depth 1 "$GITHUB_REPO" "$REPO_DIR"
    chown -R "$USER" "$REPO_DIR" || true
  fi
fi

if [ ! -d "$REPO_DIR" ]; then
  echo "No se encontró el repositorio en $REPO_DIR. Asegúrate de ejecutar este script desde el repo o usa --github-repo."
  exit 1
fi

echo "Creando virtualenv (si falta) y instalando dependencias..."
cd "$REPO_DIR"
if [ ! -d "$REPO_DIR/.venv" ]; then
  python3 -m venv "$REPO_DIR/.venv"
fi
VENV_PY="$REPO_DIR/.venv/bin/python"
VENV_PIP="$REPO_DIR/.venv/bin/pip"
progress_update 10 "Creando virtualenv e instalando pip/setuptools..."
"$VENV_PY" -m pip install --upgrade pip setuptools wheel >/dev/null

# Reinstalar requirements si han cambiado o si se pide --reinstall
REQ_FILE="$REPO_DIR/requirements.txt"
CHECKSUM_FILE="$REPO_DIR/.venv/requirements.sha256"

compute_req_checksum() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$REQ_FILE" | awk '{print $1}'
  elif command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$REQ_FILE" | awk '{print $1}'
  else
    # Fallback a python si no hay sha256sum
    "$VENV_PY" - <<PY 2>/dev/null
import hashlib,sys
print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())
PY
  fi
}

if [ -f "$REQ_FILE" ]; then
  NEEDS_INSTALL="no"
  if [ "$REINSTALL_REQ" = "yes" ]; then
    NEEDS_INSTALL="yes"
  else
    NEWSUM=$(compute_req_checksum)
    if [ -f "$CHECKSUM_FILE" ]; then
      OLDSUM=$(cat "$CHECKSUM_FILE" 2>/dev/null || true)
    else
      OLDSUM=""
    fi
    if [ "$NEWSUM" != "$OLDSUM" ]; then
      NEEDS_INSTALL="yes"
    fi
  fi

  if [ "$NEEDS_INSTALL" = "yes" ]; then
    progress_update 40 "Instalando dependencias Python desde requirements.txt..."
    "$VENV_PIP" install -r "$REQ_FILE"
    # Guardar checksum
    compute_req_checksum > "$CHECKSUM_FILE" || true
  else
    progress_update 40 "requirements.txt sin cambios; omitiendo pip install."
  fi
fi

echo "Instalando scripts en /usr/local/bin ..."
install -m 0755 "$REPO_DIR/tools/picontrol-reset-admin.sh" "$RESET_BIN"
install -m 0755 "$REPO_DIR/tools/picontrol-firstboot.sh" "$FIRSTBOOT_BIN"
install -m 0755 "$REPO_DIR/tools/picontrol-rotate-secret.sh" "/usr/local/bin/picontrol-rotate-secret.sh"
install -m 0755 "$REPO_DIR/tools/picontrol-cleanup.sh" "/usr/local/bin/picontrol-cleanup.sh" || true
install -m 0755 "$REPO_DIR/tools/picontrol-restart.sh" "/usr/local/bin/picontrol-restart.sh" || true
# Install GUI wrappers (if present in repo)
install -m 0755 "$REPO_DIR/tools/picontrol-reset-admin-gui.sh" "/usr/local/bin/picontrol-reset-admin-gui.sh" || true
install -m 0755 "$REPO_DIR/tools/picontrol-rotate-secret-gui.sh" "/usr/local/bin/picontrol-rotate-secret-gui.sh" || true
install -m 0755 "$REPO_DIR/tools/picontrol-restart-gui.sh" "/usr/local/bin/picontrol-restart-gui.sh" || true
install -m 0755 "$REPO_DIR/tools/picontrol-firstboot-gui.sh" "/usr/local/bin/picontrol-firstboot-gui.sh" || true

if [ "${INSTALL_MODE:-system}" = "local" ]; then
  # For local installs, copy user-wrappers to ~/.local/bin instead of /usr/local/bin
  mkdir -p "$HOME/.local/bin"
  install -m 0755 "$REPO_DIR/tools/picontrol-reset-admin.sh" "$HOME/.local/bin/picontrol-reset-admin.sh" || true
  install -m 0755 "$REPO_DIR/tools/picontrol-rotate-secret.sh" "$HOME/.local/bin/picontrol-rotate-secret.sh" || true
  install -m 0755 "$REPO_DIR/tools/picontrol-restart.sh" "$HOME/.local/bin/picontrol-restart.sh" || true
  install -m 0755 "$REPO_DIR/tools/picontrol-reset-admin-gui.sh" "$HOME/.local/bin/picontrol-reset-admin-gui.sh" || true
  install -m 0755 "$REPO_DIR/tools/picontrol-rotate-secret-gui.sh" "$HOME/.local/bin/picontrol-rotate-secret-gui.sh" || true
  install -m 0755 "$REPO_DIR/tools/picontrol-restart-gui.sh" "$HOME/.local/bin/picontrol-restart-gui.sh" || true
  install -m 0755 "$REPO_DIR/tools/picontrol-firstboot-gui.sh" "$HOME/.local/bin/picontrol-firstboot-gui.sh" || true
fi

# --- Privilegios delegados para reiniciar (system install) ---
if [ "${INSTALL_MODE:-system}" = "system" ]; then
  # Crear grupo limitado para admins de picontrol
  if ! getent group picontrol-admins >/dev/null 2>&1; then
    echo "Creando grupo 'picontrol-admins'..."
    groupadd --system picontrol-admins || true
  fi
  # Añadir el usuario del servicio al grupo para permitir reinicios sin contraseña
  if id -u "$SERVICE_USER" >/dev/null 2>&1; then
    usermod -aG picontrol-admins "$SERVICE_USER" || true
  fi

  # Crear una entrada sudoers específica y segura para permitir reinicios sin contraseña
  SUDOERS_FILE="/etc/sudoers.d/picontrol"
  cat > "$SUDOERS_FILE" <<'SUDO'
# Permitir a miembros de picontrol-admins reiniciar los servicios de PiControl sin contraseña
%picontrol-admins ALL=(root) NOPASSWD: /usr/local/bin/picontrol-restart.sh
SUDO
  chmod 0440 "$SUDOERS_FILE" || true
  echo "Archivo sudoers creado en $SUDOERS_FILE (permite ejecutar /usr/local/bin/picontrol-restart.sh sin contraseña para el grupo picontrol-admins)."
fi

progress_update 60 "Instalando servicios systemd y configurando unidades..."

echo "Instalando servicio systemd..."
if [ "${INSTALL_MODE:-system}" = "system" ]; then
  install -m 0644 "$REPO_DIR/install/picontrol-firstboot.service" "$SERVICE_FILE"
fi

echo "Recargando systemd y habilitando servicio..."
if [ "${INSTALL_MODE:-system}" = "system" ]; then
  systemctl daemon-reload
  systemctl enable --now picontrol-firstboot.service || true
fi

# Crear e instalar unidad systemd para la API (picontrol.service)
PICONTROL_SERVICE_FILE="/etc/systemd/system/picontrol.service"

# Crear usuario de servicio específico si no existe
SERVICE_USER="picontrol"
if [ "${INSTALL_MODE:-system}" = "system" ]; then
  if ! id -u "$SERVICE_USER" >/dev/null 2>&1; then
    echo "Creando usuario de servicio $SERVICE_USER ..."
    useradd --system --no-create-home --home-dir "$TARGET_LIB_DIR" --shell /usr/sbin/nologin "$SERVICE_USER" || true
  fi
fi

CONFIG_FILE="/etc/default/picontrol"

# Crear archivo de configuración seguro con SECRET_KEY si no existe
if [ ! -f "$CONFIG_FILE" ]; then
  echo "Generando archivo de configuración $CONFIG_FILE con SECRET_KEY..."
  # Generar una secret key segura usando python3
  if command -v python3 >/dev/null 2>&1; then
    SECRET_VAL=$(python3 - <<'PY'
import secrets
print(secrets.token_urlsafe(32))
PY
)
  else
    # Fallback a /dev/urandom en base64
    SECRET_VAL=$(head -c 48 /dev/urandom | base64 | tr -d '\n')
  fi
  mkdir -p "$(dirname "$CONFIG_FILE")"
  cat > "$CONFIG_FILE" <<EOF
# Configuration for PiControl
# Do not share this file; contains SECRET_KEY for session encryption
SECRET_KEY=$SECRET_VAL
EOF
  chmod 0600 "$CONFIG_FILE"
  chown root:root "$CONFIG_FILE"
  echo "Archivo $CONFIG_FILE creado con permisos 600."
else
  echo "Archivo de configuración $CONFIG_FILE ya existe; preservando SECRET_KEY existente."
fi

if [ "${INSTALL_MODE:-system}" = "local" ]; then
  # For local installs, write a per-user config under $TARGET_LIB_DIR
  CONFIG_FILE_USER="$TARGET_LIB_DIR/picontrol.env"
  if [ ! -f "$CONFIG_FILE_USER" ]; then
    mkdir -p "$(dirname "$CONFIG_FILE_USER")"
    echo "SECRET_KEY=$SECRET_VAL" > "$CONFIG_FILE_USER"
    chmod 0600 "$CONFIG_FILE_USER"
    chown "$USER":"$USER" "$CONFIG_FILE_USER" || true
    echo "Archivo de configuración local creado en $CONFIG_FILE_USER"
  fi
fi

echo "Creando unidad systemd para la API en $PICONTROL_SERVICE_FILE (usuario: $SERVICE_USER)"
cat > "$PICONTROL_SERVICE_FILE" <<EOF
[Unit]
Description=PiControl API (uvicorn)
After=network.target picontrol-firstboot.service
Requires=picontrol-firstboot.service
Wants=picontrol-firstboot.service

[Service]
# Use the environment file for secrets and configuration
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=$REPO_DIR
EnvironmentFile=$CONFIG_FILE
# Esperar hasta 30 segundos a que firstboot marque completion; si no, fallará y systemd reintentará
ExecStartPre=/bin/sh -c 'for i in '\''1 2 3 4 5 6 7 8 9 10'\''; do [ -f /var/lib/picontrol/firstboot_done ] && exit 0; sleep 3; done; exit 1'
ExecStart=$REPO_DIR/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
EOF

echo "Recargando systemd y habilitando picontrol.service..."
if [ "${INSTALL_MODE:-system}" = "system" ]; then
  systemctl daemon-reload
  systemctl enable --now picontrol.service || true
else
  echo "Instalación local: no se crea unidad systemd. Para ejecutar PiControl en modo local puedes lanzar: $REPO_DIR/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000"
fi

progress_update 80 "Inicializando base de datos y ajustando permisos..."

# Instalar y habilitar cleanup timer/service para borrar registros antiguos
CLEANUP_SERVICE_SRC="$REPO_DIR/install/cleanup_picontrol.service"
CLEANUP_TIMER_SRC="$REPO_DIR/install/cleanup_picontrol.timer"
if [ -f "$CLEANUP_SERVICE_SRC" ]; then
  echo "Instalando cleanup service..."
  install -m 0644 "$CLEANUP_SERVICE_SRC" "/etc/systemd/system/cleanup_picontrol.service"
fi
if [ -f "$CLEANUP_TIMER_SRC" ]; then
  echo "Instalando cleanup timer..."
  install -m 0644 "$CLEANUP_TIMER_SRC" "/etc/systemd/system/cleanup_picontrol.timer"
fi
echo "Instalando wrapper de cleanup en /usr/local/bin..."
install -m 0755 "$REPO_DIR/tools/picontrol-cleanup.sh" "/usr/local/bin/picontrol-cleanup.sh" || true

echo "Recargando systemd y habilitando cleanup.timer..."
systemctl daemon-reload
systemctl enable --now cleanup_picontrol.timer || true

# Inicializar la base de datos en /var/lib/picontrol/pi_control.db si no existe.
VENV_PY="$REPO_DIR/.venv/bin/python"
DB_PATH="/var/lib/picontrol/pi_control.db"

# Asegurar directorios y permisos
echo "Creando /var/log/picontrol y ajustando permisos..."
mkdir -p /var/log/picontrol
chown "$SERVICE_USER":"$SERVICE_USER" /var/log/picontrol || true
chmod 0750 /var/log/picontrol || true

echo "Ajustando propiedad de $TARGET_LIB_DIR y $DB_PATH..."
mkdir -p "$(dirname "$DB_PATH")"
if [ "${INSTALL_MODE:-system}" = "system" ]; then
  chown -R "$SERVICE_USER":"$SERVICE_USER" "$TARGET_LIB_DIR" || true
else
  chown -R "$USER":"$USER" "$TARGET_LIB_DIR" || true
fi

if [ ! -f "$DB_PATH" ]; then
  if [ -x "$VENV_PY" ]; then
    echo "Inicializando BD en $DB_PATH usando venv en $REPO_DIR ..."
    "$VENV_PY" -c "import sys; sys.path.insert(0, '$REPO_DIR'); from app.db import init_db; init_db()"
    chown "$SERVICE_USER":"$SERVICE_USER" "$DB_PATH" || true
    echo "Base de datos inicializada y propiedad ajustada a $SERVICE_USER"
  else
    echo "No se encontró venv-python en $VENV_PY; creando fichero vacío $DB_PATH y ajustando permisos"
    touch "$DB_PATH"
    chown "$SERVICE_USER":"$SERVICE_USER" "$DB_PATH" || true
  fi
else
  echo "Base de datos ya existe en $DB_PATH"
fi

# Crear acceso en el escritorio del usuario principal (asumimos usuario con UID 1000 si existe)
DESKTOP_USER=""
if [ -n "$USER_ARG" ]; then
  DESKTOP_USER="$USER_ARG"
else
  if id -u pi >/dev/null 2>&1; then
    DESKTOP_USER=pi
  else
    # buscar primer usuario con UID 1000
    DESKTOP_USER=$(awk -F: '$3==1000{print $1; exit}' /etc/passwd || true)
  fi
fi

if [ -n "$DESKTOP_USER" ]; then
  if getent passwd "$DESKTOP_USER" >/dev/null 2>&1; then
    USER_HOME=$(getent passwd "$DESKTOP_USER" | cut -d: -f6)
    DESKTOP_DIR="$USER_HOME/Desktop"
    mkdir -p "$DESKTOP_DIR"
[ -n "$DESKTOP_USER" ] && cat > "$DESKTOP_DIR/PiControl Reset Admin.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Reset PiControl Admin
Exec=/usr/local/bin/picontrol-reset-admin-gui.sh
Icon=utilities-terminal
Terminal=true
EOF
    chown "$DESKTOP_USER":"$DESKTOP_USER" "$DESKTOP_DIR/PiControl Reset Admin.desktop" || true
    chmod 0755 "$DESKTOP_DIR/PiControl Reset Admin.desktop"
    echo "Acceso directo creado en $DESKTOP_DIR/PiControl Reset Admin.desktop"
  # Crear acceso directo para rotar SECRET_KEY
  cat > "$DESKTOP_DIR/PiControl Rotate Secret.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Rotate PiControl Secret
Exec=/usr/local/bin/picontrol-rotate-secret-gui.sh
Icon=security-high
Terminal=true
EOF
  chown "$DESKTOP_USER":"$DESKTOP_USER" "$DESKTOP_DIR/PiControl Rotate Secret.desktop" || true
  chmod 0755 "$DESKTOP_DIR/PiControl Rotate Secret.desktop"
  echo "Acceso directo creado en $DESKTOP_DIR/PiControl Rotate Secret.desktop"
  # Crear acceso directo para reiniciar los servicios de PiControl
[...skipping unchanged lines...]
  cat > "$DESKTOP_DIR/PiControl Restart Services.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Restart PiControl Services
Exec=/usr/local/bin/picontrol-restart-gui.sh
Icon=system-restart
Terminal=true
EOF
  chown "$DESKTOP_USER":"$DESKTOP_USER" "$DESKTOP_DIR/PiControl Restart Services.desktop" || true
  chmod 0755 "$DESKTOP_DIR/PiControl Restart Services.desktop"
  echo "Acceso directo creado en $DESKTOP_DIR/PiControl Restart Services.desktop"
  else
    echo "Usuario especificado '$DESKTOP_USER' no existe. Omitiendo acceso en Desktop."
  fi
else
  echo "No se encontró usuario de escritorio (pi o UID 1000). Omitiendo acceso en Desktop."
fi

echo "Instalación completada. El servicio picontrol-firstboot está habilitado y se ejecutará en el siguiente arranque (o ya se lanzó)."
echo "Si quieres desinstalar, borra los archivos instalados y deshabilita el servicio con: systemctl disable --now picontrol-firstboot.service"

progress_update 100 "Instalación completada."

if use_gui; then
  # close progress (stdin->zenity via fd3 will exit when script exits)
  true
else
  echo "Instalación completada."
fi

exit 0
