from abc import ABC, abstractmethod
from typing import Optional
from datetime import date
from election_app.domain.entities.candidate import Candidate


class ICandidateRepository(ABC):

    @abstractmethod
    def create_candidate(
        self,
        full_name: str,
        birth_date: date,
        passport_id: int
    ) -> int:
        """
        Создаёт запись о кандидате, возвращает candidate_id.
        """
        pass

    @abstractmethod
    def update_candidate_program_and_account(
        self,
        candidate_id: int,
        campaign_program_id: int,
        account_id: int
    ) -> None:
        """
        Обновляет поля campaign_program_id и account_id у кандидата.
        """
        pass

    @abstractmethod
    def find_candidate_by_id(self, candidate_id: int) -> Optional[Candidate]:
        """
        Находит кандидата по ID, или None, если не найден.
        """
        pass

    @abstractmethod
    def find_by_passport_id(self, passport_id: int) -> Optional[Candidate]:
        """
        Находит кандидата по passport_id, или None, если не найден.
        """
        pass
