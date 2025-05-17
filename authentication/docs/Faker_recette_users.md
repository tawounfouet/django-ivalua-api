



```sh
mkdir -p authentication/management/commands
touch authentication/management/__init__.py
touch authentication/management/commands/__init__.py

touch authentication/management/commands/generate_fake_users.py


# Générer 20 utilisateurs (valeur par défaut)
python manage.py generate_fake_users

# Générer 50 utilisateurs
python manage.py generate_fake_users --count=50

# Supprimer les utilisateurs existants et en générer 30 nouveaux
python manage.py generate_fake_users --clean --count=30

# Créer un superuser admin@example.com avec le mot de passe "adminpass"
python manage.py generate_fake_users --create-superuser

# Définir 50% des utilisateurs comme fournisseurs
python manage.py generate_fake_users --supplier-ratio=0.5

# Utiliser une autre locale pour les données
python manage.py generate_fake_users --locale=en_US

```