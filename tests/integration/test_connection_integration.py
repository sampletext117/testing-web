import pytest
from election_app.data_access.database import get_connection


@pytest.mark.asyncio
async def test_db_connection():
    conn = await get_connection()
    assert conn is not None
    await conn.close()
