from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class CandidateAccount:
    account_id: int
    candidate_id: int
    balance: float
    last_transaction_date: Optional[datetime] = None
