FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml /app/
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -e .
COPY worker.py /app/worker.py
CMD ["python", "-m", "worker"]
