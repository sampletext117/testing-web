from datetime import date
from typing import Optional


class RegisterElectionUseCase:
    def __init__(self, election_repository):
        self.election_repo = election_repository

    async def execute(
        self,
        election_name: str,
        start_date: date,
        end_date: date,
        description: Optional[str] = None
    ) -> int:

        if not election_name.strip():
            raise ValueError("Название выборов не может быть пустым.")

        if end_date < start_date:
            raise ValueError("Дата окончания выборов не может быть раньше даты начала.")

        new_election_id = await self.election_repo.create_election(
            election_name=election_name,
            start_date=start_date,
            end_date=end_date,
            description=description or ""
        )

        return new_election_id
