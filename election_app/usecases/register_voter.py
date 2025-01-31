from datetime import date, datetime
from typing import Optional


def calculate_age(birth_date: date) -> int:
    """
    Утилитарная функция для вычисления полного возраста
    (упрощённо — разница по годам).
    """
    today = date.today()
    years = today.year - birth_date.year
    # Если дата рождения ещё не наступила в текущем году, вычитаем 1
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        years -= 1
    return years


class RegisterVoterUseCase:
    def __init__(
        self,
        voter_repository,    # IVoterRepository
        passport_repository  # IPassportRepository
    ):
        """
        :param voter_repository: Интерфейс репозитория для таблицы voter
        :param passport_repository: Интерфейс репозитория для таблицы passport
        """
        self.voter_repo = voter_repository
        self.passport_repo = passport_repository

    async def execute(
        self,
        full_name: str,
        birth_date: date,
        passport_number: str,
        issued_by: Optional[str],
        issue_date: Optional[date],
        country: str
    ) -> int:
        """
        Регистрирует нового избирателя, создаёт запись в таблицах passport и voter.
        Возвращает идентификатор нового избирателя (voter_id).
        """

        # 1. Проверка возраста (должен быть >= 18)
        age = calculate_age(birth_date)
        if age < 18:
            raise ValueError(
                f"Избиратель должен быть совершеннолетним (18+). Текущий возраст: {age}"
            )

        # 2. Проверка гражданства РФ
        if country.lower() != "россия":
            raise ValueError("Только граждане РФ могут быть избирателями.")

        # 3. Проверить, что паспорт ещё не зарегистрирован
        existing_passport = await self.passport_repo.find_by_number(passport_number)
        if existing_passport is not None:
            raise ValueError("Паспорт с таким номером уже зарегистрирован.")

        # 4. Создать запись в таблице passport
        passport_id = await self.passport_repo.create_passport(
            passport_number=passport_number,
            issued_by=issued_by,
            issue_date=issue_date,
            country=country
        )

        # 5. Создать запись в таблице voter
        voter_id = await self.voter_repo.create_voter(
            full_name=full_name,
            birth_date=birth_date,
            passport_id=passport_id
        )

        return voter_id
