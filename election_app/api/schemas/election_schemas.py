from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime


class ElectionCreateRequest(BaseModel):
    election_name: str = Field(..., example="Выборы 2025")
    start_date: date = Field(..., example="2025-03-01")
    end_date: date = Field(..., example="2025-03-10")
    description: Optional[str] = Field(None, example="Описание крупных выборов")


class ElectionPatchRequest(BaseModel):
    election_name: Optional[str] = Field(None, example="Новые Выборы")
    start_date: Optional[date] = Field(None)
    end_date: Optional[date] = Field(None)
    description: Optional[str] = Field(None, example="Новое описание")


class ElectionResponse(BaseModel):
    election_id: int = Field(..., example=10)
    election_name: str = Field(..., example="Выборы 2025")
    start_date: date = Field(..., example="2025-03-01")
    end_date: date = Field(..., example="2025-03-10")
    description: Optional[str] = Field(None, example="Описание")
    # created_at, updated_at - при необходимости

    class Config:
        orm_mode = True


class CandidateWithCount(BaseModel):
    candidate_id: int = Field(..., example=2)
    candidate_name: str = Field(..., example="Иванов Иван")
    vote_count: int = Field(..., example=120)


class ElectionResultsResponse(BaseModel):
    election_id: int = Field(..., example=10)
    election_name: Optional[str] = Field(None, example="Выборы 2025")
    total_votes: int = Field(..., example=300)
    results: List[CandidateWithCount] = Field(..., example=[{"candidate_id":2, "candidate_name":"Иванов Иван","vote_count":120}])
    winner: Optional[CandidateWithCount] = None

    class Config:
        orm_mode = True
