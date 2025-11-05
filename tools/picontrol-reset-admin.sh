#!/usr/bin/env bash
# Wrapper script that protects the admin reset for PiControl
# Verifies it runs on the original Raspberry Pi (machine-id) before allowing reset.

set -euo pipefail

LIB_DIR="/var/lib/picontrol"
STORED_ID="$LIB_DIR/machine-id"
CURRENT_ID_FILE="/etc/machine-id"

if [ ! -f "$STORED_ID" ]; then
  echo "Installation file not found ($STORED_ID). Cannot verify machine. Aborting."
  exit 1
fi
if [ ! -f "$CURRENT_ID_FILE" ]; then
  echo "/etc/machine-id not found. Aborting."
  exit 1
fi

STORED=$(cat "$STORED_ID" | tr -d '\n\r')
CURRENT=$(cat "$CURRENT_ID_FILE" | tr -d '\n\r')

if [ "$STORED" != "$CURRENT" ]; then
  echo "This tool can only run on the original Raspberry Pi. Aborting."
  exit 1
fi
echo "Machine verified. Running admin reset locally..."
PYTHON_EXEC="/usr/bin/env python3"
SCRIPT_DIR="$(dirname "$0")/.."

# Execute Python script that performs the reset (creates an admin account with a random password)
"$PYTHON_EXEC" "$SCRIPT_DIR/tools/reset_admin.py"

exit 0
