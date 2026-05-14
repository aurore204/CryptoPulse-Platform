import requests # Pour faire des requêtes HTTP
import pandas as pd
import psycopg2
from dotenv import load_dotenv
import os
pd.set_option('display.max_columns', None)  # Affiche toutes les colonnes
pd.set_option('display.width', None)        # Pas de limite de largeur
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

print("Chargement des données crypto...")
response = requests.get(url, params=params)
data = response.json()#.json() pour convertir la réponse en format JSON (dictionnaire Python)
print(f"Succès ! {len(data)} cryptos chargées")# len permet de compter
    
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
# Connexion à PostgreSQL
conn = psycopg2.connect(
     host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)
cursor = conn.cursor()#cursor qui pemet d'ecrire les données dans la bd

# Insérer chaque ligne du tableau dans la base
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

conn.commit()# Valider les changements dans la base de données
cursor.close()#fermer l'ecriture en bd
conn.close()# fermer la connexion à la base de données

print(f"{len(df)} cryptos stockées dans PostgreSQL !")
