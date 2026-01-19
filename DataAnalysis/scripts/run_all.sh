#!/bin/bash

echo "=============================================================================="
echo "EXÉCUTION COMPLÈTE DU PIPELINE BIG DATA"
echo "=============================================================================="

# Check if MongoDB is running
echo ""
echo "1. Vérification de MongoDB..."
if sudo systemctl is-active --quiet mongod; then
    echo "   ✓ MongoDB est actif"
else
    echo "   ⚠ MongoDB n'est pas actif. Démarrage..."
    sudo systemctl start mongod
    sleep 3
fi

# Import data if not already done
echo ""
echo "2. Vérification des données dans MongoDB..."
COUNT=$(mongosh --quiet --eval "db.getSiblingDB('recherche_scientifique').articles.countDocuments()" | tail -1)
if [ "$COUNT" -eq "0" ]; then
    echo "   ⚠ Aucune donnée trouvée. Import en cours..."
    mongoimport --db recherche_scientifique --collection articles --file ../data/articles.json --jsonArray
else
    echo "   ✓ Données trouvées: $COUNT articles"
fi

# Run Spark analysis
echo ""
echo "3. Exécution des analyses Spark..."
cd scripts
spark-submit \
    --packages org.mongodb.spark:mongo-spark-connector_2.12:10.2.0 \
    spark_analysis.py

# Create visualizations
echo ""
echo "4. Création des visualisations..."
python3 create_visualizations.py

# Start Flask API
echo ""
echo "5. Démarrage de l'API Flask..."
cd ../api
python3 app.py &
API_PID=$!

echo ""
echo "=============================================================================="
echo " PIPELINE TERMINÉ AVEC SUCCÈS!"
echo "=============================================================================="
echo ""
echo "API Flask démarrée sur: http://localhost:5000"
echo "PID: $API_PID"
echo ""
echo "Pour arrêter l'API: kill $API_PID"
echo ""
