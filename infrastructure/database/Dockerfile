FROM python:3.11-slim

WORKDIR /app

# Устанавливаем зависимости
RUN pip install --no-cache-dir asyncpg pydantic-settings

# Копируем скрипты
# COPY . /app

COPY . .

CMD ["python", "-u", "infrastructure/database/init_db.py"]