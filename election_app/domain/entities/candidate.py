from dataclasses import dataclass
from datetime import datetime, date


@dataclass
class Candidate:
    candidate_id: int
    full_name: str
    birth_date: date
    passport_id: int
    campaign_program_id: int = None
    account_id: int = None
    created_at: datetime = None
