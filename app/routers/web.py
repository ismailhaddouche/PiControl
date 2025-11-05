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

from app.db import get_engine
from app.crud import (
    list_empleados,
    create_empleado,
    assign_rfid,
    list_fichajes,
    horas_trabajadas,
)
from app.crud import (
    create_user,
    any_admin_exists,
    get_user_by_username,
    verify_password,
    list_recent_fichajes,
    create_fichaje_by_rfid,
    create_fichaje_for_empleado,
)
from app.crud import (
    archive_empleado,
    list_archived_empleados,
    get_empleado,
    restore_empleado,
    change_user_password,
    set_config,
    get_config,
)

router = APIRouter()
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "..", "templates"))


# Filtro Jinja para formatear datetimes de forma legible (UTC -> ISO legible)
def format_datetime(value):
    try:
        # Si es naive, asumimos UTC
        if value.tzinfo is None:
            from datetime import timezone

            value = value.replace(tzinfo=timezone.utc)
        # Formato legible local/ISO
        return value.astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    except Exception:
        return str(value)


templates.env.filters["format_datetime"] = format_datetime


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
    # extraer y limpiar flash de la sesión (si existe)
    flash = request.session.pop("flash", None)
    # obtener últimos 20 fichajes para mostrar en la pantalla principal
    # y además mapear empleado_id -> nombre para mostrar nombres
    engine = get_engine()
    with Session(engine) as session:
        recientes = list_recent_fichajes(session, limit=20)
        # mostrar sólo empleados activos en la pantalla principal
        empleados = list_empleados(session, active_only=True)
        empleados_map = {e.dni: e.nombre for e in empleados}

    return templates.TemplateResponse(
        "menu.html",
        {
            "request": request,
            "recientes": recientes,
            "flash": flash,
            "empleados_map": empleados_map,
            "empleados": empleados,
        },
    )


@router.post("/admin/fichajes/manual")
def admin_fichaje_manual(request: Request, empleado_id: Optional[str] = Form(None), rfid_uid: Optional[str] = Form(None)):
    """Crear un fichaje manual seleccionando empleado o por RFID (compatibilidad).

    Guarda un mensaje en `request.session['flash']` para mostrar el resultado.
    """
    if not require_login(request):
        return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)
    engine = get_engine()
    with Session(engine) as session:
        result = None
        if empleado_id is not None:
            result = create_fichaje_for_empleado(session, empleado_id)
        elif rfid_uid:
            result = create_fichaje_by_rfid(session, rfid_uid)
    if not result:
        # mensaje genérico si no se pudo crear
        request.session["flash"] = "No se pudo crear el fichaje (empleado no encontrado)."
    else:
        fichaje, empleado, mensaje = result
        request.session["flash"] = mensaje
    return RedirectResponse(url="/admin", status_code=HTTP_302_FOUND)


@router.post("/admin/fichajes/manual_ajax")
def admin_fichaje_manual_ajax(request: Request, empleado_id: Optional[str] = Form(None), rfid_uid: Optional[str] = Form(None)):
    """Endpoint AJAX que crea un fichaje y devuelve JSON con el resultado y el nuevo registro.

    Acepta `empleado_id` (preferido) o `rfid_uid`.
    """
    if not require_login(request):
        return {"success": False, "error": "No autenticado"}
    engine = get_engine()
    with Session(engine) as session:
        result = None
        if empleado_id is not None:
            result = create_fichaje_for_empleado(session, empleado_id)
        elif rfid_uid:
            result = create_fichaje_by_rfid(session, rfid_uid)
        if not result:
            return {"success": False, "error": "Empleado no encontrado"}
        fichaje, empleado, mensaje = result
        return {
            "success": True,
            "mensaje": mensaje,
            "fichaje": {
                "id": fichaje.id,
                "timestamp": fichaje.timestamp.isoformat(),
                "empleado_id": fichaje.empleado_id,
                "empleado_nombre": empleado.nombre,
                "tipo": fichaje.tipo,
            },
        }


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
    # mostrar sólo empleados activos en la página de empleados
    empleados = list_empleados(session, active_only=True)
    return templates.TemplateResponse("empleados.html", {"request": request, "empleados": empleados})


@router.post("/admin/empleados/{empleado_id}/archive")
def admin_empleados_archive(request: Request, empleado_id: str, session: Session = Depends(get_session)):
    if not require_login(request):
        return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)
    archive_empleado(session, empleado_id)
    request.session["flash"] = f"Empleado {empleado_id} archivado."
    return RedirectResponse(url="/admin/empleados", status_code=HTTP_302_FOUND)


@router.get("/admin/empleados/archivados", response_class=HTMLResponse)
def admin_empleados_archivados(request: Request, session: Session = Depends(get_session)):
    if not require_login(request):
        return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)
    empleados = list_archived_empleados(session)
    return templates.TemplateResponse("empleados_archivados.html", {"request": request, "empleados": empleados})


