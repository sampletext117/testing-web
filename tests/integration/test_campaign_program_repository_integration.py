import pytest
import pytest_asyncio
import time
from datetime import date

from election_app.data_access.campaign_program_repository import PostgresCampaignProgramRepository
from election_app.data_access.candidate_repository import PostgresCandidateRepository
from election_app.data_access.passport_repository import PostgresPassportRepository
from election_app.domain.entities.campaign_program import CampaignProgram

@pytest_asyncio.fixture
async def campaign_repo() -> PostgresCampaignProgramRepository:
    repo = PostgresCampaignProgramRepository()
    yield repo
    # (Опционально: очистка таблицы campaign_program)

@pytest_asyncio.fixture
async def existing_candidate_id() -> int:
    """
    Фикстура, создающая тестового кандидата и возвращающая его candidate_id.
    Для создания кандидата используется уникальный passport_number.
    """
    candidate_repo = PostgresCandidateRepository()
    passport_repo = PostgresPassportRepository()
    unique_num = int(time.time() * 1000000)
    passport_number = f"TEST-PASSPORT-{unique_num}"
    pid = await passport_repo.create_passport(
        passport_number=passport_number,
        issued_by="Test Issuer",
        issue_date=date(2010, 1, 1),
        country="Россия"
    )
    cid = await candidate_repo.create_candidate(
        full_name="Test Candidate",
        birth_date=date(1980, 1, 1),
        passport_id=pid
    )
    return cid

@pytest.mark.asyncio
class TestCampaignProgramRepositoryIntegration:
    async def test_create_and_find_program(self, campaign_repo: PostgresCampaignProgramRepository, existing_candidate_id: int):
        """
        Проверяем, что можем создать предвыборную программу для кандидата и затем найти её по candidate_id.
        """
        description = "Test Campaign Program"
        # Используем существующий candidate_id из фикстуры
        program_id = await campaign_repo.create_program(candidate_id=existing_candidate_id, description=description)
        assert program_id > 0, "Должны получить валидный campaign_program_id"

        program = await campaign_repo.find_by_candidate_id(candidate_id=existing_candidate_id)
        assert program is not None, "Программа должна быть найдена для кандидата"
        assert program.campaign_program_id == program_id
        assert program.description == description

    async def test_find_by_candidate_id_not_found(self, campaign_repo: PostgresCampaignProgramRepository):
        """
        Если для кандидата с несуществующим candidate_id программа отсутствует — должен возвращаться None.
        """
        program = await campaign_repo.find_by_candidate_id(candidate_id=999999)
        assert program is None
