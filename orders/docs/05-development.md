# Guide de développement

## Configuration de l'environnement de développement

Pour commencer à développer sur l'application Orders, suivez ces étapes pour configurer votre environnement:

### Prérequis

- Python 3.10 ou supérieur
- pip (gestionnaire de paquets Python)
- virtualenv ou venv
- Git

### Installation

1. **Cloner le dépôt**

```bash
git clone <repository-url>
cd django-ivalua-api
```

2. **Créer un environnement virtuel**

```bash
python -m venv .venv
```

3. **Activer l'environnement virtuel**

Sous Windows:
```bash
.venv\Scripts\activate
```

Sous Linux/Mac:
```bash
source .venv/bin/activate
```

4. **Installer les dépendances**

```bash
pip install -r requirements.txt
```

5. **Appliquer les migrations**

```bash
python manage.py migrate
```

6. **Créer un superutilisateur**

```bash
python manage.py createsuperuser
```

7. **Générer des données de test**

```bash
python manage.py generate_fake_orders
```

8. **Lancer le serveur de développement**

```bash
python manage.py runserver
```

## Architecture du code

### Répertoires et fichiers principaux

```
orders/
├── __init__.py
├── admin.py           # Configuration de l'administration
├── api_views.py       # Vues API (viewsets DRF)
├── apps.py            # Configuration de l'application
├── models.py          # Modèles de données
├── serializers.py     # Sérialiseurs pour l'API
├── tests.py           # Tests unitaires (ancien)
├── urls.py            # Configuration des URLs
├── views.py           # Vues traditionnelles
├── docs/              # Documentation
├── management/        # Commandes personnalisées
│   └── commands/
│       └── generate_fake_orders.py
├── migrations/        # Migrations de base de données
└── tests/             # Tests unitaires organisés
    ├── __init__.py
    └── test_models.py
```

### Convention de codage

Ce projet suit les conventions PEP 8 pour le code Python. Quelques règles importantes:

- Utiliser 4 espaces pour l'indentation (pas de tabulations)
- Limiter les lignes à 79-99 caractères maximum
- Utiliser des noms descriptifs pour les variables et fonctions
- Les commentaires et docstrings doivent être en anglais
- Préférer les docstrings au format Sphinx
- Organiser les imports comme suit:
  1. Imports de la bibliothèque standard
  2. Imports de bibliothèques tierces
  3. Imports Django
  4. Imports locaux (relatifs)

## Ajouter de nouvelles fonctionnalités

### Étendre les modèles

Pour ajouter un nouveau champ à un modèle existant:

1. Modifiez le fichier `models.py` pour ajouter le nouveau champ
2. Créez une migration:
   ```bash
   python manage.py makemigrations orders
   ```
3. Appliquez la migration:
   ```bash
   python manage.py migrate orders
   ```
4. Mettez à jour les tests dans `tests/test_models.py`
5. Mettez à jour les sérialiseurs dans `serializers.py` si nécessaire

### Créer un nouveau modèle

Pour créer un nouveau modèle:

1. Ajoutez la classe du modèle dans `models.py`:
   ```python
   class NewModel(BaseModel):
       name = models.CharField(max_length=100)
       order = models.ForeignKey(Order, on_delete=models.CASCADE)
       
       class Meta:
           verbose_name = "New Model"
           verbose_name_plural = "New Models"
       
       def __str__(self):
           return self.name
   ```

2. Créez et appliquez les migrations

3. Créez un sérialiseur dans `serializers.py`:
   ```python
   class NewModelSerializer(serializers.ModelSerializer):
       class Meta:
           model = NewModel
           fields = '__all__'
   ```

4. Ajoutez un ViewSet dans `api_views.py`:
   ```python
   class NewModelViewSet(viewsets.ModelViewSet):
       queryset = NewModel.objects.all()
       serializer_class = NewModelSerializer
   ```

5. Ajoutez les routes dans `urls.py`:
   ```python
   router.register(r'newmodels', NewModelViewSet)
   ```

6. Ajoutez la configuration admin dans `admin.py`:
   ```python
   @admin.register(NewModel)
   class NewModelAdmin(admin.ModelAdmin):
       list_display = ['name', 'order']
       search_fields = ['name']
       list_filter = ['order']
   ```

