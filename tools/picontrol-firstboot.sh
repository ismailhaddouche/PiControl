#!/usr/bin/env bash
# Script que ejecuta tareas de primer arranque para PiControl
# Este script está pensado para ejecutarse por systemd en el arranque y debe ser idempotente.

set -euo pipefail

LIB_DIR="/var/lib/picontrol"
FLAG_FILE="$LIB_DIR/firstboot_done"

if [ -f "$FLAG_FILE" ]; then
  echo "Firstboot: ya ejecutado."
  exit 0
fi

echo "Firstboot: creando marcadores y comprobaciones..."
mkdir -p "$LIB_DIR"
touch "$FLAG_FILE"
chmod 0644 "$FLAG_FILE"

echo "Firstboot: completado."
exit 0
