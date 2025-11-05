#!/usr/bin/env python3
"""Utility to initialize the PiControl database on the target machine.

This is a small convenience script that calls the application's init_db()
function so deployers can run it manually (or from the installer) without
importing application modules directly.
"""
import sys

def main():
    try:
        from app.db import init_db
    except Exception as e:
        print("Error: no se puede importar app.db. Comprueba el entorno y PYTHONPATH.", e)
        sys.exit(2)

    try:
        init_db()
        print("Inicialización de la base de datos completada.")
    except Exception as e:
        print("Fallo al inicializar la base de datos:", e)
        sys.exit(1)

if __name__ == '__main__':
    main()
