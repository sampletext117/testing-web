# election_app/api/admin_panel.py
import os
from fastapi import FastAPI
from fastapi_admin.app import app as admin_app
from fastapi_admin.providers.login import UsernamePasswordProvider
from tortoise import Tortoise, fields
from tortoise.models import Model

# Пример модели администратора для fastapi-admin (используйте свои модели)
class Admin(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, unique=True)
    password = fields.CharField(max_length=128)

    class Meta:
        table = "admin"

# Функция для инициализации базы данных для Tortoise ORM
async def init_db():
    await Tortoise.init(
        db_url=os.getenv("DB_URL", "sqlite://:memory:"),
        modules={"models": ["election_app.api.admin_panel"]},
    )
    await Tortoise.generate_schemas()

# Создаем экземпляр FastAPI, если он еще не создан
admin_panel_app = FastAPI(title="Admin Panel")

@admin_panel_app.on_event("startup")
async def startup_event():
    # Инициализация базы данных (если требуется, можно подключить другую БД для админки)
    await init_db()
    # Настройка FastAPI Admin
    await admin_app.configure(
        logo_url="https://example.com/logo.png",
        template_folders=["./templates"],
        providers=[
            UsernamePasswordProvider(
                admin_model=Admin,
                login_logo_url="https://example.com/login-logo.png",
            )
        ],
    )
    # Монтируем fastapi-admin в наше приложение админки
    admin_panel_app.mount("/admin", admin_app)

@admin_panel_app.get("/")
async def admin_index():
    return {"detail": "Добро пожаловать в административную панель"}
