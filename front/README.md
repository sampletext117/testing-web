# EVoting

## Что не реализовано
Для начала, что не было реализовано:
- просмотр описания программы кандидата
- валидация в формах - если что то введено неправильно и юзер нажмет кнопку, ему ничего не сообщит интерфейс
    - это самя душная часть во фронте и занимает кучу времени...

## 6 лаба
### Фигма
- Ссылка [https://www.figma.com/design/FbwXk9lDxUtHJzyqpHbYRN/EVoting?node-id=0-1&t=hVNeGTwP63gLd8g1-1](https://www.figma.com/design/FbwXk9lDxUtHJzyqpHbYRN/EVoting?node-id=0-1&t=hVNeGTwP63gLd8g1-1) 
- в фигме настроены переходы между фреймами **(+1 доп 6 лаба)**

### Доска настроения
- Сcылка [https://ru.pinterest.com/keraki4646/evoting/](https://ru.pinterest.com/keraki4646/evoting/)



## 7-8 лабы

### Технологии

- typescript
- фреймворк vue 3
- сборщик Vite
- библиотека ui компонентов PrimeVue
- библиотека css классов TailwindCss
- Стейт менеджмент Pinia
- SPA роутинг Vue-router
- функции для апи запросов генерируются через библиотеку openapi-fetch из openapi спеки
- библиотека для тестирования vitest
- линтер eslint **(+1 доп 7 лаба)**

### Структура проекта

- src
    - api - работа с либой openapi-fetch
        - auth-middleware.ts - мидлвара для запросов, устанавливает jwt токен в хедер Authorization
        - по идее это **(+1 доп 8 лаба)**
    - components - компоненты
    - router - задание роутов для vue-router
    - stores - стейт менеджмет, выполняет роль бизнес логики и хранилища данных
        - *-store.ts - один стейт
        - *-store.spec.ts - тесты на него
    - views - целые страницы или обертки над компонентами с общими частями (например сверху хедер/навбар)
    - consts.ts - там константа BASE_URL - урл куда запросы слать
    - main.ts - точка входа в приложение
    - index.html - более настоящая точка входа, т.к. браузер сначала читает это 

### Как запустить

1. Установить node.js, лучше 20+ версию (на линуксе через apt ставится какая то супер древняя ~16)
2. Установить зависимости `npm install`
3. запустить дев сервер `npm run dev`
    - чтобы запустить тесты `npm run test`
    - чтобы собрать бандл - `npm run build` - бандл статика сгенерируется в папке dist, но ее надо будет как то раздавать

### Список команд 
установить зависимости
```sh
npm install
```

запустить дев сервер
```sh
npm run dev
```

сбилдить в статические файлы (далее раздача посредством nginx или еще чего то)
```sh
npm run build
```

запустить юнит тесты
```sh
npm run test
```

запустить линтер (eslint)
```sh
npm run lint
```


## Изменения на беке

Нужно поменять 2 файла:

### auth_endpoints.py
добавил несколько юзеров и роли им

```python
# election_app/api/v1/auth_endpoints.py

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import os
import jwt
from datetime import datetime, timedelta

router = APIRouter()

# Параметры для JWT
JWT_SECRET = os.getenv("JWT_SECRET", "mysecretkey")  # В реальности храните в секрете
JWT_ALGORITHM = "HS256"
JWT_EXP_DELTA_SECONDS = 3600  # Токен действителен 1 час


# Pydantic модели для запросов и ответов

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    role: str


class LoginResponse(BaseModel):
    token: str


class ChangePasswordRequest(BaseModel):
    email: str
    current_password: str
    new_password: str


class TwoFARequest(BaseModel):
    email: str
    code: str


class TwoFAResponse(BaseModel):
    detail: str


# Демонстрационные данные технического пользователя.
# В реальном приложении данные будут храниться в базе, а пароли — в виде хэшей.
TECH_USER = {
    "email": "tech@example.com",
    "password": "secret",  # В демо используем открытый текст; в продакшене всегда хэшируйте!
    "role": "admin"
}



users = [
    TECH_USER, 
    {"email": "test1@example.com", "password": "test1", "role": "voter"},
    {"email": "test2@example.com", "password": "test2", "role": "candidate"},
]


@router.post("/auth/login", response_model=LoginResponse)
async def login(req: LoginRequest):
    """
    Endpoint для логина.
    Принимает email и пароль; если данные корректны, возвращает JWT-токен.
    """
    found = None
    for u in users:
        if req.email == u["email"] and req.password == u["password"]:
            found = u
            break

    if found is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    payload = {
        "sub": req.email,
        "role": u["role"],
        "exp": datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return LoginResponse(token=token)

@router.post("/auth/register", response_model=LoginResponse)
async def register(req: RegisterRequest):
    """
    Endpoint для регистрации.
    Принимает email и пароль и роль, возвращает JWT-токен.
    """

    found = None
    for u in users:
        if req.email == u["email"] and req.password == u["password"]:
            found = u
            break

    if found is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already exists")

    users.append({"email": req.email, "password": req.password, "role": req.role})

    payload = {
        "sub": req.email,
        "role": req.role,
        "exp": datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return LoginResponse(token=token)


@router.post("/auth/change-password")
async def change_password(req: ChangePasswordRequest):
    """
    Endpoint для смены пароля.
    Принимает email, текущий пароль и новый пароль.
    Если текущий пароль неверный или пользователь не найден, возвращает ошибку.
    При успехе возвращает сообщение об успешной смене пароля.
    """
    if req.email != TECH_USER["email"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if req.current_password != TECH_USER["password"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")

    # В реальном приложении здесь обновляется хэш пароля в базе.
    # Для демонстрации обновляем данные в TECH_USER.
    TECH_USER["password"] = req.new_password
    return {"detail": "Password changed successfully"}


@router.post("/auth/2fa", response_model=TwoFAResponse)
async def two_factor_auth(req: TwoFARequest):
    """
    Endpoint для двухфакторной аутентификации.
    Принимает email и код 2FA.
    Для демонстрации, если код равен "123456", аутентификация проходит успешно.
    """
    if req.email != TECH_USER["email"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if req.code != "123456":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid 2FA code")
    return TwoFAResponse(detail="2FA verification successful")

```


#### api/main.py

Добавил тут корс просто

```python
# ...
    app = FastAPI(
        title="E-Voting System API",
        description="REST API для системы электронного голосования",
        version="1.0.0",
    )
    
    from fastapi.middleware.cors import CORSMiddleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"], 
        allow_headers=["*"], 
    )
# ...
```