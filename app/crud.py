from typing import List, Optional, Tuple
from sqlmodel import Session, select
from .models import Empleado, Fichaje
from .db import get_engine
from datetime import datetime
from .models import Usuario
from passlib.context import CryptContext

# Usar PBKDF2-SHA256 por compatibilidad en este entorno de desarrollo
# (evita errores con backends bcrypt nativos en contenedores limitados).
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def create_empleado(session: Session, nombre: str, rfid_uid: Optional[str] = None) -> Empleado:
    empleado = Empleado(nombre=nombre, rfid_uid=rfid_uid)
    session.add(empleado)
    session.commit()
    session.refresh(empleado)
    return empleado


def get_empleado_by_rfid(session: Session, rfid_uid: str) -> Optional[Empleado]:
    statement = select(Empleado).where(Empleado.rfid_uid == rfid_uid)
    result = session.exec(statement).first()
    return result


def get_empleado(session: Session, empleado_id: int) -> Optional[Empleado]:
    return session.get(Empleado, empleado_id)


def list_empleados(session: Session) -> List[Empleado]:
    statement = select(Empleado)
    return session.exec(statement).all()


def assign_rfid(session: Session, empleado_id: int, rfid_uid: Optional[str]) -> Optional[Empleado]:
    empleado = session.get(Empleado, empleado_id)
    if not empleado:
        return None
    empleado.rfid_uid = rfid_uid
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
    statement = select(Fichaje).where(Fichaje.empleado_id == empleado.id).order_by(Fichaje.timestamp.desc())
    last = session.exec(statement).first()
    if not last or last.tipo == "salida":
        tipo = "entrada"
        mensaje = f"Bienvenido, {empleado.nombre}!"
    else:
        tipo = "salida"
        mensaje = f"Adiós, {empleado.nombre}!"

    fichaje = Fichaje(empleado_id=empleado.id, tipo=tipo)
    session.add(fichaje)
    session.commit()
    session.refresh(fichaje)
    return fichaje, empleado, mensaje


def list_fichajes(session: Session, empleado_id: Optional[int] = None) -> List[Fichaje]:
    statement = select(Fichaje)
    if empleado_id:
        statement = statement.where(Fichaje.empleado_id == empleado_id)
    statement = statement.order_by(Fichaje.timestamp.desc())
    return session.exec(statement).all()


def horas_trabajadas(session: Session, empleado_id: int, start: Optional[datetime] = None, end: Optional[datetime] = None) -> Tuple[float, List[Tuple[datetime, Optional[datetime], float]]]:
    """Calcula horas trabajadas para un empleado en el rango [start, end].

    Retorna (total_hours, lista_de_pares) donde cada par es (entrada, salida, horas_segmento).
    Si falta una salida para una entrada, la salida será None y no contará.
    """
    stmt = select(Fichaje).where(Fichaje.empleado_id == empleado_id).order_by(Fichaje.timestamp.asc())
    fichas = session.exec(stmt).all()
    # filtrar por rango
    if start:
        fichas = [f for f in fichas if f.timestamp >= start]
    if end:
        fichas = [f for f in fichas if f.timestamp <= end]

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
