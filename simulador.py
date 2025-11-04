"""Simulador del lector RFID (CLI).

Lee `rfid_uid` por línea, envía un POST a la API `/fichajes/` y muestra el mensaje
devuelto (nombre del empleado y mensaje de bienvenida/despedida). Implementa
reintentos en caso de fallo de conexión.
"""
from __future__ import annotations

import time
import sys
from typing import Optional

import httpx

API_URL = "http://127.0.0.1:8000/fichajes/"


def enviar_fichaje(rfid: str, api_url: str = API_URL, retries: int = 3, timeout: float = 5.0) -> Optional[dict]:
    """Envía el rfid a la API y devuelve el JSON si OK, o None si falla.

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
            print(f"Fallo conexión (intento {attempt}/{retries}): {e}. Reintentando en {wait}s...")
            time.sleep(wait)
        except Exception as e:
            print("Error inesperado al conectar con la API:", e)
            return None

    print("No se pudo conectar con la API tras varios intentos.")
    return None


def main():
    api_url = API_URL
    # permitir pasar URL por argumento
    if len(sys.argv) > 1:
        api_url = sys.argv[1]
    print("Simulador RFID - escribe 'salir' para terminar. Usando API:", api_url)
    while True:
        try:
            rfid = input("Pasa una tarjeta (rfid_uid): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSaliendo")
            return
        if not rfid:
            continue
        if rfid.lower() in ("salir", "exit"):
            print("Saliendo")
            return

        data = enviar_fichaje(rfid, api_url=api_url)
        if not data:
            # ya se imprimió el error en enviar_fichaje
            continue

        # data esperado: {id, empleado_id, empleado_nombre, tipo, timestamp, mensaje}
        empleado_nombre = data.get("empleado_nombre") or data.get("empleado_nombre")
        tipo = data.get("tipo")
        mensaje = data.get("mensaje")
        ts = data.get("timestamp")

        if empleado_nombre:
            print(f"{mensaje} (empleado: {empleado_nombre}) [{tipo}] - {ts}")
        else:
            # Si no viene nombre, mostrar id
            print(f"{mensaje or 'OK'} (empleado_id={data.get('empleado_id')}) [{tipo}] - {ts}")


if __name__ == "__main__":
    main()
