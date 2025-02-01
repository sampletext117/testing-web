import pytest
import pytest_asyncio
import time
from datetime import date

from election_app.data_access.voter_repository import PostgresVoterRepository
from election_app.data_access.candidate_repository import PostgresCandidateRepository
from election_app.data_access.election_repository import PostgresElectionRepository
from election_app.data_access.vote_repository import PostgresVoteRepository
from election_app.data_access.passport_repository import PostgresPassportRepository
from election_app.usecases.vote import VoteUseCase

# Фикстура для создания тестового избирателя
@pytest_asyncio.fixture
async def test_voter_id() -> int:
    passport_repo = PostgresPassportRepository()
    unique_num = int(time.time() * 1000000)
    passport_number = f"TEST-VOTE-VOTER-PASSPORT-{unique_num}"
    pid = await passport_repo.create_passport(
        passport_number=passport_number,
        issued_by="Voter Issuer",
        issue_date=date(2010, 1, 1),
        country="Россия"
    )
    voter_repo = PostgresVoterRepository()
    vid = await voter_repo.create_voter(
        full_name="Test Voter",
        birth_date=date(1990, 1, 1),
        passport_id=pid
    )
    return vid

# Фикстура для создания тестового кандидата
@pytest_asyncio.fixture
async def test_candidate_id() -> int:
    passport_repo = PostgresPassportRepository()
    unique_num = int(time.time() * 1000000) + 1
    passport_number = f"TEST-VOTE-CANDIDATE-PASSPORT-{unique_num}"
    pid = await passport_repo.create_passport(
        passport_number=passport_number,
        issued_by="Candidate Issuer",
        issue_date=date(2010, 1, 1),
        country="Россия"
    )
    candidate_repo = PostgresCandidateRepository()
    cid = await candidate_repo.create_candidate(
        full_name="Test Candidate",
        birth_date=date(1980, 1, 1),
        passport_id=pid
    )
    return cid

# Фикстура для создания тестовых выборов (активных, чтобы голосование было допустимо)
@pytest_asyncio.fixture
async def test_election_id() -> int:
    election_repo = PostgresElectionRepository()
    today = date.today()
    # Устанавливаем даты так, чтобы сегодня находился в промежутке выборов
    start_date = today
    # Для простоты, end_date – завтра (при условии, что тест запустится в тот же день)
    end_date = today.replace(day=today.day + 1 if today.day < 28 else today.day)
    eid = await election_repo.create_election(
        election_name="Test Election for Vote",
        start_date=start_date,
        end_date=end_date,
        description="Election for vote integration test"
    )
    return eid

# Фикстура для создания юзкейса голосования
@pytest_asyncio.fixture
async def vote_use_case() -> VoteUseCase:
    voter_repo = PostgresVoterRepository()
    candidate_repo = PostgresCandidateRepository()
    election_repo = PostgresElectionRepository()
    vote_repo = PostgresVoteRepository()
    return VoteUseCase(
        voter_repository=voter_repo,
        candidate_repository=candidate_repo,
        election_repository=election_repo,
        vote_repository=vote_repo
    )

@pytest.mark.asyncio
class TestVoteUseCaseIntegration:
    async def test_successful_vote(self, vote_use_case: VoteUseCase, test_voter_id: int, test_candidate_id: int, test_election_id: int):
        """
        Проверяем успешное голосование.
        """
        vote_id = await vote_use_case.execute(
            voter_id=test_voter_id,
            candidate_id=test_candidate_id,
            election_id=test_election_id
        )
        assert vote_id > 0, "Должны получить валидный vote_id"

    async def test_already_voted_error(self, vote_use_case: VoteUseCase, test_voter_id: int, test_candidate_id: int, test_election_id: int):
        """
        Проверяем, что повторное голосование для одних и тех же выборов вызывает ошибку.
        """
        first_vote = await vote_use_case.execute(
            voter_id=test_voter_id,
            candidate_id=test_candidate_id,
            election_id=test_election_id
        )
        assert first_vote > 0

        with pytest.raises(ValueError) as exc_info:
            await vote_use_case.execute(
                voter_id=test_voter_id,
                candidate_id=test_candidate_id,
                election_id=test_election_id
            )
        assert "уже голосовал" in str(exc_info.value).lower()

    async def test_election_not_found_error(self, vote_use_case: VoteUseCase, test_voter_id: int, test_candidate_id: int):
        """
        Проверяем, что попытка голосовать в несуществующих выборах вызывает ошибку.
        """
        non_existing_election = 999999  # предполагается, что такой election_id не существует
        with pytest.raises(ValueError) as exc_info:
            await vote_use_case.execute(
                voter_id=test_voter_id,
                candidate_id=test_candidate_id,
                election_id=non_existing_election
            )
        assert "выборы" in str(exc_info.value).lower()
