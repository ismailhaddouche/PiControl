from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import List, Optional
from datetime import datetime

from app.db import get_session
from app.crud import create_checkin_by_rfid, list_checkins, hours_worked
from app.models import CheckIn

router = APIRouter()


@router.post("/checkins/")
def api_create_checkin(payload: dict, session: Session = Depends(get_session)):
    rfid_uid = payload.get("rfid_uid")
    if not rfid_uid:
        raise HTTPException(status_code=400, detail="'rfid_uid' is required")
    result = create_checkin_by_rfid(session, rfid_uid)
    if not result:
        raise HTTPException(status_code=404, detail="Employee with that RFID not found")
    checkin, employee, message = result
    return {
        "id": checkin.id,
        "employee_id": checkin.employee_id,
        "employee_name": employee.name,
        "type": checkin.type,
        "timestamp": checkin.timestamp.isoformat(),
        "message": message,
    }


@router.get("/checkins/", response_model=List[CheckIn])
def api_list_checkins(employee_id: Optional[str] = None, session: Session = Depends(get_session)):
    return list_checkins(session, employee_id=employee_id)


@router.get("/checkins/employee/{employee_id}")
def api_list_checkins_by_employee(employee_id: str, start: Optional[str] = Query(None), end: Optional[str] = Query(None), session: Session = Depends(get_session)):
    """List check-ins for employee with optional date range filter."""
    start_dt = datetime.fromisoformat(start) if start else None
    end_dt = datetime.fromisoformat(end) if end else None
    checkins = list_checkins(session, employee_id=employee_id, start=start_dt, end=end_dt)
    return [{"id": c.id, "type": c.type, "timestamp": c.timestamp.isoformat(), "employee_id": c.employee_id} for c in checkins]


@router.get("/reports/hours/{employee_id}")
def api_hours_worked(employee_id: str, start: Optional[str] = Query(None), end: Optional[str] = Query(None), session: Session = Depends(get_session)):
    start_dt = datetime.fromisoformat(start) if start else None
    end_dt = datetime.fromisoformat(end) if end else None
    total_hours, pairs = hours_worked(session, employee_id, start=start_dt, end=end_dt)
    return {"employee_id": employee_id, "total_hours": total_hours, "periods": [{"entry": e.timestamp.isoformat(), "exit": x.timestamp.isoformat(), "hours": (x.timestamp - e.timestamp).total_seconds() / 3600} for (e, x) in pairs]}
