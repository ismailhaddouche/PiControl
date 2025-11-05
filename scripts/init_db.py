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
        print("Error: cannot import app.db. Check the environment and PYTHONPATH.", e)
        sys.exit(2)

    try:
        init_db()
        print("Database initialization completed.")
    except Exception as e:
        print("Failed to initialize database:", e)
        sys.exit(1)

if __name__ == '__main__':
    main()
