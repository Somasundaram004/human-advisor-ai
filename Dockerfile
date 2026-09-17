FROM python:3.12-slim

WORKDIR /service
COPY pyproject.toml .
RUN pip install --no-cache-dir .
COPY app ./app

ENV DATABASE_PATH=/data/memory.db
RUN mkdir -p /data
VOLUME ["/data"]
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]