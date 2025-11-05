#!/usr/bin/env bash
# Picontrol restart helper
# Restart PiControl services and print basic output.

set -euo pipefail

SVC="picontrol.service"
CLEANUP_TIMER="cleanup_picontrol.timer"

echo "Attempting user-level restart first (if service installed as user)..."
if systemctl --user list-units | grep -q "picontrol.service"; then
  echo "Restarting user service picontrol.service..."
  systemctl --user restart picontrol.service && echo "User picontrol.service restarted." || echo "Failed to restart user picontrol.service"
  exit 0
fi

echo "User-level service not found. Attempting system-level restart (may require root)."
if systemctl is-active --quiet "$SVC"; then
  systemctl restart "$SVC" && echo "$SVC restarted." || echo "Failed to restart $SVC"
else
  echo "$SVC was not active; attempting start & enable"
  systemctl enable --now "$SVC" && echo "$SVC started and enabled." || echo "Failed to start $SVC"
fi

if systemctl list-units --full -all | grep -q "${CLEANUP_TIMER}"; then
  echo "Reloading and enabling timer $CLEANUP_TIMER..."
  systemctl daemon-reload || true
  systemctl enable --now "$CLEANUP_TIMER" && echo "$CLEANUP_TIMER enabled." || echo "Failed to enable $CLEANUP_TIMER"
fi

echo "Operation completed. Check status with: systemctl status $SVC"

exit 0
