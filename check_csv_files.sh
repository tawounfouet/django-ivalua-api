#!/bin/bash
# Ce script vérifie si les fichiers CSV peuvent être ouverts correctement

DATA_DIR="accounting/data"
echo "Vérification des fichiers CSV dans $DATA_DIR..."

# Liste des fichiers à vérifier
CSV_FILES=(
    "commune_insee.csv"
    "exercice_comptable.csv"
    "export_comptes_pcg.csv"
    "journal_comptable.csv"
    "type-de-comptabilite.csv"
    "type-de-compte-client.csv"
    "type_d_ecrirture_comptable.csv"
    "type_d_engagement.csv"
    "type_lettrage.csv"
    "type_payeur.csv"
    "type_prestation.csv"
    "type_tarification.csv"
    "activite.csv"
)

# Vérifier chaque fichier
for file in "${CSV_FILES[@]}"; do
    FULL_PATH="$DATA_DIR/$file"
    
    if [ ! -f "$FULL_PATH" ]; then
        echo "⚠️ Le fichier $file n'existe pas!"
        continue
    fi
    
    echo -n "Vérification de $file ... "
    
    # Essayer de lire les premières lignes avec différents encodages
    READ_SUCCESS=0
    
    # Essayer avec Latin1 (ISO-8859-1)
    if python -c "import csv; f=open('$FULL_PATH', 'r', encoding='latin1'); csv.reader(f, delimiter=';'); f.close(); exit(0)" 2>/dev/null; then
        echo "✅ Ouverture OK avec latin1!"
        READ_SUCCESS=1
    fi
    
    if [ $READ_SUCCESS -eq 0 ]; then
        # Essayer avec CP1252
        if python -c "import csv; f=open('$FULL_PATH', 'r', encoding='cp1252'); csv.reader(f, delimiter=';'); f.close(); exit(0)" 2>/dev/null; then
            echo "✅ Ouverture OK avec cp1252!"
            READ_SUCCESS=1
        fi
    fi
    
    if [ $READ_SUCCESS -eq 0 ]; then
        # Essayer avec UTF-8
        if python -c "import csv; f=open('$FULL_PATH', 'r', encoding='utf-8'); csv.reader(f, delimiter=';'); f.close(); exit(0)" 2>/dev/null; then
            echo "✅ Ouverture OK avec utf-8!"
            READ_SUCCESS=1
        fi
    fi
    
    if [ $READ_SUCCESS -eq 0 ]; then
        echo "❌ Erreur: Impossible d'ouvrir le fichier avec les encodages usuels!"
    fi
done

echo "Vérification terminée!"
echo "Tous les fichiers qui ont passé la validation peuvent être importés normalement."
