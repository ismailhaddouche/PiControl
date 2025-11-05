#!/usr/bin/env bash
# Wrapper para ejecutar la limpieza programada de PiControl (timer)
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON_EXEC="/usr/bin/env python3"

echo "Ejecutando limpieza programada de registros antiguos..."
"$PYTHON_EXEC" "$REPO_DIR/tools/cleanup_old_records.py" --delete-employees --backup-dir /var/backups/picontrol

echo "Limpieza finalizada."

exit 0
