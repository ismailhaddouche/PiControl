from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import Optional, List

from app.db import get_session
from app.crud import create_employee, list_employees, assign_rfid, get_employee
from app.models import Employee

router = APIRouter()


@router.post("/employees/", response_model=Employee)
def api_create_employee(payload: dict, session: Session = Depends(get_session)):
    document_id = payload.get("document_id")
    name = payload.get("name")
    rfid_uid = payload.get("rfid_uid")
    if not name:
        raise HTTPException(status_code=400, detail="'name' is required")
    if not document_id:
        raise HTTPException(status_code=400, detail="'document_id' is required")
    employee = create_employee(session, document_id=document_id, name=name, rfid_uid=rfid_uid)
    return employee


@router.get("/employees/", response_model=List[Employee])
def api_list_employees(session: Session = Depends(get_session)):
    return list_employees(session)


@router.put("/employees/{employee_id}/rfid", response_model=Employee)
def api_assign_rfid(employee_id: str, payload: dict, session: Session = Depends(get_session)):
    rfid_uid = payload.get("rfid_uid")
    employee = assign_rfid(session, employee_id, rfid_uid)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee
