import pytest
import pytest_asyncio
import time
from datetime import date

from election_app.data_access.vote_repository import PostgresVoteRepository
from election_app.data_access.candidate_repository import PostgresCandidateRepository
from election_app.data_access.voter_repository import PostgresVoterRepository
from election_app.data_access.election_repository import PostgresElectionRepository
from election_app.data_access.passport_repository import PostgresPassportRepository
from election_app.domain.entities.vote import Vote


# Фикстура для создания уникального тестового паспорта
@pytest_asyncio.fixture
async def create_test_passport() -> int:
    passport_repo = PostgresPassportRepository()
    unique_num = int(time.time() * 1000000)
    passport_number = f"TEST-PASSPORT-{unique_num}"
    pid = await passport_repo.create_passport(
        passport_number=passport_number,
        issued_by="Test Issuer",
        issue_date=date(2010, 1, 1),
        country="Россия"
    )
    return pid


# Фикстура для создания тестового кандидата
@pytest_asyncio.fixture
async def test_candidate_id(create_test_passport: int) -> int:
    candidate_repo = PostgresCandidateRepository()
    cid = await candidate_repo.create_candidate(
        full_name="Test Candidate",
        birth_date=date(1980, 1, 1),
        passport_id=create_test_passport
    )
    return cid


# Фикстура для создания тестового избирателя
@pytest_asyncio.fixture
async def test_voter_id(create_test_passport: int) -> int:
    from election_app.data_access.voter_repository import PostgresVoterRepository
    voter_repo = PostgresVoterRepository()
    vid = await voter_repo.create_voter(
        full_name="Test Voter",
        birth_date=date(1990, 1, 1),
        passport_id=create_test_passport
    )
    return vid


# Фикстура для создания тестовых выборов
@pytest_asyncio.fixture
async def test_election_id() -> int:
    election_repo = PostgresElectionRepository()
    eid = await election_repo.create_election(
        election_name="Test Election",
        start_date=date(2025, 1, 1),
        end_date=date(2025, 1, 10),
        description="Test Election Desc"
    )
    return eid


@pytest_asyncio.fixture
async def vote_repo() -> PostgresVoteRepository:
    repo = PostgresVoteRepository()
    yield repo


@pytest.mark.asyncio
class TestVoteRepositoryIntegration:
    async def test_record_and_find_vote(self, vote_repo: PostgresVoteRepository, test_voter_id: int,
                                        test_candidate_id: int, test_election_id: int):
        # Записываем голос
        vote_id = await vote_repo.record_vote(
            voter_id=test_voter_id,
            candidate_id=test_candidate_id,
            election_id=test_election_id
        )
        assert vote_id > 0, "Должны получить валидный vote_id"

        # Ищем голос по vote_id
        vote = await vote_repo.find_vote_by_id(vote_id)
        assert vote is not None, "Голос должен быть найден"
        assert vote.vote_id == vote_id
        assert vote.voter_id == test_voter_id
        assert vote.candidate_id == test_candidate_id
        assert vote.election_id == test_election_id

    async def test_has_already_voted(self, vote_repo: PostgresVoteRepository, test_voter_id: int,
                                     test_candidate_id: int, test_election_id: int):
        # До голосования должно возвращаться False
        already = await vote_repo.has_already_voted(test_voter_id, test_election_id)
        assert already is False

        # Записываем голос
        await vote_repo.record_vote(
            voter_id=test_voter_id,
            candidate_id=test_candidate_id,
            election_id=test_election_id
        )
        # Теперь должно возвращаться True
        already = await vote_repo.has_already_voted(test_voter_id, test_election_id)
        assert already is True

    async def test_count_votes_by_election(self, vote_repo: PostgresVoteRepository, test_voter_id: int,
                                           test_candidate_id: int, test_election_id: int):
        # Для теста создадим два голоса за разных кандидатов.
        # Первый голос уже отдан для test_candidate_id.
        await vote_repo.record_vote(
            voter_id=test_voter_id,
            candidate_id=test_candidate_id,
            election_id=test_election_id
        )
        # Создаем второго кандидата
        from election_app.data_access.candidate_repository import PostgresCandidateRepository
        candidate_repo = PostgresCandidateRepository()
        passport_repo = PostgresPassportRepository()
        unique_num = int(time.time() * 1000000) + 1
        passport_number = f"TEST-PASSPORT-{unique_num}"
        pid2 = await passport_repo.create_passport(
            passport_number=passport_number,
            issued_by="Test Issuer",
            issue_date=date(2010, 1, 1),
            country="Россия"
        )
        candidate_id_2 = await candidate_repo.create_candidate(
            full_name="Second Candidate",
            birth_date=date(1985, 1, 1),
            passport_id=pid2
        )
        await vote_repo.record_vote(
            voter_id=test_voter_id,
            candidate_id=candidate_id_2,
            election_id=test_election_id
        )
        # Подсчитываем голоса для данного выбора
        votes_count = await vote_repo.count_votes_by_election(test_election_id)
        assert isinstance(votes_count, dict)
        assert votes_count.get(test_candidate_id) == 1
        assert votes_count.get(candidate_id_2) == 1

    async def test_list_votes_by_election(self, vote_repo: PostgresVoteRepository, test_voter_id: int,
                                          test_candidate_id: int, test_election_id: int):
        # Записываем голос для данного выбора
        vote_id = await vote_repo.record_vote(
            voter_id=test_voter_id,
            candidate_id=test_candidate_id,
            election_id=test_election_id
        )
        votes = await vote_repo.list_votes_by_election(test_election_id)
        vote_ids = [v.vote_id for v in votes]
        assert vote_id in vote_ids

    async def test_list_all_votes(self, vote_repo: PostgresVoteRepository, test_voter_id: int, test_candidate_id: int,
                                  test_election_id: int):
        # Создаем голос для test_election_id
        vote1 = await vote_repo.record_vote(
            voter_id=test_voter_id,
            candidate_id=test_candidate_id,
            election_id=test_election_id
        )
        # Создаем еще одни выборы
        from election_app.data_access.election_repository import PostgresElectionRepository
        election_repo = PostgresElectionRepository()
        new_election_id = await election_repo.create_election(
            election_name="Another Election",
            start_date=date(2025, 2, 1),
            end_date=date(2025, 2, 10),
            description="Another test election"
        )
        vote2 = await vote_repo.record_vote(
            voter_id=test_voter_id,
            candidate_id=test_candidate_id,
            election_id=new_election_id
        )
        all_votes = await vote_repo.list_all_votes()
        all_vote_ids = [v.vote_id for v in all_votes]
        assert vote1 in all_vote_ids
        assert vote2 in all_vote_ids
