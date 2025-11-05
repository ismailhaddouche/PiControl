#!/usr/bin/env bash
# GUI wrapper for rotating PiControl SECRET_KEY
set -euo pipefail

SCRIPT="/usr/local/bin/picontrol-rotate-secret.sh"

has() { command -v "$1" >/dev/null 2>&1; }

if has zenity; then
  if ! zenity --question --title="Rotate SECRET_KEY" --text="¿Desea regenerar la SECRET_KEY de PiControl en esta máquina?"; then
    exit 0
  fi
fi

# Run with pkexec when available so it runs as root; otherwise open terminal
if has pkexec; then
  pkexec "$SCRIPT"
else
  if command -v x-terminal-emulator >/dev/null 2>&1; then
    x-terminal-emulator -e bash -lc "sudo $SCRIPT; echo; read -p 'Presiona Enter para cerrar...';"
  else
    sudo "$SCRIPT"
  fi
fi

exit 0
