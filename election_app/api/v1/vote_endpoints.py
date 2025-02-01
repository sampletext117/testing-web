from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional

# Импорт Pydantic-схем
from election_app.api.schemas.vote_schemas import (
    VoteCreateRequest,
    VoteResponse
)

# Репозитории (асинхронные) для проверки:
#   - voter, candidate, election, vote (для use case VoteUseCase)
from election_app.data_access.voter_repository import PostgresVoterRepository
from election_app.data_access.candidate_repository import PostgresCandidateRepository
from election_app.data_access.election_repository import PostgresElectionRepository
from election_app.data_access.vote_repository import PostgresVoteRepository

# Use Case (VoteUseCase)
from election_app.usecases.vote import VoteUseCase

router = APIRouter()

voter_repo = PostgresVoterRepository()
candidate_repo = PostgresCandidateRepository()
election_repo = PostgresElectionRepository()
vote_repo = PostgresVoteRepository()


@router.post("/votes", response_model=VoteResponse, status_code=status.HTTP_201_CREATED)
async def create_vote(req: VoteCreateRequest):
    use_case = VoteUseCase(
        voter_repository=voter_repo,
        candidate_repository=candidate_repo,
        election_repository=election_repo,
        vote_repository=vote_repo
    )

    try:
        vote_id = await use_case.execute(
            voter_id=req.voter_id,
            candidate_id=req.candidate_id,
            election_id=req.election_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка: {str(e)}")

    created_vote = await vote_repo.find_vote_by_id(vote_id)
    if not created_vote:
        raise HTTPException(status_code=500, detail="Голос не найден сразу после создания.")

    return VoteResponse(
        vote_id=created_vote.vote_id,
        voter_id=created_vote.voter_id,
        candidate_id=created_vote.candidate_id,
        election_id=created_vote.election_id,
        vote_date=created_vote.vote_date
    )


@router.get("/votes", response_model=List[VoteResponse])
async def list_votes(electionId: Optional[int] = Query(None, description="Фильтр по ID выборов")):
    try:
        if electionId is not None:
            votes_db = await vote_repo.list_votes_by_election(electionId)
        else:
            votes_db = await vote_repo.list_all_votes()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении списка голосов: {str(e)}")

    results = []
    for v in votes_db:
        results.append(VoteResponse(
            vote_id=v.vote_id,
            voter_id=v.voter_id,
            candidate_id=v.candidate_id,
            election_id=v.election_id,
            vote_date=v.vote_date
        ))
    return results
