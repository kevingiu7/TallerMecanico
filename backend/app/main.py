from datetime import datetime, timedelta
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session
from .config import get_settings
from .database import Base, engine, get_db
from .models import User, UserRole
from .schemas import (AuthResponse, ForgotPasswordRequest, LoginRequest, MessageResponse,
                      ResetPasswordRequest, RoleUpdate, UserPublic, UserRegister)
from .security import (create_access_token, get_current_user, hash_password, hash_reset_token,
                       new_reset_token, require_roles, verify_password)

Base.metadata.create_all(bind=engine)
settings = get_settings()
app = FastAPI(title="Taller Mecánico - Identidad", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=[settings.frontend_url], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/auth/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    correo = str(payload.correo).lower()
    if db.scalar(select(User).where(User.correo == correo)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe una cuenta con este correo")
    user = User(nombre=payload.nombre.strip(), apellidos=payload.apellidos.strip(), correo=correo,
                direccion=payload.direccion.strip(), telefono=payload.telefono,
                password_hash=hash_password(payload.contrasena), rol=UserRole.CLIENTE)
    db.add(user)
    db.commit()
    return {"message": "Registro completado. Ya puede iniciar sesión."}


@app.post("/api/auth/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.correo == str(payload.correo).lower()))
    if not user or not verify_password(payload.contrasena, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Correo o contraseña incorrectos")
    if not user.activo:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="La cuenta está inactiva")
    return {"access_token": create_access_token(user), "user": user}


@app.get("/api/auth/me", response_model=UserPublic)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@app.post("/api/auth/forgot-password", response_model=MessageResponse)
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    reset_url = None
    user = db.scalar(select(User).where(User.correo == str(payload.correo).lower()))
    if user and user.activo:
        token, token_hash = new_reset_token()
        user.reset_token_hash = token_hash
        user.reset_token_expires_at = datetime.utcnow() + timedelta(minutes=30)
        db.commit()
        reset_url = f"{settings.frontend_url}/?reset_token={token}"
        print(f"Password reset for {user.correo}: {reset_url}")
    response = {"message": "Si el correo está registrado, recibirá instrucciones para recuperar su contraseña."}
    if reset_url and settings.app_environment == "development":
        response["reset_url"] = reset_url
    return response


@app.post("/api/auth/reset-password", response_model=MessageResponse)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.reset_token_hash == hash_reset_token(payload.token)))
    if not user or not user.reset_token_expires_at or user.reset_token_expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El enlace de recuperación es inválido o expiró")
    user.password_hash = hash_password(payload.contrasena)
    user.reset_token_hash = None
    user.reset_token_expires_at = None
    db.commit()
    return {"message": "Contraseña actualizada. Ya puede iniciar sesión."}


@app.patch("/api/users/{user_id}/role", response_model=UserPublic)
def update_role(user_id: int, payload: RoleUpdate, db: Session = Depends(get_db),
                _: User = Depends(require_roles(UserRole.ADMINISTRADOR_TALLER))):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    user.rol = payload.rol
    db.commit()
    db.refresh(user)
    return user
