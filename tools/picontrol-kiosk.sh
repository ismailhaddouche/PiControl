#!/usr/bin/env bash
# Simple launcher for kiosk mode on Raspberry Pi
# This script attempts to launch Chromium in kiosk mode pointing to the local PiControl UI.

URL=${PICONTROL_KIOSK_URL:-http://localhost:8000/kiosk}
# Detect chromium binary path (support common package names)
CHROMIUM=${CHROMIUM_BIN:-"$(command -v chromium-browser || command -v chromium || command -v /usr/bin/chromium-browser || true)"}
if [ -z "$CHROMIUM" ]; then
  echo "Chromium no encontrado en PATH; intentando rutas alternativas..."
  if [ -x /usr/bin/chromium-browser ]; then
    CHROMIUM=/usr/bin/chromium-browser
  elif [ -x /usr/bin/chromium ]; then
    CHROMIUM=/usr/bin/chromium
  else
    echo "ERROR: Chromium no está instalado. Instala 'chromium-browser' o 'chromium' y reintenta."
    exit 1
  fi
fi

set -euo pipefail

echo "Starting PiControl kiosk: $URL"

# Wait for X to be available (if running under X desktop)
if [ -z "${DISPLAY:-}" ]; then
  # if no DISPLAY, try to set :0
  export DISPLAY=:0
fi

# Give the system a short moment to bring up the desktop
sleep 2

# Flags recomendadas para modo kiosk: pantalla completa, sin marcos ni barras del navegador
exec "$CHROMIUM" \
  --kiosk \
  --start-fullscreen \
  --noerrdialogs \
  --incognito \
  --no-first-run \
  --disable-session-crashed-bubble \
  --disable-translate \
  --disable-infobars \
  --disable-features=TranslateUI \
  --app="$URL"
