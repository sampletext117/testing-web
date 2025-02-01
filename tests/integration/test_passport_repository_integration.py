import pytest
import pytest_asyncio
import time
from datetime import date

from election_app.data_access.passport_repository import PostgresPassportRepository
from election_app.domain.entities.passport import Passport
import asyncpg

@pytest_asyncio.fixture
async def passport_repo() -> PostgresPassportRepository:
    repo = PostgresPassportRepository()
    yield repo

@pytest.mark.asyncio
class TestPassportRepositoryIntegration:
    async def test_create_and_find_by_number(self, passport_repo: PostgresPassportRepository):
        unique_num = int(time.time() * 1000000)
        passport_number = f"TEST-PASSPORT-{unique_num}"
        pid = await passport_repo.create_passport(
            passport_number=passport_number,
            issued_by="Issuer",
            issue_date=date(2010, 1, 1),
            country="Россия"
        )
        assert pid > 0, "Должны получить валидный passport_id"
        found = await passport_repo.find_by_number(passport_number)
        assert found is not None, "Паспорт должен быть найден по номеру"
        assert found.passport_id == pid
        assert found.passport_number == passport_number

    async def test_find_by_id(self, passport_repo: PostgresPassportRepository):
        unique_num = int(time.time() * 1000000)
        passport_number = f"TEST-PASSPORT-{unique_num}"
        pid = await passport_repo.create_passport(
            passport_number=passport_number,
            issued_by="Issuer",
            issue_date=date(2010, 1, 1),
            country="Россия"
        )
        found = await passport_repo.find_by_id(pid)
        assert found is not None, "Паспорт должен быть найден по ID"
        assert found.passport_id == pid
        assert found.passport_number == passport_number

    async def test_duplicate_passport(self, passport_repo: PostgresPassportRepository):
        unique_num = int(time.time() * 1000000)
        passport_number = f"TEST-PASSPORT-{unique_num}"
        pid1 = await passport_repo.create_passport(
            passport_number=passport_number,
            issued_by="Issuer",
            issue_date=date(2010, 1, 1),
            country="Россия"
        )
        # Ожидаем, что повторная попытка создания паспорта с таким же номером вызовет UniqueViolationError
        with pytest.raises(asyncpg.exceptions.UniqueViolationError):
            await passport_repo.create_passport(
                passport_number=passport_number,
                issued_by="Issuer",
                issue_date=date(2010, 1, 1),
                country="Россия"
            )