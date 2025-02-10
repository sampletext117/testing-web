from fastapi import APIRouter, HTTPException, status
from typing import List

from election_app.api.schemas.voter_schemas import (
    VoterCreateRequest,
    VoterResponse
)

from election_app.data_access.voter_repository import PostgresVoterRepository
from election_app.data_access.passport_repository import PostgresPassportRepository

from election_app.usecases.register_voter import RegisterVoterUseCase

router = APIRouter()

voter_repo = PostgresVoterRepository()
passport_repo = PostgresPassportRepository()


@router.get("/voters", response_model=List[VoterResponse], summary="Список избирателей")
async def list_voters():
    try:
        voters_db = await voter_repo.list_all_voters()
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

    result = []
    for v in voters_db:
        result.append(
            VoterResponse(
                voter_id=v.voter_id,
                full_name=v.full_name,
                birth_date=v.birth_date,
                passport_id=v.passport_id,
                created_at=v.created_at
            )
        )
    return result


@router.post("/voters", response_model=VoterResponse, status_code=status.HTTP_201_CREATED)
async def create_voter(req: VoterCreateRequest):
    use_case = RegisterVoterUseCase(voter_repo, passport_repo)
    try:
        voter_id = await use_case.execute(full_name=req.full_name,
                                          birth_date=req.birth_date,
                                          passport_number=req.passport_number,
                                          issued_by=req.issued_by,
                                          issue_date=req.issue_date,
                                          country=req.country
                                          )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    created = await voter_repo.find_voter_by_id(voter_id)
    if not created:
        raise HTTPException(status_code=500, detail="Избиратель не найден после создания")

    return VoterResponse(
        voter_id=created.voter_id,
        full_name=created.full_name,
        birth_date=created.birth_date,
        passport_id=created.passport_id,
        created_at=created.created_at
    )


@router.get("/voters/{voterId}", response_model=VoterResponse)
async def get_voter(voterId: int):
    try:
        voter = await voter_repo.find_voter_by_id(voterId)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if not voter:
        raise HTTPException(status_code=404, detail="Избиратель не найден")

    return VoterResponse(
        voter_id=voter.voter_id,
        full_name=voter.full_name,
        birth_date=voter.birth_date,
        passport_id=voter.passport_id,
        created_at=voter.created_at
    )


@router.delete("/voters/{voterId}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_voter(voterId: int):
    voter = await voter_repo.find_voter_by_id(voterId)
    if not voter:
        raise HTTPException(status_code=404, detail="Избиратель не найден")

    try:
        success = await voter_repo.delete_voter(voterId)
        if not success:
            raise HTTPException(status_code=500, detail="Не удалось удалить избирателя")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return  # 204 No Content
