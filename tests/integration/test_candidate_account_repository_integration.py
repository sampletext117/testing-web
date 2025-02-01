import pytest
import pytest_asyncio
import time
from datetime import date

from election_app.data_access.candidate_account_repository import PostgresCandidateAccountRepository
from election_app.data_access.candidate_repository import PostgresCandidateRepository
from election_app.data_access.passport_repository import PostgresPassportRepository
from election_app.domain.entities.candidate_account import CandidateAccount

@pytest_asyncio.fixture
async def account_repo() -> PostgresCandidateAccountRepository:
    repo = PostgresCandidateAccountRepository()
    yield repo
    # (Опционально: очистка таблицы candidate_account)

@pytest_asyncio.fixture
async def existing_candidate_id() -> int:
    """
    Фикстура, создающая тестового кандидата и возвращающая его candidate_id.
    """
    candidate_repo = PostgresCandidateRepository()
    passport_repo = PostgresPassportRepository()
    unique_num = int(time.time() * 1000000)
    passport_number = f"TEST-PASSPORT-{unique_num}"
    pid = await passport_repo.create_passport(
        passport_number=passport_number,
        issued_by="Test Issuer",
        issue_date=date(2010, 1, 1),
        country="Россия"
    )
    cid = await candidate_repo.create_candidate(
        full_name="Account Test Candidate",
        birth_date=date(1980, 1, 1),
        passport_id=pid
    )
    return cid

@pytest.mark.asyncio
class TestCandidateAccountRepositoryIntegration:
    async def test_create_and_find_account(self, account_repo: PostgresCandidateAccountRepository, existing_candidate_id: int):
        """
        Проверяем, что можем создать счёт кандидата и найти его по candidate_id.
        """
        candidate_id = existing_candidate_id
        initial_balance = 1000.0
        account_id = await account_repo.create_account(candidate_id=candidate_id, balance=initial_balance)
        assert account_id > 0, "Должны получить валидный account_id"

        account = await account_repo.find_by_candidate_id(candidate_id=candidate_id)
        assert account is not None, "Счёт должен быть найден для кандидата"
        assert account.account_id == account_id
        # Используем pytest.approx для сравнения числовых значений
        assert float(account.balance) == pytest.approx(initial_balance)

    async def test_update_balance(self, account_repo: PostgresCandidateAccountRepository, existing_candidate_id: int):
        """
        Проверяем обновление баланса: создаем счёт для кандидата, обновляем баланс и проверяем изменения.
        """
        candidate_id = existing_candidate_id
        initial_balance = 1500.0
        new_balance = 2000.0

        account_id = await account_repo.create_account(candidate_id=candidate_id, balance=initial_balance)
        assert account_id > 0, "Должны получить валидный account_id"

        # Обновляем баланс
        await account_repo.update_balance(account_id=account_id, new_balance=new_balance)

        # Проверяем изменения
        account = await account_repo.find_by_candidate_id(candidate_id=candidate_id)
        assert account is not None, "Счёт должен быть найден после обновления"
        assert float(account.balance) == pytest.approx(new_balance)
        assert account.last_transaction_date is not None, "Дата последней транзакции должна быть установлена"
