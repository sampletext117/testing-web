import pytest
from unittest.mock import AsyncMock
from datetime import date

from election_app.usecases.register_voter import RegisterVoterUseCase

@pytest.mark.asyncio
class TestRegisterVoterUseCaseLondon:

    async def test_successful_registration(self):
        # Arrange
        mock_voter_repo = AsyncMock()
        mock_passport_repo = AsyncMock()

        # - find_by_number(...) вернёт None, паспорт свободен
        mock_passport_repo.find_by_number.return_value = None
        # - create_passport(...) вернёт 10
        mock_passport_repo.create_passport.return_value = 10
        # - create_voter(...) вернёт 55
        mock_voter_repo.create_voter.return_value = 55

        use_case = RegisterVoterUseCase(
            voter_repository=mock_voter_repo,
            passport_repository=mock_passport_repo
        )

        # Act
        voter_id = await use_case.execute(
            full_name="Mocked User",
            birth_date=date(1990,1,1),
            passport_number="MOCK 123",
            issued_by="MockOrg",
            issue_date=date(2010,1,1),
            country="Россия"
        )

        # Assert
        assert voter_id == 55
        mock_passport_repo.find_by_number.assert_awaited_once_with("MOCK 123")
        mock_passport_repo.create_passport.assert_awaited_once()
        mock_voter_repo.create_voter.assert_awaited_once()

    async def test_passport_already_exists(self):
        # Arrange
        mock_voter_repo = AsyncMock()
        mock_passport_repo = AsyncMock()

        # find_by_number(...) вернёт "что-то не None" => уже существует
        mock_passport_repo.find_by_number.return_value = True

        use_case = RegisterVoterUseCase(mock_voter_repo, mock_passport_repo)

        # Act / Assert
        with pytest.raises(ValueError) as exc_info:
            await use_case.execute(
                full_name="Test User",
                birth_date=date(1990,1,1),
                passport_number="EXISTS 001",
                issued_by="SomeOrg",
                issue_date=date(2010,1,1),
                country="Россия"
            )
        assert "Паспорт с таким номером уже зарегистрирован" in str(exc_info.value)

    async def test_country_not_russia(self):
        # Arrange
        mock_voter_repo = AsyncMock()
        mock_passport_repo = AsyncMock()
        # Паспорт свободен
        mock_passport_repo.find_by_number.return_value = None

        use_case = RegisterVoterUseCase(mock_voter_repo, mock_passport_repo)

        # Act / Assert
        with pytest.raises(ValueError) as exc_info:
            await use_case.execute(
                full_name="John Smith",
                birth_date=date(1990,1,1),
                passport_number="USA 123",
                issued_by="US Org",
                issue_date=date(2010,1,1),
                country="USA"
            )
        assert "Только граждане РФ" in str(exc_info.value)
