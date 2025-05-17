# Interface d'administration

## Vue d'ensemble

L'application Orders dispose d'une interface d'administration Django complète et personnalisée qui permet aux administrateurs et aux gestionnaires de visualiser, créer, modifier et supprimer les données liées aux commandes.

## Configuration de l'interface d'admin

L'interface d'administration est configurée dans le fichier `admin.py`. Elle est conçue pour être intuitive et offrir des fonctionnalités avancées telles que :

- Affichage en ligne des éléments associés (inline)
- Filtres personnalisés
- Actions en lot
- Champs de recherche optimisés

## Classes d'administration principales

### OrderAdmin

Cette classe gère l'affichage et l'interaction avec les commandes dans l'interface d'administration.

```python
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_code', 'order_label', 'status_code', 'supplier', 
                    'order_date', 'items_total_amount', 'currency_code']
    list_filter = ['status_code', 'order_type_code', 'currency_code', 
                   'created', 'modified']
    search_fields = ['order_code', 'order_label', 'order_sup_name', 
                    'comment']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [OrderContactInline, OrderItemInline, OrderAddressInline]
    
    fieldsets = [
        (None, {
            'fields': [('order_code', 'order_label', 'order_type_code')]
        }),
        ('Supplier Information', {
            'fields': [('supplier', 'order_sup_name'), 
                      ('sup_nat_id', 'sup_nat_id_type')]
        }),
        ('Status & Dates', {
            'fields': [('status_code', 'status_label'), 
                      ('created', 'modified', 'order_date')]
        }),
        ('Financial Information', {
            'fields': [('items_total_amount', 'currency_code')]
        }),
        ('Additional Information', {
            'fields': ['comment', 'free_budget', 'track_timesheet'],
            'classes': ['collapse']
        }),
    ]
    
    actions = ['mark_as_approved', 'mark_as_rejected', 'mark_as_sent']
    
    def mark_as_approved(self, request, queryset):
        updated = queryset.update(status_code=OrderStatus.APPROVED)
        self.message_user(request, f'{updated} orders were marked as approved.')
    mark_as_approved.short_description = "Mark selected orders as approved"
```

### Affichage en ligne (Inlines)

Des classes d'affichage en ligne sont utilisées pour montrer les données associées directement dans la page de détail d'une commande :

```python
class OrderContactInline(admin.TabularInline):
    model = OrderContact
    extra = 0
    
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    fields = ['item_id', 'label', 'quantity', 'total_amount']
    
class OrderAddressInline(admin.TabularInline):
    model = OrderAddress
    extra = 0
    fields = ['type', 'street', 'zip_code', 'city', 'country_code']
```

## Navigation et interface utilisateur

### Page de liste des commandes

La page principale de liste des commandes affiche :

- Code de la commande
- Description
- Statut (avec indication visuelle par couleur)
- Fournisseur associé
- Date de commande
- Montant total
- Devise

Des filtres sont disponibles dans la barre latérale pour affiner la liste par :
- Statut
- Type de commande
- Devise
- Date de création/modification

### Page de détail d'une commande

La page de détail d'une commande est organisée en sections :

1. **Informations générales** : Code, description, type
2. **Informations fournisseur** : Fournisseur, nom, identifiants
3. **Statut et dates** : Statut actuel, dates de création/modification
4. **Informations financières** : Montant total, devise
5. **Informations complémentaires** : Commentaires, options spécifiques

Sous ces sections, trois onglets permettent de consulter :
- **Contacts** : Liste des contacts associés à la commande
- **Articles** : Liste des articles de la commande
- **Adresses** : Liste des adresses associées à la commande

## Actions en masse

L'administration permet d'effectuer des actions sur plusieurs commandes simultanément :

1. **Approuver les commandes** : Change le statut en "Approuvé"
2. **Rejeter les commandes** : Change le statut en "Rejeté"
3. **Marquer comme envoyé** : Change le statut en "Envoyé au fournisseur"

## Personnalisation de l'affichage

### Statuts avec code couleur

Les statuts des commandes sont affichés avec des codes couleur pour une meilleure lisibilité :

- **Brouillon** : Gris
- **Soumis** : Bleu
- **Approuvé** : Vert
- **Rejeté** : Rouge
- **Envoyé** : Orange
- **Reçu** : Vert foncé

```python
def get_status_display(self, obj):
    colors = {
        'dra': 'grey',
        'sub': 'blue',
        'app': 'green',
        'rej': 'red',
        'sen': 'orange',
        'rec': 'darkgreen',
    }
    color = colors.get(obj.status_code, 'black')
    return format_html('<span style="color: {};">{}</span>', 
                      color, obj.get_status_code_display())
get_status_display.short_description = 'Status'
```

### Affichage des montants formatés

Les montants sont affichés avec formatage de devise :

```python
def formatted_amount(self, obj):
    return format_html('{} <small>{}</small>', 
                      intcomma(obj.items_total_amount), 
                      obj.currency_code)
formatted_amount.short_description = 'Amount'
```

## Filtres personnalisés

Des filtres personnalisés sont disponibles pour faciliter la recherche :

```python
class OrderStatusFilter(admin.SimpleListFilter):
    title = 'status group'
    parameter_name = 'status_group'
    
    def lookups(self, request, model_admin):
        return (
            ('pending', 'Pending (Draft, Submitted)'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('processing', 'In Process (Sent, Acknowledged)'),
            ('completed', 'Completed (Received, Closed)'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'pending':
            return queryset.filter(status_code__in=['dra', 'sub'])
        # ...etc...
```

## Droits d'accès et permissions

L'accès à l'interface d'administration est contrôlé par les permissions Django :

- `orders.view_order` : Peut visualiser les commandes
- `orders.add_order` : Peut créer de nouvelles commandes
- `orders.change_order` : Peut modifier les commandes existantes
- `orders.delete_order` : Peut supprimer des commandes

## Personnalisation du tableau de bord

Le tableau de bord d'administration a été personnalisé pour inclure :

- Résumé des commandes par statut
- Graphique des commandes récentes
- Accès rapide aux commandes nécessitant une attention (en attente d'approbation)

## Conseils d'utilisation

1. **Recherche avancée** : Utilisez le champ de recherche pour trouver rapidement une commande par code, description ou fournisseur.

2. **Filtres combinés** : Combinez plusieurs filtres pour affiner vos résultats (par exemple, toutes les commandes approuvées d'un certain fournisseur).

3. **Actions en masse** : Utilisez les cases à cocher et le menu déroulant "Action" pour effectuer des opérations sur plusieurs commandes à la fois.

4. **Ajout rapide d'articles** : Lors de la création d'une commande, utilisez le bouton "Ajouter un autre article" pour ajouter rapidement plusieurs articles.
