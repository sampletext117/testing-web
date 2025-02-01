import pytest
import pytest_asyncio
import time
from datetime import date

from election_app.usecases.register_candidate import RegisterCandidateUseCase
from election_app.data_access.candidate_repository import PostgresCandidateRepository
from election_app.data_access.passport_repository import PostgresPassportRepository
from election_app.data_access.campaign_program_repository import PostgresCampaignProgramRepository
from election_app.data_access.candidate_account_repository import PostgresCandidateAccountRepository

@pytest_asyncio.fixture
async def candidate_use_case() -> RegisterCandidateUseCase:
    """
    Фикстура, создающая и возвращающая юзкейс регистрации кандидата,
    использующий реальные репозитории.
    """
    candidate_repo = PostgresCandidateRepository()
    passport_repo = PostgresPassportRepository()
    program_repo = PostgresCampaignProgramRepository()
    account_repo = PostgresCandidateAccountRepository()
    use_case = RegisterCandidateUseCase(
        candidate_repository=candidate_repo,
        passport_repository=passport_repo,
        campaign_program_repository=program_repo,
        candidate_account_repository=account_repo
    )
    return use_case


@pytest.mark.asyncio
async def test_register_candidate_success(candidate_use_case: RegisterCandidateUseCase):
    """
    Интеграционный тест для юзкейса регистрации кандидата.
    Проверяет, что при корректных входных данных возвращается валидный candidate_id.
    """
    unique_num = int(time.time() * 1000000)
    passport_number = f"TEST-CANDIDATE-PASSPORT-{unique_num}"

    full_name = "Test Candidate"
    birth_date = date(1970, 1, 1)
    issued_by = "Test Issuer"
    issue_date = date(2000, 1, 1)
    country = "Россия"
    program_description = "Test campaign program"
    initial_balance = 1000.0

    candidate_id = await candidate_use_case.execute(
        full_name=full_name,
        birth_date=birth_date,
        passport_number=passport_number,
        issued_by=issued_by,
        issue_date=issue_date,
        country=country,
        program_description=program_description,
        initial_balance=initial_balance
    )
    assert candidate_id > 0, "Должны получить валидный candidate_id"
