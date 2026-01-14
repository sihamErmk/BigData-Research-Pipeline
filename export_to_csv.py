import csv
from pymongo import MongoClient

# Connexion à MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['research_db']
collection = db['articles']

# Récupérer tous les articles
articles = collection.find()

# Exporter vers CSV
with open('articles.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['_id', 'source', 'mot_cle_recherche', 'titre', 'lien', 'auteurs', 'annee', 'abstract', 'journal', 'date_scraping']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
    
    writer.writeheader()
    for article in articles:
        # Convertir la liste d'auteurs en chaîne
        auteurs = article.get('auteurs', [])
        if isinstance(auteurs, list):
            auteurs = ', '.join(auteurs)
        
        writer.writerow({
            '_id': str(article.get('_id', '')),
            'source': article.get('source', ''),
            'mot_cle_recherche': article.get('mot_cle_recherche', ''),
            'titre': article.get('titre', ''),
            'lien': article.get('lien', ''),
            'auteurs': auteurs,
            'annee': article.get('annee', ''),
            'abstract': article.get('abstract', ''),
            'journal': article.get('journal', ''),
            'date_scraping': article.get('date_scraping', '')
        })

print(f"✅ Export terminé! {collection.count_documents({})} articles exportés vers 'articles.csv'")
