# Guide d'utilisation

Ce guide détaille les différentes fonctionnalités de l'application "Orders" et explique comment l'utiliser efficacement au sein du système P2P Ivalua.

## Accès à l'application

### Interface utilisateur

L'application Orders est accessible via deux interfaces principales :

1. **Interface d'administration Django** : Pour les administrateurs et gestionnaires
   - URL : `/admin/orders/`
   - Nécessite des identifiants administrateur

2. **API REST** : Pour l'intégration avec d'autres applications
   - URL : `/api/orders/`
   - Nécessite une authentification via token

## Gestion des commandes

### Création d'une commande

#### Via l'interface d'administration

1. Accédez à l'interface d'administration
2. Cliquez sur "Commandes" puis "Ajouter une commande"
3. Remplissez les informations obligatoires :
   - Identifiant externe (object_id)
   - Code de commande (order_code)
   - Description (order_label)
   - Type de commande
   - ID du panier (basket_id)
   - Fournisseur (si connu)
   - Statut
   - Devise
4. Cliquez sur "Enregistrer"
5. Après l'enregistrement initial, vous pourrez ajouter :
   - Des contacts associés à la commande
   - Des articles de commande
   - Des adresses (facturation, livraison)

#### Via l'API REST

Utilisez une requête POST vers `/api/orders/` avec un payload JSON similaire à :

```json
{
  "object_id": 1,
  "ord_id_origin": 1001,
  "order_code": "PO000123",
  "order_label": "Commande de fournitures bureau",
  "order_type_code": "default",
  "basket_id": 1,
  "supplier": 1,
  "order_sup_name": "Fournisseur ABC",
  "status_code": "dra",
  "currency_code": "EUR"
}
```

### Consultation des commandes

#### Via l'interface d'administration

1. Accédez à l'interface d'administration
2. Cliquez sur "Commandes" pour voir la liste
3. Utilisez les filtres disponibles dans la barre latérale pour affiner la recherche :
   - Par statut
   - Par type
   - Par devise
   - Par date de création
4. Utilisez le champ de recherche pour trouver une commande par :
   - Code de commande
   - Description
   - Nom du fournisseur
5. Cliquez sur un code de commande pour voir les détails

#### Via l'API REST

Pour obtenir toutes les commandes :
```
GET /api/orders/
```

Pour obtenir une commande spécifique :
```
GET /api/orders/1/
```

Pour filtrer les commandes :
```
GET /api/orders/?status_code=app&supplier=1
```

Pour rechercher des commandes :
```
GET /api/orders/?search=PO000123
```

### Modification d'une commande

#### Via l'interface d'administration

1. Accédez à la page de détail de la commande
2. Modifiez les champs souhaités
3. Pour ajouter un article à la commande :
   - Faites défiler jusqu'à la section "Articles de commande"
   - Cliquez sur "Ajouter un article"
   - Remplissez les détails de l'article
   - Cliquez sur "Enregistrer"
4. Pour ajouter une adresse :
   - Faites défiler jusqu'à la section "Adresses"
   - Cliquez sur "Ajouter une adresse"
   - Sélectionnez le type d'adresse (facturation ou livraison)
   - Remplissez les détails de l'adresse
   - Cliquez sur "Enregistrer"
5. Pour ajouter des contacts :
   - Faites défiler jusqu'à la section "Contacts"
   - Cliquez sur "Ajouter un contact"
   - Remplissez les coordonnées du contact
   - Cliquez sur "Enregistrer"

#### Via l'API REST

Pour mettre à jour une commande complète :
```
PUT /api/orders/1/
```

Pour mettre à jour partiellement une commande :
```
PATCH /api/orders/1/
```

### Changement de statut d'une commande

#### Via l'interface d'administration

1. Pour changer le statut d'une seule commande :
   - Accédez à la page de détail de la commande
   - Modifiez le champ "Status code"
   - Cliquez sur "Enregistrer"

2. Pour changer le statut de plusieurs commandes :
   - Dans la liste des commandes, cochez les cases des commandes à modifier
   - Dans le menu déroulant "Actions", sélectionnez l'action appropriée :
     - "Marquer comme approuvé"
     - "Marquer comme rejeté"
     - "Marquer comme envoyé"
   - Cliquez sur "Go"

#### Via l'API REST

```
PATCH /api/orders/1/
{
  "status_code": "app"
}
```

### Suppression d'une commande

#### Via l'interface d'administration

1. Accédez à la liste des commandes
2. Cochez la case à côté de la commande à supprimer
3. Dans le menu déroulant "Actions", sélectionnez "Supprimer les commandes sélectionnées"
4. Confirmez la suppression

Alternativement, depuis la page de détail d'une commande :
1. Cliquez sur le bouton "Supprimer" en bas de page
2. Confirmez la suppression

#### Via l'API REST

```
DELETE /api/orders/1/
```

## Gestion des articles de commande

### Ajout d'articles à une commande existante

#### Via l'interface d'administration

1. Accédez à la page de détail de la commande
2. Faites défiler jusqu'à la section "Articles de commande"
3. Cliquez sur "Ajouter un article"
4. Remplissez les champs obligatoires :
   - ID de l'article
   - Description
   - Quantité
   - Montant total
5. Cliquez sur "Enregistrer"

#### Via l'API REST

```
POST /api/orderitems/
{
  "order": 1,
  "item_id": 123,
  "label": "Écran d'ordinateur 24 pouces",
  "quantity": 2,
  "total_amount": 350.00
}
```

### Modification d'un article

#### Via l'interface d'administration

1. Accédez à la page de détail de la commande
2. Faites défiler jusqu'à la section "Articles de commande"
3. Cliquez sur l'article à modifier
4. Modifiez les champs souhaités
5. Cliquez sur "Enregistrer"