@router.get("/admin/empleados/{empleado_id}/historial", response_class=HTMLResponse)
def admin_empleado_historial(request: Request, empleado_id: str, session: Session = Depends(get_session)):
    if not require_login(request):
        return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)
    # obtener empleado y su historial de fichajes
    empleado = get_empleado(session, empleado_id)
    if not empleado:
        return RedirectResponse(url="/admin/empleados/archivados", status_code=HTTP_302_FOUND)
    fichas = list_fichajes(session, empleado_id=empleado.dni)
    return templates.TemplateResponse("empleado_historial.html", {"request": request, "empleado": empleado, "fichas": fichas})


@router.post("/admin/empleados/{empleado_id}/restore")
def admin_empleados_restore(request: Request, empleado_id: str, session: Session = Depends(get_session)):
    if not require_login(request):
        return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)
    restored = restore_empleado(session, empleado_id)
    if restored:
        request.session["flash"] = f"Empleado {empleado_id} restaurado."
    # Al restaurar, redirigir al listado de empleados activos para que se vea inmediatamente
    return RedirectResponse(url="/admin/empleados", status_code=HTTP_302_FOUND)


@router.post("/admin/empleados")
def admin_empleados_add(request: Request, dni: str = Form(...), nombre: str = Form(...), rfid_uid: Optional[str] = Form(None), session: Session = Depends(get_session)):
    if not require_login(request):
        return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)
    create_empleado(session, dni=dni, nombre=nombre, rfid_uid=rfid_uid)
    return RedirectResponse(url="/admin/empleados", status_code=HTTP_302_FOUND)


@router.post("/admin/empleados/{empleado_id}/assign")
def admin_empleados_assign(request: Request, empleado_id: str, rfid_uid: str = Form(...), session: Session = Depends(get_session)):
    if not require_login(request):
        return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)
    assign_rfid(session, empleado_id, rfid_uid)
    return RedirectResponse(url="/admin/empleados", status_code=HTTP_302_FOUND)


@router.post("/admin/empleados/{empleado_id}/assign_ajax")
def admin_empleados_assign_ajax(request: Request, empleado_id: str, rfid_uid: str = Form(...), session: Session = Depends(get_session)):
    """Endpoint JSON para asignar RFID (usado por JS)."""
    if not require_login(request):
        return {"success": False, "error": "No autenticado"}
    empleado = assign_rfid(session, empleado_id, rfid_uid)
    if not empleado:
        return {"success": False, "error": "Empleado no encontrado"}
    return {"success": True, "nombre": empleado.nombre, "rfid_uid": empleado.rfid_uid}


@router.get("/admin/fichajes", response_class=HTMLResponse)
def admin_fichajes(request: Request, empleado_id: Optional[str] = None, start: Optional[str] = None, end: Optional[str] = None, session: Session = Depends(get_session)):
    """Página de histórico con filtros opcionales:
    - empleado_id: filtra por empleado (si no se pasa, muestra todos)
    - start, end: ISO datetime strings para limitar rango (opcional)
    """
    if not require_login(request):
        return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)

    # convertir fechas si vienen
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

    # obtener fichajes filtrados por la base de datos (más eficiente)
    fichas = list_fichajes(session, empleado_id=empleado_id, start=start_dt, end=end_dt)

    # pasar lista de empleados para el select de filtrado
    empleados = list_empleados(session)
    empleados_map = {e.dni: e.nombre for e in empleados}

    return templates.TemplateResponse("fichajes.html", {"request": request, "fichas": fichas, "empleados": empleados, "empleados_map": empleados_map, "filter": {"empleado_id": empleado_id, "start": start, "end": end}})


@router.get("/admin/reportes", response_class=HTMLResponse)
def admin_reportes(request: Request, session: Session = Depends(get_session)):
    if not require_login(request):
        return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)
    empleados = list_empleados(session)
    # pasar filtro vacío por defecto para evitar errores en la plantilla
    filter_ctx = {"empleado_id": None, "start": None, "end": None}
    return templates.TemplateResponse("reportes.html", {"request": request, "empleados": empleados, "filter": filter_ctx})


