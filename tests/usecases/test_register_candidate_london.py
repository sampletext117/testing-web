import pytest
from unittest.mock import MagicMock
from datetime import date
from election_app.usecases.register_candidate import RegisterCandidateUseCase


class TestRegisterCandidateUseCaseLondon:

    def test_successful_candidate_registration(self):
        # Arrange
        mock_candidate_repo = MagicMock()
        mock_passport_repo = MagicMock()
        mock_program_repo = MagicMock()
        mock_account_repo = MagicMock()

        # Настраиваем "поведение" репозиториев
        #   find_by_number -> возвращает None, т.е. паспорт не занят
        mock_passport_repo.find_by_number.return_value = None
        #   create_passport -> вернём 100
        mock_passport_repo.create_passport.return_value = 100
        #   create_candidate -> вернём 10 (candidate_id)
        mock_candidate_repo.create_candidate.return_value = 10
        #   create_program -> вернём 200
        mock_program_repo.create_program.return_value = 200
        #   create_account -> вернём 300
        mock_account_repo.create_account.return_value = 300

        use_case = RegisterCandidateUseCase(
            candidate_repository=mock_candidate_repo,
            passport_repository=mock_passport_repo,
            campaign_program_repository=mock_program_repo,
            candidate_account_repository=mock_account_repo
        )

        # Act
        candidate_id = use_case.execute(
            full_name="Петров Петр",
            birth_date=date(1980, 1, 1),
            passport_number="CAND 123",
            issued_by="УФМС",
            issue_date=date(2000, 1, 1),
            country="Россия",
            program_description="Моя программа",
            initial_balance=1000.0
        )

        # Assert
        assert candidate_id == 10
        mock_passport_repo.find_by_number.assert_called_once_with("CAND 123")
        mock_passport_repo.create_passport.assert_called_once()
        mock_candidate_repo.create_candidate.assert_called_once()
        mock_candidate_repo.update_candidate_program_and_account.assert_called_once_with(
            candidate_id=10, campaign_program_id=200, account_id=300
        )

    def test_candidate_under_35(self):
        """
        Тест: кандидат младше 35 -> ValueError
        """
        mock_candidate_repo = MagicMock()
        mock_passport_repo = MagicMock()
        mock_program_repo = MagicMock()
        mock_account_repo = MagicMock()

        use_case = RegisterCandidateUseCase(
            mock_candidate_repo,
            mock_passport_repo,
            mock_program_repo,
            mock_account_repo
        )

        with pytest.raises(ValueError) as exc_info:
            use_case.execute(
                full_name="Сидоров Молодой",
                birth_date=date(1995, 1, 1),  # ему около 28
                passport_number="CAND 555",
                issued_by="УФМС",
                issue_date=date(2010, 1, 1),
                country="Россия",
                program_description="Программа",
                initial_balance=500.0
            )
        assert "не младше 35 лет" in str(exc_info.value)

    def test_candidate_not_russian(self):
        """
        Тест: страна != "Россия" -> ValueError
        """
        mock_candidate_repo = MagicMock()
        mock_passport_repo = MagicMock()
        mock_program_repo = MagicMock()
        mock_account_repo = MagicMock()

        use_case = RegisterCandidateUseCase(
            mock_candidate_repo,
            mock_passport_repo,
            mock_program_repo,
            mock_account_repo
        )

        with pytest.raises(ValueError) as exc_info:
            use_case.execute(
                full_name="Mr. John",
                birth_date=date(1970, 5, 20),
                passport_number="FOREIGN 001",
                issued_by="ForeignOrg",
                issue_date=date(1990, 6, 1),
                country="USA",
                program_description="Some program",
                initial_balance=100.0
            )
        assert "гражданство РФ" in str(exc_info.value)
