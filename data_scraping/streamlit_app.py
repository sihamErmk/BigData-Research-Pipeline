import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pymongo import MongoClient
from datetime import datetime, timedelta
import subprocess
import os
from collections import Counter
import time

# Configuration de la page
st.set_page_config(
    page_title="Big Data Research Pipeline",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
    <style>
    .main {
        background-color: #f5f7fa;
    }
    .stMetric {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Connexion MongoDB
@st.cache_resource
def get_mongodb_connection():
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['research_db']
        return db
    except Exception as e:
        st.error(f"Erreur de connexion MongoDB: {e}")
        return None

# Charger les données
@st.cache_data(ttl=60)
def load_data():
    db = get_mongodb_connection()
    if db is None:
        return pd.DataFrame()

    articles = list(db.articles.find())
    if not articles:
        return pd.DataFrame()

    df = pd.DataFrame(articles)

    # Nettoyer les données
    if 'annee' in df.columns:
        df['annee'] = pd.to_numeric(df['annee'], errors='coerce')

    if 'date_scraping' in df.columns:
        df['date_scraping'] = pd.to_datetime(df['date_scraping'])

    return df

# Fonction pour lancer un spider
def run_spider(spider_name):
    script_path = os.path.expanduser("~/BigData-Research-Pipeline/data_scraping")
    venv_python = os.path.expanduser("~/BigData-Research-Pipeline/venv/bin/python")

    try:
        process = subprocess.Popen(
            [venv_python, "-m", "scrapy", "crawl", spider_name],
            cwd=script_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return process
    except Exception as e:
        st.error(f"Erreur lors du lancement: {e}")
        return None

# Sidebar Navigation
with st.sidebar:
    st.title("Big Data Pipeline")

    page = st.radio(
        "Navigation",
        ["Accueil", "Scraping", "Dashboard BI", "Analyses Avancées", "Configuration"]
    )

    st.divider()

    # Stats en temps réel
    df = load_data()
    if not df.empty:
        st.metric("Total Articles", len(df))
        st.metric("Sources", df['source'].nunique() if 'source' in df.columns else 0)
        if 'date_scraping' in df.columns:
            recent = df[df['date_scraping'] > datetime.now() - timedelta(hours=24)]
            st.metric("Dernières 24h", len(recent))

# PAGE 1: ACCUEIL
if page == "Accueil":
    st.title("Big Data Research Pipeline")
    st.markdown("### Plateforme d'analyse des publications scientifiques")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>Scraping</h3>
            <p>Collecte automatique de données depuis IEEE, ACM, ArXiv et Scholar</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <h3>Visualisation</h3>
            <p>Tableaux de bord interactifs et analyses en temps réel</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="metric-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
            <h3>Analyse BI</h3>
            <p>Insights et tendances de recherche</p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # Aperçu des données
    df = load_data()
    if not df.empty:
        st.subheader("Aperçu des Données")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Articles", len(df))
        with col2:
            st.metric("Sources Uniques", df['source'].nunique() if 'source' in df.columns else 0)
        with col3:
            if 'annee' in df.columns:
                valid_years = df['annee'].dropna()
                if len(valid_years) > 0:
                    st.metric("Année Moyenne", f"{int(valid_years.mean())}")
        with col4:
            if 'auteurs' in df.columns:
                all_authors = [author for authors in df['auteurs'].dropna() for author in authors if isinstance(authors, list)]
                st.metric("Auteurs Uniques", len(set(all_authors)))

        # Graphique rapide
        if 'source' in df.columns:
            fig = px.pie(df, names='source', title='Distribution par Source')
            st.plotly_chart(fig, width='stretch')
    else:
        st.info("Aucune donnée disponible. Lancez un scraping pour commencer!")

# PAGE 2: SCRAPING
elif page == "Scraping":
    st.title("Module de Scraping")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Lancer un Spider")

        spiders = {
            "scholar": "Google Scholar (Rapide, sans Selenium)",
            "arxiv": "ArXiv (Recommandé)",
            "ieee": "IEEE Xplore (Nécessite Chrome)",
            "acm": "ACM Digital Library (Peut être bloqué)",
            "sciencedirect": "ScienceDirect (Souvent bloqué)"
        }

        selected_spider = st.selectbox(
            "Sélectionner un spider",
            options=list(spiders.keys()),
            format_func=lambda x: spiders[x]
        )

        col_btn1, col_btn2 = st.columns(2)

        with col_btn1:
            if st.button("Lancer le Scraping", type="primary", use_container_width=True):
                with st.spinner(f"Lancement du spider {selected_spider}..."):
                    process = run_spider(selected_spider)
                    if process:
                        st.success(f"Spider {selected_spider} lancé!")
                        st.info("Le scraping s'exécute en arrière-plan. Vérifiez les logs dans le terminal.")

                        # Afficher un placeholder pour les logs
                        with st.expander("Voir les logs (limité)"):
                            log_placeholder = st.empty()
                            for _ in range(10):
                                time.sleep(1)
                                if process.poll() is not None:
                                    break
                                log_placeholder.text("Scraping en cours...")

        with col_btn2:
            if st.button("Rafraîchir les Données", use_container_width=True):
                st.cache_data.clear()
                st.rerun()

    with col2:
        st.subheader("Statistiques")
        db = get_mongodb_connection()
        if db is not None:  # FIX ICI
            total = db.articles.count_documents({})
            st.metric("Total Articles", total)

            # Articles par source
            pipeline = [
                {"$group": {"_id": "$source", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            sources = list(db.articles.aggregate(pipeline))
            for doc in sources:
                st.write(f"**{doc['_id']}**: {doc['count']}")

    st.divider()

    # Afficher les derniers articles scrapés
    st.subheader("Derniers Articles Scrapés")
    df = load_data()
    if not df.empty and 'date_scraping' in df.columns:
        recent_df = df.nlargest(10, 'date_scraping')
        for idx, row in recent_df.iterrows():
            with st.expander(f"{row.get('titre', 'Sans titre')[:80]}..."):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Source**: {row.get('source', 'N/A')}")
                    st.write(f"**Année**: {row.get('annee', 'N/A')}")
                with col2:
                    st.write(f"**Mot-clé**: {row.get('mot_cle_recherche', 'N/A')}")
                    st.write(f"**Scraped**: {row.get('date_scraping', 'N/A')}")

                if row.get('lien'):
                    st.markdown(f"[Lien vers l'article]({row['lien']})")

# PAGE 3: DASHBOARD BI
elif page == "Dashboard BI":
    st.title("Dashboard Business Intelligence")

    df = load_data()

    if df.empty:
        st.warning("Aucune donnée disponible. Veuillez lancer un scraping d'abord.")
    else:
        # Filtres
        st.sidebar.subheader("Filtres")

        sources = ['Toutes'] + list(df['source'].unique()) if 'source' in df.columns else ['Toutes']
        selected_source = st.sidebar.selectbox("Source", sources)

        if selected_source != 'Toutes':
            df = df[df['source'] == selected_source]

        # KPIs
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Articles", len(df))

        with col2:
            if 'annee' in df.columns:
                valid_years = df['annee'].dropna()
                if len(valid_years) > 0:
                    st.metric("Année Moyenne", f"{int(valid_years.mean())}")

        with col3:
            if 'auteurs' in df.columns:
                all_authors = [author for authors in df['auteurs'].dropna() for author in authors if isinstance(authors, list)]
                st.metric("Auteurs", len(set(all_authors)))

        with col4:
            if 'abstract' in df.columns:
                with_abstract = df['abstract'].notna().sum()
                st.metric("Avec Abstract", f"{with_abstract/len(df)*100:.1f}%")

        st.divider()

        # Graphiques
        col1, col2 = st.columns(2)

        with col1:
            # Distribution par source
            if 'source' in df.columns:
                source_counts = df['source'].value_counts()
                fig = px.pie(
                    values=source_counts.values,
                    names=source_counts.index,
                    title="Distribution par Source",
                    hole=0.4
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, width='stretch')

        with col2:
            # Top mots-clés
            if 'mot_cle_recherche' in df.columns:
                keyword_counts = df['mot_cle_recherche'].value_counts().head(10)
                fig = px.bar(
                    x=keyword_counts.values,
                    y=keyword_counts.index,
                    orientation='h',
                    title="Top 10 Mots-clés",
                    labels={'x': 'Nombre', 'y': 'Mot-clé'}
                )
                st.plotly_chart(fig, width='stretch')

        # Évolution temporelle
        if 'annee' in df.columns:
            st.subheader("Évolution Temporelle des Publications")

            year_counts = df.groupby('annee').size().reset_index(name='count')
            year_counts = year_counts.dropna()

            if len(year_counts) > 0:
                fig = px.line(
                    year_counts,
                    x='annee',
                    y='count',
                    markers=True,
                    title="Publications par Année"
                )
                fig.update_layout(xaxis_title="Année", yaxis_title="Nombre de Publications")
                st.plotly_chart(fig, width='stretch')

        # Top Auteurs
        if 'auteurs' in df.columns:
            st.subheader("Top 20 Auteurs les Plus Productifs")

            all_authors = []
            for authors in df['auteurs'].dropna():
                if isinstance(authors, list):
                    all_authors.extend(authors)

            if all_authors:
                author_counts = Counter(all_authors).most_common(20)
                author_df = pd.DataFrame(author_counts, columns=['Auteur', 'Publications'])

                fig = px.bar(
                    author_df,
                    x='Publications',
                    y='Auteur',
                    orientation='h',
                    title="Top 20 Auteurs"
                )
                st.plotly_chart(fig, width='stretch')

        # Table des données
        st.subheader("Table des Données")

        display_columns = ['titre', 'source', 'annee', 'mot_cle_recherche']
        available_columns = [col for col in display_columns if col in df.columns]

        if available_columns:
            st.dataframe(
                df[available_columns].head(50),
                use_container_width=True,
                height=400
            )

# PAGE 4: ANALYSES AVANCÉES
elif page == "Analyses Avancées":
    st.title("Analyses Avancées")

    df = load_data()

    if df.empty:
        st.warning("Aucune donnée disponible.")
    else:
        tab1, tab2, tab3 = st.tabs(["Analyse par Domaine", "Collaborations", "Tendances"])

        with tab1:
            st.subheader("Analyse par Domaine de Recherche")

            if 'mot_cle_recherche' in df.columns:
                selected_keyword = st.selectbox(
                    "Sélectionner un domaine",
                    df['mot_cle_recherche'].unique()
                )

                keyword_df = df[df['mot_cle_recherche'] == selected_keyword]

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Publications", len(keyword_df))
                with col2:
                    if 'annee' in keyword_df.columns:
                        valid_years = keyword_df['annee'].dropna()
                        if len(valid_years) > 0:
                            st.metric("Année Médiane", f"{int(valid_years.median())}")
                with col3:
                    if 'source' in keyword_df.columns:
                        st.metric("Sources", keyword_df['source'].nunique())

                # Évolution dans le temps
                if 'annee' in keyword_df.columns:
                    year_trend = keyword_df.groupby('annee').size().reset_index(name='count')
                    year_trend = year_trend.dropna()

                    if len(year_trend) > 0:
                        fig = px.area(
                            year_trend,
                            x='annee',
                            y='count',
                            title=f"Évolution de '{selected_keyword}'"
                        )
                        st.plotly_chart(fig, width='stretch')

        with tab2:
            st.subheader("Réseau de Collaborations")

            if 'auteurs' in df.columns:
                st.info("Analyse des co-publications entre auteurs")

                # Trouver les co-auteurs
                coauthor_pairs = []
                for authors in df['auteurs'].dropna():
                    if isinstance(authors, list) and len(authors) > 1:
                        for i in range(len(authors)):
                            for j in range(i+1, len(authors)):
                                coauthor_pairs.append((authors[i], authors[j]))

                if coauthor_pairs:
                    coauthor_counts = Counter(coauthor_pairs).most_common(10)

                    st.write("### Top 10 Collaborations")
                    for (author1, author2), count in coauthor_counts:
                        st.write(f"**{author1}** <-> **{author2}**: {count} publications")

        with tab3:
            st.subheader("Tendances de Recherche")

            if 'annee' in df.columns and 'mot_cle_recherche' in df.columns:
                # Heatmap des tendances
                trend_data = df.groupby(['annee', 'mot_cle_recherche']).size().reset_index(name='count')
                trend_data = trend_data.dropna()

                if len(trend_data) > 0:
                    pivot_data = trend_data.pivot(index='mot_cle_recherche', columns='annee', values='count').fillna(0)

                    fig = px.imshow(
                        pivot_data,
                        labels=dict(x="Année", y="Domaine", color="Publications"),
                        title="Heatmap des Tendances de Recherche",
                        aspect="auto"
                    )
                    st.plotly_chart(fig, width='stretch')

# PAGE 5: CONFIGURATION
elif page == "Configuration":
    st.title("Configuration du Système")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Base de Données")

        db = get_mongodb_connection()
        if db is not None:  # FIX ICI
            st.success("MongoDB connecté")

            if st.button("Nettoyer la Base de Données"):
                if st.checkbox("Confirmer la suppression"):
                    db.articles.delete_many({})
                    st.success("Base de données nettoyée!")
                    st.cache_data.clear()
        else:
            st.error("MongoDB non connecté")

    with col2:
        st.subheader("Export des Données")

        df = load_data()
        if not df.empty:
            csv = df.to_csv(index=False)
            st.download_button(
                label="Télécharger CSV",
                data=csv,
                file_name=f"research_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

    st.divider()

    st.subheader("Informations Système")

    col1, col2 = st.columns(2)
    with col1:
        st.write("**Python Version**:", "3.10+")
        st.write("**Streamlit Version**:", st.__version__)

    with col2:
        df = load_data()
        st.write("**Articles en Base**:", len(df))
        st.write("**Dernière MAJ**:", datetime.now().strftime("%Y-%m-%d %H:%M"))
