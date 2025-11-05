"""RFID reader simulator (CLI).

Reads `rfid_uid` per line, sends a POST to the API `/checkins/` and shows the message
returned (employee name and welcome/goodbye message). Implements
retries in case of connection failure.
"""
from __future__ import annotations

import time
import sys
from typing import Optional

import httpx

API_URL = "http://127.0.0.1:8000/checkins/"


def send_checkin(rfid: str, api_url: str = API_URL, retries: int = 3, timeout: float = 5.0) -> Optional[dict]:
    """Sends the rfid to the API and returns the JSON if OK, or None if it fails.

    Reintenta `retries` veces en errores de conexión.
    """
    attempt = 0
    while attempt < retries:
        try:
            resp = httpx.post(api_url, json={"rfid_uid": rfid}, timeout=timeout)
            if resp.status_code == 200:
                return resp.json()
            else:
                # Respuesta válida del servidor pero con error de negocio
                print(f"API ERROR ({resp.status_code}): {resp.text}")
                return None
        except (httpx.ConnectError, httpx.ReadTimeout) as e:
            attempt += 1
            wait = 0.5 * attempt
            print(f"Connection failed (attempt {attempt}/{retries}): {e}. Retrying in {wait}s...")
            time.sleep(wait)
        except Exception as e:
            print("Unexpected error connecting to API:", e)
            return None

    print("Could not connect to API after several attempts.")
    return None


def main():
    api_url = API_URL
    # allow passing URL as argument
    if len(sys.argv) > 1:
        api_url = sys.argv[1]
    print("RFID Simulator - type 'exit' to quit. Using API:", api_url)
    while True:
        try:
            rfid = input("Swipe a card (rfid_uid): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting")
            return
        if not rfid:
            continue
        if rfid.lower() in ("exit", "quit"):
            print("Exiting")
            return

        data = send_checkin(rfid, api_url=api_url)
        if not data:
            # error already printed in send_checkin
            continue

        # expected data: {id, employee_id, employee_name, type, timestamp, message}
        employee_name = data.get("employee_name") or data.get("employee_name")
        checkin_type = data.get("type")
        message = data.get("message")
        ts = data.get("timestamp")

        if employee_name:
            print(f"{message} (employee: {employee_name}) [{checkin_type}] - {ts}")
        else:
            # If no name provided, show id
            print(f"{message or 'OK'} (employee_id={data.get('employee_id')}) [{checkin_type}] - {ts}")


if __name__ == "__main__":
    main()
