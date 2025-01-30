from datetime import date
from typing import Optional


def calculate_age(birth_date: date) -> int:
    today = date.today()
    years = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        years -= 1
    return years


class RegisterCandidateUseCase:
    def __init__(
        self,
        candidate_repository,          # ICandidateRepository
        passport_repository,           # IPassportRepository
        campaign_program_repository,   # ICampaignProgramRepository
        candidate_account_repository   # ICandidateAccountRepository
    ):
        """
        :param candidate_repository: Интерфейс репозитория для таблицы candidate
        :param passport_repository: Интерфейс репозитория для таблицы passport
        :param campaign_program_repository: Интерфейс для предвыборных программ
        :param candidate_account_repository: Интерфейс для счёта кандидата
        """
        self.candidate_repo = candidate_repository
        self.passport_repo = passport_repository
        self.program_repo = campaign_program_repository
        self.account_repo = candidate_account_repository

    def execute(
        self,
        full_name: str,
        birth_date: date,
        passport_number: str,
        issued_by: Optional[str],
        issue_date: Optional[date],
        country: str,
        program_description: str,
        initial_balance: float = 0.0
    ) -> int:
        """
        Регистрирует нового кандидата, создаёт запись в passport и candidate,
        а также в таблицах campaign_program и candidate_account.
        Возвращает идентификатор кандидата (candidate_id).
        """

        # 1. Проверка возраста. Допустим, кандидат должен быть >= 35 лет.
        age = calculate_age(birth_date)
        if age < 35:
            raise ValueError(
                f"Кандидат должен быть не младше 35 лет. Текущий возраст: {age}"
            )

        # 2. Проверка гражданства РФ
        if country.lower() != "россия":
            raise ValueError("Кандидат должен иметь гражданство РФ.")

        # 3. Проверить, что паспорт ещё не зарегистрирован
        existing_passport = self.passport_repo.find_by_number(passport_number)
        if existing_passport is not None:
            raise ValueError("Паспорт с таким номером уже зарегистрирован.")

        # 4. Создать запись в таблице passport
        passport_id = self.passport_repo.create_passport(
            passport_number=passport_number,
            issued_by=issued_by,
            issue_date=issue_date,
            country=country
        )

        # 5. Создать запись в таблице candidate
        candidate_id = self.candidate_repo.create_candidate(
            full_name=full_name,
            birth_date=birth_date,
            passport_id=passport_id
        )

        # 6. Создать предвыборную программу
        program_id = self.program_repo.create_program(
            candidate_id=candidate_id,
            description=program_description
        )

        # 7. Создать счёт кандидата
        account_id = self.account_repo.create_account(
            candidate_id=candidate_id,
            balance=initial_balance
        )

        # 8. Связать программу и счёт с записью candidate
        self.candidate_repo.update_candidate_program_and_account(
            candidate_id=candidate_id,
            campaign_program_id=program_id,
            account_id=account_id
        )

        return candidate_id
