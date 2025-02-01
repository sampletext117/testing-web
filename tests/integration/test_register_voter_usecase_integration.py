import pytest
import pytest_asyncio
import time
from datetime import date

# Импортируем юзкейс регистрации избирателя
from election_app.usecases.register_voter import RegisterVoterUseCase
# Репозитории для избирателей и паспортов
from election_app.data_access.voter_repository import PostgresVoterRepository
from election_app.data_access.passport_repository import PostgresPassportRepository

@pytest_asyncio.fixture
async def voter_use_case() -> RegisterVoterUseCase:
    """
    Фикстура, создающая и возвращающая юзкейс регистрации избирателя,
    использующий реальные репозитории.
    """
    voter_repo = PostgresVoterRepository()
    passport_repo = PostgresPassportRepository()
    use_case = RegisterVoterUseCase(voter_repo, passport_repo)
    return use_case


@pytest.mark.asyncio
async def test_register_voter_success(voter_use_case: RegisterVoterUseCase):
    """
    Интеграционный тест для юзкейса регистрации избирателя.
    Проверяет, что при корректных данных возвращается валидный voter_id,
    а также (опционально) можно дополнительно проверить данные в БД.
    """
    # Генерируем уникальный номер паспорта для теста
    unique_num = int(time.time() * 1000000)
    passport_number = f"TEST-VOTER-PASSPORT-{unique_num}"

    full_name = "Test Voter"
    birth_date = date(1990, 1, 1)
    issued_by = "Test Issuer"
    issue_date = date(2010, 1, 1)
    country = "Россия"

    voter_id = await voter_use_case.execute(
        full_name=full_name,
        birth_date=birth_date,
        passport_number=passport_number,
        issued_by=issued_by,
        issue_date=issue_date,
        country=country
    )
    assert voter_id > 0, "Должны получить валидный voter_id"
