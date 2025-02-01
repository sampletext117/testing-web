import pytest
import pytest_asyncio
from datetime import date

from election_app.usecases.register_election import RegisterElectionUseCase
from election_app.data_access.election_repository import PostgresElectionRepository


@pytest_asyncio.fixture
async def register_election_use_case() -> RegisterElectionUseCase:
    election_repo = PostgresElectionRepository()
    return RegisterElectionUseCase(election_repo)


@pytest.mark.asyncio
async def test_register_election_success(register_election_use_case: RegisterElectionUseCase):
    election_name = "Integration Test Election"
    start_date = date(2025, 6, 1)
    end_date = date(2025, 6, 10)
    description = "Election created by integration test"

    eid = await register_election_use_case.execute(
        election_name=election_name,
        start_date=start_date,
        end_date=end_date,
        description=description
    )
    assert eid > 0, "Должны получить валидный election_id"

    # Дополнительная проверка: данные должны быть сохранены в БД
    from election_app.data_access.election_repository import PostgresElectionRepository
    election_repo = PostgresElectionRepository()
    election = await election_repo.find_election_by_id(eid)
    assert election is not None, "Выборы должны быть найдены"
    assert election.election_name == election_name
    assert election.start_date == start_date
    assert election.end_date == end_date
    assert election.description == description


@pytest.mark.asyncio
async def test_register_election_invalid_dates(register_election_use_case: RegisterElectionUseCase):
    """
    Проверяем, что попытка создать выборы с end_date раньше start_date вызывает ошибку.
    """
    election_name = "Invalid Election"
    start_date = date(2025, 7, 10)
    end_date = date(2025, 7, 1)  # Неверно: end_date раньше start_date
    description = "This election should fail"

    with pytest.raises(ValueError) as exc_info:
        await register_election_use_case.execute(
            election_name=election_name,
            start_date=start_date,
            end_date=end_date,
            description=description
        )
    assert "не может быть раньше" in str(exc_info.value).lower()