7. Créez des tests dans `tests/test_models.py`

### Ajouter des endpoints API

Pour ajouter un nouvel endpoint à l'API existante:

1. Créez une nouvelle méthode dans le ViewSet approprié:
   ```python
   @action(detail=True, methods=['post'])
   def custom_action(self, request, pk=None):
       instance = self.get_object()
       # Logique personnalisée
       return Response({'status': 'success'})
   ```

2. Documentez l'endpoint dans la documentation de l'API

### Ajouter une commande personnalisée

Pour créer une nouvelle commande de gestion:

1. Créez un fichier dans `management/commands/`, par exemple `new_command.py`:
   ```python
   from django.core.management.base import BaseCommand
   
   class Command(BaseCommand):
       help = 'Description of what the command does'
       
       def add_arguments(self, parser):
           parser.add_argument('--option', type=str, help='Description')
       
       def handle(self, *args, **options):
           # Logique de commande
           self.stdout.write(self.style.SUCCESS('Command completed'))
   ```

2. La commande peut être exécutée avec:
   ```bash
   python manage.py new_command --option=value
   ```

## Bonnes pratiques de développement

### Tests

Tous les nouveaux développements doivent être accompagnés de tests unitaires. La couverture de code cible est de 80% minimum.

Pour exécuter les tests:
```bash
python manage.py test orders
```

Pour exécuter un test spécifique:
```bash
python manage.py test orders.tests.test_models.OrderModelTest
```

### Optimisation des performances

- Utilisez `select_related()` et `prefetch_related()` pour optimiser les requêtes impliquant des relations
- Indexez les champs couramment utilisés dans les requêtes
- Utilisez `values()` ou `values_list()` pour les requêtes nécessitant seulement certains champs
- Préférez les mises à jour en masse avec `update()` plutôt que des boucles de sauvegarde

### Sécurité

- Validez toujours les données d'entrée
- Utilisez les permissions Django et DRF pour contrôler l'accès
- N'exposez que les données nécessaires dans l'API
- Utilisez `transaction.atomic()` pour les opérations en plusieurs étapes

## Processus de développement

### Workflow Git

1. Créez une branche pour votre fonctionnalité
   ```bash
   git checkout -b feature/nouvelle-fonctionnalite
   ```

2. Faites vos modifications

3. Exécutez les tests
   ```bash
   python manage.py test orders
   ```

4. Vérifiez la conformité du code
   ```bash
   flake8 orders
   ```

5. Soumettez un Pull Request avec une description détaillée

### Documentation

Toute nouvelle fonctionnalité doit être documentée:

1. Docstrings pour les classes et méthodes
2. Mise à jour de la documentation dans le dossier `docs/`
3. Commentaires pour le code complexe

## Résolution des problèmes courants

### Migrations

**Problème**: Conflit de migration

**Solution**:
1. Revenez à un état connu:
   ```bash
   python manage.py migrate orders <migration_avant_conflit>
   ```
2. Supprimez les fichiers de migration conflictuels
3. Régénérez une nouvelle migration:
   ```bash
   python manage.py makemigrations orders
   ```

### Performance

**Problème**: Requêtes N+1

**Solution**: Utilisez `select_related` ou `prefetch_related`:
```python
# Avant
orders = Order.objects.all()
for order in orders:
    print(order.supplier.name)  # Une requête par ordre

# Après
orders = Order.objects.select_related('supplier').all()
for order in orders:
    print(order.supplier.name)  # Pas de requête supplémentaire
```

### Données corrompues

**Problème**: Données incohérentes

**Solution**: Utilisez des transactions atomiques:
```python
from django.db import transaction

@transaction.atomic
def create_order_with_items(order_data, items_data):
    order = Order.objects.create(**order_data)
    for item_data in items_data:
        OrderItem.objects.create(order=order, **item_data)
    return order
```

## Ressources supplémentaires

- [Documentation Django](https://docs.djangoproject.com/)
- [Documentation Django REST Framework](https://www.django-rest-framework.org/)
- [PEP 8 -- Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/)
- [Two Scoops of Django](https://www.feldroy.com/books/two-scoops-of-django-3-x)
