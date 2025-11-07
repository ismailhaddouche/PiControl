from __future__ import annotations
from typing import Optional
from datetime import datetime, timezone
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, String


class Employee(SQLModel, table=True):
    """Employee record with RFID association and archive support."""
    document_id: str = Field(sa_column=Column(String(collation="NOCASE"), primary_key=True))
    name: str
    rfid_uid: Optional[str] = Field(default=None, index=True, unique=True)
    archived_at: Optional[datetime] = Field(default=None, index=True)


class CheckIn(SQLModel, table=True):
    """Entry/exit timestamp record for employees."""
    id: Optional[int] = Field(default=None, primary_key=True)
    employee_id: str = Field(foreign_key="employee.document_id")
    type: str  # 'entry' or 'exit'
    timestamp: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))


class User(SQLModel, table=True):
    """Admin user account with hashed password."""
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str
    is_admin: bool = Field(default=True)


class Config(SQLModel, table=True):
    """Key/value store for runtime configuration."""
    key: str = Field(sa_column=Column(String, primary_key=True))
    value: Optional[str] = None


class AdminAction(SQLModel, table=True):
    """Audit log of administrator actions."""
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc), index=True)
    admin_username: Optional[str] = Field(default=None, index=True)
    action: str
    details: Optional[str] = None

