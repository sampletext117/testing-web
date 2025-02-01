from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional

# DTO-модели (pydantic)
from election_app.api.schemas.election_schemas import (
    ElectionCreateRequest,
    ElectionPatchRequest,
    ElectionResponse,
    ElectionResultsResponse
)

from election_app.data_access.election_repository import PostgresElectionRepository

from election_app.usecases.register_election import RegisterElectionUseCase

from election_app.usecases.finalize_election import FinalizeElectionUseCase

from election_app.data_access.vote_repository import PostgresVoteRepository
from election_app.data_access.candidate_repository import PostgresCandidateRepository

router = APIRouter()

election_repo = PostgresElectionRepository()
vote_repo = PostgresVoteRepository()
candidate_repo = PostgresCandidateRepository()


@router.get("/elections", response_model=List[ElectionResponse])
async def list_elections():
    try:
        items = await election_repo.list_all_elections()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    results = []
    for el in items:
        results.append(ElectionResponse(
            election_id=el.election_id,
            election_name=el.election_name,
            start_date=el.start_date,
            end_date=el.end_date,
            description=el.description
        ))
    return results


@router.post("/elections", response_model=ElectionResponse, status_code=status.HTTP_201_CREATED)
async def create_election(req: ElectionCreateRequest):

    use_case = RegisterElectionUseCase(election_repo)
    try:
        election_id = await use_case.execute(
            election_name=req.election_name,
            start_date=req.start_date,
            end_date=req.end_date,
            description=req.description
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    created = await election_repo.find_election_by_id(election_id)
    if not created:
        raise HTTPException(status_code=500, detail="Выборы не найдены после создания")

    return ElectionResponse(
        election_id=created.election_id,
        election_name=created.election_name,
        start_date=created.start_date,
        end_date=created.end_date,
        description=created.description
    )


@router.get("/elections/{election_id}", response_model=ElectionResponse)
async def get_election(election_id: int):
    try:
        el = await election_repo.find_election_by_id(election_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if not el:
        raise HTTPException(status_code=404, detail="Выборы не найдены")

    return ElectionResponse(
        election_id=el.election_id,
        election_name=el.election_name,
        start_date=el.start_date,
        end_date=el.end_date,
        description=el.description
    )


@router.patch("/elections/{election_id}", response_model=ElectionResponse)
async def patch_election(election_id: int, patch: ElectionPatchRequest):
    old_el = await election_repo.find_election_by_id(election_id)
    if not old_el:
        raise HTTPException(status_code=404, detail="Выборы не найдены")

    new_name = patch.election_name if patch.election_name is not None else old_el.election_name
    new_start = patch.start_date if patch.start_date is not None else old_el.start_date
    new_end = patch.end_date if patch.end_date is not None else old_el.end_date
    new_desc = patch.description if patch.description is not None else old_el.description

    try:
        updated_ok = await election_repo.patch_election(
            election_id=election_id,
            new_name=new_name,
            new_start=new_start,
            new_end=new_end,
            new_desc=new_desc
        )
        if not updated_ok:
            raise HTTPException(status_code=500, detail="Не удалось обновить выборы")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    new_el = await election_repo.find_election_by_id(election_id)
    if not new_el:
        raise HTTPException(status_code=500, detail="Выборы пропали после обновления")

    return ElectionResponse(
        election_id=new_el.election_id,
        election_name=new_el.election_name,
        start_date=new_el.start_date,
        end_date=new_el.end_date,
        description=new_el.description
    )


@router.delete("/elections/{election_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_election(election_id: int):
    el = await election_repo.find_election_by_id(election_id)
    if not el:
        raise HTTPException(status_code=404, detail="Выборы не найдены")

    try:
        success = await election_repo.delete_election(election_id)
        if not success:
            raise HTTPException(status_code=500, detail="Не удалось удалить выборы")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return  # 204 No Content


@router.get("/results", response_model=ElectionResultsResponse)
async def get_election_results(electionId: int = Query(..., description="ID выборов")):
    # Сначала проверяем, что выборы существуют
    el = await election_repo.find_election_by_id(electionId)
    if not el:
        raise HTTPException(status_code=404, detail="Выборы не найдены")

    votes_dict = await vote_repo.count_votes_by_election(electionId)
    total = sum(votes_dict.values())

    results_list = []
    winner_cand = None
    max_votes = 0

    for cand_id, count in votes_dict.items():
        c = await candidate_repo.find_candidate_by_id(cand_id)
        if c:
            name = c.full_name
        else:
            name = f"Unknown candidate {cand_id}"

        results_list.append({
            "candidate_id": cand_id,
            "candidate_name": name,
            "vote_count": count
        })

        if count > max_votes:
            max_votes = count
            winner_cand = {
                "candidate_id": cand_id,
                "candidate_name": name,
                "vote_count": count
            }

    return ElectionResultsResponse(
        election_id=el.election_id,
        election_name=el.election_name,
        total_votes=total,
        results=results_list,  # CandidateWithCount[]
        winner=winner_cand
    )
