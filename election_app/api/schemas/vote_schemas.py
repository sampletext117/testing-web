from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class VoteCreateRequest(BaseModel):
    voter_id: int = Field(..., example=101)
    candidate_id: int = Field(..., example=2)
    election_id: int = Field(..., example=3)

class VoteResponse(BaseModel):
    vote_id: int = Field(..., example=1001)
    voter_id: int = Field(..., example=101)
    candidate_id: int = Field(..., example=2)
    election_id: int = Field(..., example=3)
    vote_date: Optional[datetime] = Field(None, example="2025-03-02T10:00:00Z")

    class Config:
        orm_mode = True
