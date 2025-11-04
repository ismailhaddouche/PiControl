from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import List, Optional
from datetime import datetime

from app.db import get_engine
from app.crud import create_fichaje_by_rfid, list_fichajes, horas_trabajadas
from app.models import Fichaje

router = APIRouter()


def get_session():
    engine = get_engine()
    with Session(engine) as session:
        yield session


@router.post("/fichajes/")
def api_create_fichaje(payload: dict, session: Session = Depends(get_session)):
    rfid_uid = payload.get("rfid_uid")
    if not rfid_uid:
        raise HTTPException(status_code=400, detail="'rfid_uid' es obligatorio")
    result = create_fichaje_by_rfid(session, rfid_uid)
    if not result:
        raise HTTPException(status_code=404, detail="Empleado con ese RFID no encontrado")
    fichaje, empleado, mensaje = result
    return {
        "id": fichaje.id,
        "empleado_id": fichaje.empleado_id,
        "empleado_nombre": empleado.nombre,
        "tipo": fichaje.tipo,
        "timestamp": fichaje.timestamp.isoformat(),
        "mensaje": mensaje,
    }


@router.get("/fichajes/", response_model=List[Fichaje])
def api_list_fichajes(empleado_id: Optional[int] = None, session: Session = Depends(get_session)):
    return list_fichajes(session, empleado_id=empleado_id)


@router.get("/fichajes/empleado/{empleado_id}")
def api_list_fichajes_por_empleado(empleado_id: int, start: Optional[str] = Query(None), end: Optional[str] = Query(None), session: Session = Depends(get_session)):
    """Listar fichajes de un empleado opcionalmente filtrando por rango ISO (start,end)."""
    start_dt = datetime.fromisoformat(start) if start else None
    end_dt = datetime.fromisoformat(end) if end else None
    fichas = list_fichajes(session, empleado_id=empleado_id)
    # filtrar por rango
    if start_dt:
        fichas = [f for f in fichas if f.timestamp >= start_dt]
    if end_dt:
        fichas = [f for f in fichas if f.timestamp <= end_dt]
    return [{"id": f.id, "tipo": f.tipo, "timestamp": f.timestamp.isoformat(), "empleado_id": f.empleado_id} for f in fichas]


@router.get("/reportes/horas/{empleado_id}")
def api_horas_trabajadas(empleado_id: int, start: Optional[str] = Query(None), end: Optional[str] = Query(None), session: Session = Depends(get_session)):
    start_dt = datetime.fromisoformat(start) if start else None
    end_dt = datetime.fromisoformat(end) if end else None
    total_hours, pairs = horas_trabajadas(session, empleado_id, start=start_dt, end=end_dt)
    return {"empleado_id": empleado_id, "total_hours": total_hours, "periodos": [{"entrada": e.isoformat(), "salida": s.isoformat(), "hours": h} for (e, s, h) in pairs]}
