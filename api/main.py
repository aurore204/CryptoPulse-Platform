from fastapi import FastAPI, Query, HTTPException  # Framework et outils de validation
import psycopg2                              # Pour se connecter à PostgreSQL 
import os                                    # Pour lire les variables d'environnement 
from dotenv import load_dotenv               # Pour charger le fichier .env
import math
from decimal import Decimal

# Chargement du fichier .env pour le développement local
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# Centralisation et harmonisation des variables d'environnement (Compatible Local & K8s)
DB_HOST = os.environ.get("DB_HOST", os.getenv("DB_HOST", "localhost"))
DB_PORT = os.environ.get("DB_PORT", os.getenv("DB_PORT", "5432"))
DB_NAME = os.environ.get("POSTGRES_DB", os.getenv("DB_NAME", "cryptopulse"))
DB_USER = os.environ.get("POSTGRES_USER", os.getenv("DB_USER"))
DB_PASSWORD = os.environ.get("POSTGRES_PASSWORD", os.getenv("DB_PASSWORD"))

# Initialisation de l'application FastAPI avec métadonnées professionnelles
app = FastAPI(
    title="CryptoPulse Rest API",
    description="API de production pour le suivi et l'analyse des cours de cryptomonnaies.",
    version="1.0.0"
)

# FONCTIONS UTILITAIRES

def get_db_connection():
    """Génère une connexion propre à la base de données PostgreSQL."""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def clean_nan(rows):
    """Sécurise les données avant la sérialisation JSON (gère les NaN, Inf et Decimals)."""
    result = []
    for row in rows:
        clean_row = {}
        for k, v in row.items():
            if v is None:
                clean_row[k] = None
            elif isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                clean_row[k] = None
            elif isinstance(v, Decimal):
                if v.is_nan() or v.is_infinite():
                    clean_row[k] = None
                else:
                    clean_row[k] = float(v)  
            elif isinstance(v, (int, str, bool)):
                clean_row[k] = v
            else:
                try:
                    clean_row[k] = str(v)
                except:
                    clean_row[k] = None
        result.append(clean_row)
    return result

@app.get("/", tags=["System"])
def health_check():
    """Vérifie l'état de santé basique de l'API."""
    return {"status": "healthy", "service": "CryptoPulse API", "version": "1.0.0"}


# SECTION : PRICES (Gestion des cours de cryptomonnaies)

@app.get("/api/v1/prices", tags=["Prices"])
def get_latest_prices(
    page: int = Query(1, ge=1, description="Numéro de la page à afficher"),
    limit: int = Query(20, ge=1, le=100, description="Nombre de résultats par page")
):
    """
    **ENDPOINT 1 :** Récupère le dernier snapshot des prix du marché avec pagination SQL.
    """
    offset = (page - 1) * limit
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Requête pro : DISTINCT ON pour n'avoir que la dernière ligne par crypto, combiné avec LIMIT/OFFSET
        cursor.execute("""
            SELECT DISTINCT ON (symbol)
                name, symbol, current_price, market_cap, total_volume,
                high_24h, low_24h, price_change_percentage_24h, last_updated
            FROM crypto_prices
            ORDER BY symbol, last_updated DESC
            LIMIT %s OFFSET %s
        """, (limit, offset))
        
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        result = [dict(zip(columns, row)) for row in rows]
        
        cursor.close()
        conn.close()
        return {"page": page, "limit": limit, "count": len(result), "data": clean_nan(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur base de données : {str(e)}")


@app.get("/api/v1/prices/{symbol}", tags=["Prices"])
def get_crypto_detail(symbol: str):
    """
    **ENDPOINT 2 :** Récupère les détails en temps réel d'une seule cryptomonnaie cible via son symbole (ex: btc, eth).
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name, symbol, current_price, market_cap, total_volume,
                   high_24h, low_24h, price_change_percentage_24h, last_updated
            FROM crypto_prices
            WHERE LOWER(symbol) = %s
            ORDER BY last_updated DESC
            LIMIT 1
        """, (symbol.lower(),))
        
        row = cursor.fetchone()
        if not row:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail=f"Cryptomonnaie '{symbol}' introuvable en base.")
            
        columns = [desc[0] for desc in cursor.description]
        result = dict(zip(columns, row))
        
        cursor.close()
        conn.close()
        return {"data": clean_nan([result])[0]}
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur SQL : {str(e)}")


@app.get("/api/v1/prices/{symbol}/history", tags=["Prices"])
def get_crypto_history(symbol: str, limit: int = Query(30, ge=1, le=500, description="Nombre de points historiques requis")):
    """
    **ENDPOINT 3 :** Récupère la série temporelle (historique) d'une crypto pour tracer des graphiques.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # On remonte l'historique chronologique pour ce symbole précis
        cursor.execute("""
            SELECT last_updated, current_price, total_volume, market_cap
            FROM crypto_prices
            WHERE LOWER(symbol) = %s
            ORDER BY last_updated DESC
            LIMIT %s
        """, (symbol.lower(), limit))
        
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        
        # Inverser les résultats pour les renvoyer dans le sens chronologique (du plus vieux au plus récent)
        result = [dict(zip(columns, row)) for row in rows][::-1]
        
        cursor.close()
        conn.close()
        return {"symbol": symbol.upper(), "data_points": len(result), "history": clean_nan(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération de l'historique : {str(e)}")


# SECTION : MARKET (Analytique et indicateurs globaux du marché)

@app.get("/api/v1/market/summary", tags=["Market"])
def get_market_summary():
    """
    **ENDPOINT 4 :** Calcule les KPI globaux de santé globale du marché (Volume global, Market Cap Global, Prix Moyen).
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT
                ROUND(AVG(current_price)::numeric, 2) as average_price,
                SUM(total_volume) as total_volume,
                SUM(market_cap) as total_market_cap
            FROM (
                SELECT DISTINCT ON (symbol) current_price, total_volume, market_cap
                FROM crypto_prices
                ORDER BY symbol, last_updated DESC
            ) latest
        """)
        row = cursor.fetchone()
        columns = [desc[0] for desc in cursor.description]
        result = dict(zip(columns, row))
        
        cursor.close()
        conn.close()
        return {"market_summary": clean_nan([result])[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur d'agrégation de marché : {str(e)}")


@app.get("/api/v1/market/performers", tags=["Market"])
def get_market_performers():
    """
    **ENDPOINT 5 :** Identifie les extrêmes du marché des dernières 24h (Top Gainer et Top Loser).
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT ON (symbol) name, symbol, price_change_percentage_24h, current_price
            FROM crypto_prices
            ORDER BY symbol, last_updated DESC
        """)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        all_cryptos = [dict(zip(columns, row)) for row in rows]
        
        # Tri des performances en ignorant les valeurs None
        sorted_cryptos = sorted(
            [c for c in all_cryptos if c['price_change_percentage_24h'] is not None],
            key=lambda x: x['price_change_percentage_24h'],
            reverse=True
        )
        
        cursor.close()
        conn.close()
        
        if not sorted_cryptos:
            return {"top_gainer": None, "top_loser": None}
            
        return {
            "top_gainer": clean_nan([sorted_cryptos[0]])[0],
            "top_loser": clean_nan([sorted_cryptos[-1]])[0]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de calcul de performance : {str(e)}")