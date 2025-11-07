#!/usr/bin/env python3
"""Regenerate SECRET_KEY and update configuration file."""
import argparse
import os
import secrets
import subprocess

CONFIG_FILE = "/etc/default/picontrol"
LIB_DIR = "/var/lib/picontrol"
OUT_FILE = os.path.join(LIB_DIR, "secret_key.txt")


def generate_secret(nbytes=32):
    return secrets.token_urlsafe(nbytes)


def write_config(secret):
    content = f"# Configuration for PiControl\n# SECRET_KEY (do not share)\nSECRET_KEY={secret}\n"
    tmp = CONFIG_FILE + ".tmp"
    with open(tmp, "w") as f:
        f.write(content)
    os.chmod(tmp, 0o600)
    os.replace(tmp, CONFIG_FILE)
    try:
        os.chown(CONFIG_FILE, 0, 0)
    except Exception:
        pass


def save_copy(secret):
    """Backup secret to file with strict permissions (opt-in only)."""
    os.makedirs(LIB_DIR, exist_ok=True)
    with open(OUT_FILE, "w") as f:
        f.write(f"SECRET_KEY={secret}\n")
    os.chmod(OUT_FILE, 0o600)


def restart_service():
    try:
        subprocess.run(["systemctl", "restart", "picontrol.service"], check=True)
        print("picontrol.service restarted successfully.")
    except subprocess.CalledProcessError as e:
        print("Warning: failed to restart picontrol.service:", e)


def main():
    parser = argparse.ArgumentParser(description="Rotate PiControl SECRET_KEY")
    parser.add_argument("--backup", action="store_true", help="Create a backup copy in /var/lib/picontrol (opt-in)")
    args = parser.parse_args()

    secret = generate_secret()
    write_config(secret)

    print("=== New SECRET_KEY (one-time output) ===")
    print(secret)
    print("======================================")

    if args.backup:
        save_copy(secret)
        print(f"Backup copy written to {OUT_FILE}")

    restart_service()


if __name__ == "__main__":
    main()
