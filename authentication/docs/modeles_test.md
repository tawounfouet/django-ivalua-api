Ce fichier de test couvre les principales fonctionnalités de vos modèles d'authentification :

1. Tests du UserManager :
- Création d'utilisateurs réguliers avec validation d'email
- Création de superutilisateurs avec validation des permissions


2. Tests du modèle User :
- Génération automatique de noms d'utilisateur
- Support pour les noms d'utilisateur personnalisés
- Normalisation des adresses email
- Fonctionnalités de verrouillage de compte
- Gestion des tentatives de connexion échouées
- Enregistrement des connexion


3. Tests du modèle UserProfile :
- Création automatique de profil
- Représentation sous forme de chaîne
- Mise à jour des champs de profil
- Valeurs par défaut pour les préférences de notification


Exécution des tests
```sh
# Pour exécuter ces tests, vous pouvez utiliser la commande suivante :
python manage.py test authentication.tests

# Ou avec pytest (si vous l'avez installé) :
pytest authentication/tests/test_models.py -v