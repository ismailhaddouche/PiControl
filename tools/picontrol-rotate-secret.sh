#!/usr/bin/env bash
# Wrapper to regenerate PiControl's SECRET_KEY tied to the machine (machine-id)

set -euo pipefail

LIB_DIR="/var/lib/picontrol"
STORED_ID="$LIB_DIR/machine-id"
CURRENT_ID_FILE="/etc/machine-id"

if [ ! -f "$STORED_ID" ]; then
  echo "Installation file not found ($STORED_ID). Cannot verify machine. Aborting."
  exit 1
fi
if [ ! -f "$CURRENT_ID_FILE" ]; then
  echo "/etc/machine-id does not exist. Aborting."
  exit 1
fi

STORED=$(cat "$STORED_ID" | tr -d '\n\r')
CURRENT=$(cat "$CURRENT_ID_FILE" | tr -d '\n\r')

if [ "$STORED" != "$CURRENT" ]; then
  echo "This tool can only be run from the original Raspberry Pi. Aborting."
  exit 1
fi

echo "Machine verified. Regenerating SECRET_KEY locally..."
PYTHON_EXEC="/usr/bin/env python3"
SCRIPT_DIR="$(dirname "$0")/.."

"$PYTHON_EXEC" "$SCRIPT_DIR/tools/rotate_secret.py"

echo "Operation completed. A copy has been saved to /var/lib/picontrol/secret_key.txt (permissions 600)."

exit 0
