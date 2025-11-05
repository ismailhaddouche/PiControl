#!/usr/bin/env bash
# Script wrapper que protege el reset de admin para PiControl
# Comprueba que se ejecute en la Raspberry Pi original (machine-id) antes de permitir el reset.

set -euo pipefail

LIB_DIR="/var/lib/picontrol"
STORED_ID="$LIB_DIR/machine-id"
CURRENT_ID_FILE="/etc/machine-id"

if [ ! -f "$STORED_ID" ]; then
  echo "No se encontró fichero de instalación ($STORED_ID). No puedo verificar la máquina. Abortando."
  exit 1
fi
if [ ! -f "$CURRENT_ID_FILE" ]; then
  echo "No existe /etc/machine-id. Abortando."
  exit 1
fi

STORED=$(cat "$STORED_ID" | tr -d '\n\r')
CURRENT=$(cat "$CURRENT_ID_FILE" | tr -d '\n\r')

if [ "$STORED" != "$CURRENT" ]; then
  echo "Esta herramienta sólo puede ejecutarse desde la Raspberry Pi original. Abortando."
  exit 1
fi

echo "Máquina verificada. Ejecutando reset del administrador localmente..."
PYTHON_EXEC="/usr/bin/env python3"
SCRIPT_DIR="$(dirname "$0")/.."

# Ejecutar script Python que hace el reset (crea una cuenta admin con contraseña aleatoria)
"$PYTHON_EXEC" "$SCRIPT_DIR/tools/reset_admin.py"

exit 0
