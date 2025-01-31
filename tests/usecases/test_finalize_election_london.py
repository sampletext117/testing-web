import pytest
from unittest.mock import AsyncMock
from datetime import date, datetime

from election_app.usecases.finalize_election import FinalizeElectionUseCase


@pytest.mark.asyncio
class TestFinalizeElectionUseCaseLondon:

    async def test_finalize_successful(self):
        """
        Тест: выборы существуют, уже закончились, есть голоса ->
        возвращаем структуру results со списком кандидатов и winner.
        """
        mock_election_repo = AsyncMock()
        mock_vote_repo = AsyncMock()
        mock_candidate_repo = AsyncMock()

        # Настраиваем возвращаемые объекты:
        # Выборы с end_date < сегодня => "закончились"
        election_obj = AsyncMock(
            election_id=1,
            election_name="Выборы 2025",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 2),
            description="Test desc"
        )
        mock_election_repo.find_election_by_id.return_value = election_obj

        # Голоса по кандидатам (candidate_id -> count)
        mock_vote_repo.count_votes_by_election.return_value = {
            100: 50,
            200: 70
        }

        # Для разных candidate_id вернём кандидатов с разными именами
        async def mock_find_candidate_by_id(cid):
            # эмулируем объект-кандидат
            # (можно вернуть реальный Candidate, MagicMock или что-то подобное)
            c = AsyncMock()
            c.candidate_id = cid
            c.full_name = f"Candidate {cid}"
            return c

        mock_candidate_repo.find_candidate_by_id.side_effect = mock_find_candidate_by_id

        use_case = FinalizeElectionUseCase(
            election_repository=mock_election_repo,
            vote_repository=mock_vote_repo,
            candidate_repository=mock_candidate_repo
        )

        # Act
        result = await use_case.execute(election_id=1)

        # Assert
        assert result["election_id"] == 1
        assert len(result["results"]) == 2
        # Победитель - кандидат 200, у которого 70 голосов
        assert result["winner"]["candidate_id"] == 200
        assert result["winner"]["vote_count"] == 70

        mock_election_repo.find_election_by_id.assert_awaited_once_with(1)
        mock_vote_repo.count_votes_by_election.assert_awaited_once_with(1)
        # Для каждого cand_id (100, 200)  проверится find_candidate_by_id
        assert mock_candidate_repo.find_candidate_by_id.await_count == 2

    async def test_election_not_found(self):
        """
        Тест: выборы не найдены -> ValueError
        """
        mock_election_repo = AsyncMock()
        mock_vote_repo = AsyncMock()
        mock_candidate_repo = AsyncMock()

        # Не нашли выборы
        mock_election_repo.find_election_by_id.return_value = None

        use_case = FinalizeElectionUseCase(
            election_repository=mock_election_repo,
            vote_repository=mock_vote_repo,
            candidate_repository=mock_candidate_repo
        )

        with pytest.raises(ValueError) as exc_info:
            await use_case.execute(election_id=999)
        assert "не найдены" in str(exc_info.value)

    async def test_election_not_ended_yet(self):
        """
        Тест: выборы существуют, но end_date >= сегодня -> ValueError,
        т.е. итоги подводить рано.
        """
        mock_election_repo = AsyncMock()
        mock_vote_repo = AsyncMock()
        mock_candidate_repo = AsyncMock()

        # Выборы ещё не закончились
        election_obj = AsyncMock(
            election_id=2,
            election_name="Early Elections",
            start_date=date(2025, 1, 1),
            end_date=date(2050, 1, 1),
            description="Some desc"
        )
        mock_election_repo.find_election_by_id.return_value = election_obj

        use_case = FinalizeElectionUseCase(
            election_repository=mock_election_repo,
            vote_repository=mock_vote_repo,
            candidate_repository=mock_candidate_repo
        )

        with pytest.raises(ValueError) as exc_info:
            await use_case.execute(election_id=2)
        assert "ещё не завершены" in str(exc_info.value)
