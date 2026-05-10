# CryptoPulse Platform

## Description

CryptoPulse Platform est un projet de type **Data Engineering + DevOps/Cloud** ayant pour objectif de construire une plateforme de collecte, traitement et exposition de données crypto en temps réel.

Ce projet simule une architecture moderne utilisée en entreprise avec pipeline de données, API et infrastructure conteneurisée.

---

##  Étape actuelle du projet

À ce stade, le projet contient :

* 📁 Structure de base du projet
* 🐍 Environnement Python virtuel (`venv`)
* 📦 Initialisation des dépendances
* 🧪 Préparation du pipeline de données (ETL à venir)

---

##  Structure du projet

```
CryptoPulse-Platform/
│
├── venv/              # Environnement virtuel Python
├── app/               # API (future FastAPI)
├── etl/               # Pipeline ETL (extraction, transformation, chargement)
├── config/            # Configuration (API, DB)
├── scripts/           # Scripts utilitaires
├── data/              # Données brutes et traitées
├── logs/              # Logs du système
├── tests/             # Tests unitaires
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

##  Mise en place de l’environnement Python

### 1. Création de l’environnement virtuel

```bash
python -m venv venv
```

### 2. Activation de l’environnement

Sous Linux / WSL :

```bash
source venv/bin/activate
```

Sous Windows :

```bash
venv\Scripts\activate
```

---

##  Installation des dépendances de base

```bash
pip install requests pandas psycopg2-binary
```

---

##  Objectif final du projet

Construire une plateforme complète incluant :

* 🔄 Pipeline ETL (Python)
* 🗄️ Base de données PostgreSQL
* 🚀 API REST (FastAPI)
* 📦 Conteneurisation avec Docker
* ☸️ Déploiement sur Kubernetes
* 📊 Monitoring avec Prometheus & Grafana
* 🔁 CI/CD avec GitHub Actions
* 🏗️ Infrastructure as Code avec Terraform

---

##  Statut actuel

✔ Projet initialisé
✔ Environnement Python configuré
⏳ Développement du pipeline ETL en cours

---

## 👨‍💻 Auteur

Projet personnel orienté **DevOps / Cloud & Data Engineering**.
