from abc import ABC, abstractmethod
from typing import Optional
from election_app.domain.entities.candidate_account import CandidateAccount


class ICandidateAccountRepository(ABC):

    @abstractmethod
    def create_account(self, candidate_id: int, balance: float) -> int:
        """
        Создаёт запись о счёте, возвращает account_id.
        """
        pass

    @abstractmethod
    def find_by_candidate_id(self, candidate_id: int) -> Optional[CandidateAccount]:
        """
        Ищет счёт по candidate_id, возвращает CandidateAccount или None.
        """
        pass

    @abstractmethod
    def update_balance(
        self,
        account_id: int,
        new_balance: float
    ) -> None:
        """
        Обновляет баланс счёта.
        """
        pass
