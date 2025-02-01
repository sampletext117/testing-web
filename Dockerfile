# Dockerfile.test

FROM python:3.10-slim

# Устанавливаем системные зависимости (если нужны)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt /app/

# Устанавливаем зависимости (сохранятся в образе и кэшируются)
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем ваш пакет в режиме разработки
COPY . /app/
RUN pip install --no-cache-dir -e .

# По умолчанию запускаем bash (но команду можно переопределить в docker-compose)
CMD ["bash"]
