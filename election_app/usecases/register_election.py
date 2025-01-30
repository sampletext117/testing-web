from datetime import date
from typing import Optional


class RegisterElectionUseCase:
    def __init__(self, election_repository):
        """
        :param election_repository: Интерфейс репозитория IElectionRepository
        """
        self.election_repo = election_repository

    def execute(
        self,
        election_name: str,
        start_date: date,
        end_date: date,
        description: Optional[str] = None
    ) -> int:
        """
        Регистрирует (создаёт) новые выборы в системе.
        Возвращает идентификатор созданных выборов (election_id).

        :param election_name: Название выборов
        :param start_date: Дата начала выборов
        :param end_date: Дата окончания выборов
        :param description: Дополнительное описание выборов (необязательно)
        """

        # 1. Проверка, что название выборов не пустое
        if not election_name.strip():
            raise ValueError("Название выборов не может быть пустым.")

        # 2. Проверка, что дата начала и окончания корректны
        if end_date < start_date:
            raise ValueError("Дата окончания выборов не может быть раньше даты начала.")

        # 3. (Опционально) Проверка, что выборы не заканчиваются «в прошлом» и т.п.
        #    Например, вы можете запретить создание выборов с end_date < сегодняшней датой.

        # 4. Создание (запись в БД)
        new_election_id = self.election_repo.create_election(
            election_name=election_name,
            start_date=start_date,
            end_date=end_date,
            description=description or ""
        )

        return new_election_id
