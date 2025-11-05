#!/usr/bin/env python3
"""Regenerate the SECRET_KEY for PiControl and write it to /etc/default/picontrol.

For security this script does NOT persistently store a copy of the key in
`/var/lib/picontrol/secret_key.txt` by default. It prints the new key to stdout
and only creates a backup file when --backup is provided.

This avoids leaving secret files on disk by default.
"""
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
    # write atomically
    tmp = CONFIG_FILE + ".tmp"
    with open(tmp, "w") as f:
        f.write(content)
    os.chmod(tmp, 0o600)
    os.replace(tmp, CONFIG_FILE)
    try:
        os.chown(CONFIG_FILE, 0, 0)
    except Exception:
        # best-effort: if not root or on systems without uid 0 mapping, ignore
        pass


def save_copy(secret):
    """Create a backup copy of the secret in LIB_DIR with strict permissions.

    This is opt-in and should only be used for one-time recovery; avoid leaving copies.
    """
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

    # Print the new secret to stdout so the operator can copy it (one-time)
    print("=== New SECRET_KEY (one-time output) ===")
    print(secret)
    print("======================================")

    if args.backup:
        save_copy(secret)
        print(f"Backup copy written to {OUT_FILE}")

    restart_service()


if __name__ == "__main__":
    main()
