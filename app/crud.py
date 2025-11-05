from typing import List, Optional, Tuple
from sqlmodel import Session, select
from sqlalchemy import desc, asc
from .models import Employee, CheckIn, Config
from .models import User, AdminAction
from .db import get_engine
from datetime import datetime, timezone
from .models import User
from passlib.context import CryptContext
import logging

# Use PBKDF2-SHA256 for compatibility in this development environment
# (avoids errors with native bcrypt backends in limited containers).
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def create_employee(session: Session, document_id: str, name: str, rfid_uid: Optional[str] = None, performed_by: Optional[str] = None) -> Employee:
    """Create or update an employee by document ID.

    If the document ID already exists, updates the record. If an RFID is assigned that already
    belongs to another employee, that employee will lose the RFID and be archived.
    """
    # normalize document_id to uppercase for case-insensitive behavior
    document_id = document_id.strip().upper()

    # if RFID exists in another employee, remove it and archive them
    if rfid_uid:
        prev = get_employee_by_rfid(session, rfid_uid)
        if prev and prev.document_id != document_id:
            prev.rfid_uid = None
            prev.archived_at = datetime.now(tz=timezone.utc)
            session.add(prev)
            try:
                log_admin_action(session, performed_by, "reassign_rfid", f"rfid {rfid_uid} removed from {prev.document_id} due to reassignment to {document_id}")
            except Exception:
                pass

    employee = session.get(Employee, document_id)
    if employee:
        employee.name = name
        if rfid_uid:
            employee.rfid_uid = rfid_uid
            employee.archived_at = None
        session.add(employee)
        session.commit()
        session.refresh(employee)
        try:
            log_admin_action(session, performed_by, "update_employee", f"updated {employee.document_id} name={name} rfid={rfid_uid}")
        except Exception:
            pass
        return employee

    employee = Employee(document_id=document_id, name=name, rfid_uid=rfid_uid)
    session.add(employee)
    session.commit()
    session.refresh(employee)
    try:
        log_admin_action(session, performed_by, "create_employee", f"created {employee.document_id} name={name} rfid={rfid_uid}")
    except Exception:
        pass
    return employee


def get_employee_by_rfid(session: Session, rfid_uid: str) -> Optional[Employee]:
    statement = select(Employee).where(Employee.rfid_uid == rfid_uid)
    result = session.exec(statement).first()
    return result


def get_employee(session: Session, document_id: str) -> Optional[Employee]:
    if not document_id:
        return None
    document_id = document_id.strip().upper()
    return session.get(Employee, document_id)


def list_employees(session: Session, active_only: bool = False) -> List[Employee]:
    statement = select(Employee)
    if active_only:
        # active = have RFID assigned and are not archived
        statement = select(Employee).where(Employee.rfid_uid != None).where(Employee.archived_at == None)
    return session.exec(statement).all()


def assign_rfid(session: Session, document_id: str, rfid_uid: Optional[str], performed_by: Optional[str] = None) -> Optional[Employee]:
    """Assign or remove RFID from an employee identified by document ID.

    If an RFID is assigned that was on another employee, removes the RFID from the previous employee and archives them.
    If RFID is removed (rfid_uid is None), the employee is archived.
    """
    if not document_id:
        return None
    document_id = document_id.strip().upper()
    employee = session.get(Employee, document_id)
    if not employee:
        return None

    if rfid_uid:
        prev = get_employee_by_rfid(session, rfid_uid)
        if prev and prev.document_id != employee.document_id:
            prev.rfid_uid = None
            prev.archived_at = datetime.now(tz=timezone.utc)
            session.add(prev)
            try:
                log_admin_action(session, performed_by, "reassign_rfid", f"rfid {rfid_uid} removed from {prev.document_id} due to reassignment to {employee.document_id}")
            except Exception:
                pass
        employee.rfid_uid = rfid_uid
        employee.archived_at = None
    else:
        # remove RFID -> archive employee
        employee.rfid_uid = None
        employee.archived_at = datetime.now(tz=timezone.utc)

    session.add(employee)
    session.commit()
    session.refresh(employee)
    try:
        log_admin_action(session, performed_by, "assign_rfid", f"assigned rfid={rfid_uid} to {employee.document_id}")
    except Exception:
        pass
    return employee


