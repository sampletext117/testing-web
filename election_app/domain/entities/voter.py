from dataclasses import dataclass
from datetime import date


@dataclass
class Voter:
    voter_id: int
    full_name: str
    birth_date: date
    passport_id: int
    created_at: date = None  # или datetime
