import psycopg2
from psycopg2 import sql
from typing import Optional

# Задайте свои параметры подключения к БД
DB_NAME = "elections_db"
DB_USER = "election_admin"
DB_PASSWORD = "admin_password"
DB_HOST = "localhost"
DB_PORT = 5432


def get_connection():
    """
    Возвращает новое соединение psycopg2 с PostgreSQL.
    В реальном проекте используйте пул соединений или ORM.
    """
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    return conn