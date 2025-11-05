from fastapi import APIRouter, Depends, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from starlette.status import HTTP_302_FOUND
from starlette.templating import Jinja2Templates
from sqlmodel import Session
import subprocess
import shutil
from starlette import status
from typing import Optional
import os
from zoneinfo import available_timezones

from app.db import get_session
from app.crud import (
    list_employees,
    create_employee,
    assign_rfid,
    list_checkins,
    hours_worked,
    create_checkin_by_rfid,
    create_checkin_for_employee,
    list_recent_checkins,
    archive_employee,
    list_archived_employees,
    get_employee,
    restore_employee,
    create_user,
    any_admin_exists,
    get_user,
    verify_password,
    update_user_password,
    set_config,
    get_config,
    log_admin_action,
    list_admin_actions,
)

router = APIRouter()
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "..", "templates"))


# Jinja filter to format datetimes in a readable local/ISO format
def format_datetime(value):
    try:
        # If naive, assume UTC
        if value.tzinfo is None:
            from datetime import timezone

            value = value.replace(tzinfo=timezone.utc)
        # Local/ISO readable format
        return value.astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    except Exception:
        return str(value)


templates.env.filters["format_datetime"] = format_datetime





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
    # Authentication against the User table
    user = get_user(session_db, username)
    if user and verify_password(password, user.hashed_password):
        request.session["user"] = username
        return RedirectResponse(url="/admin", status_code=HTTP_302_FOUND)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})


@router.get("/admin/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)


@router.get("/admin", response_class=HTMLResponse)
def admin_index(request: Request, session: Session = Depends(get_session)):
    if not require_login(request):
        return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)
    # pop and clear flash message from session (if any)
    flash = request.session.pop("flash", None)
    # fetch last 20 check-ins to show on the dashboard
    # and map employee_id -> name for display
    recent_checkins = list_recent_checkins(session, limit=20)
    # show only active employees on main screen
    employees = list_employees(session, active_only=True)
    employees_map = {e.document_id: e.name for e in employees}

    return templates.TemplateResponse(
        "menu.html",
        {
            "request": request,
            "recent_checkins": recent_checkins,
            "flash": flash,
            "employees_map": employees_map,
            "employees": employees,
        },
    )


@router.post("/admin/checkins/manual")
def admin_checkin_manual(request: Request, employee_id: Optional[str] = Form(None), rfid_uid: Optional[str] = Form(None), session: Session = Depends(get_session)):
    """Create a manual check-in selecting an employee or by RFID (compatibility).

    Stores a message in `request.session['flash']` for user feedback.
    """
    if not require_login(request):
        return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)
    
    result = None
    if employee_id is not None:
        result = create_checkin_for_employee(session, employee_id)
    elif rfid_uid:
        result = create_checkin_by_rfid(session, rfid_uid)
    
    # Log the manual check-in action for admin auditing
    try:
        username = request.session.get("user")
        if result and username:
            checkin, employee, message = result
            log_admin_action(session, username, "manual_checkin", f"checkin id={checkin.id} employee={employee.document_id} type={checkin.type}")
    except Exception:
        pass
    
    if not result:
        # generic message when creation failed
        request.session["flash"] = "Could not create check-in (employee not found)."
    else:
        checkin, employee, message = result
        request.session["flash"] = message
    
    return RedirectResponse(url="/admin", status_code=HTTP_302_FOUND)


@router.post("/admin/checkins/manual_ajax")
def admin_checkin_manual_ajax(request: Request, employee_id: Optional[str] = Form(None), rfid_uid: Optional[str] = Form(None), session: Session = Depends(get_session)):
    """AJAX endpoint that creates a check-in and returns JSON with the result and record.

    Accepts `employee_id` (preferred) or `rfid_uid`.
    """
    if not require_login(request):
        return {"success": False, "error": "Not authenticated"}
    
    result = None
    if employee_id is not None:
        result = create_checkin_for_employee(session, employee_id)
    elif rfid_uid:
        result = create_checkin_by_rfid(session, rfid_uid)
    
    if not result:
        return {"success": False, "error": "Employee not found"}
    
    checkin, employee, message = result
    try:
        username = request.session.get("user")
        if username:
            log_admin_action(session, username, "manual_checkin", f"checkin id={checkin.id} employee={employee.document_id} type={checkin.type}")
    except Exception:
        pass
    
    return {
        "success": True,
        "message": message,
        "checkin": {
            "id": checkin.id,
            "timestamp": checkin.timestamp.isoformat(),
            "employee_id": checkin.employee_id,
            "employee_name": employee.name,
                "tipo": checkin.tipo,
            },
        }


