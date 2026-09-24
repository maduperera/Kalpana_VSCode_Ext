FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api_server.py core.py ./

EXPOSE 8000

ENV CPP_BACKEND_URL=http://127.0.0.1:8081
ENV RIF_BANDS=2048
ENV RIF_KAPPA=10.0

CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
