# tests/integration/test_voter_repository_integration.py

import pytest
import pytest_asyncio
import time
from datetime import date
from election_app.data_access.voter_repository import PostgresVoterRepository
from election_app.data_access.passport_repository import PostgresPassportRepository
from election_app.domain.entities.voter import Voter

@pytest_asyncio.fixture
async def voter_repo() -> PostgresVoterRepository:
    repo = PostgresVoterRepository()
    yield repo

@pytest_asyncio.fixture
async def unique_passport_id() -> int:
    """
    Фикстура, создающая уникальный тестовый паспорт и возвращающая его passport_id.
    """
    passport_repo = PostgresPassportRepository()
    unique_num = int(time.time() * 1000000)
    passport_number = f"TEST-PASSPORT-{unique_num}"
    pid = await passport_repo.create_passport(
        passport_number=passport_number,
        issued_by="Issuer",
        issue_date=date(2010, 1, 1),
        country="Россия"
    )
    return pid


@pytest.mark.asyncio
class TestVoterRepositoryIntegration:
    async def test_create_and_find_voter(self, voter_repo: PostgresVoterRepository, unique_passport_id: int):
        new_id = await voter_repo.create_voter(
            full_name="Петров Петр",
            birth_date=date(1990, 5, 20),
            passport_id=unique_passport_id
        )
        assert new_id > 0, "Должны получить валидный voter_id"
        voter = await voter_repo.find_voter_by_id(new_id)
        assert voter is not None, "Избиратель должен быть найден"
        assert voter.voter_id == new_id
        assert voter.full_name == "Петров Петр"

    async def test_find_by_passport_id(self, voter_repo: PostgresVoterRepository, unique_passport_id: int):
        new_id = await voter_repo.create_voter(
            full_name="Сидоров Сидор",
            birth_date=date(1985, 3, 15),
            passport_id=unique_passport_id
        )
        voter = await voter_repo.find_by_passport_id(unique_passport_id)
        assert voter is not None, "Избиратель должен быть найден по passport_id"
        assert voter.voter_id == new_id

    async def test_list_all_voters(self, voter_repo: PostgresVoterRepository, unique_passport_id: int):
        # Создаем первого избирателя с фиксированным passport_id из фикстуры
        id1 = await voter_repo.create_voter("User A", date(1980, 1, 1), unique_passport_id)
        # Для второго избирателя создаём отдельный тестовый паспорт
        passport_repo = PostgresPassportRepository()
        unique_num = int(time.time() * 1000000) + 1  # для уникальности
        passport_number_2 = f"TEST-PASSPORT-{unique_num}"
        pid2 = await passport_repo.create_passport(
            passport_number=passport_number_2,
            issued_by="Issuer",
            issue_date=date(2010, 1, 1),
            country="Россия"
        )
        id2 = await voter_repo.create_voter("User B", date(1982, 2, 2), pid2)
        voters = await voter_repo.list_all_voters()
        voter_ids = [v.voter_id for v in voters]
        assert id1 in voter_ids, "User A должен присутствовать в списке"
        assert id2 in voter_ids, "User B должен присутствовать в списке"

    async def test_delete_voter(self, voter_repo: PostgresVoterRepository, unique_passport_id: int):
        new_id = await voter_repo.create_voter("Delete Me", date(1970, 1, 1), unique_passport_id)
        voter = await voter_repo.find_voter_by_id(new_id)
        assert voter is not None, "Избиратель должен быть создан"
        success = await voter_repo.delete_voter(new_id)
        assert success is True, "Удаление избирателя должно вернуть True"
        deleted = await voter_repo.find_voter_by_id(new_id)
        assert deleted is None, "Избиратель не должен быть найден после удаления"
