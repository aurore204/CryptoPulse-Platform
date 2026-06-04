from fastapi import FastAPI  # Framework pour créer l'API REST
import psycopg2              # Pour se connecter à PostgreSQL 
import os                    # Pour lire les variables d'environnement 
from dotenv import load_dotenv  # Pour charger le fichier .env
import math
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# Crée l'application FastAPI 
app = FastAPI()

def clean_nan(rows):
    """Remplace tous les NaN, Inf et convertit les Decimal pour le JSON"""
    from decimal import Decimal
    import math
    
    result = []
    for row in rows:
        clean_row = {}
        for k, v in row.items():
            # 1. Gestion des valeurs nulles (None)
            if v is None:
                clean_row[k] = None
                
            # 2. Gestion des Float (NaN / Inf)
            elif isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                clean_row[k] = None
                
            # 3. CORRECTION : Gestion des Decimal 
            elif isinstance(v, Decimal):
                if v.is_nan() or v.is_infinite():
                    clean_row[k] = None
                else:
                    clean_row[k] = float(v)  
                    
            # 4. Autres types standards compatibles JSON
            elif isinstance(v, (int, str, bool)):
                clean_row[k] = v
                
            else:
                try:
                    clean_row[k] = str(v)
                except:
                    clean_row[k] = None
                    
        result.append(clean_row)
    return result

# @app.get("/") = quand quelqu'un appelle cette URL, exécute la fonction en dessous
@app.get("/")
def home():
    return {"message": "CryptoPulse API fonctionne !"}  
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

    result = clean_nan(result)
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
    result = clean_nan(result)
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

    cursor.execute("""
        SELECT DISTINCT ON (symbol) name, symbol, price_change_percentage_24h
        FROM crypto_prices
        ORDER BY symbol, last_updated DESC
    """)
    rows = cursor.fetchall()
    sorted_by_change = sorted(rows, key=lambda x: x[2] if x[2] else 0, reverse=True)

    cursor.execute("""
        SELECT
            ROUND(AVG(current_price)::numeric, 2),
            SUM(total_volume),
            SUM(market_cap)
        FROM (
            SELECT DISTINCT ON (symbol) current_price, total_volume, market_cap
            FROM crypto_prices
            ORDER BY symbol, last_updated DESC
        ) latest
    """)
    row = cursor.fetchone()

    cursor.close()
    conn.close()

    # Convertit Decimal en float et NaN en None
    def safe(v):
        from decimal import Decimal
        if isinstance(v, float) and math.isnan(v):
            return None
        if isinstance(v, Decimal):
            return float(v)
        return v

    return {
        "best_performer":  {"name": sorted_by_change[0][0],  "symbol": sorted_by_change[0][1],  "change_24h": safe(sorted_by_change[0][2])},
        "worst_performer": {"name": sorted_by_change[-1][0], "symbol": sorted_by_change[-1][1], "change_24h": safe(sorted_by_change[-1][2])},
        "market": {
            "average_price":    safe(row[0]),
            "total_volume":     safe(row[1]),
            "total_market_cap": safe(row[2]),
        }
    }
    # Prix moyen, volume total, market cap total
  