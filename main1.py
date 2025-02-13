from fastapi import FastAPI

from election_app.api.v1.candidate_endpoints import router as candidate_router
from election_app.api.v1.voter_endpoints import router as voter_router
from election_app.api.v1.election_endpoints import router as election_router
from election_app.api.v1.vote_endpoints import router as vote_router


def create_app() -> FastAPI:

    # Фабричный метод юзаем
    app = FastAPI(
        title="E-Voting System API",
        description="REST API для системы электронного голосования",
        version="1.0.0",
    )

    app.include_router(candidate_router, prefix="/v1", tags=["Candidates"])
    app.include_router(voter_router, prefix="/v1", tags=["Voters"])
    app.include_router(election_router, prefix="/v1", tags=["Elections"])
    app.include_router(vote_router, prefix="/v1", tags=["Votes"])

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("election_app.api.main:app", host="127.0.0.1", port=8003, reload=True)
