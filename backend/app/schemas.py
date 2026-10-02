import re
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from .models import UserRole

PASSWORD_PATTERN = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,}$")


class UserRegister(BaseModel):
    nombre: str = Field(min_length=2, max_length=80)
    apellidos: str = Field(min_length=2, max_length=120)
    correo: EmailStr
    direccion: str = Field(min_length=5, max_length=255)
    telefono: str = Field(min_length=7, max_length=25)
    contrasena: str = Field(min_length=8, max_length=128)

    @field_validator("telefono")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        cleaned = re.sub(r"[\s()\-]", "", value)
        if not re.fullmatch(r"\+?\d{7,15}", cleaned):
            raise ValueError("Ingrese un teléfono válido")
        return value.strip()

    @field_validator("contrasena")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not PASSWORD_PATTERN.match(value):
            raise ValueError("La contraseña debe tener 8 caracteres, mayúscula, minúscula, número y símbolo")
        return value


class LoginRequest(BaseModel):
    correo: EmailStr
    contrasena: str = Field(min_length=1, max_length=128)


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nombre: str
    apellidos: str
    correo: EmailStr
    direccion: str
    telefono: str
    rol: UserRole
    activo: bool
    creado_en: datetime


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic


class MessageResponse(BaseModel):
    message: str
    reset_url: str | None = None


class ForgotPasswordRequest(BaseModel):
    correo: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=20, max_length=200)
    contrasena: str = Field(min_length=8, max_length=128)

    @field_validator("contrasena")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not PASSWORD_PATTERN.match(value):
            raise ValueError("La contraseña debe tener 8 caracteres, mayúscula, minúscula, número y símbolo")
        return value


class RoleUpdate(BaseModel):
    rol: UserRole
