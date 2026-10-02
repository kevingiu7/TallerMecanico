import enum
from datetime import datetime
from sqlalchemy import Boolean, DateTime, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base


class UserRole(str, enum.Enum):
    ADMINISTRADOR_TALLER = "administrador_taller"
    RECEPCIONISTA = "recepcionista"
    ASESOR_VEHICULO = "asesor_vehiculo"
    TECNICO_CONSULTOR = "tecnico_consultor"
    CLIENTE = "cliente"
    SISTEMA = "sistema"


class User(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(80), nullable=False)
    apellidos: Mapped[str] = mapped_column(String(120), nullable=False)
    correo: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    direccion: Mapped[str] = mapped_column(String(255), nullable=False)
    telefono: Mapped[str] = mapped_column(String(25), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False, default=UserRole.CLIENTE)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    reset_token_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    reset_token_expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    actualizado_en: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

