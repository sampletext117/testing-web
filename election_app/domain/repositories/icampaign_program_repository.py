from abc import ABC, abstractmethod
from typing import Optional
from election_app.domain.entities.campaign_program import CampaignProgram


class ICampaignProgramRepository(ABC):

    @abstractmethod
    def create_program(self, candidate_id: int, description: str) -> int:
        """
        Создаёт запись о предвыборной программе, возвращает campaign_program_id.
        """
        pass

    @abstractmethod
    def find_by_candidate_id(self, candidate_id: int) -> Optional[CampaignProgram]:
        """
        Возвращает программу для заданного кандидата, или None, если не найдена.
        """
        pass
