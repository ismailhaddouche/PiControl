#!/usr/bin/env bash
# Picontrol restart helper
# Reinicia los servicios de la aplicación PiControl y muestra salida básica.

set -euo pipefail

SVC="picontrol.service"
CLEANUP_TIMER="cleanup_picontrol.timer"

echo "Reiniciando servicio $SVC..."
if systemctl is-active --quiet "$SVC"; then
  systemctl restart "$SVC" && echo "$SVC reiniciado." || echo "Fallo al reiniciar $SVC"
else
  echo "$SVC no estaba activo; intentando start & enable"
  systemctl enable --now "$SVC" && echo "$SVC iniciado y habilitado." || echo "Fallo al iniciar $SVC"
fi

if systemctl list-units --full -all | grep -q "${CLEANUP_TIMER}"; then
  echo "Recargando y reiniciando timer $CLEANUP_TIMER..."
  systemctl daemon-reload || true
  systemctl enable --now "$CLEANUP_TIMER" && echo "$CLEANUP_TIMER habilitado." || echo "Fallo al habilitar $CLEANUP_TIMER"
fi

echo "Operación completada. Comprueba el estado con: systemctl status $SVC"

exit 0
