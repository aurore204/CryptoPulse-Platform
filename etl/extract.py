import requests # Pour faire des requêtes HTTP
import pandas as pd
import psycopg2
from dotenv import load_dotenv
import os
from datetime import datetime
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# ETL - Extraction des données crypto
# URL de l'API CoinGecko - GRATUIT
url = "https://api.coingecko.com/api/v3/coins/markets"

params = {
    "vs_currency": "usd",        # Prix en dollars
    "order": "market_cap_desc",  # Tri par popularité
    "per_page": 20,              # 20 cryptos
    "page": 1,                   # Page 1
    "sparkline": False           # Pas de mini-graphique
}

print(f"[EXTRACT] Récupération des données depuis CoinGecko...")
response = requests.get(url, params=params)
if response.status_code != 200:
    raise Exception(f"Erreur API : {response.status_code}")
data = response.json()#.json() pour convertir la réponse en format JSON (dictionnaire Python)
print(f"[EXTRACT] Succès ! {len(data)} cryptos récupérées avec succès")# len permet de compter
    
# TRANSFORM 

# Étape 1  Convertir en tableau (DataFrame)
df = pd.DataFrame(data)
# Étape 2 :Garder seulement les colonnes utiles
df = df[[
    'name',
    'symbol',
    'current_price',
    'market_cap',
    'total_volume',
    'high_24h',
    'low_24h',
    'price_change_percentage_24h',
    'last_updated'
]]
df['last_updated'] = pd.to_datetime(df['last_updated'])# Convertir en format datetime facilement utilisable par python
#  Arrondir les chiffres
df['current_price'] = df['current_price'].round(2)
df['price_change_percentage_24h'] = df['price_change_percentage_24h'].round(2)

#  LOAD 
# Connexion à PostgreSQL et insertion des données
try:
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    cursor = conn.cursor()

    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO crypto_prices (
                name, symbol, current_price, market_cap,
                total_volume, high_24h, low_24h,
                price_change_percentage_24h, last_updated
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            row['name'],
            row['symbol'],
            row['current_price'],
            row['market_cap'],
            row['total_volume'],
            row['high_24h'],
            row['low_24h'],
            row['price_change_percentage_24h'],
            row['last_updated']
        ))

    conn.commit()
    print(f"[TRANSFORM] Nettoyage terminé — {len(df)} lignes propres")
    print(f"[LOAD] {len(df)} cryptos stockées dans PostgreSQL ")

except Exception as e:
    print(f"[LOAD] Erreur PostgreSQL : {e}")
finally:
    cursor.close()
    conn.close()