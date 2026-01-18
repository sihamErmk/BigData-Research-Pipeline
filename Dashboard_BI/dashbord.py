import streamlit as st
import pandas as pd
import plotly.express as px
from pymongo import MongoClient
from collections import Counter
from datetime import datetime

# =============================================================================
# CONFIGURATION PAGE
# =============================================================================
st.set_page_config(
    page_title="Dashboard BI & Analyses Avancées",
    layout="wide"
)

# =============================================================================
# CONNEXION MONGODB
# =============================================================================
@st.cache_resource
def get_mongodb_connection():
    client = MongoClient("mongodb://localhost:27017/")
    return client["research_db"]

# =============================================================================
# CHARGEMENT DES DONNÉES
# =============================================================================
@st.cache_data(ttl=60)
def load_data():
    db = get_mongodb_connection()
    articles = list(db.articles.find())
    if not articles:
        return pd.DataFrame()

    df = pd.DataFrame(articles)

    if "annee" in df.columns:
        df["annee"] = pd.to_numeric(df["annee"], errors="coerce")

    if "date_scraping" in df.columns:
        df["date_scraping"] = pd.to_datetime(df["date_scraping"], errors="coerce")

    return df

# =============================================================================
# SIDEBAR
# =============================================================================
with st.sidebar:
    st.title("Navigation")

    page = st.radio(
        "Choisir une page",
        ["Dashboard BI", "Analyses Avancées"]
    )

    df_sidebar = load_data()
    if not df_sidebar.empty:
        st.metric("Total Articles", len(df_sidebar))
        if "source" in df_sidebar.columns:
            st.metric("Sources", df_sidebar["source"].nunique())

# =============================================================================
# PAGE 1 : DASHBOARD BI
# =============================================================================
if page == "Dashboard BI":
    st.title("📊 Dashboard Business Intelligence")

    df = load_data()

    if df.empty:
        st.warning("Aucune donnée disponible.")
    else:
        st.subheader("Filtres")

        if "source" in df.columns:
            sources = ["Toutes"] + list(df["source"].unique())
            selected_source = st.selectbox("Source", sources)

            if selected_source != "Toutes":
                df = df[df["source"] == selected_source]

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Publications", len(df))

        with col2:
            if "annee" in df.columns and df["annee"].notna().any():
                st.metric("Année Moyenne", int(df["annee"].mean()))

        with col3:
            if "auteurs" in df.columns:
                auteurs = [
                    a for sub in df["auteurs"].dropna()
                    if isinstance(sub, list) for a in sub
                ]
                st.metric("Auteurs", len(set(auteurs)))

        with col4:
            if "abstract" in df.columns:
                taux = df["abstract"].notna().mean() * 100
                st.metric("Avec Abstract", f"{taux:.1f}%")

        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            if "source" in df.columns:
                fig = px.pie(
                    df,
                    names="source",
                    title="Répartition par Source",
                    hole=0.4
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            if "mot_cle_recherche" in df.columns:
                top_keywords = df["mot_cle_recherche"].value_counts().head(10)
                fig = px.bar(
                    x=top_keywords.values,
                    y=top_keywords.index,
                    orientation="h",
                    title="Top 10 Mots-clés"
                )
                st.plotly_chart(fig, use_container_width=True)

        if "annee" in df.columns:
            st.subheader("Évolution Temporelle")

            trend = df.groupby("annee").size().reset_index(name="count").dropna()

            if not trend.empty:
                fig = px.line(
                    trend,
                    x="annee",
                    y="count",
                    markers=True,
                    title="Publications par Année"
                )
                st.plotly_chart(fig, use_container_width=True)

        st.subheader("Aperçu des données")
        cols = [c for c in ["titre", "source", "annee", "mot_cle_recherche"] if c in df.columns]
        st.dataframe(df[cols].head(50), use_container_width=True)

# =============================================================================
# PAGE 2 : ANALYSES AVANCÉES
# =============================================================================
elif page == "Analyses Avancées":
    st.title("📈 Analyses Avancées")

    df = load_data()

    if df.empty:
        st.warning("Aucune donnée disponible.")
    else:
        tab1, tab2 = st.tabs(["Analyse par Domaine", "Collaborations Scientifiques"])

        # ---------------------------------------------------------------------
        # ANALYSE PAR DOMAINE
        # ---------------------------------------------------------------------
        with tab1:
            if "mot_cle_recherche" in df.columns:
                keyword = st.selectbox(
                    "Choisir un domaine",
                    df["mot_cle_recherche"].dropna().unique()
                )

                sub_df = df[df["mot_cle_recherche"] == keyword]

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Publications", len(sub_df))

                with col2:
                    if "annee" in sub_df.columns and sub_df["annee"].notna().any():
                        st.metric("Année Médiane", int(sub_df["annee"].median()))

                with col3:
                    if "source" in sub_df.columns:
                        st.metric("Sources", sub_df["source"].nunique())

                if "annee" in sub_df.columns:
                    trend = sub_df.groupby("annee").size().reset_index(name="count").dropna()

                    if not trend.empty:
                        fig = px.area(
                            trend,
                            x="annee",
                            y="count",
                            title=f"Évolution du domaine : {keyword}"
                        )
                        st.plotly_chart(fig, use_container_width=True)

        # ---------------------------------------------------------------------
        # ANALYSE DES COLLABORATIONS
        # ---------------------------------------------------------------------
        with tab2:
            if "auteurs" in df.columns:
                pairs = []

                for authors in df["auteurs"].dropna():
                    if isinstance(authors, list) and len(authors) > 1:
                        for i in range(len(authors)):
                            for j in range(i + 1, len(authors)):
                                pairs.append((authors[i], authors[j]))

                if pairs:
                    top_pairs = Counter(pairs).most_common(20)

                    collab_df = pd.DataFrame(
                        [(f"{a1} ↔ {a2}", c) for (a1, a2), c in top_pairs],
                        columns=["Collaboration", "Publications"]
                    )

                    fig = px.bar(
                        collab_df,
                        x="Publications",
                        y="Collaboration",
                        orientation="h",
                        title="Top Collaborations Scientifiques"
                    )
                    st.plotly_chart(fig, use_container_width=True)
