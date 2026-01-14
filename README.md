# Research Article Scraper

## Description
Web scraper pour collecter les métadonnées d'articles scientifiques depuis IEEE, ACM et ScienceDirect.

## Structure du Projet
```
Data scraper/
├── spiders/
│   ├── __init__.py
│   ├── acm_spider.py
│   ├── ieee_spider.py
│   └── sciencedirect_spider.py
├── items.py
├── pipelines.py
├── selenium_middleware.py
├── settings.py
└── scrapy.cfg
```

## Installation

### 1. Installer les dépendances
```bash
pip install scrapy selenium pymongo
```

### 2. Installer MongoDB
- Télécharger: https://www.mongodb.com/try/download/community
- Installer et démarrer le service MongoDB

### 3. Vérifier MongoDB
```bash
# Windows
net start MongoDB

# Vérifier la connexion
mongosh
```

## Utilisation

### Scraper avec sortie JSON (sans MongoDB)
```bash
# ACM
python -m scrapy crawl acm -O acm_data.json

# IEEE
python -m scrapy crawl ieee -O ieee_data.json

# ScienceDirect
python -m scrapy crawl sciencedirect -O sciencedirect_data.json
```

### Scraper avec MongoDB (activé par défaut)
```bash
# Les données seront automatiquement stockées dans MongoDB
python -m scrapy crawl acm
python -m scrapy crawl ieee
python -m scrapy crawl sciencedirect
```

### Voir le navigateur pendant le scraping
Dans `settings.py`, ajouter:
```python
SELENIUM_HEADLESS = False
```

### Consulter les données dans MongoDB
```bash
mongosh
use research_db
db.articles.find().pretty()
db.articles.countDocuments()
```

## Configuration

### Mots-clés de recherche
Modifier dans chaque spider:
```python
keywords = ['Blockchain', 'Deep Learning', 'Big Data']
```

### MongoDB
Dans `settings.py`:
```python
MONGO_URI = 'mongodb://localhost:27017/'
MONGO_DATABASE = 'research_db'
```

### Délai entre requêtes
Dans `settings.py`:
```python
DOWNLOAD_DELAY = 3  # secondes
```

## Données Collectées
- Source (IEEE, ACM, ScienceDirect)
- Mot-clé de recherche
- Titre
- Lien
- Auteurs
- Année
- Abstract
- Journal
- Date de scraping

## Notes
- Les sites peuvent bloquer les requêtes trop fréquentes
- Selenium télécharge automatiquement ChromeDriver
- Limite: 10 articles par mot-clé par défaut
- Respecter les conditions d'utilisation des sites
