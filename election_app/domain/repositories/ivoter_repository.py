from abc import ABC, abstractmethod
from typing import Optional
from datetime import date
from election_app.domain.entities.voter import Voter


class IVoterRepository(ABC):

    @abstractmethod
    def create_voter(
        self,
        full_name: str,
        birth_date: date,
        passport_id: int
    ) -> int:
        """
        Создаёт нового избирателя, возвращает voter_id.
        """
        pass

    @abstractmethod
    def find_voter_by_id(self, voter_id: int) -> Optional[Voter]:
        """
        Возвращает избирателя по его ID или None, если не найден.
        """
        pass

    @abstractmethod
    def find_by_passport_id(self, passport_id: int) -> Optional[Voter]:
        """
        Возвращает избирателя по passport_id, или None, если не найден.
        """
        pass
