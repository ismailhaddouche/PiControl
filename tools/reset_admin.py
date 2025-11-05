#!/usr/bin/env python3
"""Script to reset/create the PiControl administrator account.

Behavior:
- Assumes it's run locally (the wrapper verifies machine-id).
- If an admin exists, it changes the password to a newly generated one and prints the
    credentials to stdout by default (or writes to /var/lib/picontrol/reset_password.txt when
    PICONTROL_ALLOW_PERSISTENT_RESET is enabled).
- If no admin exists, it creates an 'admin' user with a generated password and prints it.
"""
import os
import secrets
from sqlmodel import Session
from app.db import get_engine
from app.crud import any_admin_exists, get_user, create_user, update_user_password


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
        print(f"Credentials written to: {path} (PICONTROL_ALLOW_PERSISTENT_RESET enabled)")
        return

    # Default behaviour: print to stdout and instruct operator to copy/store securely.
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
            # if an admin with username 'admin' exists, change its password
            user = get_user(session, username)
            if user:
                changed = update_user_password(session, username, pwd, performed_by="reset_admin_script")
                if changed:
                    save_password(out_file, username, pwd)
                    print(f"Password for user '{username}' updated.")
                    print(f"Saved password info to {out_file}")
                    return
            # If there are admins but no 'admin', try changing 'admin' password as fallback
            try:
                changed = update_user_password(session, username, pwd, performed_by="reset_admin_script")
                if changed:
                    save_password(out_file, username, pwd)
                    print(f"Password for user '{username}' updated (fallback).")
                    print(f"Saved password info to {out_file}")
                    return
            except Exception:
                # last resort: create admin 'admin'
                create_user(session, username=username, password=pwd, is_admin=True, performed_by="reset_admin_script")
                save_password(out_file, username, pwd)
                print(f"Admin user '{username}' created. Password saved to {out_file}")
                return

        # no admin: create a new one
    create_user(session, username=username, password=pwd, is_admin=True, performed_by="reset_admin_script")
    save_password(out_file, username, pwd)
    print(f"Admin user '{username}' created. Password saved to {out_file}")


if __name__ == "__main__":
    main()
