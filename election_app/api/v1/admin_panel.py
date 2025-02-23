# election_app/api/v1/admin_panel.py
import os
import logging
from fastapi import FastAPI
from fastapi_admin.app import app as admin_app
from fastapi_admin.providers.login import UsernamePasswordProvider
from tortoise import Tortoise, fields
from tortoise.models import Model

# Настройка логирования
logging.basicConfig(level=logging.INFO)


# Модель администратора для FastAPI Admin
class Admin(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, unique=True)
    password = fields.CharField(max_length=128)

    class Meta:
        table = "admin"


# Функция для инициализации базы данных с подключением к PostgreSQL
async def init_db():
    db_url = f"postgres://{os.getenv('DB_USER', 'postgres')}:{os.getenv('DB_PASSWORD', 'Iamtaskforce1')}@{os.getenv('DB_HOST', '127.0.0.1')}:{os.getenv('DB_PORT', '5433')}/{os.getenv('DB_NAME', 'elections')}"

    await Tortoise.init(
        db_url=db_url,
        modules={"models": ["election_app.api.admin_panel"]},
    )
    await Tortoise.generate_schemas()


# Создаем экземпляр FastAPI для административной панели
admin_panel_app = FastAPI(title="Admin Panel")


@admin_panel_app.on_event("startup")
async def startup_event():
    logging.info("Starting up the admin panel...")
    # Инициализация базы данных
    await init_db()
    logging.info("Database initialized.")

    # Настройка FastAPI Admin
    await admin_app.configure(
        logo_url="https://example.com/logo.png",  # Замените на свой логотип
        template_folders=["./templates"],  # Если есть дополнительные шаблоны
        providers=[
            UsernamePasswordProvider(
                admin_model=Admin,
                login_logo_url="https://example.com/login-logo.png",  # Логотип на странице входа
            )
        ],
    )
    logging.info("Admin panel configured.")
    # Монтируем FastAPI Admin на путь /admin
    admin_panel_app.mount("/admin", admin_app)


@admin_panel_app.get("/")
async def admin_index():
    return {"detail": "Добро пожаловать в административную панель"}
