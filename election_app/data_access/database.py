import asyncpg
import os
import asyncio

DB_NAME = "elections"
DB_USER = "postgres"
DB_HOST = "localhost"
DB_PORT = 5433


async def get_connection():
    conn = await asyncpg.connect(
        database=DB_NAME,
        user=DB_USER,
        password="Iamtaskforce1",
        host=DB_HOST,
        port=DB_PORT
    )
    return conn


async def main():
    try:
        res = await get_connection()
    except Exception as e:
        print(e)

asyncio.run(main())
