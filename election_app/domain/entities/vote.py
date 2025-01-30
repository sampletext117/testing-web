from dataclasses import dataclass
from datetime import datetime


@dataclass
class Vote:
    vote_id: int
    voter_id: int
    candidate_id: int
    election_id: int
    vote_date: datetime = None
