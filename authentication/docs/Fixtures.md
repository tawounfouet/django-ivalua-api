

## Fixtures pour l'application Authentication
Les fixtures sont un excellent moyen de créer des données initiales pour votre application. Voici comment créer des fixtures pour votre application d'authentification.

1. Structure des fixtures
Je vais créer deux fichiers de fixtures :

users.json : Contenant des utilisateurs de différents types (admin, staff, fournisseur, utilisateur normal)
profiles.json : Contenant les profils associés à ces utilisateurs
2. Fichier users.json

## 4. Comment utiliser ces fixtures
Créez un répertoire pour les fixtures dans votre application d'authentification :
```bash
mkdir -p authentication/fixtures

touch authentication/fixtures/users.json
touch authentication/fixtures/profiles.json


# Enregistrez les fichiers JSON dans ce répertoire :

# Chargez les fixtures dans votre base de données :
python manage.py loaddata authentication/fixtures/users.json authentication/fixtures/profiles.json
```


