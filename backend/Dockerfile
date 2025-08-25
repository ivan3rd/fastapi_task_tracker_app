FROM python:3.12

WORKDIR /backend

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./ /backend

CMD ["sh", "-c", "\

  echo 'Running migrations...' && \
  alembic upgrade head && \
  echo 'Starting FastAPI...' && \
  watchfiles 'uvicorn app.main:app --host 0.0.0.0 --port 8000' \
"]
