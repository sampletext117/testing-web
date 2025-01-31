import pytest
from datetime import date

from election_app.usecases.register_voter import RegisterVoterUseCase

from election_app.domain.repositories.ivoter_repository import IVoterRepository
from election_app.domain.repositories.ipassport_repository import IPassportRepository
from election_app.domain.entities.voter import Voter
from election_app.domain.entities.passport import Passport

@pytest.mark.asyncio
class StubPassportRepository(IPassportRepository):
    """
    Асинхронная версия stub-репозитория для паспортов, хранящего всё в памяти.
    """
    def __init__(self):
        self.passports = {}
        self.next_id = 1

    async def create_passport(self, passport_number, issued_by, issue_date, country) -> int:
        pid = self.next_id
        self.next_id += 1
        self.passports[pid] = Passport(
            passport_id=pid,
            passport_number=passport_number,
            issued_by=issued_by,
            issue_date=issue_date,
            country=country
        )
        return pid

    async def find_by_number(self, passport_number):
        for p in self.passports.values():
            if p.passport_number == passport_number:
                return p
        return None

    async def find_by_id(self, passport_id):
        return self.passports.get(passport_id)

@pytest.mark.asyncio
class StubVoterRepository(IVoterRepository):
    """
    Асинхронная версия stub-репозитория для избирателей, хранящего всё в памяти.
    """
    def __init__(self):
        self.voters = {}
        self.next_id = 1

    async def create_voter(self, full_name, birth_date, passport_id) -> int:
        vid = self.next_id
        self.next_id += 1
        new_voter = Voter(
            voter_id=vid,
            full_name=full_name,
            birth_date=birth_date,
            passport_id=passport_id,
            created_at=None
        )
        self.voters[vid] = new_voter
        return vid

    async def find_voter_by_id(self, voter_id):
        return self.voters.get(voter_id)

    async def find_by_passport_id(self, passport_id):
        for v in self.voters.values():
            if v.passport_id == passport_id:
                return v
        return None


@pytest.fixture
def stub_repositories():
    """
    Pytest-фикстура, возвращающая экземпляры асинхронных stub-репозиториев.
    """
    return {
        "passport_repo": StubPassportRepository(),
        "voter_repo": StubVoterRepository()
    }

@pytest.mark.asyncio
class TestRegisterVoterUseCaseClassic:
    """
    Классический тест (classic approach), где мы используем асинхронные stub-репозитории,
    не мокая методы (никаких MagicMock).
    """

    async def test_successful_registration(self, stub_repositories):
        """
        Arrange: Создаём use case + stub-репозитории
        Act: Регистрируем нового избирателя (возраст >=18, гражданство РФ)
        Assert: Проверяем, что вернулся корректный voter_id и данные записались
        """
        use_case = RegisterVoterUseCase(
            voter_repository=stub_repositories["voter_repo"],
            passport_repository=stub_repositories["passport_repo"]
        )

        voter_id = await use_case.execute(
            full_name="Иванов Иван",
            birth_date=date(1990, 5, 20),
            passport_number="1234 567890",
            issued_by="ОВД",
            issue_date=date(2010, 2, 15),
            country="Россия"
        )

        assert voter_id == 1  # так как stub генерирует с 1
        created_voter = await stub_repositories["voter_repo"].find_voter_by_id(1)
        assert created_voter is not None
        assert created_voter.full_name == "Иванов Иван"

    async def test_registration_under_18(self, stub_repositories):
        """
        Проверяем, что при возрасте < 18 выбрасывается ValueError.
        """
        use_case = RegisterVoterUseCase(
            voter_repository=stub_repositories["voter_repo"],
            passport_repository=stub_repositories["passport_repo"]
        )

        with pytest.raises(ValueError) as exc_info:
            await use_case.execute(
                full_name="Петров Петр",
                birth_date=date(2010, 1, 1),  # Ему 13 лет
                passport_number="9999 888888",
                issued_by=None,
                issue_date=None,
                country="Россия"
            )
        assert "совершеннолетним" in str(exc_info.value)

    async def test_registration_non_russian(self, stub_repositories):
        """
        Проверяем, что если country != 'Россия', выбрасываем ValueError.
        """
        use_case = RegisterVoterUseCase(
            voter_repository=stub_repositories["voter_repo"],
            passport_repository=stub_repositories["passport_repo"]
        )

        with pytest.raises(ValueError) as exc_info:
            await use_case.execute(
                full_name="John Smith",
                birth_date=date(1990, 5, 20),
                passport_number="1111 222222",
                issued_by="US Org",
                issue_date=date(2015, 1, 1),
                country="USA"
            )
        assert "Только граждане РФ" in str(exc_info.value)
