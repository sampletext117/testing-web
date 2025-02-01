import pytest
import pytest_asyncio
from datetime import date, timedelta

from election_app.data_access.election_repository import PostgresElectionRepository
from election_app.data_access.vote_repository import PostgresVoteRepository
from election_app.data_access.candidate_repository import PostgresCandidateRepository
from election_app.usecases.finalize_election import FinalizeElectionUseCase

@pytest_asyncio.fixture
async def finished_election_id() -> int:
    """
    Фикстура, создающая выборы, которые уже закончились (end_date < today).
    """
    election_repo = PostgresElectionRepository()
    today = date.today()
    start_date = today - timedelta(days=10)
    end_date = today - timedelta(days=1)
    eid = await election_repo.create_election(
        election_name="Finished Election",
        start_date=start_date,
        end_date=end_date,
        description="Test finished election"
    )
    return eid

@pytest_asyncio.fixture
async def finalize_use_case() -> FinalizeElectionUseCase:
    election_repo = PostgresElectionRepository()
    vote_repo = PostgresVoteRepository()
    candidate_repo = PostgresCandidateRepository()
    return FinalizeElectionUseCase(
        election_repository=election_repo,
        vote_repository=vote_repo,
        candidate_repository=candidate_repo
    )

@pytest.mark.asyncio
class TestFinalizeElectionUseCaseIntegration:
    async def test_finalize_successful(self, finished_election_id: int, finalize_use_case: FinalizeElectionUseCase):
        """
        Тест: выборы уже закончились, и есть голоса → успешное подведение итогов.
        """
        # Здесь для демонстрации можно добавить тестовые голоса,
        # но если таблица голосов пуста, то итог должен обрабатывать ситуацию.
        result = await finalize_use_case.execute(finished_election_id)
        assert result["election_id"] == finished_election_id

        # Если ключ totalVotes отсутствует, вычисляем сумму голосов из results.
        total_votes = result.get("totalVotes")
        if total_votes is None:
            total_votes = sum(item.get("vote_count", 0) for item in result.get("results", []))
        if total_votes == 0:
            assert result["winner"] is None or result["winner"].get("candidate_id") is None
        else:
            assert result["winner"] is not None

    async def test_finalize_election_not_finished_error(self):
        """
        Проверяем, что попытка финализировать выборы, которые ещё не закончились, вызывает ошибку.
        """
        election_repo = PostgresElectionRepository()
        today = date.today()
        start_date = today
        end_date = today + timedelta(days=5)  # Выборы ещё не закончились
        eid = await election_repo.create_election(
            election_name="Future Election",
            start_date=start_date,
            end_date=end_date,
            description="Future test election"
        )
        from election_app.usecases.finalize_election import FinalizeElectionUseCase
        finalize_use_case = FinalizeElectionUseCase(
            election_repository=election_repo,
            vote_repository=PostgresVoteRepository(),
            candidate_repository=PostgresCandidateRepository()
        )
        with pytest.raises(ValueError) as exc_info:
            await finalize_use_case.execute(eid)
        assert "ещё не завершены" in str(exc_info.value).lower()
