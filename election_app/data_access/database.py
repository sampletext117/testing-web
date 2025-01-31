import asyncpg
import os

DB_NAME = os.getenv("DB_NAME", "elections_db")
DB_USER = os.getenv("DB_USER", "election_admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "admin_password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 5432))


async def get_connection():
    """
    Возвращает соединение asyncpg (Connection).
    В реальном проекте чаще используют пул соединений, 
    чтобы не создавать/закрывать соединение на каждый запрос.
    """
    conn = await asyncpg.connect(
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    return conn
