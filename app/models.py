from __future__ import annotations
from typing import Optional
from datetime import datetime, timezone
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, String


class Empleado(SQLModel, table=True):
    # El DNI es la clave primaria (string)
    # DNI: usar collation NOCASE en SQLite para que las búsquedas/unique sean insensibles a mayúsculas
    dni: str = Field(sa_column=Column(String(collation="NOCASE"), primary_key=True))
    nombre: str
    # RFID único (solo un empleado puede tener un RFID en un momento dado)
    rfid_uid: Optional[str] = Field(default=None, index=True, unique=True)
    # Fecha de archivo (si se ha archivado); los archivados se conservan por 4 años
    archived_at: Optional[datetime] = Field(default=None, index=True)


class Fichaje(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    # Referencia a Empleado por DNI
    empleado_id: str = Field(foreign_key="empleado.dni")
    tipo: str  # 'entrada' or 'salida'
    # Usar datetime con timezone-aware para evitar warnings de Pydantic
    timestamp: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))


class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str
    is_admin: bool = Field(default=True)


class Config(SQLModel, table=True):
    """Key/value simple storage for runtime configuration (timezone, flags...)."""
    key: str = Field(sa_column=Column(String, primary_key=True))
    value: Optional[str] = None

