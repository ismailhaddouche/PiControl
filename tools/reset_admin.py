#!/usr/bin/env python3
"""Reset or create PiControl administrator account with generated password."""
import os
import secrets
from sqlmodel import Session
from app.db import get_engine
from app.crud import any_admin_exists, get_user, create_user, update_user_password


def generate_password(n=12):
    return secrets.token_urlsafe(n)


def save_password(path: str, username: str, password: str):
    """Print credentials to stdout. Optionally write to disk if PICONTROL_ALLOW_PERSISTENT_RESET=1."""
    allow = os.environ.get("PICONTROL_ALLOW_PERSISTENT_RESET", "0")
    if allow in ("1", "true", "yes"):
        with open(path, "w") as f:
            f.write(f"username:{username}\npassword:{password}\n")
        os.chmod(path, 0o600)
        print(f"Credentials written to: {path} (PICONTROL_ALLOW_PERSISTENT_RESET enabled)")
        return

    print("=== PiControl admin credentials (one-time output) ===")
    print(f"username: {username}")
    print(f"password: {password}")
    print("=================================================")
    print("Note: for security the password has not been stored on disk. If you need a temporary file, set PICONTROL_ALLOW_PERSISTENT_RESET=1 and re-run")


def main():
    engine = get_engine()
    out_file = "/var/lib/picontrol/reset_password.txt"
    username = "admin"
    pwd = generate_password(12)

    with Session(engine) as session:
        if any_admin_exists(session):
            user = get_user(session, username)
            if user:
                changed = update_user_password(session, username, pwd, performed_by="reset_admin_script")
                if changed:
                    save_password(out_file, username, pwd)
                    print(f"Password for user '{username}' updated.")
                    print(f"Saved password info to {out_file}")
                    return
            try:
                changed = update_user_password(session, username, pwd, performed_by="reset_admin_script")
                if changed:
                    save_password(out_file, username, pwd)
                    print(f"Password for user '{username}' updated (fallback).")
                    print(f"Saved password info to {out_file}")
                    return
            except Exception:
                create_user(session, username=username, password=pwd, is_admin=True, performed_by="reset_admin_script")
                save_password(out_file, username, pwd)
                print(f"Admin user '{username}' created. Password saved to {out_file}")
                return

    create_user(session, username=username, password=pwd, is_admin=True, performed_by="reset_admin_script")
    save_password(out_file, username, pwd)
    print(f"Admin user '{username}' created. Password saved to {out_file}")


if __name__ == "__main__":
    main()
