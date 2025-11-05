#!/usr/bin/env python3
"""Script para resetear/crear usuario administrador de PiControl.

Comportamiento:
- Verifica que se ejecute localmente (se asume llamada desde el wrapper que ya comprobó machine-id).
- Si existe algún administrador, le cambia la contraseña a una generada aleatoria y la escribe en
  /var/lib/picontrol/reset_password.txt con permisos 600.
- Si no existe admin, crea uno llamado 'admin' con contraseña generada y guarda la contraseña.
"""
import os
import secrets
from sqlmodel import Session
from app.db import get_engine
from app.crud import get_user_by_username, any_admin_exists, create_user, change_user_password


def generate_password(n=12):
    return secrets.token_urlsafe(n)


def save_password(path: str, username: str, password: str):
    """Print the generated credentials to stdout instead of writing them to disk.

    For security, we avoid persisting plaintext passwords on disk by default.
    If you really need a file, set the environment variable PICONTROL_ALLOW_PERSISTENT_RESET=1
    and the function will fall back to writing the file (with 0600).
    """
    # If an operator explicitly allows persistent storage, write the file (opt-in)
    allow = os.environ.get("PICONTROL_ALLOW_PERSISTENT_RESET", "0")
    if allow in ("1", "true", "yes"):
        with open(path, "w") as f:
            f.write(f"username:{username}\npassword:{password}\n")
        os.chmod(path, 0o600)
        print(f"Credenciales escritas en: {path} (PICONTROL_ALLOW_PERSISTENT_RESET habilitado)")
        return

    # Default behaviour: print to stdout and instruct operator to copy/store securely.
    print("=== PiControl admin credentials (one-time output) ===")
    print(f"username: {username}")
    print(f"password: {password}")
    print("=================================================")
    print("Nota: por seguridad no se ha guardado la contraseña en disco. Si necesitas persistirla temporariamente, exporta PICONTROL_ALLOW_PERSISTENT_RESET=1 y vuelve a ejecutar")


def main():
    engine = get_engine()
    out_file = "/var/lib/picontrol/reset_password.txt"
    username = "admin"
    pwd = generate_password(12)

    with Session(engine) as session:
        if any_admin_exists(session):
            # si existe el admin con username 'admin', cambiar contraseña
            user = get_user_by_username(session, username)
            if user:
                changed = change_user_password(session, username, pwd, performed_by="reset_admin_script")
                if changed:
                    save_password(out_file, username, pwd)
                    print(f"Contraseña del usuario '{username}' actualizada.")
                    print(f"Saved password info to {out_file}")
                    return
            # Si hay admins pero no 'admin', intentar cambiar la contraseña 'admin' como fallback
            try:
                changed = change_user_password(session, username, pwd, performed_by="reset_admin_script")
                if changed:
                    save_password(out_file, username, pwd)
                    print(f"Contraseña del usuario '{username}' actualizada (fallback).")
                    print(f"Saved password info to {out_file}")
                    return
            except Exception:
                # último recurso: crear admin 'admin'
                create_user(session, username=username, password=pwd, is_admin=True, performed_by="reset_admin_script")
                save_password(out_file, username, pwd)
                print(f"Se creó usuario admin '{username}'. Contraseña guardada en {out_file}")
                return

        # no hay admin: crear uno nuevo
        create_user(session, username=username, password=pwd, is_admin=True, performed_by="reset_admin_script")
        save_password(out_file, username, pwd)
        print(f"Usuario admin '{username}' creado. Contraseña guardada en {out_file}")


if __name__ == "__main__":
    main()
