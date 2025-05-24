# Используйте более старый образ для совместимости (если нужно)
FROM python:3.9-slim-bullseye

# Отключите прогресс-бар pip
ENV PIP_PROGRESS_BAR=off

WORKDIR /app

# Копируем зависимости отдельно для кэширования
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Копируем остальные файлы
COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
