


```sh
# Pour générer 50 fournisseurs (valeur par défaut)
python manage.py generate_fake_suppliers

# Pour générer 100 fournisseurs
python manage.py generate_fake_suppliers --count=100

# Pour supprimer les données existantes et générer 30 nouveaux fournisseurs
python manage.py generate_fake_suppliers --clean --count=30

# Pour utiliser une autre langue pour les données générées
python manage.py generate_fake_suppliers --locale=en_US