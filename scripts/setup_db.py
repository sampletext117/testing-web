import os
import asyncio
import asyncpg

async def main():
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_user = os.getenv("DB_USER", "testuser")
    db_password = os.getenv("DB_PASSWORD", "testpass")
    db_name = os.getenv("DB_NAME", "testdb")

    del_sql_file_path = os.path.join("scripts", "del.sql")
    create_sql_file_path = os.path.join("scripts", "create.sql")
    with open(create_sql_file_path, "r", encoding="utf-8") as f:
        create_sql = f.read()
    with open(del_sql_file_path, "r", encoding="utf-8") as f:
        del_sql = f.read()

    print(f"[setup_db] Will connect to DB={db_name} on {db_host}:{db_port} as {db_user}")

    conn_str = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    conn = None
    try:
        conn = await asyncpg.connect(conn_str)
        print("[setup_db] Connected successfully. Executing del.sql ...")

        # await conn.execute(del_sql)
        #
        # print("[setup_db] Done droping schema. Now creating tables")

        await conn.execute(create_sql)

        print("[setup_db] Done creating tables.")

        # await conn.execute(
        #     '''INSERT INTO elections.passport (passport_number, issued_by, issue_date, country)
        #         VALUES (, $2, $3, $4)'''
        # )
    except Exception as e:
        print(f"[setup_db] Error: {e}")
        raise
    finally:
        if conn:
            await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
