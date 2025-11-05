#!/usr/bin/env bash
# GUI wrapper for restarting PiControl services
set -euo pipefail

SCRIPT="/usr/local/bin/picontrol-restart.sh"

has() { command -v "$1" >/dev/null 2>&1; }

if has zenity; then
  if ! zenity --question --title="Restart PiControl" --text="Do you want to restart PiControl services now?"; then
    exit 0
  fi
fi

if has pkexec; then
  pkexec "$SCRIPT"
else
  if command -v x-terminal-emulator >/dev/null 2>&1; then
    x-terminal-emulator -e bash -lc "sudo $SCRIPT; echo; read -p 'Press Enter to close...';"
  else
    sudo "$SCRIPT"
  fi
fi

exit 0
