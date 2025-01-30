from abc import ABC, abstractmethod
from typing import Optional
from election_app.domain.entities.vote import Vote


class IVoteRepository(ABC):

    @abstractmethod
    def record_vote(
        self,
        voter_id: int,
        candidate_id: int,
        election_id: int
    ) -> int:
        """
        Создаёт запись в таблице vote, возвращает vote_id.
        """
        pass

    @abstractmethod
    def has_already_voted(
        self,
        voter_id: int,
        election_id: int
    ) -> bool:
        """
        Проверяет, голосовал ли уже избиратель на данных выборах (true/false).
        """
        pass

    @abstractmethod
    def count_votes_by_election(self, election_id: int) -> dict:
        """
        Возвращает сводку по голосам для указанных выборов
        в формате {candidate_id: количество_голосов, ...}.
        """
        pass
