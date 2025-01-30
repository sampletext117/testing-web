from dataclasses import dataclass
from typing import Optional
from datetime import date


@dataclass
class Election:
    election_id: int
    election_name: str
    start_date: Optional[date]
    end_date: Optional[date]
    description: Optional[str] = None
