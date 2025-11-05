#!/usr/bin/env bash
# GUI wrapper for resetting PiControl admin account
set -euo pipefail

SCRIPT="/usr/local/bin/picontrol-reset-admin.sh"

has() { command -v "$1" >/dev/null 2>&1; }

if has zenity; then
  if ! zenity --question --title="Reset PiControl Admin" --text="Do you want to generate/reset the admin account on this machine?"; then
    exit 0
  fi
fi

if has pkexec; then
  pkexec "$SCRIPT"
else
  # fallback: open in terminal (user will be prompted for sudo)
  if command -v x-terminal-emulator >/dev/null 2>&1; then
    x-terminal-emulator -e bash -lc "sudo $SCRIPT; echo; read -p 'Press Enter to close...';"
  elif command -v xterm >/dev/null 2>&1; then
    xterm -e sudo "$SCRIPT"
  else
    sudo "$SCRIPT"
  fi
fi

exit 0
