from typing import List, Optional, Tuple
from sqlmodel import Session, select
from sqlalchemy import desc, asc
from .models import Empleado, Fichaje, Config
from .db import get_engine
from datetime import datetime, timezone
from .models import Usuario
from passlib.context import CryptContext

# Usar PBKDF2-SHA256 por compatibilidad en este entorno de desarrollo
# (evita errores con backends bcrypt nativos en contenedores limitados).
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def create_empleado(session: Session, dni: str, nombre: str, rfid_uid: Optional[str] = None) -> Empleado:
    """Crear o actualizar un empleado por DNI.

    Si el DNI ya existe, actualiza el registro. Si se asigna un RFID que ya pertenece a
    otro empleado, ese empleado perderá el RFID y quedará archivado.
    """
    # normalizar dni a mayúsculas para comportamiento case-insensitive
    dni = dni.strip().upper()

    # si existe el RFID en otro empleado, lo retiramos y lo archivamos
    if rfid_uid:
        prev = get_empleado_by_rfid(session, rfid_uid)
        if prev and prev.dni != dni:
            prev.rfid_uid = None
            prev.archived_at = datetime.now(tz=timezone.utc)
            session.add(prev)

    empleado = session.get(Empleado, dni)
    if empleado:
        empleado.nombre = nombre
        if rfid_uid:
            empleado.rfid_uid = rfid_uid
            empleado.archived_at = None
        session.add(empleado)
        session.commit()
        session.refresh(empleado)
        return empleado

    empleado = Empleado(dni=dni, nombre=nombre, rfid_uid=rfid_uid)
    session.add(empleado)
    session.commit()
    session.refresh(empleado)
    return empleado


def get_empleado_by_rfid(session: Session, rfid_uid: str) -> Optional[Empleado]:
    statement = select(Empleado).where(Empleado.rfid_uid == rfid_uid)
    result = session.exec(statement).first()
    return result


def get_empleado(session: Session, empleado_dni: str) -> Optional[Empleado]:
    if not empleado_dni:
        return None
    empleado_dni = empleado_dni.strip().upper()
    return session.get(Empleado, empleado_dni)


def list_empleados(session: Session, active_only: bool = False) -> List[Empleado]:
    statement = select(Empleado)
    if active_only:
        # activos = tienen RFID asignado y no están archivados
        statement = select(Empleado).where(Empleado.rfid_uid != None).where(Empleado.archived_at == None)
    return session.exec(statement).all()


def assign_rfid(session: Session, empleado_dni: str, rfid_uid: Optional[str]) -> Optional[Empleado]:
    """Asignar o quitar RFID a un empleado identificado por DNI.

    Si se asigna un RFID que estaba en otro empleado, retira el RFID del anterior y lo archiva.
    Si se quita el RFID (rfid_uid is None), el empleado se archiva.
    """
    if not empleado_dni:
        return None
    empleado_dni = empleado_dni.strip().upper()
    empleado = session.get(Empleado, empleado_dni)
    if not empleado:
        return None

    if rfid_uid:
        prev = get_empleado_by_rfid(session, rfid_uid)
        if prev and prev.dni != empleado.dni:
            prev.rfid_uid = None
            prev.archived_at = datetime.now(tz=timezone.utc)
            session.add(prev)
        empleado.rfid_uid = rfid_uid
        empleado.archived_at = None
    else:
        # quitar RFID -> archivar empleado
        empleado.rfid_uid = None
        empleado.archived_at = datetime.now(tz=timezone.utc)

    session.add(empleado)
    session.commit()
    session.refresh(empleado)
    return empleado


def create_fichaje_by_rfid(session: Session, rfid_uid: str) -> Optional[Tuple[Fichaje, Empleado, str]]:
    """Crea un fichaje para el empleado con rfid_uid.

    Devuelve una tupla (fichaje, empleado, mensaje) o None si no existe el empleado.
    """
    empleado = get_empleado_by_rfid(session, rfid_uid)
    if not empleado:
        return None

    # determinar tipo: si último fichaje fue 'entrada' -> ahora 'salida', si no -> 'entrada'
    statement = select(Fichaje).where(Fichaje.empleado_id == empleado.dni).order_by(desc(Fichaje.timestamp))
    last = session.exec(statement).first()
    if not last or last.tipo == "salida":
        tipo = "entrada"
        mensaje = f"Bienvenido, {empleado.nombre}!"
    else:
        tipo = "salida"
        mensaje = f"Adiós, {empleado.nombre}!"

    fichaje = Fichaje(empleado_id=empleado.dni, tipo=tipo)
    session.add(fichaje)
    session.commit()
    session.refresh(fichaje)
    return fichaje, empleado, mensaje


def list_fichajes(session: Session, empleado_id: Optional[str] = None, start: Optional[datetime] = None, end: Optional[datetime] = None) -> List[Fichaje]:
    """Devuelve fichajes opcionalmente filtrados por empleado y rango de fechas.

    El filtrado se realiza en la consulta SQL para eficiencia.
    """
    statement = select(Fichaje)
    if empleado_id:
        empleado_id = empleado_id.strip().upper()
        statement = statement.where(Fichaje.empleado_id == empleado_id)
    if start:
        statement = statement.where(Fichaje.timestamp >= start)
    if end:
        statement = statement.where(Fichaje.timestamp <= end)
    statement = statement.order_by(desc(Fichaje.timestamp))
    return session.exec(statement).all()


