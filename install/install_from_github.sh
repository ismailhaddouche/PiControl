#!/usr/bin/env bash
# Instalador que clona el repositorio desde GitHub y ejecuta el instalador local
# Uso: sudo install/install_from_github.sh <git_repo_url> [branch] [--user USER]

set -euo pipefail

usage() {
  cat <<EOF
Usage: $0 <git_repo_url> [branch] [--user USER]

Example:
  sudo $0 https://github.com/usuario/PiControl.git main --user pi

This script will clone the repo to /opt/picontrol (or pull if exists), create a venv,
install Python requirements, and run the repository's install/pi_installer.sh script.
EOF
  exit 1
}

if [ "$#" -lt 1 ]; then
  usage
fi

REPO_URL="$1"
BRANCH="main"
USER_ARG=""
if [ "$#" -ge 2 ]; then
  BRANCH="$2"
fi

shift 2 || true
while [ "$#" -gt 0 ]; do
  case "$1" in
    --user|-u)
      USER_ARG="$2"
      shift 2
      ;;
    --help|-h)
      usage
      ;;
    *)
      echo "Unknown arg: $1"
      usage
      ;;
  esac
done

DEST_DIR="/opt/picontrol"
VENV_DIR="$DEST_DIR/.venv"

if [ "$EUID" -ne 0 ]; then
  echo "This installer must be run as root (it installs system services and writes to /opt)."
  exit 1
fi

echo "Cloning $REPO_URL (branch $BRANCH) into $DEST_DIR ..."
if [ -d "$DEST_DIR/.git" ]; then
  echo "Repository already exists, fetching and resetting to $BRANCH"
  git -C "$DEST_DIR" fetch --all --prune
  git -C "$DEST_DIR" checkout "$BRANCH"
  git -C "$DEST_DIR" reset --hard "origin/$BRANCH"
else
  rm -rf "$DEST_DIR"
  git clone --depth 1 --branch "$BRANCH" "$REPO_URL" "$DEST_DIR"
fi

echo "Creating virtualenv in $VENV_DIR ..."
python3 -m venv "$VENV_DIR"
# Use pip from venv
PIP="$VENV_DIR/bin/pip"
PYTHON="$VENV_DIR/bin/python"

if [ -f "$DEST_DIR/requirements.txt" ]; then
  echo "Installing Python requirements..."
  "$PIP" install --upgrade pip
  "$PIP" install -r "$DEST_DIR/requirements.txt"
else
  echo "No requirements.txt found in repo; skipping pip install"
fi

echo "Running repository installer..."
if [ -x "$DEST_DIR/install/pi_installer.sh" ]; then
  if [ -n "$USER_ARG" ]; then
    "$DEST_DIR/install/pi_installer.sh" --user "$USER_ARG"
  else
    "$DEST_DIR/install/pi_installer.sh"
  fi
else
  echo "Installer script not found or not executable: $DEST_DIR/install/pi_installer.sh"
  exit 1
fi

echo "Installation from GitHub complete."
echo "Please check systemd service status: systemctl status picontrol-firstboot.service"

exit 0
