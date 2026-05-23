from fastapi import FastAPI  # Framework pour créer l'API REST
import psycopg2              # Pour se connecter à PostgreSQL (même lib que dans l'ETL)
import os                    # Pour lire les variables d'environnement (DB_HOST, DB_NAME...)
from dotenv import load_dotenv  # Pour charger le fichier .env

# Remonte d'un dossier depuis api/main.py pour trouver le .env à la racine du projet
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# Crée l'application FastAPI — tout s'accroche à cette variable
app = FastAPI()

# Endpoint de base — accessible sur http://localhost:8000/
# @app.get("/") = quand quelqu'un appelle cette URL, exécute la fonction en dessous
@app.get("/")
def home():
    return {"message": "CryptoPulse API fonctionne !"}  # Retourné automatiquement en JSON
@app.get("/data/raw")
def get_raw_data():
    # Connexion à PostgreSQL avec les variables du .env (même chose que dans l'ETL)
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    cursor = conn.cursor()

    # Récupère toutes les lignes de la table
    cursor.execute("SELECT * FROM crypto_prices ORDER BY last_updated DESC")
    rows = cursor.fetchall()  # fetchall() = récupère TOUS les résultats

      # Récupère les noms des colonnes depuis le curseur
    columns = [desc[0] for desc in cursor.description]
    # cursor.description contient les infos de chaque colonne
    # desc[0] = le nom de la colonne

    # Associe chaque valeur à son nom de colonne
    result = [dict(zip(columns, row)) for row in rows]
    # zip(columns, row) = [("name", "Bitcoin"), ("symbol", "btc"), ...]
    # dict(...) = {"name": "Bitcoin", "symbol": "btc", ...}

    cursor.close()
    conn.close()

    # Retourne les données en JSON
    return {"data": result}

@app.get("/data/clean")
def get_clean_data():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    cursor = conn.cursor()

    # Seulement les colonnes utiles, et seulement le dernier prix de chaque crypto
    cursor.execute("""
        SELECT DISTINCT ON (symbol)
            name, symbol, current_price,
            market_cap, total_volume,
            high_24h, low_24h,
            price_change_percentage_24h,
            last_updated
        FROM crypto_prices
        ORDER BY symbol, last_updated DESC
    """)
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    result = [dict(zip(columns, row)) for row in rows]

    cursor.close()
    conn.close()

    return {"data": result}

@app.get("/stats")
def get_stats():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    cursor = conn.cursor()

    # Crypto qui a le plus augmenté en 24h
    cursor.execute("""
        SELECT DISTINCT ON (symbol) name, symbol, price_change_percentage_24h
        FROM crypto_prices
        ORDER BY symbol, last_updated DESC
    """)
    rows = cursor.fetchall()
    # Trier en Python pour trouver le max et le min
    sorted_by_change = sorted(rows, key=lambda x: x[2] if x[2] else 0, reverse=True)
    best_performer  = {"name": sorted_by_change[0][0],  "symbol": sorted_by_change[0][1],  "change_24h": sorted_by_change[0][2]}
    worst_performer = {"name": sorted_by_change[-1][0], "symbol": sorted_by_change[-1][1], "change_24h": sorted_by_change[-1][2]}

    # Prix moyen, volume total, market cap total
    cursor.execute("""
        SELECT
            ROUND(AVG(current_price)::numeric, 2),  -- prix moyen de toutes les cryptos
            SUM(total_volume),                       -- volume total du marché
            SUM(market_cap)                          -- capitalisation totale du marché
        FROM (
            SELECT DISTINCT ON (symbol) current_price, total_volume, market_cap
            FROM crypto_prices
            ORDER BY symbol, last_updated DESC
        ) latest
    """)
    row = cursor.fetchone()  # fetchone() = récupère UNE seule ligne (on a qu'un résultat)

    cursor.close()
    conn.close()

    return {
        "best_performer":  best_performer,   # crypto qui a le plus monté
        "worst_performer": worst_performer,  # crypto qui a le plus baissé
        "market": {
            "average_price":      row[0],  # prix moyen
            "total_volume":       row[1],  # volume total
            "total_market_cap":   row[2],  # capitalisation totale
        }
    }