def list_recent_fichajes(session: Session, limit: int = 20) -> List[Fichaje]:
    """Devuelve las últimas `limit` fichajes ordenados por timestamp descendente."""
    statement = select(Fichaje).order_by(desc(Fichaje.timestamp)).limit(limit)
    return session.exec(statement).all()


def create_fichaje_for_empleado(session: Session, empleado_dni: str) -> Optional[Tuple[Fichaje, Empleado, str]]:
    """Crea un fichaje para el empleado por su id.

    Devuelve (fichaje, empleado, mensaje) o None si no existe el empleado.
    """
    empleado = get_empleado(session, empleado_dni)
    if not empleado:
        return None

    # determinar tipo según último fichaje
    statement = select(Fichaje).where(Fichaje.empleado_id == empleado.dni).order_by(desc(Fichaje.timestamp))
    last = session.exec(statement).first()
    if not last or last.tipo == "salida":
        tipo = "entrada"
        mensaje = f"Bienvenido, {empleado.nombre}!"
    else:
        tipo = "salida"
        mensaje = f"Adiós, {empleado.nombre}!"

    fichaje = Fichaje(empleado_id=empleado.dni, tipo=tipo)
    session.add(fichaje)
    session.commit()
    session.refresh(fichaje)
    return fichaje, empleado, mensaje


def horas_trabajadas(session: Session, empleado_id: str, start: Optional[datetime] = None, end: Optional[datetime] = None) -> Tuple[float, List[Tuple[datetime, Optional[datetime], float]]]:
    """Calcula horas trabajadas para un empleado en el rango [start, end].

    El filtrado por fechas se realiza en la consulta SQL para mayor eficiencia.
    Retorna (total_hours, lista_de_pares) donde cada par es (entrada, salida, horas_segmento).
    Si falta una salida para una entrada, la salida será None y no contará.
    """
    stmt = select(Fichaje).where(Fichaje.empleado_id == empleado_id)
    if start:
        stmt = stmt.where(Fichaje.timestamp >= start)
    if end:
        stmt = stmt.where(Fichaje.timestamp <= end)
    stmt = stmt.order_by(asc(Fichaje.timestamp))
    fichas = session.exec(stmt).all()

    total_seconds = 0.0
    pairs: List[Tuple[datetime, Optional[datetime], float]] = []
    entrada_ts: Optional[datetime] = None
    for f in fichas:
        if f.tipo == "entrada":
            entrada_ts = f.timestamp
        elif f.tipo == "salida" and entrada_ts is not None:
            delta = (f.timestamp - entrada_ts).total_seconds()
            hours = max(0.0, delta / 3600.0)
            total_seconds += delta
            pairs.append((entrada_ts, f.timestamp, hours))
            entrada_ts = None

    total_hours = total_seconds / 3600.0
    return total_hours, pairs


def create_user(session: Session, username: str, password: str, is_admin: bool = True) -> Usuario:
    hashed = pwd_context.hash(password)
    user = Usuario(username=username, hashed_password=hashed, is_admin=is_admin)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def get_user_by_username(session: Session, username: str) -> Optional[Usuario]:
    stmt = select(Usuario).where(Usuario.username == username)
    return session.exec(stmt).first()


def any_admin_exists(session: Session) -> bool:
    stmt = select(Usuario).where(Usuario.is_admin == True)
    return session.exec(stmt).first() is not None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def change_user_password(session: Session, username: str, new_password: str) -> bool:
    """Change password for a user identified by username. Returns True if updated."""
    stmt = select(Usuario).where(Usuario.username == username)
    user = session.exec(stmt).first()
    if not user:
        return False
    user.hashed_password = pwd_context.hash(new_password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return True


def set_config(session: Session, key: str, value: str) -> None:
    key = key.strip()
    stmt = select(Config).where(Config.key == key)
    item = session.exec(stmt).first()
    if item:
        item.value = value
        session.add(item)
    else:
        item = Config(key=key, value=value)
        session.add(item)
    session.commit()


def get_config(session: Session, key: str) -> Optional[str]:
    key = key.strip()
    stmt = select(Config).where(Config.key == key)
    item = session.exec(stmt).first()
    return item.value if item else None


def archive_empleado(session: Session, empleado_dni: str) -> Optional[Empleado]:
    """Marca un empleado como archivado (archived_at = now) y quita su RFID.

    Normaliza el DNI (upper) antes de operar.
    """
    if not empleado_dni:
        return None
    empleado_dni = empleado_dni.strip().upper()
    empleado = session.get(Empleado, empleado_dni)
    if not empleado:
        return None
    empleado.rfid_uid = None
    empleado.archived_at = datetime.now(tz=timezone.utc)
    session.add(empleado)
    session.commit()
    session.refresh(empleado)
    return empleado


def list_archived_empleados(session: Session) -> List[Empleado]:
    """Devuelve empleados que tienen archived_at != None."""
    stmt = select(Empleado).where(Empleado.archived_at != None)
    return session.exec(stmt).all()


def restore_empleado(session: Session, empleado_dni: str) -> Optional[Empleado]:
    """Restaura un empleado del archivo (archived_at = None).

    Normaliza el DNI (upper) antes de operar.
    """
    if not empleado_dni:
        return None
    empleado_dni = empleado_dni.strip().upper()
    empleado = session.get(Empleado, empleado_dni)
    if not empleado:
        return None
    empleado.archived_at = None
    session.add(empleado)
    session.commit()
    session.refresh(empleado)
    return empleado
