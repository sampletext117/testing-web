from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime

class CandidateCreateRequest(BaseModel):
    full_name: str = Field(..., example="Иванов Иван Иванович")
    birth_date: date = Field(..., example="1980-05-20")
    passport_number: str = Field(..., example="1234 567890")
    issued_by: Optional[str] = Field(None, example="УФМС г.Москвы")
    issue_date: Optional[date] = Field(None, example="2010-01-01")
    country: str = Field(..., example="Россия")
    program_description: Optional[str] = Field(None, example="Моя программа")
    initial_balance: Optional[float] = Field(None, ge=0, example=1000.0)


class CandidatePatchRequest(BaseModel):
    programDescription: Optional[str] = Field(None, example="Обновлённая программа")
    balance: Optional[float] = Field(None, ge=0, example=1500.0)


class CandidateResponse(BaseModel):
    candidate_id: int = Field(..., example=10)
    full_name: str = Field(..., example="Иванов Иван Иванович")
    birth_date: date = Field(..., example="1980-05-20")
    passport_id: Optional[int] = Field(None, example=55)
    campaign_program_id: Optional[int] = Field(None, example=101)
    account_id: Optional[int] = Field(None, example=202)
    created_at: Optional[datetime] = Field(None, example="2023-01-01T10:00:00Z")

    class Config:
        orm_mode = True