@router.get("/admin/setup", response_class=HTMLResponse)
def admin_setup_get(request: Request, session: Session = Depends(get_session)):
    # If an admin user already exists, redirect to login
    if any_admin_exists(session):
        return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)
    return templates.TemplateResponse("setup.html", {"request": request})


@router.post("/admin/setup")
def admin_setup_post(request: Request, username: str = Form(...), password: str = Form(...), session: Session = Depends(get_session)):
    if any_admin_exists(session):
        return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)
    # create admin user (setup action)
    create_user(session, username=username, password=password, is_admin=True, performed_by="setup")
    return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)


@router.get("/admin/employees", response_class=HTMLResponse)
def admin_employees(request: Request, session: Session = Depends(get_session)):
    if not require_login(request):
        return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)
    # show only active employees on the employees page
    employees = list_employees(session, active_only=True)
    employees = employees
    return templates.TemplateResponse("employees.html", {"request": request, "employees": employees, "employees": employees})


@router.post("/admin/employees/{employee_id}/archive")
def admin_employees_archive(request: Request, employee_id: str, session: Session = Depends(get_session)):
    if not require_login(request):
        return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)
    username = request.session.get("user")
    archive_employee(session, employee_id, performed_by=username)
    request.session["flash"] = f"Employee {employee_id} archived."
    return RedirectResponse(url="/admin/employees", status_code=HTTP_302_FOUND)


@router.get("/admin/employees/archived", response_class=HTMLResponse)
def admin_employees_archived(request: Request, session: Session = Depends(get_session)):
    if not require_login(request):
        return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)
    employees = list_archived_employees(session)
    employees = employees
    return templates.TemplateResponse("employees_archived.html", {"request": request, "employees": employees, "employees": employees})


@router.get("/admin/employees/{employee_id}/history", response_class=HTMLResponse)
def admin_employee_history(request: Request, employee_id: str, session: Session = Depends(get_session)):
    if not require_login(request):
        return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)
    # get employee and their check-in history
    employee = get_employee(session, employee_id)
    if not employee:
        return RedirectResponse(url="/admin/employees/archived", status_code=HTTP_302_FOUND)
    fichas = list_checkins(session, employee_id=employee.document_id)
    employee = employee
    checkins = fichas
    return templates.TemplateResponse("employee_history.html", {"request": request, "employee": employee, "employee": employee, "fichas": fichas, "checkins": checkins})


@router.post("/admin/employees/{employee_id}/restore")
def admin_employees_restore(request: Request, employee_id: str, session: Session = Depends(get_session)):
    if not require_login(request):
        return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)
    username = request.session.get("user")
    restored = restore_employee(session, employee_id, performed_by=username)
    if restored:
        request.session["flash"] = f"Employee {employee_id} restored."
    # Al restaurar, redirigir al listado de employees activos para que se vea inmediatamente
    return RedirectResponse(url="/admin/employees", status_code=HTTP_302_FOUND)


@router.post("/admin/employees")
def admin_employees_add(request: Request, dni: str = Form(...), nombre: str = Form(...), rfid_uid: Optional[str] = Form(None), session: Session = Depends(get_session)):
    if not require_login(request):
        return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)
    username = request.session.get("user")
    create_employee(session, dni=dni, nombre=nombre, rfid_uid=rfid_uid, performed_by=username)
    return RedirectResponse(url="/admin/employees", status_code=HTTP_302_FOUND)


@router.post("/admin/employees/{employee_id}/assign")
def admin_employees_assign(request: Request, employee_id: str, rfid_uid: str = Form(...), session: Session = Depends(get_session)):
    if not require_login(request):
        return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)
    username = request.session.get("user")
    assign_rfid(session, employee_id, rfid_uid, performed_by=username)
    return RedirectResponse(url="/admin/employees", status_code=HTTP_302_FOUND)


