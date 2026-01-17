"""
Flask API for Big Data Analysis - Scientific Research
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from pymongo import MongoClient
from collections import Counter
import os

app = Flask(__name__)
CORS(app)

# ============================================================================
# MongoDB connection
# ============================================================================
try:
    client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
    client.server_info()  # Test connection
    db = client["recherche_scientifique"]
    collection = db["articles"]
    print("✓ Connexion MongoDB réussie!")
except Exception as e:
    print(f" Erreur de connexion MongoDB: {e}")
    collection = None


# ============================================================================
# HEALTH CHECK
# ============================================================================
@app.route("/api/health", methods=["GET"])
def health_check():
    """Check API health"""
    return jsonify({
        "status": "healthy",
        "mongodb_connected": collection is not None
    })


# ============================================================================
# OVERVIEW STATISTICS
# ============================================================================
@app.route("/api/stats/overview", methods=["GET"])
def get_overview():
    """Get general statistics"""
    if collection is None:  
        return jsonify({"error": "MongoDB not connected"}), 500

    # Access nested fields correctly
    total_articles = collection.count_documents({})
    
    # Categories are in content.categorie
    categories = collection.distinct("content.categorie")
    
    # Sources are in metadata.source
    sources = collection.distinct("metadata.source")
    
    # Years are in metadata.annee
    years = collection.distinct("metadata.annee")

    # Authors are in content.auteurs (array)
    all_authors = set()
    for doc in collection.find({}, {"content.auteurs": 1}):
        if "content" in doc and "auteurs" in doc["content"]:
            # auteurs is an array in your JSON structure
            authors = doc["content"]["auteurs"]
            if isinstance(authors, list):
                all_authors.update(authors)

    return jsonify({
        "total_articles": total_articles,
        "total_categories": len(categories),
        "total_sources": len(sources),
        "total_authors": len(all_authors),
        "years_range": {
            "min": min(years) if years else None,
            "max": max(years) if years else None
        },
        "categories": sorted(categories),
        "sources": sorted(sources)
    })


# ============================================================================
# PUBLICATIONS BY YEAR
# ============================================================================
@app.route("/api/stats/by-year", methods=["GET"])
def get_by_year():
    """Publications by year"""
    if collection is None:  
        return jsonify({"error": "MongoDB not connected"}), 500

    pipeline = [
        {"$group": {"_id": "$metadata.annee", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]

    results = list(collection.aggregate(pipeline))
    return jsonify([
        {"annee": r["_id"], "nombre_publications": r["count"]}
        for r in results
    ])


# ============================================================================
# PUBLICATIONS BY CATEGORY
# ============================================================================
@app.route("/api/stats/by-category", methods=["GET"])
def get_by_category():
    """Publications by category"""
    if collection is None:  
        return jsonify({"error": "MongoDB not connected"}), 500

    pipeline = [
        {"$group": {"_id": "$content.categorie", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]

    results = list(collection.aggregate(pipeline))
    total = sum(r["count"] for r in results)

    return jsonify([
        {
            "categorie": r["_id"],
            "nombre_publications": r["count"],
            "pourcentage": round((r["count"] / total) * 100, 2) if total else 0
        }
        for r in results
    ])


# ============================================================================
# PUBLICATIONS BY SOURCE
# ============================================================================
@app.route("/api/stats/by-source", methods=["GET"])
def get_by_source():
    """Publications by source"""
    if collection is None:  
        return jsonify({"error": "MongoDB not connected"}), 500

    pipeline = [
        {"$group": {"_id": "$metadata.source", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]

    results = list(collection.aggregate(pipeline))
    return jsonify([
        {"source": r["_id"], "nombre_publications": r["count"]}
        for r in results
    ])


# ============================================================================
# EVOLUTION (CATEGORY × YEAR)
# ============================================================================
@app.route("/api/stats/evolution", methods=["GET"])
def get_evolution():
    """Get evolution by category and year"""
    if collection is None:  
        return jsonify({"error": "MongoDB not connected"}), 500

    pipeline = [
        {
            "$group": {
                "_id": {
                    "annee": "$metadata.annee",
                    "categorie": "$content.categorie"
                },
                "count": {"$sum": 1}
            }
        },
        {"$sort": {"_id.annee": 1}}
    ]

    results = list(collection.aggregate(pipeline))
    return jsonify([
        {
            "annee": r["_id"]["annee"],
            "categorie": r["_id"]["categorie"],
            "nombre_publications": r["count"]
        }
        for r in results
    ])


# ============================================================================
# TOP AUTHORS
# ============================================================================
@app.route("/api/stats/top-authors", methods=["GET"])
def get_top_authors():
    """Get top authors"""
    if collection is None:  
        return jsonify({"error": "MongoDB not connected"}), 500

    limit = request.args.get("limit", 20, type=int)
    
    # Use aggregation to unwind authors array
    pipeline = [
        {"$unwind": "$content.auteurs"},
        {"$group": {
            "_id": "$content.auteurs",
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}},
        {"$limit": limit}
    ]
    
    results = list(collection.aggregate(pipeline))
    return jsonify([
        {"auteur": r["_id"], "nombre_publications": r["count"]}
        for r in results
    ])


# ============================================================================
# RECENT TRENDS (2020+)
# ============================================================================
@app.route("/api/stats/trends-recent", methods=["GET"])
def get_recent_trends():
    """Get recent trends (2020+)"""
    if collection is None:  
        return jsonify({"error": "MongoDB not connected"}), 500

    pipeline = [
        {"$match": {"metadata.annee": {"$gte": 2020}}},
        {"$group": {"_id": "$content.categorie", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]

    results = list(collection.aggregate(pipeline))
    return jsonify([
        {"categorie": r["_id"], "nombre_publications": r["count"]}
        for r in results
    ])


# ============================================================================
# WEAK SIGNALS (GROWTH ANALYSIS)
# ============================================================================
@app.route("/api/stats/weak-signals", methods=["GET"])
def get_weak_signals():
    """Detect weak signals"""
    if collection is None:  
        return jsonify({"error": "MongoDB not connected"}), 500

    old = {
        r["_id"]: r["count"]
        for r in collection.aggregate([
            {"$match": {"metadata.annee": {"$gte": 2016, "$lte": 2019}}},
            {"$group": {"_id": "$content.categorie", "count": {"$sum": 1}}}
        ])
    }

    new = {
        r["_id"]: r["count"]
        for r in collection.aggregate([
            {"$match": {"metadata.annee": {"$gte": 2020}}},
            {"$group": {"_id": "$content.categorie", "count": {"$sum": 1}}}
        ])
    }

    categories = set(old) | set(new)
    signals = []

    for cat in categories:
        old_c = old.get(cat, 0)
        new_c = new.get(cat, 0)
        growth = ((new_c - old_c) / old_c * 100) if old_c else (100 if new_c else 0)

        signals.append({
            "categorie": cat,
            "count_old": old_c,
            "count_new": new_c,
            "croissance_pct": round(growth, 2)
        })

    return jsonify(sorted(signals, key=lambda x: x["croissance_pct"], reverse=True))


# ============================================================================
# COLLABORATIONS
# ============================================================================
@app.route("/api/stats/collaborations", methods=["GET"])
def get_collaborations():
    """Analyze collaborations"""
    if collection is None:  
        return jsonify({"error": "MongoDB not connected"}), 500

    solo = collab = 0
    for article in collection.find({}, {"content.auteurs": 1}):
        if "content" in article and "auteurs" in article["content"]:
            count = len(article["content"]["auteurs"])
            if count == 1:
                solo += 1
            elif count > 1:
                collab += 1

    total = solo + collab
    return jsonify({
        "solo_publications": solo,
        "collaborative_publications": collab,
        "total": total,
        "collaboration_rate": round(collab / total * 100, 2) if total else 0
    })


# ============================================================================
# SEARCH ARTICLES
# ============================================================================
@app.route("/api/articles/search", methods=["GET"])
def search_articles():
    """Search articles"""
    if collection is None:  
        return jsonify({"error": "MongoDB not connected"}), 500

    query = request.args.get("q", "")
    category = request.args.get("category", "")
    year = request.args.get("year", type=int)
    limit = request.args.get("limit", 50, type=int)

    filters = {}
    if query:
        filters["$or"] = [
            {"content.titre": {"$regex": query, "$options": "i"}},
            {"content.auteurs": {"$regex": query, "$options": "i"}}
        ]
    if category:
        filters["content.categorie"] = category
    if year:
        filters["metadata.annee"] = year

    articles = list(collection.find(filters, {"_id": 0}).limit(limit))
    return jsonify({"count": len(articles), "articles": articles})


# ============================================================================
# GET ARTICLE BY ID
# ============================================================================
@app.route("/api/articles/<article_id>", methods=["GET"])
def get_article(article_id):
    """Get specific article"""
    if collection is None:  
        return jsonify({"error": "MongoDB not connected"}), 500

    article = collection.find_one({"_id": article_id}, {"_id": 0})
    if article:
        return jsonify(article)
    return jsonify({"error": "Article not found"}), 404


# ============================================================================
# SERVE VISUALIZATIONS
# ============================================================================
@app.route("/api/visualizations/<path:filename>")
def serve_visualization(filename):
    viz_dir = os.path.join(os.path.dirname(__file__), "..", "visualizations")
    return send_from_directory(viz_dir, filename)


@app.route("/api/visualizations", methods=["GET"])
def list_visualizations():
    """List all visualizations"""
    viz_dir = os.path.join(os.path.dirname(__file__), "..", "visualizations")
    if os.path.exists(viz_dir):
        files = [f for f in os.listdir(viz_dir) if f.endswith(('.png', '.html'))]
        return jsonify({"count": len(files), "visualizations": sorted(files)})
    return jsonify({"error": "Visualization directory not found"}), 404


# ============================================================================
# RUN APP
# ============================================================================
if __name__ == "__main__":
    print("=" * 80)
    print("🚀 Flask API Started")
    print("=" * 80)
    print("\nAvailable endpoints:")
    print("  GET /api/health")
    print("  GET /api/stats/overview")
    print("  GET /api/stats/by-year")
    print("  GET /api/stats/by-category")
    print("  GET /api/stats/by-source")
    print("  GET /api/stats/evolution")
    print("  GET /api/stats/top-authors?limit=20")
    print("  GET /api/stats/trends-recent")
    print("  GET /api/stats/weak-signals")
    print("  GET /api/stats/collaborations")
    print("  GET /api/articles/search?q=query&category=cat&year=2020")
    print("  GET /api/articles/<id>")
    print("  GET /api/visualizations")
    print("  GET /api/visualizations/<filename>")
    print("\n" + "=" * 80 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
