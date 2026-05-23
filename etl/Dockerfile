# Étape 1 : builder 
FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --target=/app/packages -r requirements.txt

#Étape 2 : image finale 
FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /app/packages /app/packages
COPY etl/ /app/

ENV PYTHONPATH=/app/packages

CMD ["python3", "extract.py"]