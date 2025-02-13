import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from fastapi.testclient import TestClient
from datetime import date, timedelta
from election_app.api.main import app

# Подключаем сценарии из feature-файла
scenarios("evoting_e2e.feature")

# Фикстура для клиента (TestClient работает in-process)
@pytest.fixture
def client():
    return TestClient(app)

# Фикстура для хранения контекста (общего словаря для передачи данных между шагами)
@pytest.fixture
def context():
    return {}

# Определяем шаг для технического пользователя с target_fixture "tech_user"
@given(parsers.parse('a technical user with email "{email}" and password "{password}"'),
       target_fixture="tech_user")
def technical_user(context, email, password):
    context["email"] = email
    context["password"] = password
    return context

# Шаг логина
@when("this user logs in and obtains a JWT token")
def user_logs_in(client, tech_user):
    payload = {"email": tech_user["email"], "password": tech_user["password"]}
    response = client.post("/auth/login", json=payload)
    tech_user["login_response"] = response

@then("a token should be returned and status code is 200")
def token_returned(tech_user):
    response = tech_user["login_response"]
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert "token" in data, "No token in response"
    tech_user["token"] = data["token"]

# Шаг регистрации избирателя (без таблицы)
@when(parsers.cfparse('the voter is registered with full_name "{full_name}", birth_date "{birth_date}", passport_number "{passport_number}", issued_by "{issued_by}", issue_date "{issue_date}", country "{country}"'))
def register_voter(client, tech_user, full_name, birth_date, passport_number, issued_by, issue_date, country):
    payload = {
        "full_name": full_name,
        "birth_date": birth_date,
        "passport_number": passport_number,
        "issued_by": issued_by,
        "issue_date": issue_date,
        "country": country
    }
    response = client.post("/v1/voters", json=payload)
    tech_user["voter_response"] = response

@then("the voter_id is returned with status 201")
def voter_registered(tech_user):
    response = tech_user["voter_response"]
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    data = response.json()
    assert "voter_id" in data, "No voter_id in response"
    tech_user["voter_id"] = data["voter_id"]

# Шаг регистрации кандидата (без таблицы)
@when(parsers.cfparse('the candidate is registered with full_name "{full_name}", birth_date "{birth_date}", passport_number "{passport_number}", issued_by "{issued_by}", issue_date "{issue_date}", country "{country}", program_description "{program_description}", initial_balance "{initial_balance}"'))
def register_candidate(client, tech_user, full_name, birth_date, passport_number, issued_by, issue_date, country, program_description, initial_balance):
    payload = {
        "full_name": full_name,
        "birth_date": birth_date,
        "passport_number": passport_number,
        "issued_by": issued_by,
        "issue_date": issue_date,
        "country": country,
        "program_description": program_description,
        "initial_balance": float(initial_balance)
    }
    response = client.post("/v1/candidates", json=payload)
    tech_user["candidate_response"] = response

@then("the candidate_id is returned with status 201")
def candidate_registered(tech_user):
    response = tech_user["candidate_response"]
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    data = response.json()
    assert "candidate_id" in data, "No candidate_id in response"
    tech_user["candidate_id"] = data["candidate_id"]

# Шаг создания выборов (без таблицы)
@when(parsers.cfparse('an election is created with election_name "{election_name}", start_date "{start_date}", end_date "{end_date}", description "{description}"'))
def create_election(client, tech_user, election_name, start_date, end_date, description):
    # Обработка специальных значений для дат
    today = date.today()
    if start_date.lower() == "today":
        start_date = today.isoformat()
    if end_date.lower() == "tomorrow":
        end_date = (today + timedelta(days=1)).isoformat()
    payload = {
        "election_name": election_name,
        "start_date": start_date,
        "end_date": end_date,
        "description": description
    }
    response = client.post("/v1/elections", json=payload)
    tech_user["election_response"] = response

@then("the election_id is returned with status 201")
def election_created(tech_user):
    response = tech_user["election_response"]
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    data = response.json()
    assert "election_id" in data, "No election_id in response"
    tech_user["election_id"] = data["election_id"]

# Шаг голосования
@when("the voter votes for the candidate in that election")
def voter_votes(client, tech_user):
    payload = {
        "voter_id": tech_user.get("voter_id"),
        "candidate_id": tech_user.get("candidate_id"),
        "election_id": tech_user.get("election_id")
    }
    response = client.post("/v1/votes", json=payload)
    tech_user["vote_response"] = response

@then("a vote_id is returned with status 201")
def vote_recorded(tech_user):
    response = tech_user["vote_response"]
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    data = response.json()
    assert "vote_id" in data, "No vote_id in response"
    tech_user["vote_id"] = data["vote_id"]

# Шаг запроса результатов
@when("the results are requested for that election")
def request_results(client, tech_user):
    params = {"electionId": tech_user.get("election_id")}
    response = client.get("/v1/results", params=params)
    tech_user["results_response"] = response

@then("the results should indicate at least 1 vote")
def results_check(tech_user):
    response = tech_user["results_response"]
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    total_votes = data.get("totalVotes")
    if total_votes is None:
        total_votes = sum(item.get("vote_count", 0) for item in data.get("results", []))
    assert total_votes >= 1, "No votes found in results"
