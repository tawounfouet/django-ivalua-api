


```sh
python -m venv .venv
# macOS/Linux 
source .venv/bin/activate

# Windows
source .venv\Scripts\activate

pip install django
pip install djangorestframework
pip install djangorestframework-simplejwt Pillow django-filter
pip install pytest
pip install pytest-django
pip install django-cors-headers


django-admin startproject project .

```

## Problème d'incohérence des migrations
Cette erreur se produit car vous essayez de créer un modèle utilisateur personnalisé alors que la base de données contient déjà des migrations appliquées qui dépendent du modèle utilisateur par défaut de Django.

Pour résoudre ce problème de migration, vous avez quelques options :

**Option 1** : Réinitialiser complètement la base de données (recommandé pour le développement)

```sh
# Supprimez le fichier de base de données (db.sqlite3) :
rm db.sqlite3

# Supprimez toutes les migrations existantes
rm -rf */migrations/0*.py

# Créez à nouveau toutes les migrations :
python manage.py makemigrations
# Appliquez les migrations :
python manage.py migrate

```