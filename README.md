CryptoPulse Platform

Data Platform Cloud-native — Projet CV niveau Junior Confirmé
Data Engineering + DevOps/Cloud — Roadmap 8 semaines


📌 Description
CryptoPulse Platform est une plateforme de données moderne construite de A à Z, combinant Data Engineering et DevOps/Cloud. Elle collecte les données des 20 plus grosses cryptomonnaies en temps réel via l'API CoinGecko, les stocke dans PostgreSQL, et les expose via une API REST.
Ce projet simule une architecture utilisée en production dans les entreprises tech.

🏗️ Architecture
┌─────────────────────────────────────────────────────────┐
│                    CryptoPulse Platform                  │
│                                                         │
│  ┌──────────────┐    ┌──────────────┐    ┌───────────┐  │
│  │ API CoinGecko│───▶│  ETL Python  │───▶│PostgreSQL │  │
│  │  (20 cryptos)│    │  (toutes les │    │           │  │
│  └──────────────┘    │   heures)    │    └─────┬─────┘  │
│                      └──────────────┘          │        │
│                                                ▼        │
│                                        ┌──────────────┐ │
│                                        │  API REST    │ │
│                                        │  (FastAPI)   │ │
│                                        └──────────────┘ │
└─────────────────────────────────────────────────────────┘

📁 Structure du projet
CryptoPulse-Platform/
│
├── api/                    # API REST (FastAPI)
│   └── main.py             # Endpoints /data/raw /data/clean /stats
│
├── etl/                    # Pipeline ETL
│   └── extract.py          # Extraction → Transformation → Chargement
│
├── config/                 # Configuration
├── scripts/                # Scripts utilitaires
├── data/                   # Données brutes et traitées
├── logs/                   # Logs du système
├── tests/                  # Tests unitaires
│
├── .env                    # Variables d'environnement (non commité)
├── .gitignore
├── requirements.txt
└── README.md

📊 Roadmap — 8 semaines
PhaseDuréeDescriptionTechnologiesStatutPhase 1Semaine 1Source de données, nettoyage, stockagePython, Pandas, PostgreSQL✅ TerminéPhase 2Semaine 2Pipeline ETL complet + automatisation cronPython, PostgreSQL, Cron✅ TerminéPhase 3Semaine 2-3API REST exposition des donnéesFastAPI, uvicorn TerminéPhase 4Semaine 3-4Conteneurisation complèteDocker, docker-compose⏳ En coursPhase 5Semaine 4-5Déploiement KubernetesKubernetes, Minikube, Helm🔜 À venirPhase 6Semaine 6Infrastructure as CodeTerraform🔜 À venirPhase 7Semaine 7Monitoring productionPrometheus, Grafana🔜 À venirPhase 8Semaine 8CI/CD + documentation finaleGitHub Actions🔜 À venir

✅ Phase 1 & 2 — Pipeline ETL
Ce que fait le pipeline
API CoinGecko (20 cryptos en temps réel)
        │
        ▼
  EXTRACT — requête HTTP avec retry automatique
        │
        ▼
  TRANSFORM — sélection des colonnes, typage, arrondi, validation
        │
        ▼
  LOAD — UPSERT PostgreSQL (pas de doublons)
Lancer le pipeline manuellement
bashsource venv/bin/activate
python3 etl/extract.py
Automatisation — cron (toutes les heures)
bash# Voir les tâches actives
crontab -l

# Contenu du crontab
0 * * * * /chemin/vers/venv/bin/python3 /chemin/vers/etl/extract.py >> ~/cron_crypto.log 2>&1
Schéma de la table PostgreSQL
sqlCREATE TABLE crypto_prices (
    id                          SERIAL PRIMARY KEY,
    name                        TEXT NOT NULL,
    symbol                      TEXT NOT NULL,
    current_price               NUMERIC(20, 2),
    market_cap                  BIGINT,
    total_volume                BIGINT,
    high_24h                    NUMERIC(20, 2),
    low_24h                     NUMERIC(20, 2),
    price_change_percentage_24h NUMERIC(10, 2),
    last_updated                TIMESTAMPTZ,
    UNIQUE (symbol, last_updated)
);
Données collectées

Source : API CoinGecko (gratuite)
Fréquence : toutes les heures
Volume : 20 cryptos par run
Stratégie : UPSERT — mise à jour si le prix existe déjà, insertion sinon


✅ Phase 3 — API REST (FastAPI)
Endpoints disponibles
MéthodeEndpointDescriptionGET/Health check — vérifie que l'API fonctionneGET/data/rawToutes les données brutes de la tableGET/data/cleanDernier prix de chaque crypto, sans doublonsGET/statsBest/worst performer 24h + statistiques marché
Documentation interactive
FastAPI génère automatiquement une documentation Swagger :
http://localhost:8000/docs
Lancer l'API
bashsource venv/bin/activate
cd api
uvicorn main:app --reload
Exemples de réponses
GET /data/clean
json{
  "data": [
    {
      "name": "Bitcoin",
      "symbol": "btc",
      "current_price": 77381.0,
      "market_cap": 1550280491898,
      "total_volume": 26258039993,
      "high_24h": 78024.0,
      "low_24h": 76757.0,
      "price_change_percentage_24h": -0.35,
      "last_updated": "2026-05-22T08:19:24+02:00"
    }
  ]
}
GET /stats
json{
  "best_performer":  { "name": "Hyperliquid", "symbol": "hype", "change_24h": 2.18 },
  "worst_performer": { "name": "Monero",      "symbol": "xmr",  "change_24h": -3.86 },
  "market": {
    "average_price":    4090.52,
    "total_volume":     110736302017,
    "total_market_cap": 2459583016180
  }
}

⚙️ Installation
Prérequis

Python 3.10+
PostgreSQL
Ubuntu / WSL

1. Cloner le projet
bashgit clone https://github.com/ton-user/CryptoPulse-Platform.git
cd CryptoPulse-Platform
2. Créer l'environnement virtuel
bashpython3 -m venv venv
source venv/bin/activate
3. Installer les dépendances
bashpip install -r requirements.txt
4. Configurer les variables d'environnement
Crée un fichier .env à la racine du projet :
envDB_HOST=localhost
DB_NAME=cryptopulse
DB_USER=postgres
DB_PASSWORD=ton_mot_de_passe
DB_PORT=5432
5. Initialiser la base de données
bashsudo -u postgres psql
sqlCREATE DATABASE cryptopulse;
6. Lancer le pipeline ETL
bashpython3 etl/extract.py
7. Lancer l'API
bashcd api
uvicorn main:app --reload

 Dépendances
txtrequests
pandas
psycopg2-binary
python-dotenv
fastapi
uvicorn


 Auteur
Projet personnel orienté DevOps / Cloud & Data Engineering.
Construit progressivement — une phase à la fois, une technologie à la fois.