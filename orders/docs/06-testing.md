# Tests et qualité du code

## Vue d'ensemble

L'application Orders utilise un système de tests complet pour garantir la qualité du code et le bon fonctionnement des fonctionnalités. Cette documentation explique comment les tests sont organisés, comment les exécuter et comment assurer la qualité du code.

## Structure des tests

Les tests sont organisés dans le répertoire `tests/` avec la structure suivante :

```
orders/
└── tests/
    ├── __init__.py
    ├── test_models.py
    ├── test_api.py
    ├── test_admin.py
    └── test_commands.py
```

### Types de tests

1. **Tests unitaires** : Tests isolés des fonctions et méthodes individuelles
2. **Tests d'intégration** : Tests du comportement de plusieurs composants fonctionnant ensemble
3. **Tests API** : Tests des endpoints de l'API REST
4. **Tests fonctionnels** : Tests du comportement général de l'application

## Tests des modèles

Le fichier `test_models.py` contient des tests pour tous les modèles de l'application Orders. Ces tests vérifient :

- La création et la validation des objets
- Les contraintes et validations de champs
- Les méthodes personnalisées des modèles
- Les relations entre modèles

Exemple de test pour le modèle Order :

```python
class OrderModelTest(TestCase):
    """Test suite for the Order model."""
    
    def setUp(self):
        """Set up test data."""
        # Create a test supplier
        self.supplier = Supplier.objects.create(
            object_id=1,
            code='SUP000001',
            supplier_name='Test Supplier',
            legal_name='Test Supplier Legal Name',
            creation_system_date=timezone.now().date(),
        )
        
        # Create valid order data
        self.valid_order_data = {
            'object_id': 1,
            'ord_id_origin': 1001,
            'order_code': 'PO000001',
            'order_label': 'Test Order',
            'order_type_code': OrderType.DEFAULT,
            'basket_id': 1,
            'supplier': self.supplier,
            'order_sup_id': 1,
            'order_sup_name': 'Test Supplier',
            'created': timezone.now().date(),
            'login_created': 'testuser',
            'status_code': OrderStatus.DRAFT,
            'order_date': timezone.now().date(),
            'currency_code': 'EUR',
        }
        
    def test_create_order(self):
        """Test creating a valid order."""
        order = Order.objects.create(**self.valid_order_data)
        self.assertEqual(order.order_code, 'PO000001')
        self.assertEqual(order.status_code, OrderStatus.DRAFT)
        self.assertEqual(order.supplier, self.supplier)
```

## Tests de l'API

Le fichier `test_api.py` contient des tests pour les endpoints de l'API REST. Ces tests vérifient :

- La récupération de données (GET)
- La création de données (POST)
- La mise à jour de données (PUT/PATCH)
- La suppression de données (DELETE)
- Le filtrage et la recherche
- L'authentification et les permissions

Exemple de test pour l'API des commandes :

```python
class OrderAPITest(APITestCase):
    def setUp(self):
        # Create a user for authentication
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create test data
        self.supplier = Supplier.objects.create(
            object_id=1,
            code='SUP000001',
            supplier_name='Test Supplier',
            creation_system_date=timezone.now().date(),
        )
        
        self.order = Order.objects.create(
            object_id=1,
            ord_id_origin=1001,
            order_code='PO000001',
            order_label='Test Order',
            order_type_code=OrderType.DEFAULT,
            basket_id=1,
            supplier=self.supplier,
            order_sup_id=1,
            order_sup_name='Test Supplier',
            status_code=OrderStatus.DRAFT,
            currency_code='EUR',
        )
    
    def test_list_orders(self):
        """Test listing orders via API."""
        url = reverse('order-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_order(self):
        """Test creating an order via API."""
        url = reverse('order-list')
        data = {
            'object_id': 2,
            'ord_id_origin': 1002,
            'order_code': 'PO000002',
            'order_label': 'Another Test Order',
            'order_type_code': OrderType.DEFAULT,
            'basket_id': 2,
            'supplier': self.supplier.id,
            'order_sup_id': 1,
            'order_sup_name': 'Test Supplier',
            'status_code': OrderStatus.DRAFT,
            'currency_code': 'EUR',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 2)
```

## Tests des commandes de gestion

Le fichier `test_commands.py` contient des tests pour les commandes de gestion personnalisées. Ces tests vérifient :

- L'exécution correcte des commandes
- Le traitement des arguments
- La gestion des erreurs
- Les résultats attendus

Exemple de test pour la commande `generate_fake_orders` :

