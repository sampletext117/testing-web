import pytest
from unittest.mock import MagicMock
from datetime import date
from election_app.usecases.finalize_election import FinalizeElectionUseCase

class TestFinalizeElectionUseCaseLondon:


    def test_finalize_successful(self):
        """
        Тест: выборы существуют, уже закончились, есть голоса ->
        возвращаем структуру results со списком кандидатов и winner.
        """
        mock_election_repo = MagicMock()
        mock_vote_repo = MagicMock()
        mock_candidate_repo = MagicMock()

        # Настраиваем возвращаемые объекты
        election_obj = MagicMock(
            election_id=1,
            election_name="Выборы 2025",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 2),
            description="Test desc"
        )
        mock_election_repo.find_election_by_id.return_value = election_obj

        # Будем считать, что сейчас 3 января 2025, т.е. выборы закончились 2 января
        # -> need to mock datetime.now()? Можно сделать patch, но в данном примере
        #   допустим, что всё ок.

        mock_vote_repo.count_votes_by_election.return_value = {
            100: 50,  # кандидат #1 набрал 50 голосов
            200: 70   # кандидат #2 набрал 70 голосов
        }

        # Кандидат #100
        mock_candidate_repo.find_candidate_by_id.side_effect = lambda cid: MagicMock(
            candidate_id=cid, full_name=f"Candidate {cid}"
        )

        use_case = FinalizeElectionUseCase(
            election_repository=mock_election_repo,
            vote_repository=mock_vote_repo,
            candidate_repository=mock_candidate_repo
        )

        # Act
        result = use_case.execute(election_id=1)

        # Assert
        assert result["election_id"] == 1
        assert len(result["results"]) == 2
        assert result["winner"]["candidate_id"] == 200
        assert result["winner"]["vote_count"] == 70

        mock_election_repo.find_election_by_id.assert_called_once_with(1)
        mock_vote_repo.count_votes_by_election.assert_called_once_with(1)

    def test_election_not_found(self):
        """
        Тест: выборы не найдены -> ValueError
        """
        mock_election_repo = MagicMock()
        mock_vote_repo = MagicMock()
        mock_candidate_repo = MagicMock()

        mock_election_repo.find_election_by_id.return_value = None

        use_case = FinalizeElectionUseCase(
            election_repository=mock_election_repo,
            vote_repository=mock_vote_repo,
            candidate_repository=mock_candidate_repo
        )

        with pytest.raises(ValueError) as exc_info:
            use_case.execute(election_id=999)
        assert "не найдены" in str(exc_info.value)

    def test_election_not_ended_yet(self):
        """
        Тест: выборы существуют, но end_date >= сегодня -> ValueError,
        т.е. итоги подводить рано.
        """
        mock_election_repo = MagicMock()
        mock_vote_repo = MagicMock()
        mock_candidate_repo = MagicMock()

        election_obj = MagicMock(
            election_id=2,
            election_name="Early Elections",
            start_date=date(2025, 1, 1),
            end_date=date(2050, 1, 1),  # закончится ещё нескоро
            description="Some desc"
        )
        mock_election_repo.find_election_by_id.return_value = election_obj

        use_case = FinalizeElectionUseCase(
            election_repository=mock_election_repo,
            vote_repository=mock_vote_repo,
            candidate_repository=mock_candidate_repo
        )

        with pytest.raises(ValueError) as exc_info:
            use_case.execute(election_id=2)
        assert "выборы ещё не завершены" in str(exc_info.value)