@router.post("/admin/employees/{employee_id}/assign_ajax")
def admin_employees_assign_ajax(request: Request, employee_id: str, rfid_uid: str = Form(...), session: Session = Depends(get_session)):
    """Endpoint JSON para asignar RFID (usado por JS)."""
    if not require_login(request):
        return {"success": False, "error": "Not authenticated"}
    username = request.session.get("user")
    employee = assign_rfid(session, employee_id, rfid_uid, performed_by=username)
    if not employee:
        return {"success": False, "error": "Employee not found"}
    return {"success": True, "nombre": employee.name, "rfid_uid": employee.rfid_uid}


@router.get("/admin/checkins", response_class=HTMLResponse)
def admin_checkins(request: Request, employee_id: Optional[str] = None, start: Optional[str] = None, end: Optional[str] = None, session: Session = Depends(get_session)):
    """History page with optional filters:
    - employee_id: filter by employee (if not provided, show all)
    - start, end: ISO datetime strings to limit the range (optional)
    """
    if not require_login(request):
        return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)

    # parse optional dates
    start_dt = None
    end_dt = None
    from datetime import datetime

    try:
        if start:
            start_dt = datetime.fromisoformat(start)
    except Exception:
        start_dt = None
    try:
        if end:
            end_dt = datetime.fromisoformat(end)
    except Exception:
        end_dt = None

    # get filtered check-ins from the DB (more efficient)
    fichas = list_checkins(session, employee_id=employee_id, start=start_dt, end=end_dt)

    # pass employee list for the filter select
    employees = list_employees(session)
    employees_map = {e.document_id: e.name for e in employees}

    checkins = fichas
    employees = employees
    return templates.TemplateResponse("checkins.html", {"request": request, "fichas": fichas, "checkins": checkins, "employees": employees, "employees": employees, "employees_map": employees_map, "filter": {"employee_id": employee_id, "start": start, "end": end}})


@router.get("/admin/reports", response_class=HTMLResponse)
def admin_reports(request: Request, session: Session = Depends(get_session)):
    if not require_login(request):
        return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)
    employees = list_employees(session)
    # pass empty filter by default to avoid template errors
    filter_ctx = {"employee_id": None, "start": None, "end": None}
    employees = employees
    return templates.TemplateResponse("reports.html", {"request": request, "employees": employees, "employees": employees, "filter": filter_ctx})


@router.get("/admin/logs", response_class=HTMLResponse)
def admin_logs(request: Request, start: Optional[str] = None, end: Optional[str] = None, admin: Optional[str] = None, action: Optional[str] = None, page: int = 1, page_size: int = 100, session: Session = Depends(get_session)):
    """Page to view admin audit logs.

    GET parameters:
    - start, end: ISO datetime strings (e.g. 2025-11-05T00:00)
    - admin: actor username
    - action: filter by action
    - page, page_size: pagination
    """
    if not require_login(request):
        return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)

    from datetime import datetime

    start_dt = None
    end_dt = None
    try:
        if start:
            start_dt = datetime.fromisoformat(start)
    except Exception:
        start_dt = None
    try:
        if end:
            end_dt = datetime.fromisoformat(end)
    except Exception:
        end_dt = None

    # pagination
    page = max(1, page)
    page_size = max(10, min(1000, page_size))
    offset = (page - 1) * page_size

    entries = list_admin_actions(session, start=start_dt, end=end_dt, admin_username=admin, action=action, limit=page_size, offset=offset)

    # pass to template
    return templates.TemplateResponse(
        "admin_logs.html",
        {
            "request": request,
            "entries": entries,
            "filter": {"start": start, "end": end, "admin": admin, "action": action},
            "page": page,
            "page_size": page_size,
        },
    )


