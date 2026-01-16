"""
Main PySpark analysis script for scientific research publications
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, count, year, desc, explode, split, lower, trim,
    collect_list, size, countDistinct, avg, sum as spark_sum,
    regexp_replace, when, lit
)
from pyspark.ml.feature import Tokenizer, StopWordsRemover, CountVectorizer, IDF
import os

# Create results directory if it doesn't exist
os.makedirs('../results', exist_ok=True)

print("=" * 80)
print("INITIALISATION DE SPARK SESSION")
print("=" * 80)

# Initialize Spark Session with MongoDB connector
spark = SparkSession.builder \
    .appName("ScientificResearchAnalysis") \
    .config("spark.mongodb.read.connection.uri", "mongodb://127.0.0.1/recherche_scientifique.articles") \
    .config("spark.mongodb.write.connection.uri", "mongodb://127.0.0.1/recherche_scientifique.articles") \
    .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:10.2.0") \
    .getOrCreate()

print("\n✓ Spark session créée avec succès!\n")

# Load data from MongoDB
print("=" * 80)
print("CHARGEMENT DES DONNÉES DEPUIS MONGODB")
print("=" * 80)

df = spark.read.format("mongodb").load()

print("\n✓ Données chargées avec succès!\n")

# Show schema
print("=" * 80)
print("SCHÉMA DES DONNÉES")
print("=" * 80)
df.printSchema()

# Show sample data
print("\n" + "=" * 80)
print("ÉCHANTILLON DES DONNÉES (5 premiers enregistrements)")
print("=" * 80)
df.show(5, truncate=False)

# Get total count
total_articles = df.count()
print(f"\n📊 Total d'articles: {total_articles}\n")

# ============================================================================
# ANALYSE 1: STATISTIQUES DES PUBLICATIONS PAR ANNÉE
# ============================================================================
print("=" * 80)
print("ANALYSE 1: PUBLICATIONS PAR ANNÉE")
print("=" * 80)

publications_par_annee = df.groupBy("annee") \
    .count() \
    .orderBy("annee") \
    .withColumnRenamed("count", "nombre_publications")

publications_par_annee.show()

# Save to CSV
publications_par_annee.toPandas().to_csv(
    '../results/publications_par_annee.csv', 
    index=False
)
print("✓ Sauvegardé: results/publications_par_annee.csv\n")

# ============================================================================
# ANALYSE 2: STATISTIQUES DES PUBLICATIONS PAR CATÉGORIE
# ============================================================================
print("=" * 80)
print("ANALYSE 2: PUBLICATIONS PAR CATÉGORIE")
print("=" * 80)

publications_par_categorie = df.groupBy("categorie") \
    .count() \
    .orderBy(desc("count")) \
    .withColumnRenamed("count", "nombre_publications")

publications_par_categorie.show()

# Calculate percentages
total = df.count()
publications_par_categorie_pct = publications_par_categorie.withColumn(
    "pourcentage",
    (col("nombre_publications") / total * 100)
)

publications_par_categorie_pct.toPandas().to_csv(
    '../results/publications_par_categorie.csv',
    index=False
)
print("✓ Sauvegardé: results/publications_par_categorie.csv\n")

# ============================================================================
# ANALYSE 3: PUBLICATIONS PAR SOURCE
# ============================================================================
print("=" * 80)
print("ANALYSE 3: PUBLICATIONS PAR SOURCE")
print("=" * 80)

publications_par_source = df.groupBy("source") \
    .count() \
    .orderBy(desc("count")) \
    .withColumnRenamed("count", "nombre_publications")

publications_par_source.show()
publications_par_source.toPandas().to_csv(
    '../results/publications_par_source.csv',
    index=False
)
print("✓ Sauvegardé: results/publications_par_source.csv\n")

# ============================================================================
# ANALYSE 4: ÉVOLUTION PAR CATÉGORIE ET ANNÉE
# ============================================================================
print("=" * 80)
print("ANALYSE 4: ÉVOLUTION TEMPORELLE PAR CATÉGORIE")
print("=" * 80)

evolution_categorie = df.groupBy("annee", "categorie") \
    .count() \
    .orderBy("annee", "categorie") \
    .withColumnRenamed("count", "nombre_publications")

evolution_categorie.show(30)
evolution_categorie.toPandas().to_csv(
    '../results/evolution_categorie_annee.csv',
    index=False
)
print("✓ Sauvegardé: results/evolution_categorie_annee.csv\n")

# ============================================================================
# ANALYSE 5: TOP AUTEURS LES PLUS PRODUCTIFS
# ============================================================================
print("=" * 80)
print("ANALYSE 5: TOP AUTEURS")
print("=" * 80)

# Split authors by comma and explode
df_authors = df.withColumn(
    "auteur", 
    explode(split(col("auteurs"), ","))
)

# Clean author names
df_authors = df_authors.withColumn(
    "auteur",
    trim(regexp_replace(col("auteur"), r'\s+', ' '))
)

# Count publications per author
top_auteurs = df_authors.groupBy("auteur") \
    .agg(
        count("*").alias("nombre_publications"),
        collect_list("categorie").alias("categories")
    ) \
    .orderBy(desc("nombre_publications"))

top_auteurs_clean = top_auteurs.select(
    "auteur",
    "nombre_publications"
)

top_auteurs_clean.show(20, truncate=False)
top_auteurs_clean.toPandas().to_csv(
    '../results/top_auteurs.csv',
    index=False
)
print("✓ Sauvegardé: results/top_auteurs.csv\n")

# ============================================================================
# ANALYSE 6: COLLABORATIONS (AUTEURS MULTIPLES)
# ============================================================================
print("=" * 80)
print("ANALYSE 6: ANALYSE DES COLLABORATIONS")
print("=" * 80)

df_with_author_count = df.withColumn(
    "nombre_auteurs",
    size(split(col("auteurs"), ","))
)

# Articles with multiple authors (collaborations)
collaborations = df_with_author_count.filter(col("nombre_auteurs") > 1)
solo_articles = df_with_author_count.filter(col("nombre_auteurs") == 1)

collab_stats = spark.createDataFrame([
    ("Collaborations (multiple auteurs)", collaborations.count()),
    ("Publications solo (1 auteur)", solo_articles.count()),
    ("Total", df.count())
], ["Type", "Nombre"])

collab_stats.show()
collab_stats.toPandas().to_csv(
    '../results/statistiques_collaborations.csv',
    index=False
)
print("✓ Sauvegardé: results/statistiques_collaborations.csv\n")

# ============================================================================
# ANALYSE 7: TENDANCES RÉCENTES (2020+)
# ============================================================================
print("=" * 80)
print("ANALYSE 7: TENDANCES RÉCENTES (2020 et après)")
print("=" * 80)

tendances_recentes = df.filter(col("annee") >= 2020) \
    .groupBy("categorie") \
    .count() \
    .orderBy(desc("count")) \
    .withColumnRenamed("count", "nombre_publications")

tendances_recentes.show()
tendances_recentes.toPandas().to_csv(
    '../results/tendances_recentes.csv',
    index=False
)
print("✓ Sauvegardé: results/tendances_recentes.csv\n")

# ============================================================================
# ANALYSE 8: CATÉGORIES ÉMERGENTES (Signaux Faibles)
# ============================================================================
print("=" * 80)
print("ANALYSE 8: DÉTECTION DE SIGNAUX FAIBLES")
print("=" * 80)

# Compare 2016-2019 vs 2020-2025
periode_ancienne = df.filter((col("annee") >= 2016) & (col("annee") <= 2019)) \
    .groupBy("categorie") \
    .count() \
    .withColumnRenamed("count", "count_old")

periode_recente = df.filter((col("annee") >= 2020) & (col("annee") <= 2025)) \
    .groupBy("categorie") \
    .count() \
    .withColumnRenamed("count", "count_new")

# Join and calculate growth
croissance = periode_ancienne.join(
    periode_recente,
    "categorie",
    "outer"
).fillna(0)

croissance = croissance.withColumn(
    "croissance_pct",
    when(col("count_old") > 0, 
         ((col("count_new") - col("count_old")) / col("count_old") * 100)
    ).otherwise(lit(100.0))
).orderBy(desc("croissance_pct"))

print("\n📈 Catégories en forte croissance (signaux faibles):")
croissance.show()

croissance.toPandas().to_csv(
    '../results/signaux_faibles_croissance.csv',
    index=False
)
print("✓ Sauvegardé: results/signaux_faibles_croissance.csv\n")

# ============================================================================
# ANALYSE 9: MÉTRIQUES GLOBALES
# ============================================================================
print("=" * 80)
print("ANALYSE 9: MÉTRIQUES GLOBALES")
print("=" * 80)

metriques = spark.createDataFrame([
    ("Total Publications", total_articles),
    ("Nombre de Catégories", df.select("categorie").distinct().count()),
    ("Nombre de Sources", df.select("source").distinct().count()),
    ("Année Min", df.agg({"annee": "min"}).collect()[0][0]),
    ("Année Max", df.agg({"annee": "max"}).collect()[0][0]),
    ("Nombre Total d'Auteurs Uniques", df_authors.select("auteur").distinct().count())
], ["Métrique", "Valeur"])

metriques.show(truncate=False)
metriques.toPandas().to_csv(
    '../results/metriques_globales.csv',
    index=False
)
print("✓ Sauvegardé: results/metriques_globales.csv\n")

# ============================================================================
# SAVE COMPLETE DATASET FOR VISUALIZATION
# ============================================================================
print("=" * 80)
print("EXPORT DU DATASET COMPLET")
print("=" * 80)

df.toPandas().to_csv(
    '../results/dataset_complet.csv',
    index=False
)
print("✓ Sauvegardé: results/dataset_complet.csv\n")

print("=" * 80)
print("✅ TOUTES LES ANALYSES SONT TERMINÉES!")
print("=" * 80)
print("\nFichiers générés dans le dossier 'results/':")
print("  - publications_par_annee.csv")
print("  - publications_par_categorie.csv")
print("  - publications_par_source.csv")
print("  - evolution_categorie_annee.csv")
print("  - top_auteurs.csv")
print("  - statistiques_collaborations.csv")
print("  - tendances_recentes.csv")
print("  - signaux_faibles_croissance.csv")
print("  - metriques_globales.csv")
print("  - dataset_complet.csv")

# Stop Spark
spark.stop()
print("\n✓ Spark session fermée.\n")
