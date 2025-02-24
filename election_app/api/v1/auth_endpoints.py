# election_app/api/v1/auth_endpoints.py

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import os
import jwt
from datetime import datetime, timedelta

router = APIRouter()

# Параметры для JWT
JWT_SECRET = os.getenv("JWT_SECRET", "mysecretkey")  # В реальности храните в секрете
JWT_ALGORITHM = "HS256"
JWT_EXP_DELTA_SECONDS = 3600  # Токен действителен 1 час


# Pydantic модели для запросов и ответов

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    role: str


class LoginResponse(BaseModel):
    token: str


class ChangePasswordRequest(BaseModel):
    email: str
    current_password: str
    new_password: str


class TwoFARequest(BaseModel):
    email: str
    code: str


class TwoFAResponse(BaseModel):
    detail: str


# Демонстрационные данные технического пользователя.
# В реальном приложении данные будут храниться в базе, а пароли — в виде хэшей.
TECH_USER = {
    "email": "tech@example.com",
    "password": "secret",  # В демо используем открытый текст; в продакшене всегда хэшируйте!
    "role": "admin"
}



users = [
    TECH_USER, 
    {"email": "test1@example.com", "password": "test1", "role": "voter"},
    {"email": "test2@example.com", "password": "test2", "role": "candidate"},
]


@router.post("/auth/login", response_model=LoginResponse)
async def login(req: LoginRequest):
    """
    Endpoint для логина.
    Принимает email и пароль; если данные корректны, возвращает JWT-токен.
    """
    found = None
    for u in users:
        if req.email == u["email"] and req.password == u["password"]:
            found = u
            break

    if found is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    payload = {
        "sub": req.email,
        "role": u["role"],
        "exp": datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return LoginResponse(token=token)

@router.post("/auth/register", response_model=LoginResponse)
async def register(req: RegisterRequest):
    """
    Endpoint для регистрации.
    Принимает email и пароль и роль, возвращает JWT-токен.
    """

    found = None
    for u in users:
        if req.email == u["email"] and req.password == u["password"]:
            found = u
            break

    if found is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already exists")

    users.append({"email": req.email, "password": req.password, "role": req.role})

    payload = {
        "sub": req.email,
        "role": req.role,
        "exp": datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return LoginResponse(token=token)


@router.post("/auth/change-password")
async def change_password(req: ChangePasswordRequest):
    """
    Endpoint для смены пароля.
    Принимает email, текущий пароль и новый пароль.
    Если текущий пароль неверный или пользователь не найден, возвращает ошибку.
    При успехе возвращает сообщение об успешной смене пароля.
    """
    if req.email != TECH_USER["email"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if req.current_password != TECH_USER["password"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")

    # В реальном приложении здесь обновляется хэш пароля в базе.
    # Для демонстрации обновляем данные в TECH_USER.
    TECH_USER["password"] = req.new_password
    return {"detail": "Password changed successfully"}


@router.post("/auth/2fa", response_model=TwoFAResponse)
async def two_factor_auth(req: TwoFARequest):
    """
    Endpoint для двухфакторной аутентификации.
    Принимает email и код 2FA.
    Для демонстрации, если код равен "123456", аутентификация проходит успешно.
    """
    if req.email != TECH_USER["email"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if req.code != "123456":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid 2FA code")
    return TwoFAResponse(detail="2FA verification successful")
