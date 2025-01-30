from typing import Optional
import psycopg2

from election_app.domain.repositories.icampaign_program_repository import ICampaignProgramRepository
from election_app.domain.entities.campaign_program import CampaignProgram
from election_app.data_access.database import get_connection


class PostgresCampaignProgramRepository(ICampaignProgramRepository):
    def create_program(self, candidate_id: int, description: str) -> int:
        """
        Создаёт запись о предвыборной программе.
        """
        conn = get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO elections.campaign_program (candidate_id, description)
                        VALUES (%s, %s)
                        RETURNING campaign_program_id
                        """,
                        (candidate_id, description)
                    )
                    new_id = cur.fetchone()[0]
            return new_id
        finally:
            conn.close()

    def find_by_candidate_id(self, candidate_id: int) -> Optional[CampaignProgram]:
        """
        Возвращает программу для заданного кандидата.
        """
        conn = get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT campaign_program_id, candidate_id, description
                        FROM elections.campaign_program
                        WHERE candidate_id = %s
                        """,
                        (candidate_id,)
                    )
                    row = cur.fetchone()
                    if row:
                        return CampaignProgram(
                            campaign_program_id=row[0],
                            candidate_id=row[1],
                            description=row[2]
                        )
                    return None
        finally:
            conn.close()
