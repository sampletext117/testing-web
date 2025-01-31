import pytest
from unittest.mock import AsyncMock
from datetime import date, datetime

from election_app.usecases.vote import VoteUseCase


@pytest.mark.asyncio
class TestVoteUseCaseLondon:

    async def test_successful_vote(self):
        # Arrange
        mock_voter_repo = AsyncMock()
        mock_candidate_repo = AsyncMock()
        mock_election_repo = AsyncMock()
        mock_vote_repo = AsyncMock()

        mock_voter_repo.find_voter_by_id.return_value = AsyncMock()
        mock_candidate_repo.find_candidate_by_id.return_value = AsyncMock()
        mock_election_repo.find_election_by_id.return_value = AsyncMock(
            election_id=1,
            start_date=date(2000, 1, 1),
            end_date=date(2050, 1, 10),
            election_name="Test election",
            description="Desc"
        )
        mock_vote_repo.has_already_voted.return_value = False
        mock_vote_repo.record_vote.return_value = 777

        use_case = VoteUseCase(
            voter_repository=mock_voter_repo,
            candidate_repository=mock_candidate_repo,
            election_repository=mock_election_repo,
            vote_repository=mock_vote_repo
        )

        # Act
        vote_id = await use_case.execute(
            voter_id=101, candidate_id=202, election_id=303
        )

        # Assert
        assert vote_id == 777
        mock_voter_repo.find_voter_by_id.assert_awaited_once_with(101)
        mock_candidate_repo.find_candidate_by_id.assert_awaited_once_with(202)
        mock_election_repo.find_election_by_id.assert_awaited_once_with(303)
        mock_vote_repo.has_already_voted.assert_awaited_once_with(101, 303)
        # Важно: метод record_vote вызывается с именованными аргументами
        # в коде use case? Если да, проверяйте именованно:
        mock_vote_repo.record_vote.assert_awaited_once_with(
            voter_id=101,
            candidate_id=202,
            election_id=303
        )

    async def test_election_not_found(self):
        mock_voter_repo = AsyncMock()
        mock_candidate_repo = AsyncMock()
        mock_election_repo = AsyncMock()
        mock_vote_repo = AsyncMock()

        # find_election_by_id вернёт None
        mock_election_repo.find_election_by_id.return_value = None

        use_case = VoteUseCase(
            voter_repository=mock_voter_repo,
            candidate_repository=mock_candidate_repo,
            election_repository=mock_election_repo,
            vote_repository=mock_vote_repo
        )

        with pytest.raises(ValueError) as exc_info:
            await use_case.execute(voter_id=1, candidate_id=2, election_id=999)
        assert "Выборы с id=999 не найдены" in str(exc_info.value)

    async def test_already_voted(self):
        mock_voter_repo = AsyncMock()
        mock_candidate_repo = AsyncMock()
        mock_election_repo = AsyncMock()
        mock_vote_repo = AsyncMock()

        mock_voter_repo.find_voter_by_id.return_value = AsyncMock()
        mock_candidate_repo.find_candidate_by_id.return_value = AsyncMock()
        mock_election_repo.find_election_by_id.return_value = AsyncMock(
            start_date=date(2000, 1, 1),
            end_date=date(2050, 1, 10)
        )
        mock_vote_repo.has_already_voted.return_value = True

        use_case = VoteUseCase(
            voter_repository=mock_voter_repo,
            candidate_repository=mock_candidate_repo,
            election_repository=mock_election_repo,
            vote_repository=mock_vote_repo
        )

        with pytest.raises(ValueError) as exc_info:
            await use_case.execute(voter_id=1, candidate_id=2, election_id=3)
        assert "Избиратель уже голосовал" in str(exc_info.value)
