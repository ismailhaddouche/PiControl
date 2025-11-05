#!/usr/bin/env python3
"""Limpiar fichajes y empleados antiguos.

Por defecto elimina fichajes con más de 4 años + 1 día de antigüedad.
Opcionalmente puede eliminar empleados archivados con archived_at antiguo y/o empleados
inactivos (sin fichajes recientes) si se pasa --delete-employees.

Hace un backup de la base de datos antes de modificarla.
"""
from __future__ import annotations
import argparse
import shutil
import os
from datetime import datetime, timezone, timedelta
from sqlmodel import Session, select
from app.db import get_engine
from app.models import Empleado, Fichaje


DEFAULT_DB_DIR = os.environ.get("PICONTROL_DB_DIR", "/var/lib/picontrol")
DB_PATH = os.path.join(DEFAULT_DB_DIR, "pi_control.db")
BACKUP_DIR = os.environ.get("PICONTROL_BACKUP_DIR", "/var/backups/picontrol")


def backup_db(db_path: str, backup_dir: str) -> str:
    os.makedirs(backup_dir, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dest = os.path.join(backup_dir, f"pi_control.db.backup.{ts}")
    shutil.copy2(db_path, dest)
    return dest


def parse_args():
    p = argparse.ArgumentParser(description="Cleanup old records (fichajes/empleados) in PiControl DB")
    p.add_argument("--days", type=int, default=4 * 365 + 1,
                   help="Age in days to consider for deletion (default 4 years + 1 day)")
    p.add_argument("--delete-employees", action="store_true",
                   help="Also delete employees archived before cutoff or inactive since cutoff")
    p.add_argument("--dry-run", action="store_true", help="Do not modify DB, just print what would be done")
    p.add_argument("--db-path", default=DB_PATH, help="Path to sqlite DB file")
    p.add_argument("--backup-dir", default=BACKUP_DIR, help="Directory to store DB backups")
    return p.parse_args()


def main():
    args = parse_args()
    cutoff = datetime.now(timezone.utc) - timedelta(days=args.days)
    print(f"Cutoff datetime (UTC): {cutoff.isoformat()}")

    if not os.path.isfile(args.db_path):
        print(f"Database not found at {args.db_path}")
        return

    if not args.dry_run:
        print("Creating DB backup...")
        b = backup_db(args.db_path, args.backup_dir)
        print(f"Backup created at {b}")
    else:
        print("Dry-run: skipping backup")

    engine = get_engine()
    # Note: get_engine uses PICONTROL_DB_DIR default; ensure it points to args.db_path location if overriden
    # If the engine points elsewhere, user should set PICONTROL_DB_DIR env var when running.

    to_delete_empleados = []
    deleted_fichajes = 0

    with Session(engine) as session:
        # Delete fichajes older than cutoff
        stmt = select(Fichaje).where(Fichaje.timestamp <= cutoff)
        old_fichajes = session.exec(stmt).all()
        print(f"Found {len(old_fichajes)} fichajes older than cutoff")
        if not args.dry_run:
            for f in old_fichajes:
                session.delete(f)
            session.commit()
            deleted_fichajes = len(old_fichajes)

        if args.delete_employees:
            empleados = session.exec(select(Empleado)).all()
            for e in empleados:
                remove = False
                reason = None
                if e.archived_at is not None and e.archived_at <= cutoff:
                    remove = True
                    reason = f"archived_at {e.archived_at} <= cutoff"
                else:
                    # check last fichaje
                    last_stmt = select(Fichaje).where(Fichaje.empleado_id == e.dni).order_by(Fichaje.timestamp.desc())
                    last = session.exec(last_stmt).first()
                    if not last or last.timestamp <= cutoff:
                        remove = True
                        reason = f"last_fichaje {getattr(last, 'timestamp', None)} <= cutoff or none"

                if remove:
                    to_delete_empleados.append((e, reason))

            print(f"Found {len(to_delete_empleados)} empleados to delete (delete_employees=True)")
            if not args.dry_run:
                for e, reason in to_delete_empleados:
                    print(f"Deleting empleado {e.dni} ({e.nombre}): {reason}")
                    session.delete(e)
                session.commit()

    print("Cleanup complete.")
    if args.dry_run:
        print("Dry-run mode, no changes were made.")
    else:
        print(f"Deleted fichajes: {deleted_fichajes}; Deleted empleados: {len(to_delete_empleados)}")


if __name__ == "__main__":
    main()