```python
class GenerateFakeOrdersTest(TestCase):
    def setUp(self):
        # Create a supplier for testing
        self.supplier = Supplier.objects.create(
            object_id=1,
            code='SUP000001',
            supplier_name='Test Supplier',
            creation_system_date=timezone.now().date(),
        )
    
    def test_generate_fake_orders(self):
        """Test the generate_fake_orders command."""
        call_command('generate_fake_orders', count=5)
        
        # Verify 5 orders were created
        self.assertEqual(Order.objects.count(), 5)
        
        # Verify orders have items
        order = Order.objects.first()
        self.assertTrue(order.items.exists())
```

## Exécution des tests

### Exécuter tous les tests

```bash
python manage.py test orders
```

### Exécuter un fichier de tests spécifique

```bash
python manage.py test orders.tests.test_models
```

### Exécuter une classe de tests spécifique

```bash
python manage.py test orders.tests.test_models.OrderModelTest
```

### Exécuter un test spécifique

```bash
python manage.py test orders.tests.test_models.OrderModelTest.test_create_order
```

### Exécuter les tests avec couverture

```bash
coverage run --source='orders' manage.py test orders
coverage report
```

Pour générer un rapport HTML de couverture :

```bash
coverage html
```

## Intégration continue

L'application Orders est intégrée dans un système d'intégration continue qui exécute automatiquement les tests à chaque commit et pull request. Ce système vérifie :

1. **Exécution de tous les tests** : S'assure que tous les tests passent
2. **Couverture de code** : Vérifie que la couverture de code est suffisante (> 80%)
3. **Qualité du code** : Vérifie que le code respecte les standards PEP 8

## Qualité du code

### Linting et vérification de style

Nous utilisons Flake8 pour vérifier la conformité du code aux standards PEP 8 :

```bash
flake8 orders/
```

Configuration Flake8 dans `setup.cfg` :

```ini
[flake8]
max-line-length = 99
exclude = .git,__pycache__,build,dist,migrations
```

### Types statiques

Nous utilisons mypy pour la vérification des types :

```bash
mypy orders/
```

### Documentation du code

Toutes les classes, méthodes et fonctions doivent être documentées selon le format docstring Sphinx :

```python
def my_function(param1, param2):
    """
    Description de la fonction.
    
    Args:
        param1: Description du premier paramètre
        param2: Description du deuxième paramètre
    
    Returns:
        Description de la valeur de retour
    
    Raises:
        Exception: Description de l'exception
    """
    pass
```

## Meilleures pratiques

### Écriture de tests efficaces

1. **Isolez les tests** : Chaque test doit être indépendant et ne pas dépendre des autres tests
2. **Utilisez setUp et tearDown** : Préparez et nettoyez l'environnement de test
3. **Testez les cas limites** : N'oubliez pas de tester les cas d'erreur et les valeurs limites
4. **Utilisez des assertions spécifiques** : Préférez `assertEqual` à `assertTrue(a == b)`
5. **Nommez vos tests clairement** : Le nom du test doit décrire ce qu'il teste

### Conseils pour la maintenabilité des tests

1. **Modularité** : Divisez les grands tests en tests plus petits et ciblés
2. **Évitez la duplication** : Utilisez des helpers ou des fixtures pour le code commun
3. **Maintenez les tests à jour** : Mettez à jour les tests lorsque le code change
4. **Commentez les tests complexes** : Expliquez la logique des tests difficiles à comprendre
5. **Équilibre couverture et lisibilité** : Visez une bonne couverture sans rendre les tests illisibles

## Dépannage des tests

### Tests qui échouent de manière intermittente

Problèmes courants :
- Dépendances entre tests
- Race conditions
- Dépendances externes non mockées

Solution :
- Assurez-vous que chaque test nettoie après lui
- Utilisez des transactions pour isoler les changements de base de données
- Mockez les services externes

### Tests lents

Pour accélérer l'exécution des tests :

1. **Utilisez une base de données en mémoire** :
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.sqlite3',
           'NAME': ':memory:',
       }
   }
   ```

2. **Minimisez les opérations coûteuses** : Limitez le nombre d'objets créés dans les tests

3. **Parallélisez les tests** :
   ```bash
   pytest -xvs orders/ -n 4
   ```

## Ressources

- [Documentation des tests Django](https://docs.djangoproject.com/en/stable/topics/testing/)
- [Django REST Framework - Testing](https://www.django-rest-framework.org/api-guide/testing/)
- [Coverage.py](https://coverage.readthedocs.io/)
- [Pytest Django](https://pytest-django.readthedocs.io/)
