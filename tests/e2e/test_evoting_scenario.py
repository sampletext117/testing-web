import pytest
import pytest_asyncio
import time
from datetime import date, timedelta
import httpx
from fastapi import status

# Импортируем приложение
from election_app.api.main import app

@pytest_asyncio.fixture
async def async_client():
    """
    Фикстура, создающая асинхронный HTTP-клиент, работающий с нашим FastAPI-приложением.
    Используется встроенный ASGI-приложение для тестирования.
    """
    async with httpx.AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_evoting_scenario(async_client: httpx.AsyncClient):
    # 1. Регистрация избирателя
    unique_voter_num = int(time.time() * 1000000)
    voter_data = {
        "full_name": "John Doe",
        "birth_date": "1990-01-01",
        "passport_number": f"VOTER-PASSPORT-{unique_voter_num}",
        "issued_by": "Test Authority",
        "issue_date": "2010-01-01",
        "country": "Россия"
    }
    response = await async_client.post("/v1/voters", json=voter_data)
    assert response.status_code == status.HTTP_201_CREATED, f"Ошибка при регистрации избирателя: {response.text}"
    voter_resp = response.json()
    voter_id = voter_resp["voter_id"]
    assert voter_id > 0

    # 2. Регистрация кандидата
    unique_candidate_num = int(time.time() * 1000000) + 1
    candidate_data = {
        "full_name": "Alice Candidate",
        "birth_date": "1970-05-05",
        "passport_number": f"CANDIDATE-PASSPORT-{unique_candidate_num}",
        "issued_by": "Test Authority",
        "issue_date": "2000-01-01",
        "country": "Россия",
        "program_description": "Test campaign program",
        "initial_balance": 1000.0
    }
    response = await async_client.post("/v1/candidates", json=candidate_data)
    assert response.status_code == status.HTTP_201_CREATED, f"Ошибка при регистрации кандидата: {response.text}"
    candidate_resp = response.json()
    candidate_id = candidate_resp["candidate_id"]
    assert candidate_id > 0

    # 3. Создание выборов
    today = date.today()
    election_data = {
        "election_name": "E2E Test Election",
        "start_date": today.isoformat(),
        # Чтобы выборы были активны, установим end_date на следующий день
        "end_date": (today + timedelta(days=1)).isoformat(),
        "description": "Election for E2E testing"
    }
    response = await async_client.post("/v1/elections", json=election_data)
    assert response.status_code == status.HTTP_201_CREATED, f"Ошибка при создании выборов: {response.text}"
    election_resp = response.json()
    election_id = election_resp["election_id"]
    assert election_id > 0

    # 4. Голосование: избиратель голосует за кандидата в рамках созданных выборов
    vote_data = {
        "voter_id": voter_id,
        "candidate_id": candidate_id,
        "election_id": election_id
    }
    response = await async_client.post("/v1/votes", json=vote_data)
    assert response.status_code == status.HTTP_201_CREATED, f"Ошибка при голосовании: {response.text}"
    vote_resp = response.json()
    vote_id = vote_resp["vote_id"]
    assert vote_id > 0

    # 5. Получение итогов выборов
    response = await async_client.get("/v1/results", params={"electionId": election_id})
    assert response.status_code == status.HTTP_200_OK, f"Ошибка при получении результатов: {response.text}"
    results = response.json()
    # Проверяем, что результаты относятся к созданным выборам
    assert results["election_id"] == election_id
    # Если ключ totalVotes отсутствует, вычисляем его как сумму голосов из списка results
    total_votes = results.get("totalVotes")
    if total_votes is None:
        total_votes = sum(item.get("vote_count", 0) for item in results.get("results", []))
    assert total_votes >= 1, "Общее количество голосов должно быть не менее 1"
    if total_votes > 0:
        assert results.get("winner") is not None, "При наличии голосов должен быть определён победитель"
