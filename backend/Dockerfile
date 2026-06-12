FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
 && pip install --no-cache-dir "cloud-sql-python-connector[pg8000]" pg8000

COPY alembic.ini .
COPY alembic/ ./alembic/
COPY app/ ./app/

ENV PORT=8080
EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
