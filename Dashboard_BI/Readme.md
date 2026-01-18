# BigData Research Pipeline - Dashboard BI et Analyses Avancées

Ce projet est une application de Business Intelligence développée avec Streamlit. Elle permet d'explorer, de filtrer et d'analyser des données issues de publications scientifiques stockées dans une base de données MongoDB.

## Fonctionnalités principales

### Dashboard BI
- Indicateurs clés (KPI) : Publications, Année Moyenne, nombre d'Auteurs et taux d'Abstracts.
- Répartition par Source : Visualisation des parts de marché des différentes plateformes.
- Top 10 Mots-clés : Les thématiques les plus populaires dans la recherche.
- Évolution Temporelle : Analyse du volume de publications par année.

### Analyses Avancées
- Analyse par Domaine : Exploration détaillée par mot-clé (Data Mining, AI, Deep Learning).
- Collaborations Scientifiques : Identification des auteurs et partenariats les plus actifs.

## Aperçu du Dashboard

### Statistiques Globales
![Distribution par Source](Dashboard_BI/chart1.png)
*Répartition des articles par source.*

![Top 10 Mots-clés](Dashboard_BI/chart2.png)
*Les 10 mots-clés les plus fréquents.*

![Evolution Temporelle](Dashboard_BI/Chart3.png)
*Progression historique des publications.*

### Analyses Spécifiques par Domaine
![Analyse Data Mining](Dashboard_BI/chart5.png)
*Focus sur l'évolution du Data Mining.*

![Analyse Artificial Intelligence](Dashboard_BI/chart6.png)
*Focus sur l'évolution de l'Intelligence Artificielle.*

![Analyse Deep Learning](Dashboard_BI/chart7.png)
*Focus sur l'évolution du Deep Learning.*

### Collaborations et Auteurs
![Top Auteurs](Dashboard_BI/Chart4.png)
*Classement des auteurs les plus prolifiques.*

## Technologies utilisées

- Python (Streamlit, Pandas, Plotly)
- MongoDB (Base de données NoSQL)
- PyMongo (Driver de connexion)

## Installation

1. Assurez-vous d'avoir MongoDB installé et configuré.
2. Installez les dépendances nécessaires :
   ```bash
   pip install -r Dashboard_BI/requirements.txt
