"""RFID hardware integration module.

Provides a small pluggable service to read RFID tags from common readers and
dispatch them to the application (either creating checkins or producing a
pending assignment token when the 'assign' button is pressed).

Supported backends:
- evdev: read from an input device (USB HID readers that act like keyboards)
- mock: in-memory (for tests or environments without hardware)

Configuration via environment variables:
- PICONTROL_RFID_ENABLED=1 to enable
- PICONTROL_RFID_MODE=evdev|mock  (default: evdev)
- PICONTROL_RFID_DEVICE=/dev/input/eventX (for evdev)
- PICONTROL_RFID_ASSIGN_BUTTON_GPIO=<BCM pin> (optional, gpiozero required)
- PICONTROL_RFID_PENDING_FILE=/var/lib/picontrol/rfid_assign_pending.json

This module is intentionally conservative: failing to import optional libs
will disable the corresponding features and log warnings.
"""

import os
import threading
import time
import json
import logging
from datetime import datetime
import asyncio

logger = logging.getLogger("picontrol.rfid")

try:
    from sqlmodel import Session
    from app.db import get_engine
    from app.crud import create_checkin_by_rfid, assign_rfid
except Exception:
    # import-time resilience for test/static analysis
    get_engine = None
    create_checkin_by_rfid = None
    assign_rfid = None

# Optional RC522 support (mfrc522 library). Provide a helper to write/read tags
_rc522_available = False
_rc522_cls = None
try:
    from mfrc522 import SimpleMFRC522  # type: ignore
    _rc522_available = True
    _rc522_cls = SimpleMFRC522
except Exception:
    # Not available (not running on Raspberry Pi or package not installed)
    _rc522_available = False
    _rc522_cls = None


PENDING_FILE = os.environ.get("PICONTROL_RFID_PENDING_FILE", "/var/lib/picontrol/rfid_assign_pending.json")


