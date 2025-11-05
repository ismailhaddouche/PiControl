#!/usr/bin/env bash
# Script that executes first boot tasks for PiControl
# This script is designed to be run by systemd at boot and must be idempotent.

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
