#!/usr/bin/env python3
"""Regenera la SECRET_KEY para PiControl y la escribe en /etc/default/picontrol.

Este script está pensado para ejecutarse localmente (desde el wrapper que valida machine-id).
Genera una clave segura, la escribe en /etc/default/picontrol con permisos 600 y guarda una copia
en /var/lib/picontrol/secret_key.txt (modo 600) para que el administrador pueda consultarla si es necesario.
Finalmente reinicia el servicio `picontrol.service` para aplicar la nueva clave.
"""
import os
import secrets
import stat
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
    os.chown(CONFIG_FILE, 0, 0)


def save_copy(secret):
    os.makedirs(LIB_DIR, exist_ok=True)
    with open(OUT_FILE, "w") as f:
        f.write(f"SECRET_KEY={secret}\n")
    os.chmod(OUT_FILE, 0o600)


def restart_service():
    try:
        subprocess.run(["systemctl", "restart", "picontrol.service"], check=True)
        print("picontrol.service reiniciado correctamente.")
    except subprocess.CalledProcessError as e:
        print("Advertencia: fallo al reiniciar picontrol.service:", e)


def main():
    secret = generate_secret()
    write_config(secret)
    save_copy(secret)
    print(f"Nueva SECRET_KEY generada y guardada en {CONFIG_FILE} y copia en {OUT_FILE}")
    restart_service()


if __name__ == "__main__":
    main()
