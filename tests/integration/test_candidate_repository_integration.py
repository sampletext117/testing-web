import pytest
import pytest_asyncio
from datetime import date
import time

from election_app.data_access.candidate_repository import PostgresCandidateRepository
from election_app.data_access.passport_repository import PostgresPassportRepository
from election_app.domain.entities.candidate import Candidate


@pytest_asyncio.fixture
async def candidate_repo() -> PostgresCandidateRepository:
    """
    Фикстура, возвращающая экземпляр PostgresCandidateRepository.
    """
    repo = PostgresCandidateRepository()
    yield repo
    # Опционально можно добавить очистку таблицы кандидатов здесь


@pytest_asyncio.fixture
async def passport_id() -> int:
    """
    Фикстура, создающая тестовый паспорт с уникальным номером и возвращающая его passport_id.
    """
    passport_repo = PostgresPassportRepository()  # Прямой импорт, без await при создании объекта
    unique_num = int(time.time() * 1000000)
    passport_number = f"TEST-PASSPORT-{unique_num}"
    pid = await passport_repo.create_passport(
        passport_number=passport_number,
        issued_by="Test Issuer",
        issue_date=date(2010, 1, 1),
        country="Россия"
    )
    return pid


@pytest.mark.asyncio
class TestCandidateRepositoryIntegration:
    async def test_create_and_find_candidate(self, candidate_repo: PostgresCandidateRepository, passport_id: int):
        """
        Проверяем, что можем создать кандидата и найти его по ID.
        """
        new_id = await candidate_repo.create_candidate(
            full_name="Иванов Иван",
            birth_date=date(1980, 5, 20),
            passport_id=passport_id
        )
        assert new_id > 0, "Должны получить валидный candidate_id"

        candidate = await candidate_repo.find_candidate_by_id(new_id)
        assert candidate is not None, "Кандидат должен быть найден"
        assert candidate.candidate_id == new_id
        assert candidate.full_name == "Иванов Иван"

    async def test_list_candidates(self, candidate_repo: PostgresCandidateRepository, passport_id: int):
        """
        Проверяем, что list_candidates() возвращает всех кандидатов, включая только что созданных.
        Для каждого кандидата используется уникальный passport_id.
        """
        # Создаем первого кандидата с использованием фикстуры passport_id
        id1 = await candidate_repo.create_candidate("Candidate A", date(1975, 1, 1), passport_id)

        # Для второго кандидата создаем отдельный паспорт
        passport_repo = __import__("election_app.data_access.passport_repository",
                                   fromlist=["PostgresPassportRepository"]).PostgresPassportRepository()
        unique_num = int(time.time() * 1000000) + 1  # +1 для уникальности
        passport_number = f"TEST-PASSPORT-{unique_num}"
        passport_id_b = await passport_repo.create_passport(
            passport_number=passport_number,
            issued_by="Test Issuer",
            issue_date=date(2010, 1, 1),
            country="Россия"
        )
        id2 = await candidate_repo.create_candidate("Candidate B", date(1970, 5, 5), passport_id_b)

        all_cands = await candidate_repo.list_candidates()
        cand_ids = [c.candidate_id for c in all_cands]

        assert id1 in cand_ids, "Candidate A должен присутствовать в списке"
        assert id2 in cand_ids, "Candidate B должен присутствовать в списке"

    async def test_patch_candidate(self, candidate_repo: PostgresCandidateRepository, passport_id: int):
        """
        Проверяем частичный апдейт кандидата (patch_candidate):
        обновляем program и balance.
        """
        cid = await candidate_repo.create_candidate("Patch Me", date(1985, 1, 1), passport_id)
        ok = await candidate_repo.patch_candidate(candidate_id=cid, program="Новая программа", balance=1234.5)
        assert ok is True, "patch_candidate должен вернуть True при успешном обновлении"

        updated = await candidate_repo.find_candidate_by_id(cid)
        assert updated is not None, "Кандидат должен существовать после патча"
        # Проверяем, что после обновления поля campaign_program_id и account_id установлены
        assert updated.campaign_program_id is not None, "campaign_program_id должен быть установлен"
        assert updated.account_id is not None, "account_id должен быть установлен"

    async def test_delete_candidate(self, candidate_repo: PostgresCandidateRepository, passport_id: int):
        """
        Проверяем удаление кандидата.
        """
        cid = await candidate_repo.create_candidate("To Delete", date(1972, 4, 4), passport_id)
        candidate = await candidate_repo.find_candidate_by_id(cid)
        assert candidate is not None, "Кандидат должен быть создан"

        success = await candidate_repo.delete_candidate(cid)
        assert success is True, "Удаление кандидата должно вернуть True"

        gone = await candidate_repo.find_candidate_by_id(cid)
        assert gone is None, "Кандидат не должен быть найден после удаления"
