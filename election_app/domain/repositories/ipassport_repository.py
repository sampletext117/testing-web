from abc import ABC, abstractmethod
from typing import Optional
from election_app.domain.entities.passport import Passport
from datetime import date


class IPassportRepository(ABC):

    @abstractmethod
    def create_passport(
        self,
        passport_number: str,
        issued_by: Optional[str],
        issue_date: Optional[date],
        country: str
    ) -> int:
        """
        Создаёт запись в таблице passport, возвращает passport_id.
        """
        pass

    @abstractmethod
    def find_by_number(self, passport_number: str) -> Optional[Passport]:
        """
        Ищет паспорт по номеру, возвращает объект Passport или None.
        """
        pass

    @abstractmethod
    def find_by_id(self, passport_id: int) -> Optional[Passport]:
        """
        Ищет паспорт по ID, возвращает объект Passport или None.
        """
        pass
