# CryptoPulse Platform

Plateforme de données cloud-native qui collecte les prix des 20 plus grosses cryptomonnaies en temps réel via l'API CoinGecko, les stocke dans PostgreSQL, et les expose via une API REST.

Projet CV orienté Data Engineering + DevOps/Cloud — construit progressivement sur 8 semaines.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    CryptoPulse Platform                 │
│                                                         │
│  ┌──────────────┐    ┌──────────────┐    ┌───────────┐  │
│  │ API CoinGecko│───▶│  ETL Python  │───▶│PostgreSQL │  │
│  │  (20 cryptos)│    │  (horaire)   │    └─────┬─────┘  │
│  └──────────────┘    └──────────────┘          │        │
│                                                ▼        │
│                                        ┌──────────────┐ │
│                                        │  API REST    │ │
│                                        │  (FastAPI)   │ │
│                                        └──────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## Structure

```
CryptoPulse-Platform/
├── api/
│   └── main.py        # Endpoints /data/raw /data/clean /stats
├── etl/
│   └── extract.py     # Extract → Transform → Load
├── config/
├── scripts/
├── data/
├── logs/
├── tests/
├── .env               # Non commité
├── requirements.txt
└── README.md
```

## Roadmap — 8 semaines

| Phase | Durée | Description | Stack | Statut |
|-------|-------|-------------|-------|--------|
| 1 | Semaine 1 | Source de données, nettoyage, stockage | Python, Pandas, PostgreSQL | ✅ Terminé |
| 2 | Semaine 2 | Pipeline ETL + automatisation cron | Python, PostgreSQL, Cron | ✅ Terminé |
| 3 | Semaine 2–3 | API REST exposition des données | FastAPI, uvicorn | ✅ Terminé |
| 4 | Semaine 3–4 | Conteneurisation complète | Docker, docker-compose | ⏳ En cours |
| 5 | Semaine 4–5 | Déploiement Kubernetes | Kubernetes, Minikube, Helm | 🔜 À venir |
| 6 | Semaine 6 | Infrastructure as Code | Terraform | 🔜 À venir |
| 7 | Semaine 7 | Monitoring production | Prometheus, Grafana | 🔜 À venir |
| 8 | Semaine 8 | CI/CD + documentation finale | GitHub Actions | 🔜 À venir |

---

## Phases 1 & 2 — Pipeline ETL

```
API CoinGecko (20 cryptos)
        │
        ▼  EXTRACT — requête HTTP avec retry automatique
        │
        ▼  TRANSFORM — sélection des colonnes, typage, arrondi, validation
        │
        ▼  LOAD — UPSERT PostgreSQL (pas de doublons)
```

**Lancer le pipeline manuellement**

```bash
source venv/bin/activate
python3 etl/extract.py
```

**Automatisation — cron toutes les heures**

```bash
crontab -l

0 * * * * /chemin/vers/venv/bin/python3 /chemin/vers/etl/extract.py >> ~/cron_crypto.log 2>&1
```

**Schéma PostgreSQL**

```sql
CREATE TABLE crypto_prices (
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
```

- Source : API CoinGecko (gratuite)
- Fréquence : toutes les heures
- Volume : 20 cryptos par run
- Stratégie : UPSERT — mise à jour si existant, insertion sinon

---

## Phase 3 — API REST (FastAPI)

```bash
source venv/bin/activate
cd api
uvicorn main:app --reload
```

Documentation Swagger : `http://localhost:8000/docs`

**Endpoints**

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/` | Health check |
| GET | `/data/raw` | Toutes les données brutes |
| GET | `/data/clean` | Dernier prix de chaque crypto, sans doublons |
| GET | `/stats` | Best/worst performer 24h + statistiques marché |

**GET /data/clean**

```json
{
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
```

**GET /stats**

```json
{
  "best_performer":  { "name": "Hyperliquid", "symbol": "hype", "change_24h": 2.18 },
  "worst_performer": { "name": "Monero",      "symbol": "xmr",  "change_24h": -3.86 },
  "market": {
    "average_price":    4090.52,
    "total_volume":     110736302017,
    "total_market_cap": 2459583016180
  }
}
```

---

## Installation

**Prérequis :** Python 3.10+, PostgreSQL, Ubuntu / WSL

```bash
git clone https://github.com/ton-user/CryptoPulse-Platform.git
cd CryptoPulse-Platform
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Créer un fichier `.env` à la racine :

```env
DB_HOST=localhost
DB_NAME=cryptopulse
DB_USER=postgres
DB_PASSWORD=ton_mot_de_passe
DB_PORT=5432
```

```bash
sudo -u postgres psql -c "CREATE DATABASE cryptopulse;"
python3 etl/extract.py
```

## Dépendances

```
requests
pandas
psycopg2-binary
python-dotenv
fastapi
uvicorn
```