def create_checkin_by_rfid(session: Session, rfid_uid: str) -> Optional[Tuple[CheckIn, Employee, str]]:
    """Create a check-in for the employee with rfid_uid.

    Returns a tuple (checkin, employee, message) or None if employee doesn't exist.
    """
    employee = get_employee_by_rfid(session, rfid_uid)
    if not employee:
        return None

    # determine type: if last check-in was 'entry' -> now 'exit', otherwise -> 'entry'
    statement = select(CheckIn).where(CheckIn.employee_id == employee.document_id).order_by(desc(CheckIn.timestamp))
    last = session.exec(statement).first()
    if not last or last.type == "exit":
        type_val = "entry"
        message = f"Welcome, {employee.name}!"
    else:
        type_val = "exit"
        message = f"Goodbye, {employee.name}!"

    checkin = CheckIn(employee_id=employee.document_id, type=type_val)
    session.add(checkin)
    session.commit()
    session.refresh(checkin)
    return checkin, employee, message


def list_checkins(session: Session, employee_id: Optional[str] = None, start: Optional[datetime] = None, end: Optional[datetime] = None) -> List[CheckIn]:
    """Return check-ins optionally filtered by employee and date range.

    Args:
        session: Database session
        employee_id: Filter by employee document ID
        start: Start datetime (inclusive)
        end: End datetime (inclusive)
    """
    statement = select(CheckIn)
    if employee_id:
        employee_id = employee_id.strip().upper()
        statement = statement.where(CheckIn.employee_id == employee_id)
    if start:
        statement = statement.where(CheckIn.timestamp >= start)
    if end:
        statement = statement.where(CheckIn.timestamp <= end)
    statement = statement.order_by(desc(CheckIn.timestamp))
    return session.exec(statement).all()


def create_checkin_for_employee(session: Session, document_id: str) -> Optional[Tuple[CheckIn, Employee, str]]:
    """Create a check-in for employee by document ID (manual check-in)."""
    employee = get_employee(session, document_id)
    if not employee:
        return None
    
    # determine type: if last check-in was 'entry' -> now 'exit', otherwise -> 'entry'
    statement = select(CheckIn).where(CheckIn.employee_id == employee.document_id).order_by(desc(CheckIn.timestamp))
    last = session.exec(statement).first()
    if not last or last.type == "exit":
        type_val = "entry"
        message = f"Welcome, {employee.name}!"
    else:
        type_val = "exit"
        message = f"Goodbye, {employee.name}!"

    checkin = CheckIn(employee_id=employee.document_id, type=type_val)
    session.add(checkin)
    session.commit()
    session.refresh(checkin)
    return checkin, employee, message


def list_recent_checkins(session: Session, limit: int = 20) -> List[CheckIn]:
    """Return recent check-ins ordered by most recent first."""
    statement = select(CheckIn).order_by(desc(CheckIn.timestamp)).limit(limit)
    return session.exec(statement).all()


def hours_worked(session: Session, employee_id: str, start: Optional[datetime] = None, end: Optional[datetime] = None):
    """Calculate hours worked for an employee in a time range.
    
    Returns (total_hours, pairs) where pairs are (entry_checkin, exit_checkin) tuples.
    """
    if not employee_id:
        return 0, []
    
    employee_id = employee_id.strip().upper()
    checkins = list_checkins(session, employee_id=employee_id, start=start, end=end)
    
    # Group into entry/exit pairs
    pairs = []
    entry = None
    
    for checkin in reversed(checkins):  # Process chronologically
        if checkin.type == "entry":
            entry = checkin
        elif checkin.type == "exit" and entry:
            pairs.append((entry, checkin))
            entry = None
    
    # Calculate total hours
    total_hours = 0
    for entry_checkin, exit_checkin in pairs:
        delta = exit_checkin.timestamp - entry_checkin.timestamp
        total_hours += delta.total_seconds() / 3600  # Convert to hours
    
    return total_hours, pairs


def list_archived_employees(session: Session) -> List[Employee]:
    """Return list of archived employees."""
    statement = select(Employee).where(Employee.archived_at != None).order_by(desc(Employee.archived_at))
    return session.exec(statement).all()


def restore_employee(session: Session, document_id: str, performed_by: Optional[str] = None) -> Optional[Employee]:
    """Restore an archived employee."""
    if not document_id:
        return None
    document_id = document_id.strip().upper()
    employee = session.get(Employee, document_id)
    if not employee:
        return None
    
    employee.archived_at = None
    session.add(employee)
    session.commit()
    session.refresh(employee)
    try:
        log_admin_action(session, performed_by, "restore_employee", f"restored {employee.document_id}")
    except Exception:
        pass
    return employee


def archive_employee(session: Session, document_id: str, performed_by: Optional[str] = None) -> Optional[Employee]:
    """Mark an employee as archived (archived_at = now) and remove their RFID."""
    if not document_id:
        return None
    document_id = document_id.strip().upper()
    employee = session.get(Employee, document_id)
    if not employee:
        return None
    employee.rfid_uid = None
    employee.archived_at = datetime.now(tz=timezone.utc)
    session.add(employee)
    session.commit()
    session.refresh(employee)
    try:
        log_admin_action(session, performed_by, "archive_employee", f"archived {employee.document_id}")
    except Exception:
        pass
    return employee


