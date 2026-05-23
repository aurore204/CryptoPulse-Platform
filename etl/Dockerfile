FROM python:3.11-slim

# Dossier de travail dans le conteneur
WORKDIR /app

# Installation des dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code ETL
COPY etl/ .
CMD ["python3", "extract.py"]