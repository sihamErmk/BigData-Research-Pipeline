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
    fieldnames = ['titre', 'auteurs', 'annee', 'source', 'lien', 'resume']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
    
    writer.writeheader()
    for article in articles:
        writer.writerow({
            'titre': article.get('titre', ''),
            'auteurs': article.get('auteurs', ''),
            'annee': article.get('annee', ''),
            'source': article.get('source', ''),
            'lien': article.get('lien', ''),
            'resume': article.get('resume', '')
        })

print(f"✅ Export terminé! {collection.count_documents({})} articles exportés vers 'articles.csv'")
