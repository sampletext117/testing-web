from abc import ABC, abstractmethod
from typing import Optional
from election_app.domain.entities.election import Election
from datetime import date


class IElectionRepository(ABC):

    @abstractmethod
    def create_election(
        self,
        election_name: str,
        start_date: date,
        end_date: date,
        description: str
    ) -> int:
        """
        Создаёт запись о выборах, возвращает election_id.
        """
        pass

    @abstractmethod
    def find_election_by_id(self, election_id: int) -> Optional[Election]:
        """
        Находит выборы по их ID, или None, если не найдены.
        """
        pass

    @abstractmethod
    def update_election_status(self, election_id: int, new_status: str) -> None:
        """
        (Опционально) Если есть столбец status в таблице election,
        можно обновлять статус (например, "FINISHED").
        """
        pass
