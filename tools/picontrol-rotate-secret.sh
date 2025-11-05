#!/usr/bin/env bash
# Wrapper para regenerar la SECRET_KEY de PiControl vinculado a la máquina (machine-id)

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

echo "Máquina verificada. Regenerando SECRET_KEY localmente..."
PYTHON_EXEC="/usr/bin/env python3"
SCRIPT_DIR="$(dirname "$0")/.."

"$PYTHON_EXEC" "$SCRIPT_DIR/tools/rotate_secret.py"

echo "Operación completada. Se ha guardado una copia en /var/lib/picontrol/secret_key.txt (permisos 600)."

exit 0
