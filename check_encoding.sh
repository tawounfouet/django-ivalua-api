#!/bin/bash
# Script pour vérifier et convertir l'encodage des fichiers CSV

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <chemin_fichier_csv>"
    exit 1
fi

FILE_PATH="$1"

if [ ! -f "$FILE_PATH" ]; then
    echo "Erreur: Le fichier '$FILE_PATH' n'existe pas."
    exit 1
fi

# Vérifier l'encodage actuel
echo "Vérification de l'encodage du fichier $FILE_PATH..."
ENCODING=$(file -bi "$FILE_PATH" | awk -F "=" '{print $2}')
echo "Encodage détecté: $ENCODING"

# Demander à l'utilisateur s'il souhaite convertir le fichier
echo -n "Voulez-vous convertir ce fichier en UTF-8? (o/n): "
read ANSWER

if [ "$ANSWER" = "o" ] || [ "$ANSWER" = "O" ]; then
    echo "Conversion en cours..."
    # Créer un backup du fichier original
    cp "$FILE_PATH" "${FILE_PATH}.bak"
    echo "Backup créé: ${FILE_PATH}.bak"
    
    # Essayer différents encodages pour la conversion
    ENCODINGS=("latin1" "cp1252" "iso-8859-1" "windows-1252")
    
    for ENC in "${ENCODINGS[@]}"; do
        echo "Essai de conversion depuis $ENC vers UTF-8..."
        iconv -f "$ENC" -t UTF-8 "${FILE_PATH}.bak" > "${FILE_PATH}.utf8" 2>/dev/null
        
        if [ $? -eq 0 ]; then
            mv "${FILE_PATH}.utf8" "$FILE_PATH"
            echo "Conversion réussie! Fichier sauvegardé en UTF-8."
            echo "Nouvel encodage:"
            file -bi "$FILE_PATH"
            exit 0
        fi
    done
    
    echo "Échec de toutes les tentatives de conversion. Le fichier n'a pas été modifié."
    exit 1
else
    echo "Aucune conversion effectuée."
fi
