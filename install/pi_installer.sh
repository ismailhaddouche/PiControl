#!/usr/bin/env bash
# Instalador para Raspberry Pi - configura servicio de primer arranque y script de reseteo local
# Debe ejecutarse como root en la Raspberry Pi destino.

set -euo pipefail

TARGET_LIB_DIR="/var/lib/picontrol"
RESET_BIN="/usr/local/bin/picontrol-reset-admin.sh"
FIRSTBOOT_BIN="/usr/local/bin/picontrol-firstboot.sh"
SERVICE_FILE="/etc/systemd/system/picontrol-firstboot.service"

usage() {
  cat <<EOF
Usage: $0 [--user USER]

  --user USER, -u USER   Crear acceso .desktop para el usuario USER (opcional).
EOF
  exit 1
}

USER_ARG=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --user|-u)
      shift
      USER_ARG="$1"
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

if [ "$EUID" -ne 0 ]; then
  echo "Este instalador debe correrse como root. Salida."
  exit 1
fi

echo "Creando directorio $TARGET_LIB_DIR ..."
mkdir -p "$TARGET_LIB_DIR"
chown root:root "$TARGET_LIB_DIR"
chmod 0755 "$TARGET_LIB_DIR"

echo "Guardando machine-id en $TARGET_LIB_DIR/machine-id ..."
if [ -f /etc/machine-id ]; then
  cat /etc/machine-id > "$TARGET_LIB_DIR/machine-id"
else
  hostnamectl --no-pager status | head -n 1 > "$TARGET_LIB_DIR/machine-id" || true
fi

echo "Instalando scripts en /usr/local/bin ..."
install -m 0755 "$(dirname "$0")/../tools/picontrol-reset-admin.sh" "$RESET_BIN"
install -m 0755 "$(dirname "$0")/../tools/picontrol-firstboot.sh" "$FIRSTBOOT_BIN"

echo "Instalando servicio systemd..."
install -m 0644 "$(dirname "$0")/picontrol-firstboot.service" "$SERVICE_FILE"

echo "Recargando systemd y habilitando servicio..."
systemctl daemon-reload
systemctl enable --now picontrol-firstboot.service || true

# Crear e instalar unidad systemd para la API (picontrol.service)
PICONTROL_SERVICE_FILE="/etc/systemd/system/picontrol.service"

# Determinar usuario para ejecutar el servicio (usar el mismo usuario de escritorio si existe)
SERVICE_USER="www-data"
if [ -n "$DESKTOP_USER" ]; then
  if getent passwd "$DESKTOP_USER" >/dev/null 2>&1; then
    SERVICE_USER="$DESKTOP_USER"
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
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=/opt/picontrol
Environment=SECRET_KEY=devsecret
# Esperar hasta 30 segundos a que firstboot marque completion; si no, fallará y systemd reintentará
ExecStartPre=/bin/sh -c 'for i in \'1 2 3 4 5 6 7 8 9 10\'; do [ -f /var/lib/picontrol/firstboot_done ] && exit 0; sleep 3; done; exit 1'
ExecStart=/opt/picontrol/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
EOF

echo "Recargando systemd y habilitando picontrol.service..."
systemctl daemon-reload
systemctl enable --now picontrol.service || true

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
    cat > "$DESKTOP_DIR/PiControl Reset Admin.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Reset PiControl Admin
Exec=$RESET_BIN
Icon=utilities-terminal
Terminal=true
EOF
    chown "$DESKTOP_USER":"$DESKTOP_USER" "$DESKTOP_DIR/PiControl Reset Admin.desktop" || true
    chmod 0755 "$DESKTOP_DIR/PiControl Reset Admin.desktop"
    echo "Acceso directo creado en $DESKTOP_DIR/PiControl Reset Admin.desktop"
  else
    echo "Usuario especificado '$DESKTOP_USER' no existe. Omitiendo acceso en Desktop."
  fi
else
  echo "No se encontró usuario de escritorio (pi o UID 1000). Omitiendo acceso en Desktop."
fi

echo "Instalación completada. El servicio picontrol-firstboot está habilitado y se ejecutará en el siguiente arranque (o ya se lanzó)."
echo "Si quieres desinstalar, borra los archivos instalados y deshabilita el servicio con: systemctl disable --now picontrol-firstboot.service"

exit 0
