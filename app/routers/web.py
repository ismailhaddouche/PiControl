from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.status import HTTP_302_FOUND
from starlette.templating import Jinja2Templates
from sqlmodel import Session
from typing import Optional
import os

from app.db import get_engine
from app.crud import list_empleados, create_empleado, assign_rfid, list_fichajes, horas_trabajadas
from app.crud import create_user, any_admin_exists, get_user_by_username, verify_password

router = APIRouter()
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "..", "templates"))


def get_session():
    engine = get_engine()
    with Session(engine) as session:
        yield session


def require_login(request: Request):
    user = request.session.get("user")
    if not user:
        return False
    return True


@router.get("/admin/login", response_class=HTMLResponse)
def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/admin/login")
def login_post(request: Request, username: str = Form(...), password: str = Form(...), session_db: Session = Depends(get_session)):
    # Autenticación contra la tabla Usuario
    user = get_user_by_username(session_db, username)
    if user and verify_password(password, user.hashed_password):
        request.session["user"] = username
        return RedirectResponse(url="/admin", status_code=HTTP_302_FOUND)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Credenciales inválidas"})


@router.get("/admin/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)


@router.get("/admin", response_class=HTMLResponse)
def admin_index(request: Request):
    if not require_login(request):
        return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)
    return templates.TemplateResponse("menu.html", {"request": request})


@router.get("/admin/setup", response_class=HTMLResponse)
def admin_setup_get(request: Request, session: Session = Depends(get_session)):
    # Si ya existe admin, redirige al login
    if any_admin_exists(session):
        return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)
    return templates.TemplateResponse("setup.html", {"request": request})


@router.post("/admin/setup")
def admin_setup_post(request: Request, username: str = Form(...), password: str = Form(...), session: Session = Depends(get_session)):
    if any_admin_exists(session):
        return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)
    # crear usuario admin
    create_user(session, username=username, password=password, is_admin=True)
    return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)


@router.get("/admin/empleados", response_class=HTMLResponse)
def admin_empleados(request: Request, session: Session = Depends(get_session)):
    if not require_login(request):
        return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)
    empleados = list_empleados(session)
    return templates.TemplateResponse("empleados.html", {"request": request, "empleados": empleados})


@router.post("/admin/empleados")
def admin_empleados_add(request: Request, nombre: str = Form(...), rfid_uid: Optional[str] = Form(None), session: Session = Depends(get_session)):
    if not require_login(request):
        return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)
    create_empleado(session, nombre=nombre, rfid_uid=rfid_uid)
    return RedirectResponse(url="/admin/empleados", status_code=HTTP_302_FOUND)


@router.post("/admin/empleados/{empleado_id}/assign")
def admin_empleados_assign(request: Request, empleado_id: int, rfid_uid: str = Form(...), session: Session = Depends(get_session)):
    if not require_login(request):
        return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)
    assign_rfid(session, empleado_id, rfid_uid)
    return RedirectResponse(url="/admin/empleados", status_code=HTTP_302_FOUND)


@router.post("/admin/empleados/{empleado_id}/assign_ajax")
def admin_empleados_assign_ajax(request: Request, empleado_id: int, rfid_uid: str = Form(...), session: Session = Depends(get_session)):
    """Endpoint JSON para asignar RFID (usado por JS)."""
    if not require_login(request):
        return {"success": False, "error": "No autenticado"}
    empleado = assign_rfid(session, empleado_id, rfid_uid)
    if not empleado:
        return {"success": False, "error": "Empleado no encontrado"}
    return {"success": True, "nombre": empleado.nombre, "rfid_uid": empleado.rfid_uid}


@router.get("/admin/fichajes", response_class=HTMLResponse)
def admin_fichajes(request: Request, session: Session = Depends(get_session)):
    if not require_login(request):
        return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)
    fichas = list_fichajes(session)
    return templates.TemplateResponse("fichajes.html", {"request": request, "fichas": fichas})


@router.get("/admin/reportes", response_class=HTMLResponse)
def admin_reportes(request: Request, session: Session = Depends(get_session)):
    if not require_login(request):
        return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)
    empleados = list_empleados(session)
    return templates.TemplateResponse("reportes.html", {"request": request, "empleados": empleados})


@router.get("/admin/reportes/horas", response_class=HTMLResponse)
def admin_reportes_result(request: Request, empleado_id: int, start: Optional[str] = None, end: Optional[str] = None, session: Session = Depends(get_session)):
    if not require_login(request):
        return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)
    start_dt = None
    end_dt = None
    if start:
        from datetime import datetime

        start_dt = datetime.fromisoformat(start)
    if end:
        from datetime import datetime

        end_dt = datetime.fromisoformat(end)
    total_hours, pairs = horas_trabajadas(session, empleado_id, start=start_dt, end=end_dt)
    return templates.TemplateResponse("reportes_result.html", {"request": request, "total_hours": total_hours, "pairs": pairs, "empleado_id": empleado_id})
