from dataclasses import dataclass
from typing import Optional
from datetime import date


@dataclass
class Passport:
    passport_id: int
    passport_number: str
    issued_by: Optional[str] = None
    issue_date: Optional[date] = None
    country: str = "Россия"
