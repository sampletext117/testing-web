from fastapi import APIRouter, HTTPException, status
from typing import List


from election_app.api.schemas.candidate_schemas import (
    CandidateCreateRequest,
    CandidatePatchRequest,
    CandidateResponse
)

from election_app.data_access.candidate_repository import PostgresCandidateRepository
from election_app.data_access.passport_repository import PostgresPassportRepository
from election_app.data_access.campaign_program_repository import PostgresCampaignProgramRepository
from election_app.data_access.candidate_account_repository import PostgresCandidateAccountRepository

from election_app.usecases.register_candidate import RegisterCandidateUseCase

router = APIRouter()

candidate_repo = PostgresCandidateRepository()
passport_repo = PostgresPassportRepository()
program_repo = PostgresCampaignProgramRepository()
account_repo = PostgresCandidateAccountRepository()


@router.get("/candidates", response_model=List[CandidateResponse])
async def list_candidates():
    candidates_db = await candidate_repo.list_candidates()
    results = []
    for c in candidates_db:
        results.append(
            CandidateResponse(
                candidate_id=c.candidate_id,
                full_name=c.full_name,
                birth_date=c.birth_date,
                passport_id=c.passport_id,
                campaign_program_id=c.campaign_program_id,
                account_id=c.account_id,
                created_at=c.created_at
            )
        )
    return results


@router.post("/candidates", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
async def create_candidate(req: CandidateCreateRequest):
    use_case = RegisterCandidateUseCase(
        candidate_repository=candidate_repo,
        passport_repository=passport_repo,
        campaign_program_repository=program_repo,
        candidate_account_repository=account_repo
    )

    # Выполняем use case
    try:
        candidate_id = await use_case.execute(
            full_name=req.full_name,
            birth_date=req.birth_date,
            passport_number=req.passport_number,
            issued_by=req.issued_by,
            issue_date=req.issue_date,
            country=req.country,
            program_description=req.program_description,
            initial_balance=req.initial_balance or 0.0
        )
    except ValueError as e:
        # Если use case кидает ValueError (несовершеннолетний, не РФ и т.д.)
        raise HTTPException(status_code=400, detail=str(e))

    created = await candidate_repo.find_candidate_by_id(candidate_id)
    if not created:
        raise HTTPException(status_code=500, detail="Кандидат не найден после создания (ошибка репо)")

    return CandidateResponse(
        candidate_id=created.candidate_id,
        full_name=created.full_name,
        birth_date=created.birth_date,
        passport_id=created.passport_id,
        campaign_program_id=created.campaign_program_id,
        account_id=created.account_id,
        created_at=created.created_at
    )


@router.get("/candidates/{candidate_id}", response_model=CandidateResponse)
async def get_candidate(candidate_id: int):
    candidate = await candidate_repo.find_candidate_by_id(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Кандидат не найден")

    return CandidateResponse(
        candidate_id=candidate.candidate_id,
        full_name=candidate.full_name,
        birth_date=candidate.birth_date,
        passport_id=candidate.passport_id,
        campaign_program_id=candidate.campaign_program_id,
        account_id=candidate.account_id,
        created_at=candidate.created_at
    )


@router.patch("/candidates/{candidate_id}", response_model=CandidateResponse)
async def patch_candidate(candidate_id: int, patch: CandidatePatchRequest):
    candidate = await candidate_repo.find_candidate_by_id(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Кандидат не найден")

    program = patch.programDescription
    balance = patch.balance

    try:
        await candidate_repo.patch_candidate(candidate_id, program, balance)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Не удалось обновить кандидата")

    updated = await candidate_repo.find_candidate_by_id(candidate_id)
    if not updated:
        raise HTTPException(status_code=500, detail="Кандидат пропал после обновления")

    return CandidateResponse(
        candidate_id=updated.candidate_id,
        full_name=updated.full_name,
        birth_date=updated.birth_date,
        passport_id=updated.passport_id,
        campaign_program_id=updated.campaign_program_id,
        account_id=updated.account_id,
        created_at=updated.created_at
    )


@router.delete("/candidates/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_candidate(candidate_id: int):
    candidate = await candidate_repo.find_candidate_by_id(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Кандидат не найден")

    success = await candidate_repo.delete_candidate(candidate_id)
    if not success:
        raise HTTPException(status_code=500, detail="Не удалось удалить кандидата")

    return  # 204 No Content
