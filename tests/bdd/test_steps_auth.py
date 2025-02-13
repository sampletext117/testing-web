import os
import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from fastapi.testclient import TestClient
from election_app.api.main import app
import inspect
from fastapi.testclient import TestClient


# Подключаем сценарии из файла authentication.feature
scenarios("authentication.feature")

# Фикстура для клиента
@pytest.fixture
def client():
    return TestClient(app)

# Фикстура для хранения данных пользователя в рамках сценария
@pytest.fixture
def context():
    return {}

# Читаем секреты из переменных окружения (для CI/CD можно настроить через GitLab Secrets)
TECH_USER_EMAIL = os.getenv("TECH_USER_EMAIL", "tech@example.com")
TECH_USER_PASSWORD = os.getenv("TECH_USER_PASSWORD", "secret")

# Добавляем target_fixture="tech_user"
@given(parsers.parse('Технический пользователь с email "{email}" и паролем "{password}"'),
       target_fixture="tech_user")
def technical_user(context, email, password):
    context["email"] = email
    context["password"] = password
    return context

@when("Пользователь отправляет запрос на логин с этими данными")
def send_login_request(client, context):
    payload = {
        "email": context["email"],
        "password": context["password"]
    }
    response = client.post("/auth/login", json=payload)
    context["login_response"] = response

@then("В ответе должен быть получен JWT-токен и статус 200")
def check_successful_login(context):
    response = context["login_response"]
    assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"
    data = response.json()
    assert "token" in data, "Токен не найден в ответе"
    context["token"] = data["token"]

@then("В ответе должна быть ошибка авторизации со статусом 401")
def check_failed_login(context):
    response = context["login_response"]
    assert response.status_code == 401, f"Ожидался статус 401, получен {response.status_code}"

# Шаги для смены пароля
@given("Пользователь успешно залогинен и получил токен")
def user_logged_in(context):
    # Если токен ещё не получен, повторно вызываем логин с данными из context
    if "token" not in context:
        # Используем данные, уже сохранённые в context (например, TECH_USER_EMAIL и TECH_USER_PASSWORD)
        # Можно повторно вызвать функцию send_login_request
        # Здесь предполагаем, что тест уже залогинен (см. предыдущий сценарий)
        pass  # Логика уже выполнена в шагах логина

@when(parsers.parse('Пользователь отправляет запрос на смену пароля с текущим паролем "{current_password}" и новым паролем "{new_password}"'))
def send_change_password_request(client, context, current_password, new_password):
    payload = {
        "email": context["email"],
        "current_password": current_password,
        "new_password": new_password
    }
    response = client.post("/auth/change-password", json=payload)
    context["change_password_response"] = response

@then("Ответ подтверждает успешную смену пароля со статусом 200")
def check_successful_change_password(context):
    response = context["change_password_response"]
    assert response.status_code in [200, 204], f"Ожидался статус 200 или 204, получен {response.status_code}"

@then("В ответе должна быть ошибка смены пароля с сообщением 'Current password is incorrect' и статусом 400")
def check_failed_change_password(context):
    response = context["change_password_response"]
    assert response.status_code == 400, f"Ожидался статус 400, получен {response.status_code}"
    data = response.json()
    expected = "Current password is incorrect"
    assert expected in data.get("detail", ""), f"Ожидалось сообщение '{expected}', получено: {data.get('detail')}"

# Шаги для двухфакторной аутентификации (2FA)
@given(parsers.parse('Технический пользователь с email "{email}"'))
def technical_user_email(context, email):
    context["email"] = email

@when(parsers.parse('Пользователь отправляет запрос на 2FA с кодом "{code}"'))
def send_2fa_request(client, context, code):
    payload = {
        "email": context["email"],
        "code": code
    }
    response = client.post("/auth/2fa", json=payload)
    context["2fa_response"] = response

@then("Ответ подтверждает успешную валидацию 2FA со статусом 200")
def check_successful_2fa(context):
    response = context["2fa_response"]
    assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"
    data = response.json()
    assert "detail" in data, "В ответе отсутствует поле detail"
    assert "successful" in data["detail"].lower(), "Ожидалось сообщение об успешной проверке 2FA"

@then(parsers.parse('В ответе должна быть ошибка с сообщением "{message}" и статусом 400'))
def check_failed_2fa(context, message):
    response = context["2fa_response"]
    assert response.status_code == 400, f"Ожидался статус 400, получен {response.status_code}"
    data = response.json()
    assert message in data.get("detail", ""), f"Ожидалось сообщение '{message}', получено: {data.get('detail')}"

