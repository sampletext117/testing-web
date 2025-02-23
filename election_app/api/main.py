from fastapi import FastAPI, Request
from starlette.responses import Response
import election_app.tracing
import election_app.logging_config
from election_app.api.v1.admin_panel import admin_panel_app
from election_app.api.v1.candidate_endpoints import router as candidate_router
from election_app.api.v1.voter_endpoints import router as voter_router
from election_app.api.v1.election_endpoints import router as election_router
from election_app.api.v1.vote_endpoints import router as vote_router
from election_app.api.v1.auth_endpoints import router as auth_router


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
    app.include_router(auth_router, prefix="", tags=["Auth"])
    app.mount("/admin", admin_panel_app)  # Монтируем админку
    return app

app = create_app()

@app.middleware("http")
async def add_backend_header(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["X-Backend-ID"] = "8000"
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("election_app.api.main:app", host="127.0.0.1", port=8000, reload=True)
