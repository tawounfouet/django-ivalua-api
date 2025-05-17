# API et intégrations

## Vue d'ensemble de l'API

L'application Orders expose une API RESTful complète construite avec Django REST Framework (DRF). Cette API permet l'interaction programmatique avec les commandes et leurs données associées, facilitant l'intégration avec d'autres systèmes.

## Points d'accès (endpoints)

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/orders/` | GET | Liste toutes les commandes |
| `/api/orders/` | POST | Crée une nouvelle commande |
| `/api/orders/{id}/` | GET | Détails d'une commande spécifique |
| `/api/orders/{id}/` | PUT/PATCH | Met à jour une commande |
| `/api/orders/{id}/` | DELETE | Supprime une commande |
| `/api/ordercontacts/` | GET/POST | Liste/Crée des contacts de commande |
| `/api/ordercontacts/{id}/` | GET/PUT/PATCH/DELETE | Opérations sur un contact spécifique |
| `/api/orderitems/` | GET/POST | Liste/Crée des articles de commande |
| `/api/orderitems/{id}/` | GET/PUT/PATCH/DELETE | Opérations sur un article spécifique |
| `/api/orderaddresses/` | GET/POST | Liste/Crée des adresses de commande |
| `/api/orderaddresses/{id}/` | GET/PUT/PATCH/DELETE | Opérations sur une adresse spécifique |

## Configuration de l'API

L'API est configurée dans le fichier `api_views.py` en utilisant les ViewSets de Django REST Framework :

```python
class OrderViewSet(viewsets.ModelViewSet):
    """
    API endpoint for orders.
    """
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status_code', 'supplier', 'order_type_code']
    search_fields = ['order_code', 'order_label', 'order_sup_name']
```

Les URLs sont configurées dans `urls.py` à l'aide du router DRF :

```python
router = DefaultRouter()
router.register(r'orders', OrderViewSet)
router.register(r'ordercontacts', OrderContactViewSet)
router.register(r'orderitems', OrderItemViewSet)
router.register(r'orderaddresses', OrderAddressViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
```

## Sérialiseurs

Les sérialiseurs traduisent les modèles Django en formats JSON/XML et inversement. Ils sont définis dans `serializers.py` :

### OrderSerializer

```python
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    contacts = OrderContactSerializer(many=True, read_only=True)
    addresses = OrderAddressSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = '__all__'
```

### OrderItemSerializer

```python
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'
```

### OrderContactSerializer

```python
class OrderContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderContact
        fields = '__all__'
```

### OrderAddressSerializer

```python
class OrderAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderAddress
        fields = '__all__'
```

## Filtrage et recherche

L'API prend en charge le filtrage et la recherche pour faciliter la récupération des données :

- **Filtrage** : Permet de filtrer les commandes par statut, fournisseur, type, etc.
  ```
  /api/orders/?status_code=app&supplier=1
  ```

- **Recherche** : Permet de rechercher des commandes par texte
  ```
  /api/orders/?search=PO000123
  ```

- **Pagination** : Les résultats sont paginés automatiquement
  ```
  {
    "count": 100,
    "next": "http://example.com/api/orders/?page=2",
    "previous": null,
    "results": [...]
  }
  ```

## Authentification et sécurité

L'API utilise plusieurs mécanismes d'authentification et de sécurité :

1. **Token Authentication** : Chaque requête doit inclure un token dans l'en-tête
   ```
   Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
   ```

2. **Permissions** : Les permissions suivantes sont appliquées :
   - `IsAuthenticated` : L'utilisateur doit être authentifié
   - Permissions spécifiques basées sur les rôles

## Exemples d'utilisation de l'API

### Création d'une commande (Python)

```python
import requests

url = "http://example.com/api/orders/"
headers = {
    "Authorization": "Token YOUR_TOKEN_HERE",
    "Content-Type": "application/json"
}
data = {
    "object_id": 1,
    "ord_id_origin": 1001,
    "order_code": "PO000001",
    "order_label": "Test Order",
    "order_type_code": "default",
    "basket_id": 1,
    "supplier": 1,
    "status_code": "dra",
    "currency_code": "EUR"
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

### Récupération des commandes (JavaScript)

```javascript
fetch('http://example.com/api/orders/?status_code=app', {
  headers: {
    'Authorization': 'Token YOUR_TOKEN_HERE'
  }
})
.then(response => response.json())
.then(data => console.log(data));
```

## Intégrations avec d'autres systèmes

### Intégration avec l'API Ivalua

L'application Orders peut s'intégrer avec l'API Ivalua pour synchroniser les données de commande. Pour ce faire, utilisez :

```bash
python manage.py sync_ivalua_orders
```

### Intégration avec les systèmes ERP

Des connecteurs personnalisés peuvent être développés pour l'intégration avec des systèmes ERP tels que SAP, Oracle, etc. Consultez les exemples dans le dossier `management/commands/`.

## Documentation de l'API

Une documentation interactive de l'API est disponible via Swagger/OpenAPI :

```
/api/docs/
```

Cette interface permet de :
- Parcourir tous les endpoints disponibles
- Tester les requêtes directement dans le navigateur
- Consulter les schémas de données
- Comprendre les exigences d'authentification
