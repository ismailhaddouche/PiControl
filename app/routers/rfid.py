from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Request
from sqlmodel import Session
import os
import json
from app.db import get_session
from app.crud import assign_rfid, get_user
from datetime import datetime
from app import rfid as rfid_service
import asyncio

# lazy import of RC522 write helper
try:
    from app.rfid import write_rc522_tag
except Exception:
    write_rc522_tag = None

router = APIRouter()

PENDING_FILE = os.environ.get("PICONTROL_RFID_PENDING_FILE", "/var/lib/picontrol/rfid_assign_pending.json")


def _read_pending():
    if not os.path.exists(PENDING_FILE):
        return None
    try:
        with open(PENDING_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return None


def _clear_pending():
    try:
        if os.path.exists(PENDING_FILE):
            os.remove(PENDING_FILE)
    except Exception:
        pass


@router.get("/rfid/pending")
def api_rfid_pending():
    data = _read_pending()
    if not data:
        return {"pending": False}
    return {"pending": True, "rfid_uid": data.get("rfid_uid"), "timestamp": data.get("timestamp")}


@router.post("/rfid/assign")
def api_rfid_assign(request: Request, payload: dict, session: Session = Depends(get_session)):
    """Assign the pending RFID to an employee.

    Payload: { "employee_id": "<document_id>" }
    The authenticated session user will be used as the actor (performed_by) for audit logs.
    """
    # require authenticated app admin
    session_user = None
    try:
        session_user = request.session.get("user")
    except Exception:
        session_user = None

    if not session_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    try:
        user = get_user(session, session_user)
        if not user or not getattr(user, "is_admin", False):
            raise HTTPException(status_code=403, detail="Admin privileges required")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to verify user permissions")

    employee_id = payload.get("employee_id")
    if not employee_id:
        raise HTTPException(status_code=400, detail="employee_id required")

    pending = _read_pending()
    if not pending:
        raise HTTPException(status_code=404, detail="No pending RFID assignment")
    rfid_uid = pending.get("rfid_uid")
    if not rfid_uid:
        raise HTTPException(status_code=400, detail="Invalid pending RFID payload")

    # use session user as performed_by for audit
    performed_by = session_user

    employee = assign_rfid(session, employee_id, rfid_uid, performed_by=performed_by)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    _clear_pending()
    # broadcast assignment event
    try:
        from app.rfid import push_event
        push_event({"type": "rfid_assigned", "rfid_uid": rfid_uid, "employee_id": employee.document_id, "employee_name": employee.name, "timestamp": datetime.utcnow().isoformat()})
    except Exception:
        pass
    return {"status": "ok", "employee_id": employee.document_id, "rfid_uid": rfid_uid}


@router.post("/rfid/mock")
def api_rfid_mock(request: Request, payload: dict, session: Session = Depends(get_session)):
    """Inject a fake tag for testing. Only intended for development/test environments.

    Payload: { "rfid_uid": "..." }
    Protected: only app admins can call this endpoint.
    """
    # require authenticated app admin
    session_user = None
    try:
        session_user = request.session.get("user")
    except Exception:
        session_user = None

    if not session_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    try:
        user = get_user(session, session_user)
        if not user or not getattr(user, "is_admin", False):
            raise HTTPException(status_code=403, detail="Admin privileges required")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to verify user permissions")

    uid = payload.get("rfid_uid")
    if not uid:
        raise HTTPException(status_code=400, detail="rfid_uid required")
    # lazy import to avoid hardware deps at module import time
    try:
        from app.rfid import inject_tag
        inject_tag(uid)
        return {"status": "injected", "rfid_uid": uid}
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to inject tag")


@router.websocket("/ws/rfid")
async def websocket_rfid(ws: WebSocket):
    """WebSocket endpoint that streams RFID events in real-time as JSON messages."""
    await ws.accept()
    try:
        # register this websocket to receive broadcasts
        rfid_service.register_websocket(ws)
        # keep connection open until client disconnects
        while True:
            try:
                await ws.receive_text()
            except WebSocketDisconnect:
                break
    finally:
        try:
            rfid_service.unregister_websocket(ws)
        except Exception:
            pass


@router.post("/rfid/write_assign")
async def api_rfid_write_assign(request: Request, payload: dict, session: Session = Depends(get_session)):
    """Write employee identifier to an RC522 tag and assign the tag UID to the employee.

    Payload: { "employee_id": "<document_id>", "performed_by": "admin", "write_text": "optional text to write" }
    """
    employee_id = payload.get("employee_id")
    # prefer the authenticated session user as the actor
    session_user = None
    try:
        session_user = request.session.get("user")
    except Exception:
        session_user = None

    performed_by = session_user or payload.get("performed_by")
    write_text = payload.get("write_text")
    if not employee_id:
        raise HTTPException(status_code=400, detail="employee_id required")

    if write_rc522_tag is None:
        raise HTTPException(status_code=503, detail="RC522 write support not available on server")

    # Default write_text to employee_id if not provided
    if not write_text:
        write_text = str(employee_id)

    # require authenticated app admin
    if not session_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        user = get_user(session, session_user)
        if not user or not getattr(user, "is_admin", False):
            raise HTTPException(status_code=403, detail="Admin privileges required")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to verify user permissions")

    uid = None
    stored = None
    wrapper_path = "/usr/local/bin/picontrol-write-rfid"
    use_wrapper = False
    write_err = None

    if write_rc522_tag is not None:
        try:
            # run blocking RC522 write in thread
            uid, stored = await asyncio.to_thread(write_rc522_tag, write_text)
        except Exception as e:
            # if direct write fails (permissions or runtime), attempt wrapper fallback
            use_wrapper = True
            write_err = e
    else:
        use_wrapper = True

    if use_wrapper:
        import shutil
        if not shutil.which(wrapper_path):
            # no wrapper available
            raise HTTPException(status_code=503, detail=f"RC522 write not available and wrapper not found: {write_err}")
        try:
            # run wrapper with sudo; it will output UID\nstored_text on success
            proc = await asyncio.create_subprocess_exec("sudo", wrapper_path, write_text, "--timeout", "30", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            out, err = await proc.communicate()
            if proc.returncode != 0:
                raise Exception(err.decode().strip() or "wrapper failed")
            lines = out.decode().strip().splitlines()
            if not lines:
                raise Exception("wrapper returned no output")
            uid = lines[0].strip()
            stored = lines[1].strip() if len(lines) > 1 else ""
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to write RC522 tag via wrapper: {e}")

    # Now assign in DB
    try:
        employee = assign_rfid(session, employee_id, str(uid), performed_by=performed_by)
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        # Broadcast assignment event
        try:
            from app.rfid import push_event
            push_event({"type": "rfid_assigned", "rfid_uid": str(uid), "employee_id": employee.document_id, "employee_name": employee.name, "timestamp": datetime.utcnow().isoformat()})
        except Exception:
            pass
        return {"status": "ok", "employee_id": employee.document_id, "rfid_uid": str(uid), "stored_text": stored}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to assign RFID in DB: {e}")