# --- User management functions ---
def create_user(session: Session, username: str, password: str, is_admin: bool = True, performed_by: Optional[str] = None) -> User:
    """Create a new user with hashed password."""
    hashed_password = pwd_context.hash(password)
    user = User(username=username, hashed_password=hashed_password, is_admin=is_admin)
    session.add(user)
    session.commit()
    session.refresh(user)
    try:
        log_admin_action(session, performed_by, "create_user", f"created user {username} is_admin={is_admin}")
    except Exception:
        pass
    return user


def get_user(session: Session, username: str) -> Optional[User]:
    """Get user by username."""
    statement = select(User).where(User.username == username)
    return session.exec(statement).first()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(session: Session, username: str, password: str) -> Optional[User]:
    """Authenticate user with username and password."""
    user = get_user(session, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def update_user_password(session: Session, username: str, new_password: str, performed_by: Optional[str] = None) -> Optional[User]:
    """Update user password."""
    user = get_user(session, username)
    if not user:
        return None
    
    user.hashed_password = pwd_context.hash(new_password)
    session.add(user)
    session.commit()
    session.refresh(user)
    try:
        log_admin_action(session, performed_by, "update_password", f"updated password for {username}")
    except Exception:
        pass
    return user


def list_users(session: Session) -> List[User]:
    """List all users."""
    return session.exec(select(User)).all()


def any_admin_exists(session: Session) -> bool:
    """Check if any admin user exists."""
    statement = select(User).where(User.is_admin == True)
    return session.exec(statement).first() is not None


# --- Configuration functions ---
def get_config(session: Session, key: str) -> Optional[str]:
    """Get configuration value by key."""
    config = session.get(Config, key)
    return config.value if config else None


def set_config(session: Session, key: str, value: str, performed_by: Optional[str] = None):
    """Set configuration value."""
    key = key.strip()
    config = session.get(Config, key)
    if config:
        config.value = value
    else:
        config = Config(key=key, value=value)
    session.add(config)
    session.commit()
    try:
        log_admin_action(session, performed_by, "set_config", f"set {key}={value}")
    except Exception:
        pass


def list_configs(session: Session) -> List[Config]:
    """List all configuration entries."""
    return session.exec(select(Config)).all()


# --- Admin action logging ---
def log_admin_action(session: Session, admin_username: Optional[str], action: str, details: Optional[str] = None):
    """Log an admin action for audit purposes."""
    if not admin_username:
        return
    
    logger = logging.getLogger("picontrol.admin")
    try:
        # Log to file (if configured)
        try:
            logger.info(f"actor={admin_username} action={action} details={details}")
        except Exception:
            pass
        
        admin_action = AdminAction(
            admin_username=admin_username,
            action=action,
            details=details
        )
        session.add(admin_action)
        session.commit()
        session.refresh(admin_action)
        return admin_action
    except Exception:
        session.rollback()
        raise


def list_admin_actions(session: Session, start: Optional[datetime] = None, end: Optional[datetime] = None, admin_username: Optional[str] = None, action: Optional[str] = None, limit: int = 200, offset: int = 0) -> List[AdminAction]:
    """Return audit records filtered by date range, admin, or action.

    - start/end: datetime objects (timezone-aware preferred)
    - admin_username: filter by actor username
    - action: filter by action name (exact match)
    - limit/offset: simple pagination
    """
    statement = select(AdminAction)
    if start:
        statement = statement.where(AdminAction.timestamp >= start)
    if end:
        statement = statement.where(AdminAction.timestamp <= end)
    if admin_username:
        statement = statement.where(AdminAction.admin_username == admin_username)
    if action:
        statement = statement.where(AdminAction.action == action)
    statement = statement.order_by(desc(AdminAction.timestamp)).offset(offset).limit(limit)
    return session.exec(statement).all()


# --- Initialization helpers ---
def init_default_admin(session: Session):
    """Initialize default admin user if none exists."""
    users = list_users(session)
    if not users:
        create_user(session, "admin", "admin123", is_admin=True)
        logging.info("Created default admin user (username: admin, password: admin123)")


def init_default_config(session: Session):
    """Initialize default configuration values."""
    configs = list_configs(session)
    if not configs:
        set_config(session, "timezone", "UTC")
        set_config(session, "company_name", "PiControl Company")
        set_config(session, "max_hours_per_day", "8")
        logging.info("Initialized default configuration")