class RFIDService:
    def __init__(self, mode="evdev", device=None, assign_button_gpio=None):
        self.mode = mode
        self.device = device
        self.assign_button_gpio = assign_button_gpio
        self._stop = threading.Event()
        self._thread = None
        self._button = None
        # backend helpers
        self._use_evdev = False
        try:
            if mode == "evdev":
                import evdev  # type: ignore
                self.evdev = evdev
                self._use_evdev = True
        except Exception:
            logger.warning("evdev not available; evdev backend disabled")

        # Optional gpio button
        self._button_available = False
        try:
            if assign_button_gpio is not None:
                from gpiozero import Button  # type: ignore
                self._button = Button(int(assign_button_gpio))
                self._button_available = True
        except Exception:
            logger.warning("gpiozero not available or button init failed; assign-button disabled")

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, name="rfid-reader", daemon=True)
        self._thread.start()
        logger.info("RFIDService started (mode=%s device=%s assign_button=%s)", self.mode, self.device, self.assign_button_gpio)

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2)

    def _run(self):
        if self.mode == "evdev" and self._use_evdev:
            self._run_evdev()
        else:
            logger.info("RFIDService running in mock mode (no hardware).")
            # Mock loop does nothing; sleep until stopped
            while not self._stop.is_set():
                time.sleep(1)

    # ------------------ evdev backend ------------------
    def _run_evdev(self):
        # Find device
        try:
            dev_path = self.device
            if not dev_path:
                # choose first keyboard-like device if not provided
                from evdev import list_devices, InputDevice
                devices = list_devices()
                if not devices:
                    logger.warning("No evdev devices found")
                    return
                dev_path = devices[0]

            device = self.evdev.InputDevice(dev_path)
            logger.info("Listening for RFID events on %s", dev_path)
        except Exception as e:
            logger.exception("Failed to open evdev device: %s", e)
            return

        buffer = []
        # minimal mapping from KEY_* to characters (numbers/letters)
        keymap = {
            # numbers
            'KEY_0': '0','KEY_1':'1','KEY_2':'2','KEY_3':'3','KEY_4':'4','KEY_5':'5','KEY_6':'6','KEY_7':'7','KEY_8':'8','KEY_9':'9',
            # letters
        }
        # add letters A..Z
        for c in range(ord('A'), ord('Z')+1):
            keymap[f'KEY_{chr(c)}'] = chr(c).lower()

        # common punctuation
        keymap.update({
            'KEY_MINUS': '-', 'KEY_EQUAL': '=', 'KEY_SPACE': ' ', 'KEY_ENTER': '\n', 'KEY_KPENTER': '\n'
        })

        for event in device.read_loop():
            if self._stop.is_set():
                break
            try:
                if event.type == self.evdev.ecodes.EV_KEY:
                    keyevent = self.evdev.categorize(event)
                    if keyevent.keystate == keyevent.key_down:
                        code = keyevent.keycode
                        # keycode can be list on some devices
                        if isinstance(code, list):
                            code = code[0]
                        ch = keymap.get(code)
                        if ch is None:
                            # ignore unknown key
                            continue
                        if ch == '\n':
                            if buffer:
                                uid = ''.join(buffer).strip()
                                buffer = []
                                self._process_tag(uid)
                        else:
                            buffer.append(ch)
            except Exception:
                logger.exception("Error while reading evdev event")

    # ------------------ tag processing ------------------
    def _process_tag(self, uid: str):
        """Called when a full UID is read from hardware."""
        logger.info("RFID tag read: %s", uid)
        # check if assign button is pressed (if available)
        assign_mode = False
        try:
            if self._button_available and self._button.is_pressed:
                assign_mode = self._button.is_pressed
        except Exception:
            assign_mode = False

        if assign_mode:
            logger.info("Assign button pressed: writing pending assignment for %s", uid)
            self._write_pending(uid)
            return

        # Normal checkin flow: create checkin via DB
        # Normal checkin flow: create checkin via DB
        try:
            if get_engine is None or create_checkin_by_rfid is None:
                logger.warning("DB/CRUD not available in this environment; dropping tag %s", uid)
                return
            engine = get_engine()
            from sqlmodel import Session
            with Session(engine) as session:
                res = create_checkin_by_rfid(session, uid)
                if res:
                    checkin, employee, message = res
                    logger.info("Checkin created for %s: %s", employee.document_id, message)
                    # Broadcast event with checkin details
                    try:
                        ev = {
                            "type": "checkin",
                            "rfid_uid": uid,
                            "employee_id": employee.document_id,
                            "employee_name": employee.name,
                            "checkin_type": checkin.type,
                            "checkin_id": checkin.id,
                            "timestamp": checkin.timestamp.isoformat(),
                            "message": message,
                        }
                        push_event(ev)
                    except Exception:
                        logger.exception("Failed to push checkin event")
                else:
                    logger.info("No employee found for RFID %s", uid)
                    # broadcast unknown tag event
                    try:
                        push_event({"type": "rfid_unknown", "rfid_uid": uid, "timestamp": datetime.utcnow().isoformat()})
                    except Exception:
                        pass
        except Exception:
            logger.exception("Failed to create checkin for RFID %s", uid)

    def _write_pending(self, uid: str):
        payload = {"rfid_uid": uid, "timestamp": datetime.utcnow().isoformat()}
        try:
            os.makedirs(os.path.dirname(PENDING_FILE), exist_ok=True)
            with open(PENDING_FILE, "w") as f:
                json.dump(payload, f)
            # ensure permissive ownership in container-less environments
            try:
                os.chmod(PENDING_FILE, 0o600)
            except Exception:
                pass
        except Exception:
            logger.exception("Failed to write pending RFID file")

    # ------------------ helpers for external injection ------------------
    def inject_tag(self, uid: str):
        """Inject a tag programmatically (useful for tests)."""
        self._process_tag(uid)


# Singleton service holder
_service = None
# Async event queue and broadcaster loop (set at startup)
event_queue = None  # type: asyncio.Queue | None
event_loop = None
_ws_connections = set()