@router.get("/admin/reportes/horas", response_class=HTMLResponse)
def admin_reportes_result(request: Request, empleado_id: str, start: Optional[str] = None, end: Optional[str] = None, session: Session = Depends(get_session)):
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

    # Obtener pares de entrada/salida desde la función existente
    total_hours, pairs = horas_trabajadas(session, empleado_id, start=start_dt, end=end_dt)

    # Agrupar horas por día, teniendo en cuenta cruces de medianoche
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

    # convertir seconds a horas decimales (float) y crear lista ordenada por fecha
    per_day = []
    for day in sorted(per_day_seconds.keys()):
        hours = per_day_seconds[day] / 3600.0
        per_day.append((day, round(hours, 2)))

    # total horas (usar total_hours calculado por horas_trabajadas para compatibilidad)
    total_hours_rounded = round(total_hours, 2)

    # pasar empleado id y periodo para que la plantilla muestre contexto
    return templates.TemplateResponse(
        "reportes_result.html",
        {
            "request": request,
            "total_hours": total_hours_rounded,
            "per_day": per_day,
            "empleado_id": empleado_id,
            "start": start,
            "end": end,
        },
    )


@router.get("/admin/configuracion", response_class=HTMLResponse)
def admin_configuracion(request: Request, session: Session = Depends(get_session)):
    """Página de configuración - placeholder."""
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
        "configuracion.html",
        {"request": request, "auto_update": auto_update, "timezone": timezone_cfg, "flash": flash, "tz_list": tz_list},
    )


@router.post("/admin/configuracion/change_password")
def admin_change_password(request: Request, new_password: str = Form(...), confirm_password: str = Form(...), session: Session = Depends(get_session)):
    if not require_login(request):
        return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)
    if new_password != confirm_password:
        request.session["flash"] = "Las contraseñas no coinciden"
        return RedirectResponse(url="/admin/configuracion", status_code=HTTP_302_FOUND)
    username = request.session.get("user")
    if not username:
        request.session["flash"] = "Usuario no autenticado"
        return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)
    changed = change_user_password(session, username, new_password)
    request.session["flash"] = "Contraseña actualizada" if changed else "No se pudo actualizar la contraseña"
    return RedirectResponse(url="/admin/configuracion", status_code=HTTP_302_FOUND)


@router.get("/admin/configuracion/export_db")
def admin_export_db(request: Request):
    if not require_login(request):
        return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)
    # Ubicación relativa del archivo sqlite en el workspace (puede variar en despliegues)
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "pi_control.db"))
    if not os.path.exists(db_path):
        request.session["flash"] = "Archivo de base de datos no encontrado"
        return RedirectResponse(url="/admin/configuracion", status_code=HTTP_302_FOUND)
    return FileResponse(db_path, media_type="application/x-sqlite3", filename="pi_control.db")


@router.post("/admin/configuracion/import_db")
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
        request.session["flash"] = "Base de datos importada. Reinicie el servidor si procede."
    except Exception as e:
        request.session["flash"] = f"Error al importar la BD: {e}"
    return RedirectResponse(url="/admin/configuracion", status_code=HTTP_302_FOUND)


@router.post("/admin/configuracion/set_timezone")
def admin_set_timezone(request: Request, timezone: str = Form(...), session: Session = Depends(get_session)):
    if not require_login(request):
        return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)
    # Guardar en configuración y, opcionalmente, intentar aplicar con timedatectl
    set_config(session, "timezone", timezone)
    # Intentar aplicar en el sistema (puede requerir privilegios)
    try:
        subprocess.run(["timedatectl", "set-timezone", timezone], check=True, capture_output=True)
        request.session["flash"] = f"Zona horaria establecida a {timezone}"
    except Exception:
        request.session["flash"] = f"Zona horaria guardada (no se pudo aplicar en el sistema, se necesitan privilegios)"
    return RedirectResponse(url="/admin/configuracion", status_code=HTTP_302_FOUND)


@router.post("/admin/configuracion/sync_time")
def admin_sync_time(request: Request):
    if not require_login(request):
        return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)
    # Intentar forzar sincronización de hora. Puede requerir utilidades instaladas y permisos.
    try:
        # Preferir timedatectl
        res = subprocess.run(["timedatectl", "set-ntp", "true"], check=True, capture_output=True)
        request.session["flash"] = "Sincronización NTP activada (timedatectl)"
    except Exception:
        try:
            # Fallback a ntpdate
            res = subprocess.run(["ntpdate", "-u", "pool.ntp.org"], check=True, capture_output=True)
            request.session["flash"] = "Hora sincronizada con pool.ntp.org"
        except Exception as e:
            request.session["flash"] = f"No se pudo sincronizar la hora: {e}"
    return RedirectResponse(url="/admin/configuracion", status_code=HTTP_302_FOUND)


@router.post("/admin/configuracion/set_auto_update")
def admin_set_auto_update(request: Request, enabled: Optional[str] = Form(None), session: Session = Depends(get_session)):
    if not require_login(request):
        return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)
    val = "true" if enabled == "on" else "false"
    set_config(session, "auto_update", val)
    request.session["flash"] = "Actualización automática habilitada" if val == "true" else "Actualización automática deshabilitada"
    return RedirectResponse(url="/admin/configuracion", status_code=HTTP_302_FOUND)
