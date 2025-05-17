# Architecture et modèles de données

## Vue d'ensemble de l'architecture

L'application Orders suit l'architecture standard de Django avec une séparation claire entre les modèles, les vues et les contrôleurs (pattern MVT - Model-View-Template). Elle utilise également Django REST Framework pour exposer une API RESTful.

## Diagramme de classes simplifié

```
+----------------+       +------------------+       +----------------+
|     Order      |<----->|   OrderContact   |       |   OrderItem    |
+----------------+       +------------------+       +----------------+
| id             |       | order (FK)       |       | order (FK)     |
| object_id      |       | requester_info   |       | item_id        |
| order_code     |       | billing_info     |       | label          |
| supplier (FK)  |       | delivery_info    |       | quantity       |
| status_code    |       | supplier_info    |       | total_amount   |
| ...            |       +------------------+       | ...            |
+----------------+                                  +----------------+
       ^
       |
       v
+----------------+
| OrderAddress   |
+----------------+
| order (FK)     |
| type           |
| street         |
| city           |
| ...            |
+----------------+
```

## Modèles de données détaillés

### Modèle Order

Ce modèle est le cœur de l'application et représente une commande dans le système.

#### Principaux champs

| Nom du champ | Type | Description |
|--------------|------|-------------|
| id | AutoField | Clé primaire |
| object_id | PositiveIntegerField | Identifiant dans le système externe |
| ord_id_origin | PositiveIntegerField | ID d'origine dans le système source |
| order_code | CharField | Code unique de la commande (ex: PO000001) |
| order_label | CharField | Description de la commande |
| order_type_code | CharField | Type de commande (défaut, blanket, contrat, spécial) |
| supplier | ForeignKey | Lien vers le fournisseur (optionnel) |
| status_code | CharField | Statut actuel de la commande |
| created | DateField | Date de création |
| modified | DateField | Date de dernière modification |
| order_date | DateField | Date officielle de la commande |
| items_total_amount | DecimalField | Montant total des articles |
| currency_code | CharField | Code devise (ex: EUR, USD) |

#### Relations

- Relation One-to-Many avec OrderContact
- Relation One-to-Many avec OrderItem
- Relation One-to-Many avec OrderAddress
- Relation Many-to-One avec Supplier

### Modèle OrderContact

Ce modèle gère les informations de contact associées à une commande.

#### Principaux champs

| Nom du champ | Type | Description |
|--------------|------|-------------|
| order | ForeignKey | Lien vers la commande associée |
| requester_firstname | CharField | Prénom du demandeur |
| requester_lastname | CharField | Nom du demandeur |
| requester_email | EmailField | Email du demandeur |
| billing_firstname | CharField | Prénom du contact facturation |
| billing_lastname | CharField | Nom du contact facturation |
| billing_email | EmailField | Email du contact facturation |
| delivery_firstname | CharField | Prénom du contact livraison |
| delivery_lastname | CharField | Nom du contact livraison |
| delivery_email | EmailField | Email du contact livraison |

### Modèle OrderItem

Ce modèle représente une ligne de commande individuelle.

#### Principaux champs

| Nom du champ | Type | Description |
|--------------|------|-------------|
| order | ForeignKey | Lien vers la commande associée |
| item_id | PositiveIntegerField | ID de l'article dans le système externe |
| label | CharField | Description de l'article |
| family_label | CharField | Famille de produit |
| quantity | DecimalField | Quantité commandée |
| total_amount | DecimalField | Montant total pour cet article |

### Modèle OrderAddress

Ce modèle gère les adresses associées à une commande.

#### Principaux champs

| Nom du champ | Type | Description |
|--------------|------|-------------|
| order | ForeignKey | Lien vers la commande associée |
| type | CharField | Type d'adresse (facturation, livraison, fournisseur) |
| street | CharField | Nom de la rue |
| zip_code | CharField | Code postal |
| city | CharField | Ville |
| country_code | CharField | Code pays |

## Énumérations et choix

### OrderStatus

```python
class OrderStatus(models.TextChoices):
    INITIAL = 'ini', _('Initial')
    DRAFT = 'dra', _('Draft')
    SUBMITTED = 'sub', _('Submitted')
    APPROVED = 'app', _('Approved')
    REJECTED = 'rej', _('Rejected')
    SENT = 'sen', _('Sent to supplier')
    ACKNOWLEDGED = 'ack', _('Acknowledged')
    PARTIALLY_RECEIVED = 'par', _('Partially received')
    RECEIVED = 'rec', _('Received')
    CANCELLED = 'can', _('Cancelled')
    CLOSED = 'clo', _('Closed')
    TERMINATED = 'end', _('Terminated')
```

### OrderType

```python
class OrderType(models.TextChoices):
    DEFAULT = 'default', _('Default')
    BLANKET = 'blanket', _('Blanket order')
    CONTRACT = 'contract', _('Contract-based')
    SPECIAL = 'special', _('Special order')
```

### AddressType

```python
class AddressType(models.TextChoices):
    BILLING = 'billing', _('Billing address')
    DELIVERY = 'delivery', _('Delivery address')
    SUPPLIER = 'supplier', _('Supplier address')
```

## Relations avec d'autres modèles

### Relation avec le modèle Supplier

La commande est associée à un fournisseur via une relation ForeignKey. Cette relation est optionnelle, car une commande peut être créée avant qu'un fournisseur ne soit assigné.

```python
supplier = models.ForeignKey(
    Supplier,
    on_delete=models.PROTECT,
    null=True,
    blank=True,
    related_name="orders",
    verbose_name=_("supplier"),
    help_text=_("Associated supplier record")
)
```

## Migrations

Les migrations de base de données sont générées automatiquement par Django. Pour appliquer les migrations, utilisez :

```bash
python manage.py migrate orders
```

Pour créer une nouvelle migration après modification des modèles :

```bash
python manage.py makemigrations orders
```

## Considérations de performance

- Des index de base de données sont définis sur les champs fréquemment utilisés pour les requêtes, comme `order_code`, `status_code` et `supplier`.
- Les relations ForeignKey utilisent `models.PROTECT` pour éviter la suppression accidentelle de données associées.
- Les requêtes complexes devraient utiliser `select_related()` et `prefetch_related()` pour optimiser les performances.