async def _broadcaster_task():
    """Background async task that broadcasts events from event_queue to connected websockets."""
    global event_queue, _ws_connections
    if event_queue is None:
        return
    while True:
        try:
            ev = await event_queue.get()
            # broadcast to all websockets
            dead = []
            for ws in list(_ws_connections):
                try:
                    # send_json is async
                    await ws.send_json(ev)
                except Exception:
                    # mark dead connection for removal
                    dead.append(ws)
            for d in dead:
                try:
                    _ws_connections.discard(d)
                except Exception:
                    pass
        except asyncio.CancelledError:
            break
        except Exception:
            logger.exception("Exception in broadcaster task")


def register_websocket(ws):
    """Register a WebSocket connection (must be called from event loop)."""
    _ws_connections.add(ws)


def unregister_websocket(ws):
    try:
        _ws_connections.discard(ws)
    except Exception:
        pass


def start_service_if_configured():
    global _service
    enabled = os.environ.get("PICONTROL_RFID_ENABLED", "0")
    if enabled not in ("1", "true", "True"):
        logger.info("RFID disabled by configuration")
        return

    mode = os.environ.get("PICONTROL_RFID_MODE", "evdev")
    device = os.environ.get("PICONTROL_RFID_DEVICE")
    assign_pin = os.environ.get("PICONTROL_RFID_ASSIGN_BUTTON_GPIO")
    _service = RFIDService(mode=mode, device=device, assign_button_gpio=assign_pin)
    # Prepare async event queue and broadcaster if running inside an event loop
    try:
        global event_queue, event_loop, _broadcaster_handle
        event_loop = asyncio.get_event_loop()
        event_queue = asyncio.Queue()
        # start broadcaster task
        _broadcaster_handle = event_loop.create_task(_broadcaster_task())
    except Exception:
        logger.warning("Could not start RFID event broadcaster (no event loop?)")

    _service.start()


def push_event(ev: dict):
    """Push an event into the asyncio queue for broadcasting.

    This can be called from any thread.
    """
    global event_loop, event_queue
    try:
        if event_loop is not None and event_queue is not None:
            event_loop.call_soon_threadsafe(event_queue.put_nowait, ev)
            return True
    except Exception:
        logger.exception("Failed to call_soon_threadsafe to push event")
    return False


def stop_service():
    global _service
    if _service:
        _service.stop()
    # cancel broadcaster task if present
    try:
        global _broadcaster_handle
        if '_broadcaster_handle' in globals() and _broadcaster_handle:
            _broadcaster_handle.cancel()
    except Exception:
        pass


def inject_tag(uid: str):
    global _service
    if not _service:
        # create a temporary service in mock mode
        svc = RFIDService(mode="mock")
        svc.inject_tag(uid)
        return
    _service.inject_tag(uid)


def write_rc522_tag(text: str, timeout: int = 30):
    """Blocking write to an RC522 tag using mfrc522.SimpleMFRC522.

    Returns the numeric UID read from the tag after writing. Raises RuntimeError
    if RC522 support is not available or the write fails.
    """
    if not _rc522_available or _rc522_cls is None:
        raise RuntimeError("RC522 support not available on this system")

    # The SimpleMFRC522.write method will block waiting for a tag to be presented.
    # We create an instance and call write(text). It will use RPi.GPIO internally.
    try:
        reader = _rc522_cls()
        # write returns nothing; after writing, do a read to obtain UID/text
        reader.write(text)
        # read back to obtain UID (blocks until a tag is presented again, but most readers keep the tag present)
        uid, stored = reader.read()
        # cleanup handled by underlying library; attempt to cleanup GPIO
        try:
            import RPi.GPIO as GPIO  # type: ignore
            GPIO.cleanup()
        except Exception:
            pass
        return uid, stored
    except Exception as e:
        # Try to cleanup and re-raise
        try:
            import RPi.GPIO as GPIO  # type: ignore
            GPIO.cleanup()
        except Exception:
            pass
        raise RuntimeError(f"RC522 write failed: {e}")