@router.get("/admin/reports/horas", response_class=HTMLResponse)
def admin_reports_result(request: Request, employee_id: str, start: Optional[str] = None, end: Optional[str] = None, session: Session = Depends(get_session)):
    if not require_login(request):
        return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)

    from datetime import datetime, time, timedelta

    start_dt = None
    end_dt = None
    try:
        if start:
            # datetime-local inputs may not include timezone; parse as is
            start_dt = datetime.fromisoformat(start)
    except Exception:
        start_dt = None
    try:
        if end:
            end_dt = datetime.fromisoformat(end)
    except Exception:
        end_dt = None

    # Get in/out pairs using existing helper
    total_hours, pairs = hours_worked(session, employee_id, start=start_dt, end=end_dt)

    # Group hours per day, accounting for midnight crossings
    per_day_seconds = {}
    for entrada, salida, _ in pairs:
        if not salida:
            continue
        current = entrada
        # normalizar tzinfo
        tz = entrada.tzinfo
        while current < salida:
            # calcular el final del día para current
            next_day = (current + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            if tz is not None and next_day.tzinfo is None:
                next_day = next_day.replace(tzinfo=tz)
            segment_end = min(salida, next_day)
            seconds = (segment_end - current).total_seconds()
            day_key = current.date().isoformat()
            per_day_seconds[day_key] = per_day_seconds.get(day_key, 0.0) + seconds
            current = segment_end

    # convert seconds to decimal hours (float) and create a sorted list by date
    per_day = []
    for day in sorted(per_day_seconds.keys()):
        hours = per_day_seconds[day] / 3600.0
        per_day.append((day, round(hours, 2)))

    # total hours (use total_hours from hours_worked for compatibility)
    total_hours_rounded = round(total_hours, 2)

    # pass employee id and period for template context
    return templates.TemplateResponse(
        "reports_result.html",
        {
            "request": request,
            "total_hours": total_hours_rounded,
            "per_day": per_day,
            "employee_id": employee_id,
            "employee_id": employee_id,
            "start": start,
            "end": end,
        },
    )


@router.get("/admin/configuration", response_class=HTMLResponse)
def admin_configuration(request: Request, session: Session = Depends(get_session)):
    """Settings page - placeholder."""
    if not require_login(request):
        return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)
    # obtener valores actuales de configuración
    auto_update = get_config(session, "auto_update") or "false"
    timezone_cfg = get_config(session, "timezone") or "UTC"
    # Construir lista de zonas horarias utilizando zoneinfo (stdlib). Si falla, usar una lista corta por defecto.
    try:
        tz_list = sorted(available_timezones())
    except Exception:
        tz_list = [
            "UTC",
            "Europe/Madrid",
            "Europe/London",
            "America/New_York",
            "America/Los_Angeles",
            "Asia/Shanghai",
            "Asia/Tokyo",
        ]
    flash = request.session.pop("flash", None)
    return templates.TemplateResponse(
        "configuration.html",
        {"request": request, "auto_update": auto_update, "timezone": timezone_cfg, "flash": flash, "tz_list": tz_list},
    )


@router.post("/admin/restart")
def admin_restart(request: Request, session: Session = Depends(get_session)):
    """Endpoint seguro para que un admin inicie el reinicio de servicios de PiControl.

    - Requiere estar autenticado.
    - Ejecuta el wrapper `picontrol-restart.sh`.
    - Registra la acción en la tabla de auditoría y guarda un message flash.
    """
    if not require_login(request):
        return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)

    username = request.session.get("user")
    # Preferir ejecutar con sudo si existe una regla específica instalada
    restart_cmd = None
    if os.path.exists("/etc/sudoers.d/picontrol"):
        # usar sudo -n para evitar prompt interactivo si algo va mal
        restart_cmd = ["/usr/bin/sudo", "-n", "/usr/local/bin/picontrol-restart.sh"]
    else:
        restart_cmd = ["/usr/local/bin/picontrol-restart.sh"]

    try:
        proc = subprocess.run(restart_cmd, check=False, capture_output=True, text=True)
        out = (proc.stdout or "") + "\n" + (proc.stderr or "")
        try:
            # Grabar acción en BD (truncar a 2000 chars para evitar límites)
            log_admin_action(session, username or "unknown", "restart_service", out[:2000])
        except Exception:
            pass
        if proc.returncode == 0:
            request.session["flash"] = "Reinicio solicitado correctamente. Comprueba los logs si es necesario."
        else:
            request.session["flash"] = f"Error al solicitar reinicio (código {proc.returncode}). Revisa logs." 
    except Exception as e:
        try:
            log_admin_action(session, username or "unknown", "restart_service_error", str(e)[:2000])
        except Exception:
            pass
        request.session["flash"] = f"Excepción al intentar reiniciar: {e}"

    return RedirectResponse(url="/admin/configuration", status_code=HTTP_302_FOUND)


