from __future__ import annotations
from typing import Optional
from datetime import datetime, timezone
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, String


class Employee(SQLModel, table=True):
    # The document ID is the primary key (string)
    # Document ID: use NOCASE collation in SQLite for case-insensitive searches/unique constraints
    document_id: str = Field(sa_column=Column(String(collation="NOCASE"), primary_key=True))
    name: str
    # Unique RFID (only one employee can have an RFID at a given time)
    rfid_uid: Optional[str] = Field(default=None, index=True, unique=True)
    # Archive date (if archived); archived employees are kept for 4 years
    archived_at: Optional[datetime] = Field(default=None, index=True)


class CheckIn(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    # Reference to Employee by document ID
    employee_id: str = Field(foreign_key="employee.document_id")
    type: str  # 'entry' or 'exit'
    # Use timezone-aware datetime to avoid Pydantic warnings
    timestamp: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str
    is_admin: bool = Field(default=True)


class Config(SQLModel, table=True):
    """Key/value simple storage for runtime configuration (timezone, flags...)."""
    key: str = Field(sa_column=Column(String, primary_key=True))
    value: Optional[str] = None


class AdminAction(SQLModel, table=True):
    """Record of actions performed by administrators.

    Used for internal auditing and traceability of sensitive operations.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc), index=True)
    admin_username: Optional[str] = Field(default=None, index=True)
    action: str
    details: Optional[str] = None

