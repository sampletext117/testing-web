import pytest
from unittest.mock import MagicMock
from datetime import date

from election_app.usecases.register_voter import RegisterVoterUseCase

class TestRegisterVoterUseCaseLondon:
    def test_successful_registration(self):
        # Arrange
        mock_voter_repo = MagicMock()
        mock_passport_repo = MagicMock()

        # Настраиваем "поведение" моков:
        # - find_by_number(...) вернёт None, значит паспорт свободен
        # - create_passport(...) вернёт 10 (например)
        mock_passport_repo.find_by_number.return_value = None
        mock_passport_repo.create_passport.return_value = 10

        # - create_voter(...) вернёт 55 (например)
        mock_voter_repo.create_voter.return_value = 55

        use_case = RegisterVoterUseCase(
            voter_repository=mock_voter_repo,
            passport_repository=mock_passport_repo
        )

        # Act
        voter_id = use_case.execute(
            full_name="Mocked User",
            birth_date=date(1990,1,1),
            passport_number="MOCK 123",
            issued_by="MockOrg",
            issue_date=date(2010,1,1),
            country="Россия"
        )

        # Assert
        assert voter_id == 55

        # Дополнительно проверяем, что методы были вызваны с нужными аргументами
        mock_passport_repo.find_by_number.assert_called_once_with("MOCK 123")
        mock_passport_repo.create_passport.assert_called_once()
        mock_voter_repo.create_voter.assert_called_once()

    def test_passport_already_exists(self):
        # Arrange
        mock_voter_repo = MagicMock()
        mock_passport_repo = MagicMock()

        # find_by_number(...) вернёт "что-то не None" => уже существует
        mock_passport_repo.find_by_number.return_value = True

        use_case = RegisterVoterUseCase(mock_voter_repo, mock_passport_repo)

        # Act / Assert
        with pytest.raises(ValueError) as exc_info:
            use_case.execute(
                full_name="Test User",
                birth_date=date(1990,1,1),
                passport_number="EXISTS 001",
                issued_by="SomeOrg",
                issue_date=date(2010,1,1),
                country="Россия"
            )
        assert "Паспорт с таким номером уже зарегистрирован" in str(exc_info.value)

    def test_country_not_russia(self):
        # Arrange
        mock_voter_repo = MagicMock()
        mock_passport_repo = MagicMock()
        mock_passport_repo.find_by_number.return_value = None  # Паспорт свободен

        use_case = RegisterVoterUseCase(mock_voter_repo, mock_passport_repo)

        # Act / Assert
        with pytest.raises(ValueError) as exc_info:
            use_case.execute(
                full_name="John Smith",
                birth_date=date(1990,1,1),
                passport_number="USA 123",
                issued_by="US Org",
                issue_date=date(2010,1,1),
                country="USA"
            )
        assert "Только граждане РФ" in str(exc_info.value)
