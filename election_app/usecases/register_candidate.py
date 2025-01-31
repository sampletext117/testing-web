from datetime import date
from typing import Optional

def calculate_age(birth_date: date) -> int:
    today = date.today()
    years = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        years -= 1
    return years

class RegisterCandidateUseCase:
    def __init__(self, candidate_repository, passport_repository,
                 campaign_program_repository, candidate_account_repository):
        self.candidate_repo = candidate_repository
        self.passport_repo = passport_repository
        self.program_repo = campaign_program_repository
        self.account_repo = candidate_account_repository

    async def execute(
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

        age = calculate_age(birth_date)
        if age < 35:
            raise ValueError(f"Кандидат должен быть не младше 35 лет. Текущий возраст: {age}")

        if country.lower() != "россия":
            raise ValueError("Кандидат должен иметь гражданство РФ.")

        existing_passport = await self.passport_repo.find_by_number(passport_number)
        if existing_passport is not None:
            raise ValueError("Паспорт с таким номером уже зарегистрирован.")

        passport_id = await self.passport_repo.create_passport(
            passport_number=passport_number,
            issued_by=issued_by,
            issue_date=issue_date,
            country=country
        )

        candidate_id = await self.candidate_repo.create_candidate(
            full_name=full_name,
            birth_date=birth_date,
            passport_id=passport_id
        )

        program_id = await self.program_repo.create_program(
            candidate_id=candidate_id,
            description=program_description
        )

        account_id = await self.account_repo.create_account(
            candidate_id=candidate_id,
            balance=initial_balance
        )

        await self.candidate_repo.update_candidate_program_and_account(
            candidate_id=candidate_id,
            campaign_program_id=program_id,
            account_id=account_id
        )

        return candidate_id
