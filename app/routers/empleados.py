from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import Optional, List

from app.db import get_engine
from app.crud import create_empleado, list_empleados, assign_rfid, get_empleado
from app.models import Empleado

router = APIRouter()


def get_session():
    engine = get_engine()
    with Session(engine) as session:
        yield session


@router.post("/empleados/", response_model=Empleado)
def api_create_empleado(payload: dict, session: Session = Depends(get_session)):
    nombre = payload.get("nombre")
    rfid_uid = payload.get("rfid_uid")
    if not nombre:
        raise HTTPException(status_code=400, detail="'nombre' es obligatorio")
    empleado = create_empleado(session, nombre=nombre, rfid_uid=rfid_uid)
    return empleado


@router.get("/empleados/", response_model=List[Empleado])
def api_list_empleados(session: Session = Depends(get_session)):
    return list_empleados(session)


@router.put("/empleados/{empleado_id}/rfid", response_model=Empleado)
def api_assign_rfid(empleado_id: int, payload: dict, session: Session = Depends(get_session)):
    rfid_uid = payload.get("rfid_uid")
    empleado = assign_rfid(session, empleado_id, rfid_uid)
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return empleado