Alternativement, depuis la liste des articles :
1. Accédez à l'interface d'administration
2. Cliquez sur "Articles de commande"
3. Cliquez sur l'article à modifier

#### Via l'API REST

```
PATCH /api/orderitems/1/
{
  "quantity": 3,
  "total_amount": 525.00
}
```

## Gestion des contacts de commande

### Types de contacts

Une commande peut avoir plusieurs types de contacts associés :

1. **Demandeur** : La personne qui a initialement demandé la commande
2. **Contact facturation** : La personne responsable des questions de facturation
3. **Contact livraison** : La personne qui réceptionnera les articles
4. **Contact fournisseur** : Le contact chez le fournisseur pour cette commande

### Ajout de contacts à une commande

#### Via l'interface d'administration

1. Accédez à la page de détail de la commande
2. Faites défiler jusqu'à la section "Contacts"
3. Cliquez sur "Ajouter un contact"
4. Remplissez les informations pour le(s) type(s) de contact approprié(s)
   - Vous pouvez remplir plusieurs types de contacts dans un même enregistrement
   - Laissez vides les champs des types de contacts non concernés
5. Cliquez sur "Enregistrer"

#### Via l'API REST

```
POST /api/ordercontacts/
{
  "order": 1,
  "requester_firstname": "Jean",
  "requester_lastname": "Dupont",
  "requester_email": "jean.dupont@example.com",
  "billing_firstname": "Marie",
  "billing_lastname": "Martin",
  "billing_email": "marie.martin@example.com"
}
```

## Gestion des adresses

### Types d'adresses

Une commande peut avoir plusieurs adresses associées :

1. **Adresse de facturation** : Où la facture sera envoyée
2. **Adresse de livraison** : Où les articles seront livrés
3. **Adresse du fournisseur** : L'adresse du fournisseur pour cette commande

### Ajout d'adresses à une commande

#### Via l'interface d'administration

1. Accédez à la page de détail de la commande
2. Faites défiler jusqu'à la section "Adresses"
3. Cliquez sur "Ajouter une adresse"
4. Sélectionnez le type d'adresse
5. Remplissez les informations d'adresse :
   - Numéro
   - Rue
   - Code postal
   - Ville
   - Pays
6. Cliquez sur "Enregistrer"

#### Via l'API REST

```
POST /api/orderaddresses/
{
  "order": 1,
  "type": "billing",
  "street": "123 Rue des Exemples",
  "zip_code": "75001",
  "city": "Paris",
  "country_code": "FR"
}
```

## Recherche et filtrage

### Recherche avancée dans l'interface d'administration

1. Accédez à la liste des commandes
2. Utilisez le champ de recherche en haut à droite
3. La recherche s'effectue sur plusieurs champs :
   - Code de commande
   - Description
   - Nom du fournisseur
   - Commentaire

### Filtres disponibles

Dans la barre latérale de la liste des commandes, vous pouvez filtrer par :
- Statut
- Type de commande
- Devise
- Date de création
- Date de modification

### Utilisation de l'API pour des requêtes complexes

Pour des recherches plus complexes, utilisez l'API avec plusieurs paramètres :

```
GET /api/orders/?status_code=app&supplier=1&order_date__gte=2025-01-01
```

## Exportation de données

### Export CSV depuis l'interface d'administration

1. Accédez à la liste des commandes
2. Sélectionnez les commandes à exporter
3. Dans le menu déroulant "Actions", sélectionnez "Exporter les commandes sélectionnées (CSV)"
4. Cliquez sur "Go"
5. Enregistrez le fichier CSV

### Export via l'API

Pour exporter des données via l'API, utilisez le paramètre `format=csv` :

```
GET /api/orders/?format=csv
```

## Intégration avec d'autres systèmes

### Flux de travail typiques

1. **Création de commande dans un ERP externe**
   - L'ERP crée une commande via l'API
   - L'application Orders stocke la commande avec le statut "Initial"
   - L'application renvoie l'ID de la commande à l'ERP

2. **Synchronisation périodique**
   - Un script de synchronisation s'exécute régulièrement
   - Le script récupère les commandes modifiées depuis la dernière synchronisation
   - Les changements sont propagés vers les systèmes externes

### Webhooks

Pour les notifications en temps réel, vous pouvez configurer des webhooks :

1. Accédez à l'interface d'administration
2. Naviguez vers "Webhooks"
3. Ajoutez un nouveau webhook avec :
   - URL de destination
   - Événements à surveiller (création/modification/suppression de commande)
   - Secret partagé pour la vérification des signatures

## Bonnes pratiques

### Gestion efficace des commandes

1. **Utiliser des codes de commande cohérents**
   - Suivez une convention de nommage (ex : PO-AAAAMMJJ-XXXX)
   - Facilitez l'identification visuelle des commandes par type ou département

2. **Statuts des commandes**
   - Mettez à jour les statuts en temps opportun
   - Utilisez les actions en lot pour traiter plusieurs commandes similaires

3. **Documentation**
   - Utilisez le champ commentaire pour documenter les décisions importantes
   - Mentionnez les références externes dans le champ approprié

### Sécurité et confidentialité

1. **Contrôle d'accès**
   - Limitez l'accès à l'application aux utilisateurs autorisés
   - Assignez des permissions appropriées selon les rôles

2. **Traçabilité**
   - Tous les changements sont journalisés avec horodatage et utilisateur
   - Consultez l'historique des modifications pour l'audit

3. **Protection des données sensibles**
   - Les données sensibles comme les coordonnées bancaires ne doivent pas être saisies dans les champs de texte libre
