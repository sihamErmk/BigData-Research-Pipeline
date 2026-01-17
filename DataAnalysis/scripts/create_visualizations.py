"""
 all visualizations from analysis results
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import warnings

warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10

# Create visualizations directory
os.makedirs('../visualizations', exist_ok=True)

print("=" * 80)
print("CRÉATION DES VISUALISATIONS")
print("=" * 80)

# Load all results
try:
    pub_annee = pd.read_csv('../results/publications_par_annee.csv')
    pub_categorie = pd.read_csv('../results/publications_par_categorie.csv')
    pub_source = pd.read_csv('../results/publications_par_source.csv')
    evolution = pd.read_csv('../results/evolution_categorie_annee.csv')
    top_auteurs = pd.read_csv('../results/top_auteurs.csv')
    tendances = pd.read_csv('../results/tendances_recentes.csv')
    signaux = pd.read_csv('../results/signaux_faibles_croissance.csv')
    
    print("✓ Tous les fichiers CSV chargés avec succès!\n")
except Exception as e:
    print(f" Erreur lors du chargement des fichiers: {e}")
    print("Assurez-vous d'avoir exécuté spark_analysis.py d'abord!")
    exit(1)

# ============================================================================
# VIZ 1: ÉVOLUTION TEMPORELLE DES PUBLICATIONS
# ============================================================================
print(" Création: Évolution temporelle des publications...")

fig, ax = plt.subplots(figsize=(14, 6))
ax.plot(pub_annee['annee'], pub_annee['nombre_publications'], 
        marker='o', linewidth=2, markersize=8, color='steelblue')
ax.fill_between(pub_annee['annee'], pub_annee['nombre_publications'], 
                 alpha=0.3, color='steelblue')
ax.set_xlabel('Année', fontsize=12, fontweight='bold')
ax.set_ylabel('Nombre de Publications', fontsize=12, fontweight='bold')
ax.set_title('Évolution des Publications Scientifiques par Année', 
             fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('../visualizations/1_evolution_annuelle.png', dpi=300, bbox_inches='tight')
plt.close()

# Interactive version
fig_interactive = px.line(pub_annee, x='annee', y='nombre_publications',
                          title='Évolution Temporelle Interactive',
                          markers=True)
fig_interactive.update_layout(
    xaxis_title="Année",
    yaxis_title="Nombre de Publications",
    hovermode='x unified'
)
fig_interactive.write_html('../visualizations/1_evolution_annuelle_interactive.html')

print("  ✓ 1_evolution_annuelle.png")
print("  ✓ 1_evolution_annuelle_interactive.html")

# ============================================================================
# VIZ 2: DISTRIBUTION PAR CATÉGORIE (BAR CHART)
# ============================================================================
print(" Création: Distribution par catégorie...")

fig, ax = plt.subplots(figsize=(12, 6))
colors = sns.color_palette("Set2", len(pub_categorie))
bars = ax.barh(pub_categorie['categorie'], pub_categorie['nombre_publications'], 
               color=colors, edgecolor='black', linewidth=1.2)

# Add value labels
for i, (bar, val) in enumerate(zip(bars, pub_categorie['nombre_publications'])):
    ax.text(val + 1, bar.get_y() + bar.get_height()/2, 
            f'{int(val)}', va='center', fontweight='bold')

ax.set_xlabel('Nombre de Publications', fontsize=12, fontweight='bold')
ax.set_ylabel('Catégorie', fontsize=12, fontweight='bold')
ax.set_title('Distribution des Publications par Catégorie', 
             fontsize=14, fontweight='bold')
ax.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.savefig('../visualizations/2_distribution_categories.png', dpi=300, bbox_inches='tight')
plt.close()

print("  ✓ 2_distribution_categories.png")

# ============================================================================
# VIZ 3: RÉPARTITION PAR CATÉGORIE (PIE CHART)
# ============================================================================
print(" Création: Diagramme circulaire des catégories...")

fig, ax = plt.subplots(figsize=(10, 8))
wedges, texts, autotexts = ax.pie(
    pub_categorie['nombre_publications'], 
    labels=pub_categorie['categorie'],
    autopct='%1.1f%%',
    startangle=90,
    colors=colors,
    explode=[0.05] * len(pub_categorie),
    shadow=True
)

for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')
    autotext.set_fontsize(10)

ax.set_title('Répartition des Publications par Catégorie', 
             fontsize=14, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig('../visualizations/3_pie_categories.png', dpi=300, bbox_inches='tight')
plt.close()

print("  ✓ 3_pie_categories.png")

# ============================================================================
# VIZ 4: ÉVOLUTION PAR CATÉGORIE (LINE CHART)
# ============================================================================
print(" Création: Évolution par catégorie...")

fig = px.line(evolution, x='annee', y='nombre_publications', color='categorie',
              title='Évolution Temporelle par Catégorie de Recherche',
              markers=True, line_shape='spline')

fig.update_layout(
    xaxis_title="Année",
    yaxis_title="Nombre de Publications",
    legend_title="Catégorie",
    hovermode='x unified',
    height=600
)

fig.write_html('../visualizations/4_evolution_categories_interactive.html')

print("  ✓ 4_evolution_categories_interactive.html")

# Static version
pivot = evolution.pivot(index='annee', columns='categorie', values='nombre_publications').fillna(0)
fig, ax = plt.subplots(figsize=(14, 7))
for col in pivot.columns:
    ax.plot(pivot.index, pivot[col], marker='o', label=col, linewidth=2)

ax.set_xlabel('Année', fontsize=12, fontweight='bold')
ax.set_ylabel('Nombre de Publications', fontsize=12, fontweight='bold')
ax.set_title('Évolution par Catégorie au Fil du Temps', fontsize=14, fontweight='bold')
ax.legend(title='Catégorie', bbox_to_anchor=(1.05, 1), loc='upper left')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('../visualizations/4_evolution_categories.png', dpi=300, bbox_inches='tight')
plt.close()

print("  ✓ 4_evolution_categories.png")

# ============================================================================
# VIZ 5: TOP 20 AUTEURS
# ============================================================================
print(" Création: Top 20 auteurs...")

top_20 = top_auteurs.head(20).sort_values('nombre_publications')

fig, ax = plt.subplots(figsize=(12, 10))
bars = ax.barh(top_20['auteur'], top_20['nombre_publications'], 
               color='coral', edgecolor='black', linewidth=1.2)

# Add value labels
for bar in bars:
    width = bar.get_width()
    ax.text(width + 0.1, bar.get_y() + bar.get_height()/2,
            f'{int(width)}', va='center', fontweight='bold')

ax.set_xlabel('Nombre de Publications', fontsize=12, fontweight='bold')
ax.set_ylabel('Auteur', fontsize=12, fontweight='bold')
ax.set_title('Top 20 Auteurs les Plus Productifs', fontsize=14, fontweight='bold')
ax.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.savefig('../visualizations/5_top_20_auteurs.png', dpi=300, bbox_inches='tight')
plt.close()

print("  ✓ 5_top_20_auteurs.png")

# ============================================================================
# VIZ 6: HEATMAP CATÉGORIE × ANNÉE
# ============================================================================
print(" Création: Heatmap catégorie × année...")

pivot_heatmap = evolution.pivot(index='categorie', columns='annee', 
                                  values='nombre_publications').fillna(0)

fig, ax = plt.subplots(figsize=(14, 6))
sns.heatmap(pivot_heatmap, annot=True, fmt='.0f', cmap='YlOrRd', 
            linewidths=0.5, cbar_kws={'label': 'Nombre de Publications'},
            ax=ax)
ax.set_title('Heatmap: Publications par Catégorie et Année', 
             fontsize=14, fontweight='bold')
ax.set_xlabel('Année', fontsize=12, fontweight='bold')
ax.set_ylabel('Catégorie', fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig('../visualizations/6_heatmap_categorie_annee.png', dpi=300, bbox_inches='tight')
plt.close()

print("  ✓ 6_heatmap_categorie_annee.png")

# ============================================================================
# VIZ 7: SIGNAUX FAIBLES (CROISSANCE)
# ============================================================================
print(" Création: Signaux faibles (croissance)...")

signaux_sorted = signaux.sort_values('croissance_pct', ascending=True)

fig, ax = plt.subplots(figsize=(12, 6))
colors_growth = ['green' if x > 0 else 'red' for x in signaux_sorted['croissance_pct']]
bars = ax.barh(signaux_sorted['categorie'], signaux_sorted['croissance_pct'],
               color=colors_growth, edgecolor='black', linewidth=1.2)

ax.axvline(x=0, color='black', linestyle='--', linewidth=1)
ax.set_xlabel('Taux de Croissance (%)', fontsize=12, fontweight='bold')
ax.set_ylabel('Catégorie', fontsize=12, fontweight='bold')
ax.set_title('Signaux Faibles: Croissance par Catégorie (2016-2019 vs 2020+)', 
             fontsize=14, fontweight='bold')
ax.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.savefig('../visualizations/7_signaux_faibles_croissance.png', dpi=300, bbox_inches='tight')
plt.close()

print("  ✓ 7_signaux_faibles_croissance.png")

# ============================================================================
# VIZ 8: TENDANCES RÉCENTES (2020+)
# ============================================================================
print(" Création: Tendances récentes...")

fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(tendances['categorie'], tendances['nombre_publications'],
       color='teal', edgecolor='black', linewidth=1.2)
ax.set_xlabel('Catégorie', fontsize=12, fontweight='bold')
ax.set_ylabel('Nombre de Publications', fontsize=12, fontweight='bold')
ax.set_title('Tendances Récentes (2020 et après)', fontsize=14, fontweight='bold')
plt.xticks(rotation=45, ha='right')
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('../visualizations/8_tendances_recentes.png', dpi=300, bbox_inches='tight')
plt.close()

print("  ✓ 8_tendances_recentes.png")

# ============================================================================
# VIZ 9: DASHBOARD COMPLET (PLOTLY)
# ============================================================================
print(" Création: Dashboard complet interactif...")

fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=('Publications par Année', 'Distribution par Catégorie',
                    'Top 10 Auteurs', 'Tendances Récentes'),
    specs=[[{'type': 'scatter'}, {'type': 'bar'}],
           [{'type': 'bar'}, {'type': 'bar'}]]
)

# Plot 1: Evolution annuelle
fig.add_trace(
    go.Scatter(x=pub_annee['annee'], y=pub_annee['nombre_publications'],
               mode='lines+markers', name='Publications',
               line=dict(color='steelblue', width=3)),
    row=1, col=1
)

# Plot 2: Catégories
fig.add_trace(
    go.Bar(x=pub_categorie['categorie'], y=pub_categorie['nombre_publications'],
           name='Catégories', marker_color='indianred'),
    row=1, col=2
)

# Plot 3: Top 10 auteurs
top_10 = top_auteurs.head(10).sort_values('nombre_publications')
fig.add_trace(
    go.Bar(y=top_10['auteur'], x=top_10['nombre_publications'],
           name='Auteurs', orientation='h', marker_color='coral'),
    row=2, col=1
)

# Plot 4: Tendances récentes
fig.add_trace(
    go.Bar(x=tendances['categorie'], y=tendances['nombre_publications'],
           name='Tendances', marker_color='teal'),
    row=2, col=2
)

fig.update_layout(
    height=800,
    showlegend=False,
    title_text="Dashboard Analytique - Recherche Scientifique",
    title_font_size=20
)

fig.write_html('../visualizations/9_dashboard_complet.html')

print("  ✓ 9_dashboard_complet.html")

# ============================================================================
# VIZ 10: WORD CLOUD DES CATÉGORIES
# ============================================================================
print(" Création: Word Cloud des catégories...")

# Create word frequency dictionary
word_freq = dict(zip(pub_categorie['categorie'], pub_categorie['nombre_publications']))

wordcloud = WordCloud(width=1200, height=600, background_color='white',
                      colormap='viridis', relative_scaling=0.5,
                      min_font_size=10).generate_from_frequencies(word_freq)

fig, ax = plt.subplots(figsize=(14, 7))
ax.imshow(wordcloud, interpolation='bilinear')
ax.axis('off')
ax.set_title('Word Cloud: Catégories de Recherche', fontsize=16, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig('../visualizations/10_wordcloud_categories.png', dpi=300, bbox_inches='tight')
plt.close()

print("  ✓ 10_wordcloud_categories.png")

print("\n" + "=" * 80)
print(" TOUTES LES VISUALISATIONS ONT ÉTÉ CRÉÉES AVEC SUCCÈS!")
print("=" * 80)
print("\nFichiers générés dans 'visualizations/':")
print("  1. 1_evolution_annuelle.png & .html")
print("  2. 2_distribution_categories.png")
print("  3. 3_pie_categories.png")
print("  4. 4_evolution_categories.png & .html")
print("  5. 5_top_20_auteurs.png")
print("  6. 6_heatmap_categorie_annee.png")
print("  7. 7_signaux_faibles_croissance.png")
print("  8. 8_tendances_recentes.png")
print("  9. 9_dashboard_complet.html")
print(" 10. 10_wordcloud_categories.png")
print("\n")
