import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from fastapi.testclient import TestClient
from datetime import date, timedelta

from election_app.api.main import app

# Подключаем все сценарии из файла evoting_e2e.feature:
scenarios("features/evoting_e2e.feature")

@pytest.fixture
def client():
    """
    Фикстура для получения TestClient (in-process).
    Так мы не запускаем uvicorn, а напрямую обращаемся к app.
    """
    return TestClient(app)


@given(parsers.parse('a technical user with email "{email}" and password "{password}"'))
def tech_user(context, email, password):
    """
    Сохраняем в контекст email и пароль тех. пользователя.
    В pytest-bdd обычно "context" не используется, поэтому
    можно хранить в глобальных переменных или фикстуре.
    """
    return {"email": email, "password": password}


@when("this user logs in and obtains a JWT token")
def user_logs_in(client, tech_user):
    """
    Отправка запроса на /auth/login
    """
    payload = {
        "email": tech_user["email"],
        "password": tech_user["password"]
    }
    response = client.post("/auth/login", json=payload)
    tech_user["login_response"] = response


@then("a token should be returned and status code is 200")
def token_returned(tech_user):
    response = tech_user["login_response"]
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert "token" in data, "No token in response"


# ------------------- Шаги для регистрации избирателя -------------------

@when(parsers.cfparse('a voter is registered with:\n{table_data:S}'))
def register_voter(client, tech_user, table_data):
    """
    Здесь мы получаем raw-строку "table_data",
    но проще распарсить вручную или использовать ast.literal_eval (если формат JSON).
    Для демонстрации используем вручную.
    """
    # table_data может выглядеть так:
    #  | full_name       | Voter One         |
    #  | birth_date      | 1990-01-01        |
    #  ...
    # Нам нужно вручную преобразовать в dict
    lines = table_data.strip().split("\n")
    # Каждая строка вида: | ключ | значение |
    voter_payload = {}
    for line in lines:
        parts = [p.strip() for p in line.split("|") if p.strip()]
        # parts[0] = ключ, parts[1] = значение
        voter_payload[parts[0]] = parts[1]

    response = client.post("/v1/voters", json=voter_payload)
    tech_user["voter_response"] = response


@then("the voter_id is returned with status 201")
def voter_registered(tech_user):
    resp = tech_user["voter_response"]
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}"
    data = resp.json()
    assert "voter_id" in data, "No voter_id in response"
    assert data["voter_id"] > 0, "Invalid voter_id"


# ------------------- Шаги для регистрации кандидата -------------------

@when(parsers.cfparse('a candidate is registered with:\n{table_data:S}'))
def register_candidate(client, tech_user, table_data):
    lines = table_data.strip().split("\n")
    candidate_payload = {}
    for line in lines:
        parts = [p.strip() for p in line.split("|") if p.strip()]
        candidate_payload[parts[0]] = parts[1]

    # Преобразуем initial_balance в float
    if "initial_balance" in candidate_payload:
        candidate_payload["initial_balance"] = float(candidate_payload["initial_balance"])

    response = client.post("/v1/candidates", json=candidate_payload)
    tech_user["candidate_response"] = response


@then("the candidate_id is returned with status 201")
def candidate_registered(tech_user):
    resp = tech_user["candidate_response"]
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}"
    data = resp.json()
    assert "candidate_id" in data, "No candidate_id in response"
    assert data["candidate_id"] > 0, "Invalid candidate_id"
    tech_user["candidate_id"] = data["candidate_id"]


# ------------------- Шаги для создания выборов -------------------

@when(parsers.cfparse('an election is created with:\n{table_data:S}'))
def create_election(client, tech_user, table_data):
    lines = table_data.strip().split("\n")
    election_payload = {}
    for line in lines:
        parts = [p.strip() for p in line.split("|") if p.strip()]
        election_payload[parts[0]] = parts[1]

    # Обработка today/tomorrow
    today = date.today()
    if election_payload["start_date"].lower() == "today":
        election_payload["start_date"] = today.isoformat()
    else:
        election_payload["start_date"] = date.fromisoformat(election_payload["start_date"]).isoformat()

    if election_payload["end_date"].lower() == "tomorrow":
        end_date = today + timedelta(days=1)
        election_payload["end_date"] = end_date.isoformat()
    else:
        election_payload["end_date"] = date.fromisoformat(election_payload["end_date"]).isoformat()

    response = client.post("/v1/elections", json=election_payload)
    tech_user["election_response"] = response


@then("the election_id is returned with status 201")
def election_created(tech_user):
    resp = tech_user["election_response"]
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}"
    data = resp.json()
    assert "election_id" in data, "No election_id in response"
    assert data["election_id"] > 0, "Invalid election_id"
    tech_user["election_id"] = data["election_id"]


# ------------------- Шаги для голосования -------------------

@when("the voter votes for the candidate in that election")
def voter_casts_vote(client, tech_user):
    # Не сохраняли voter_id, candidate_id... Нужно либо достать их, либо
    # предполагаем, что voter_id => v1/voters ответ, candidate_id => candidate_registered ...
    # Для демонстрации упрощённо, voter_id берём из "voter_response".
    # Однако, выше, voter_id не сохраняем. Исправим, чтобы сохранить
    # voter_id / candidate_id
    #
    # Считаем, что voter_id => tech_user["voter_id"]
    # candidate_id => tech_user["candidate_id"]
    voter_resp = tech_user["voter_response"].json()
    candidate_id = tech_user["candidate_id"]
    election_id = tech_user["election_id"]

    payload = {
        "voter_id": voter_resp["voter_id"],  #
        "candidate_id": candidate_id,
        "election_id": election_id
    }
    response = client.post("/v1/votes", json=payload)
    tech_user["vote_response"] = response


@then("a vote_id is returned with status 201")
def vote_recorded(tech_user):
    resp = tech_user["vote_response"]
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}"
    data = resp.json()
    assert "vote_id" in data, "No vote_id in response"
    assert data["vote_id"] > 0, "Invalid vote_id"


# ------------------- Шаги для получения результатов -------------------

@when("the results are requested for that election")
def get_results(client, tech_user):
    election_id = tech_user["election_id"]
    resp = client.get("/v1/results", params={"electionId": election_id})
    tech_user["results_response"] = resp


@then("the results should indicate at least 1 vote")
def results_vote_count(tech_user):
    resp = tech_user["results_response"]
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    data = resp.json()
    assert data.get("election_id") == tech_user["election_id"], "Election ID mismatch"
    total_votes = data.get("totalVotes")
    if total_votes is None:
        total_votes = sum(item.get("vote_count", 0) for item in data.get("results", []))
    assert total_votes >= 1, "No votes found in results"
    # Дополнительно: если total_votes>0, проверяем что есть winner
    if total_votes > 0:
        assert data.get("winner") is not None, "No winner in results"

