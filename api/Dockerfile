FROM python:3.11-slim

WORKDIR /app

# On copie les dépendances et on les installe
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# On copie le code de l'API
COPY api/ /app/
EXPOSE 8000
#commande de lancement
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]