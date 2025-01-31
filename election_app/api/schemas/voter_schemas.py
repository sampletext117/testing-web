from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime


class VoterCreateRequest(BaseModel):
    full_name: str = Field(..., example="Петров Пётр Петрович")
    birth_date: date = Field(..., example="1990-05-20")
    passport_number: str = Field(..., example="9999 123456")
    issued_by: Optional[str] = Field(None, example="УФМС г.Москвы")
    issue_date: Optional[date] = Field(None, example="2010-02-15")
    country: str = Field(..., example="Россия")


class VoterResponse(BaseModel):

    voter_id: int = Field(..., example=10)
    full_name: str = Field(..., example="Петров Пётр Петрович")
    birth_date: date = Field(..., example="1990-05-20")
    passport_id: Optional[int] = Field(None, example=101)
    created_at: Optional[datetime] = Field(None, example="2023-01-01T09:00:00Z")

    class Config:
        orm_mode = True