@router.post("/admin/configuration/change_password")
def admin_change_password(request: Request, new_password: str = Form(...), confirm_password: str = Form(...), session: Session = Depends(get_session)):
    if not require_login(request):
        return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)
    if new_password != confirm_password:
        request.session["flash"] = "Passwords do not match"
        return RedirectResponse(url="/admin/configuration", status_code=HTTP_302_FOUND)
    username = request.session.get("user")
    if not username:
        request.session["flash"] = "User not authenticated"
        return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)
    changed = update_user_password(session, username, new_password, performed_by=username)
    request.session["flash"] = "Password updated" if changed else "Could not update password"
    return RedirectResponse(url="/admin/configuration", status_code=HTTP_302_FOUND)


@router.get("/admin/configuration/export_db")
def admin_export_db(request: Request):
    if not require_login(request):
        return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)
    # Ubicación relativa del archivo sqlite en el workspace (puede variar en despliegues)
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "pi_control.db"))
    if not os.path.exists(db_path):
        request.session["flash"] = "Database file not found"
        return RedirectResponse(url="/admin/configuration", status_code=HTTP_302_FOUND)
    return FileResponse(db_path, media_type="application/x-sqlite3", filename="pi_control.db")


@router.post("/admin/configuration/import_db")
def admin_import_db(request: Request, file: UploadFile = File(...)):
    if not require_login(request):
        return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)
    target_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "pi_control.db"))
    try:
        # Guardar archivo subido en temporal y luego mover
        tmp_path = target_path + ".upload_tmp"
        with open(tmp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        # Reemplazar base de datos
        shutil.move(tmp_path, target_path)
        request.session["flash"] = "Database imported. Restart the server if required."
    except Exception as e:
        request.session["flash"] = f"Error importing DB: {e}"
    return RedirectResponse(url="/admin/configuration", status_code=HTTP_302_FOUND)


@router.post("/admin/configuration/set_timezone")
def admin_set_timezone(request: Request, timezone: str = Form(...), session: Session = Depends(get_session)):
    if not require_login(request):
        return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)
    # Guardar en configuración y, opcionalmente, intentar aplicar con timedatectl
    set_config(session, "timezone", timezone)
    # Intentar aplicar en el sistema (puede requerir privilegios)
    try:
        subprocess.run(["timedatectl", "set-timezone", timezone], check=True, capture_output=True)
        request.session["flash"] = f"Timezone set to {timezone}"
    except Exception:
        request.session["flash"] = f"Timezone saved (could not apply at system level, privileges required)"
    return RedirectResponse(url="/admin/configuration", status_code=HTTP_302_FOUND)


@router.post("/admin/configuration/sync_time")
def admin_sync_time(request: Request):
    if not require_login(request):
        return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)
    # Intentar forzar sincronización de hora. Puede requerir utilidades instaladas y permisos.
    try:
        # Preferir timedatectl
        res = subprocess.run(["timedatectl", "set-ntp", "true"], check=True, capture_output=True)
        request.session["flash"] = "NTP synchronization enabled (timedatectl)"
    except Exception:
        try:
            # Fallback a ntpdate
            res = subprocess.run(["ntpdate", "-u", "pool.ntp.org"], check=True, capture_output=True)
            request.session["flash"] = "Time synchronized with pool.ntp.org"
        except Exception as e:
            request.session["flash"] = f"Could not synchronize time: {e}"
    return RedirectResponse(url="/admin/configuration", status_code=HTTP_302_FOUND)


@router.post("/admin/configuration/set_auto_update")
def admin_set_auto_update(request: Request, enabled: Optional[str] = Form(None), session: Session = Depends(get_session)):
    if not require_login(request):
        return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)
    val = "true" if enabled == "on" else "false"
    set_config(session, "auto_update", val)
    request.session["flash"] = "Auto-update enabled" if val == "true" else "Auto-update disabled"
    return RedirectResponse(url="/admin/configuration", status_code=HTTP_302_FOUND)
