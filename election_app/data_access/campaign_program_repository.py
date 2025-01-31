from typing import Optional
import asyncpg

from election_app.domain.repositories.icampaign_program_repository import ICampaignProgramRepository
from election_app.domain.entities.campaign_program import CampaignProgram
from election_app.data_access.database import get_connection


class PostgresCampaignProgramRepository(ICampaignProgramRepository):
    async def create_program(self, candidate_id: int, description: str) -> int:
        """
        Создаёт запись о предвыборной программе, возвращает campaign_program_id.
        """
        conn = await get_connection()
        try:
            row = await conn.fetchrow(
                """
                INSERT INTO elections.campaign_program (candidate_id, description)
                VALUES ($1, $2)
                RETURNING campaign_program_id
                """,
                candidate_id, description
            )
            return row["campaign_program_id"] if row else 0
        finally:
            await conn.close()

    async def find_by_candidate_id(self, candidate_id: int) -> Optional[CampaignProgram]:
        """
        Возвращает программу для заданного кандидата, или None, если не найдена.
        """
        conn = await get_connection()
        try:
            row = await conn.fetchrow(
                """
                SELECT campaign_program_id, candidate_id, description
                FROM elections.campaign_program
                WHERE candidate_id = $1
                """,
                candidate_id
            )
            if row:
                return CampaignProgram(
                    campaign_program_id=row["campaign_program_id"],
                    candidate_id=row["candidate_id"],
                    description=row["description"]
                )
            return None
        finally:
            await conn.close()
