from __future__ import annotations
from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel


class Empleado(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    rfid_uid: Optional[str] = Field(default=None, index=True)


class Fichaje(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    empleado_id: int = Field(foreign_key="empleado.id")
    tipo: str  # 'entrada' or 'salida'
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str
    is_admin: bool = Field(default=True)
