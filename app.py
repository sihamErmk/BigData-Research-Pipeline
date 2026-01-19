"""
Application Streamlit Complète pour Big Data Research Pipeline
Avec intégration de l'analyse Spark - VERSION CORRIGÉE
"""

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
import sys

# ================================================================================
# CONFIGURATION DE LA PAGE
# ================================================================================
st.set_page_config(
    page_title="Big Data Research Pipeline",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================================================================================
# CSS PERSONNALISÉ
# ================================================================================
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
    .log-container {
        background-color: #1e1e1e;
        color: #d4d4d4;
        padding: 15px;
        border-radius: 5px;
        font-family: monospace;
        font-size: 12px;
        max-height: 400px;
        overflow-y: auto;
        white-space: pre-wrap;
    }
    </style>
""", unsafe_allow_html=True)

# ================================================================================
# CONNEXION MONGODB
# ================================================================================
@st.cache_resource
def get_mongodb_connection():
    try:
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        # Test de la connexion
        client.server_info()
        db = client['research_db']
        return db
    except Exception as e:
        st.error(f"Erreur de connexion MongoDB: {e}")
        return None

# ================================================================================
# CHARGEMENT DES DONNÉES
# ================================================================================
@st.cache_data(ttl=60)
def load_data():
    db = get_mongodb_connection()
    if db is None:
        return pd.DataFrame()

    try:
        articles = list(db.articles.find().limit(10000))
        if not articles:
            return pd.DataFrame()

        df = pd.DataFrame(articles)

        if 'annee' in df.columns:
            df['annee'] = pd.to_numeric(df['annee'], errors='coerce')

        if 'date_scraping' in df.columns:
            df['date_scraping'] = pd.to_datetime(df['date_scraping'], errors='coerce')

        return df
    except Exception as e:
        st.error(f"Erreur chargement données: {e}")
        return pd.DataFrame()

# ================================================================================
# CHARGEMENT DES RÉSULTATS SPARK
# ================================================================================
@st.cache_data(ttl=300)
def load_spark_results():
    results_dir = os.path.expanduser("~/BigData-Research-Pipeline/results")
    results = {}
    
    files = {
        'publications_annee': 'publications_par_annee.csv',
        'publications_categorie': 'publications_par_categorie.csv',
        'publications_source': 'publications_par_source.csv',
        'evolution_categorie': 'evolution_categorie_annee.csv',
        'top_auteurs': 'top_auteurs.csv',
        'tendances_recentes': 'tendances_recentes.csv',
        'signaux_faibles': 'signaux_faibles_croissance.csv',
        'metriques_globales': 'metriques_globales.csv'
    }
    
    for key, filename in files.items():
        filepath = os.path.join(results_dir, filename)
        if os.path.exists(filepath):
            try:
                results[key] = pd.read_csv(filepath)
            except Exception as e:
                st.warning(f"Erreur lecture {filename}: {e}")
    
    return results

# ================================================================================
# LANCER UN SPIDER
# ================================================================================
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
        st.error(f"Erreur lancement spider: {e}")
        return None

# ================================================================================
# LANCER L'ANALYSE SPARK - VERSION CORRIGÉE
# ================================================================================
def run_spark_analysis():
    script_path = os.path.expanduser("~/BigData-Research-Pipeline/DataAnalysis/scripts")
    analysis_script = os.path.join(script_path, "spark_analysis.py")
    
    if not os.path.exists(analysis_script):
        st.error(f"Script Spark introuvable: {analysis_script}")
        return None
    
    try:
        # Version corrigée avec le bon connecteur MongoDB
        process = subprocess.Popen(
            [
                "spark-submit",
                "--packages", "org.mongodb.spark:mongo-spark-connector_2.12:10.1.1",
                "--conf", "spark.mongodb.input.uri=mongodb://localhost:27017/research_db.articles",
                "--conf", "spark.mongodb.output.uri=mongodb://localhost:27017/research_db.articles",
                analysis_script
            ],
            cwd=script_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        return process
    except Exception as e:
        st.error(f"Erreur lancement Spark: {e}")
        return None

# ================================================================================
# SIDEBAR NAVIGATION
# ================================================================================
with st.sidebar:
    st.title("Big Data Pipeline")
    
    page = st.radio(
        "Navigation",
        [
            "Accueil", 
            "Scraping", 
            "Dashboard BI", 
            "Analyse Spark",
            "Analyses Avancees", 
            "Configuration"
        ]
    )
    
    st.divider()
    
    # Vérification MongoDB
    db = get_mongodb_connection()
    if db is not None:
        st.success("MongoDB connecte")
    else:
        st.error("MongoDB deconnecte")
    
    df = load_data()
    if not df.empty:
        st.metric("Total Articles", len(df))
        st.metric("Sources", df['source'].nunique() if 'source' in df.columns else 0)
        if 'date_scraping' in df.columns:
            recent = df[df['date_scraping'] > datetime.now() - timedelta(hours=24)]
            st.metric("Dernieres 24h", len(recent))

# ================================================================================
# PAGE 1: ACCUEIL
# ================================================================================
if page == "Accueil":
    st.title("Big Data Research Pipeline")
    st.markdown("### Plateforme d'analyse des publications scientifiques")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>Scraping</h3>
            <p>Collecte automatique depuis IEEE, ACM, ArXiv et Scholar</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <h3>Visualisation</h3>
            <p>Tableaux de bord interactifs</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
            <h3>Analyse BI</h3>
            <p>Insights avec Spark</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    df = load_data()
    if not df.empty:
        st.subheader("Apercu des Donnees")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Articles", len(df))
        with col2:
            st.metric("Sources Uniques", df['source'].nunique() if 'source' in df.columns else 0)
        with col3:
            if 'annee' in df.columns:
                valid_years = df['annee'].dropna()
                if len(valid_years) > 0:
                    st.metric("Annee Moyenne", f"{int(valid_years.mean())}")
        with col4:
            if 'auteurs' in df.columns:
                all_authors = [author for authors in df['auteurs'].dropna() for author in authors if isinstance(authors, list)]
                st.metric("Auteurs Uniques", len(set(all_authors)))
        
        if 'source' in df.columns:
            fig = px.pie(df, names='source', title='Distribution par Source')
            st.plotly_chart(fig, width='stretch')
    else:
        st.info("Aucune donnee disponible. Lancez un scraping pour commencer!")

# ================================================================================
# PAGE 2: SCRAPING
# ================================================================================
elif page == "Scraping":
    st.title("Module de Scraping")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Lancer un Spider")
        
        spiders = {
            "scholar": "Google Scholar (Rapide)",
            "arxiv": "ArXiv (Recommande)",
            "ieee": "IEEE Xplore",
            "acm": "ACM Digital Library"
        }
        
        selected_spider = st.selectbox(
            "Selectionner un spider",
            options=list(spiders.keys()),
            format_func=lambda x: spiders[x]
        )
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("Lancer le Scraping", type="primary"):
                with st.spinner(f"Lancement du spider {selected_spider}..."):
                    process = run_spider(selected_spider)
                    if process:
                        st.success(f"Spider {selected_spider} lance!")
        
        with col_btn2:
            if st.button("Rafraichir"):
                st.cache_data.clear()
                st.rerun()
    
    with col2:
        st.subheader("Statistiques")
        db = get_mongodb_connection()
        if db is not None:
            total = db.articles.count_documents({})
            st.metric("Total Articles", total)
            
            pipeline = [
                {"$group": {"_id": "$source", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            sources = list(db.articles.aggregate(pipeline))
            for doc in sources:
                st.write(f"**{doc['_id']}**: {doc['count']}")
    
    st.divider()
    
    st.subheader("Derniers Articles")
    df = load_data()
    if not df.empty and 'date_scraping' in df.columns:
        recent_df = df.nlargest(10, 'date_scraping')
        for idx, row in recent_df.iterrows():
            with st.expander(f"{row.get('titre', 'Sans titre')[:80]}..."):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Source**: {row.get('source', 'N/A')}")
                    st.write(f"**Annee**: {row.get('annee', 'N/A')}")
                with col2:
                    st.write(f"**Mot-cle**: {row.get('mot_cle_recherche', 'N/A')}")
                
                if row.get('lien'):
                    st.markdown(f"[Lien]({row['lien']})")

# ================================================================================
# PAGE 3: DASHBOARD BI
# ================================================================================
elif page == "Dashboard BI":
    st.title("Dashboard Business Intelligence")
    
    df = load_data()
    
    if df.empty:
        st.warning("Aucune donnee disponible.")
    else:
        st.sidebar.subheader("Filtres")
        
        sources = ['Toutes'] + list(df['source'].unique()) if 'source' in df.columns else ['Toutes']
        selected_source = st.sidebar.selectbox("Source", sources)
        
        if selected_source != 'Toutes':
            df = df[df['source'] == selected_source]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Articles", len(df))
        
        with col2:
            if 'annee' in df.columns:
                valid_years = df['annee'].dropna()
                if len(valid_years) > 0:
                    st.metric("Annee Moyenne", f"{int(valid_years.mean())}")
        
        with col3:
            if 'auteurs' in df.columns:
                all_authors = [author for authors in df['auteurs'].dropna() for author in authors if isinstance(authors, list)]
                st.metric("Auteurs", len(set(all_authors)))
        
        with col4:
            if 'abstract' in df.columns:
                with_abstract = df['abstract'].notna().sum()
                st.metric("Avec Abstract", f"{with_abstract/len(df)*100:.1f}%")
        
        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'source' in df.columns:
                source_counts = df['source'].value_counts()
                fig = px.pie(
                    values=source_counts.values,
                    names=source_counts.index,
                    title="Distribution par Source",
                    hole=0.4
                )
                st.plotly_chart(fig, width='stretch')
        
        with col2:
            if 'mot_cle_recherche' in df.columns:
                keyword_counts = df['mot_cle_recherche'].value_counts().head(10)
                fig = px.bar(
                    x=keyword_counts.values,
                    y=keyword_counts.index,
                    orientation='h',
                    title="Top 10 Mots-cles"
                )
                st.plotly_chart(fig, width='stretch')
        
        if 'annee' in df.columns:
            st.subheader("Evolution Temporelle")
            
            year_counts = df.groupby('annee').size().reset_index(name='count')
            year_counts = year_counts.dropna()
            
            if len(year_counts) > 0:
                fig = px.line(
                    year_counts,
                    x='annee',
                    y='count',
                    markers=True,
                    title="Publications par Annee"
                )
                st.plotly_chart(fig, width='stretch')
        
        if 'auteurs' in df.columns:
            st.subheader("Top 20 Auteurs")
            
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
                    orientation='h'
                )
                st.plotly_chart(fig, width='stretch')
        
        st.subheader("Table des Donnees")
        
        display_columns = ['titre', 'source', 'annee', 'mot_cle_recherche']
        available_columns = [col for col in display_columns if col in df.columns]
        
        if available_columns:
            st.dataframe(df[available_columns].head(50), width='stretch', height=400)

# ================================================================================
# PAGE 4: ANALYSE SPARK
# ================================================================================
elif page == "Analyse Spark":
    st.title("Analyse Big Data avec Apache Spark")
    
    st.markdown("Cette page presente les resultats de l'analyse PySpark.")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("Lancer l'Analyse Spark", type="primary"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            log_placeholder = st.empty()
            
            status_text.text("Demarrage de Spark...")
            progress_bar.progress(10)
            
            process = run_spark_analysis()
            
            if process:
                logs = []
                status_text.text("Execution en cours...")
                progress_bar.progress(30)
                
                # Lecture des logs en temps réel
                while True:
                    line = process.stderr.readline()
                    if line == '' and process.poll() is not None:
                        break
                    if line:
                        logs.append(line.strip())
                        # Afficher les 30 dernières lignes
                        recent_logs = logs[-30:]
                        log_text = "\n".join(recent_logs)
                        log_placeholder.markdown(
                            f'<div class="log-container">{log_text}</div>', 
                            unsafe_allow_html=True
                        )
                
                progress_bar.progress(90)
                
                if process.returncode == 0:
                    progress_bar.progress(100)
                    status_text.empty()
                    log_placeholder.empty()
                    st.success("Analyse Spark terminee avec succes!")
                    st.cache_data.clear()
                    time.sleep(1)
                    st.rerun()
                else:
                    progress_bar.empty()
                    status_text.empty()
                    st.error("Erreur lors de l'execution Spark")
                    st.markdown("**Logs d'erreur:**")
                    with st.expander("Voir les logs complets", expanded=True):
                        st.code("\n".join(logs), language="log")
    
    st.divider()
    
    results = load_spark_results()
    
    if not results:
        st.warning("Aucun resultat Spark disponible. Lancez l'analyse d'abord.")
    else:
        if 'metriques_globales' in results:
            st.subheader("Metriques Globales")
            
            metrics_df = results['metriques_globales']
            
            cols = st.columns(len(metrics_df))
            for idx, row in metrics_df.iterrows():
                with cols[idx % len(cols)]:
                    st.metric(row['Métrique'], row['Valeur'])
        
        st.divider()
        
        tab1, tab2, tab3, tab4 = st.tabs([
            "Evolution Temporelle",
            "Categories",
            "Top Auteurs",
            "Tendances"
        ])
        
        with tab1:
            if 'publications_annee' in results:
                st.subheader("Publications par Annee")
                
                pub_annee = results['publications_annee']
                
                fig = px.line(
                    pub_annee,
                    x='annee_num',
                    y='nombre_publications',
                    markers=True,
                    title="Evolution des Publications"
                )
                st.plotly_chart(fig, width='stretch')
                st.dataframe(pub_annee, width='stretch')
            
            if 'evolution_categorie' in results:
                st.subheader("Evolution par Categorie")
                
                evolution = results['evolution_categorie']
                
                fig = px.line(
                    evolution,
                    x='annee_num',
                    y='nombre_publications',
                    color='categorie',
                    markers=True,
                    title="Tendances par Categorie"
                )
                st.plotly_chart(fig, width='stretch')
                
                pivot_data = evolution.pivot(
                    index='categorie',
                    columns='annee_num',
                    values='nombre_publications'
                ).fillna(0)
                
                fig_heat = px.imshow(
                    pivot_data,
                    labels=dict(x="Annee", y="Categorie", color="Publications"),
                    aspect="auto",
                    title="Heatmap Categorie-Annee"
                )
                st.plotly_chart(fig_heat, width='stretch')
        
        with tab2:
            col1, col2 = st.columns(2)
            
            with col1:
                if 'publications_categorie' in results:
                    st.subheader("Par Categorie")
                    
                    pub_cat = results['publications_categorie']
                    
                    fig = px.bar(
                        pub_cat,
                        x='nombre_publications',
                        y='categorie',
                        orientation='h',
                        title="Distribution par Categorie"
                    )
                    st.plotly_chart(fig, width='stretch')
                    st.dataframe(pub_cat, width='stretch')
            
            with col2:
                if 'publications_source' in results:
                    st.subheader("Par Source")
                    
                    pub_source = results['publications_source']
                    
                    fig = px.pie(
                        pub_source,
                        values='nombre_publications',
                        names='source',
                        hole=0.4,
                        title="Repartition par Source"
                    )
                    st.plotly_chart(fig, width='stretch')
                    st.dataframe(pub_source, width='stretch')
        
        with tab3:
            if 'top_auteurs' in results:
                st.subheader("Top Auteurs")
                
                top_auteurs = results['top_auteurs'].head(30)
                
                fig = px.bar(
                    top_auteurs.head(20),
                    x='nombre_publications',
                    y='auteur',
                    orientation='h',
                    title="Top 20 Auteurs"
                )
                st.plotly_chart(fig, width='stretch')
                st.dataframe(top_auteurs, width='stretch', height=400)
        
        with tab4:
            col1, col2 = st.columns(2)
            
            with col1:
                if 'tendances_recentes' in results:
                    st.subheader("Tendances Recentes")
                    
                    tendances = results['tendances_recentes']
                    
                    fig = px.bar(
                        tendances,
                        x='nombre_publications',
                        y='categorie',
                        orientation='h',
                        title="Categories Emergentes"
                    )
                    st.plotly_chart(fig, width='stretch')
                    st.dataframe(tendances, width='stretch')
            
            with col2:
                if 'signaux_faibles' in results:
                    st.subheader("Taux de Croissance")
                    
                    signaux = results['signaux_faibles']
                    
                    fig = px.bar(
                        signaux,
                        x='croissance_pct',
                        y='categorie',
                        orientation='h',
                        color='croissance_pct',
                        color_continuous_scale='RdYlGn',
                        title="Croissance par Categorie (%)"
                    )
                    st.plotly_chart(fig, width='stretch')
                    st.dataframe(signaux, width='stretch')

# ================================================================================
# PAGE 5: ANALYSES AVANCÉES
# ================================================================================
elif page == "Analyses Avancees":
    st.title("Analyses Avancees")
    
    df = load_data()
    
    if df.empty:
        st.warning("Aucune donnee disponible.")
    else:
        tab1, tab2 = st.tabs(["Par Domaine", "Collaborations"])
        
        with tab1:
            if 'mot_cle_recherche' in df.columns:
                selected_keyword = st.selectbox(
                    "Domaine",
                    df['mot_cle_recherche'].unique()
                )
                
                keyword_df = df[df['mot_cle_recherche'] == selected_keyword]
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Publications", len(keyword_df))
                with col2:
                    if 'annee' in keyword_df.columns:
                        valid_years = keyword_df['annee'].dropna()
                        if len(valid_years) > 0:
                            st.metric("Annee Mediane", f"{int(valid_years.median())}")
                with col3:
                    if 'source' in keyword_df.columns:
                        st.metric("Sources", keyword_df['source'].nunique())
                
                if 'annee' in keyword_df.columns:
                    year_trend = keyword_df.groupby('annee').size().reset_index(name='count')
                    year_trend = year_trend.dropna()
                    
                    if len(year_trend) > 0:
                        fig = px.area(year_trend, x='annee', y='count', title=f"Evolution - {selected_keyword}")
                        st.plotly_chart(fig, width='stretch')
        
        with tab2:
            if 'auteurs' in df.columns:
                coauthor_pairs = []
                for authors in df['auteurs'].dropna():
                    if isinstance(authors, list) and len(authors) > 1:
                        for i in range(len(authors)):
                            for j in range(i+1, len(authors)):
                                coauthor_pairs.append((authors[i], authors[j]))
                
                if coauthor_pairs:
                    coauthor_counts = Counter(coauthor_pairs).most_common(20)
                    
                    collab_df = pd.DataFrame(
                        [(f"{a1} <-> {a2}", count) for (a1, a2), count in coauthor_counts],
                        columns=['Collaboration', 'Publications']
                    )
                    
                    fig = px.bar(collab_df, x='Publications', y='Collaboration', 
                                orientation='h', title="Top Collaborations")
                    st.plotly_chart(fig, width='stretch')

# ================================================================================
# PAGE 6: CONFIGURATION
# ================================================================================
elif page == "Configuration":
    st.title("Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Base de Donnees")
        
        db = get_mongodb_connection()
        if db is not None:
            st.success("MongoDB connecte")
            
            total = db.articles.count_documents({})
            st.metric("Articles", total)
            
            if st.button("Nettoyer la base"):
                if st.checkbox("Confirmer la suppression"):
                    db.articles.delete_many({})
                    st.success("Base nettoyee!")
                    st.cache_data.clear()
                    st.rerun()
        else:
            st.error("MongoDB non connecte")
    
    with col2:
        st.subheader("Export des Donnees")
        
        df = load_data()
        if not df.empty:
            csv = df.to_csv(index=False)
            st.download_button(
                label="Telecharger CSV MongoDB",
                data=csv,
                file_name=f"data_mongodb_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
            
            results = load_spark_results()
            if results:
                st.write("**Resultats Spark:**")
                for key, result_df in results.items():
                    csv_result = result_df.to_csv(index=False)
                    st.download_button(
                        label=f"Telecharger {key}",
                        data=csv_result,
                        file_name=f"{key}_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        key=f"btn_{key}"
                    )
    
    st.divider()
    
    st.subheader("Informations Systeme")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Python:**", sys.version.split()[0])
        st.write("**Streamlit:**", st.__version__)
        st.write("**Pandas:**", pd.__version__)
    
    with col2:
        df = load_data()
        st.write("**Articles en base:**", len(df))
        st.write("**Derniere MAJ:**", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


