# API REST du Module de Comptabilité

Cette documentation décrit en détail l'API REST exposée par le module de comptabilité du projet P2P Ivalua.

## Vue d'ensemble

L'API REST du module de comptabilité permet d'accéder et de manipuler toutes les ressources comptables de manière programmatique. Elle suit les principes RESTful et utilise le format JSON pour les échanges de données.

Tous les points d'entrée de l'API sont accessibles via le préfixe : `/api/v1.0/acc/`

## Authentification

L'API utilise le système d'authentification standard du projet P2P Ivalua. Toutes les requêtes doivent inclure un jeton d'authentification valide dans l'en-tête HTTP :

```
Authorization: Bearer <token>
```

Pour obtenir un jeton d'authentification, utilisez le point d'entrée d'authentification du projet principal :

```
POST /api/v1.0/auth/token/
```

## Format des réponses

Toutes les réponses de l'API sont au format JSON et suivent une structure commune :

- Pour les collections (listes) :
  ```json
  {
    "count": 42,
    "next": "http://api.example.org/api/v1.0/acc/resources/?page=2",
    "previous": null,
    "results": [
      {
        "id": "...",
        "attribute1": "...",
        "attribute2": "..."
      },
      ...
    ]
  }
  ```

- Pour les ressources individuelles :
  ```json
  {
    "id": "...",
    "attribute1": "...",
    "attribute2": "...",
    "related_resource": {
      "id": "...",
      "name": "..."
    }
  }
  ```

## Points d'entrée de l'API

### Plan Comptable Général

#### Classes comptables

```
GET /api/v1.0/acc/accounting-classes/
GET /api/v1.0/acc/accounting-classes/{id}/
```

Exemple de réponse :
```json
{
  "id": "1",
  "code": "1",
  "name": "Comptes de capitaux",
  "chapters_count": 5
}
```

#### Chapitres comptables

```
GET /api/v1.0/acc/accounting-chapters/
GET /api/v1.0/acc/accounting-chapters/{id}/
```

Exemple de réponse :
```json
{
  "id": "10",
  "code": "10",
  "name": "Capital et réserves",
  "accounting_class": {
    "id": "1",
    "code": "1",
    "name": "Comptes de capitaux"
  },
  "sections_count": 3
}
```

#### Sections comptables

```
GET /api/v1.0/acc/accounting-sections/
GET /api/v1.0/acc/accounting-sections/{id}/
```

Exemple de réponse :
```json
{
  "id": "101",
  "code": "101",
  "name": "Capital",
  "chapter": {
    "id": "10",
    "code": "10",
    "name": "Capital et réserves"
  },
  "accounts_count": 5
}
```

#### Comptes du Grand Livre

```
GET /api/v1.0/acc/general-ledger-accounts/
GET /api/v1.0/acc/general-ledger-accounts/{id}/
```

Exemple de réponse :
```json
{
  "id": "101000",
  "account_number": "101000",
  "short_name": "Capital",
  "full_name": "Capital social",
  "section": {
    "id": "101",
    "code": "101",
    "name": "Capital"
  },
  "is_balance_sheet": true,
  "budget_account_code": "1010",
  "recovery_status": "ACTIF",
  "financial_statement_group": "CAPITAUX"
}
```

### Bases comptables

#### Exercices fiscaux

```
GET /api/v1.0/acc/fiscal-years/
GET /api/v1.0/acc/fiscal-years/{id}/
POST /api/v1.0/acc/fiscal-years/
PUT /api/v1.0/acc/fiscal-years/{id}/
PATCH /api/v1.0/acc/fiscal-years/{id}/
DELETE /api/v1.0/acc/fiscal-years/{id}/
```

Exemple de requête de création :
```json
{
  "year": 2025,
  "name": "EXERCICE 2025",
  "start_date": "2025-01-01",
  "end_date": "2025-12-31",
  "is_current": true,
  "is_closed": false
}
```

#### Types de comptabilité

```
GET /api/v1.0/acc/accounting-types/
GET /api/v1.0/acc/accounting-types/{id}/
POST /api/v1.0/acc/accounting-types/
PUT /api/v1.0/acc/accounting-types/{id}/
PATCH /api/v1.0/acc/accounting-types/{id}/
DELETE /api/v1.0/acc/accounting-types/{id}/
```

#### Journaux comptables

```
GET /api/v1.0/acc/accounting-journals/
GET /api/v1.0/acc/accounting-journals/{id}/
POST /api/v1.0/acc/accounting-journals/
PUT /api/v1.0/acc/accounting-journals/{id}/
PATCH /api/v1.0/acc/accounting-journals/{id}/
DELETE /api/v1.0/acc/accounting-journals/{id}/
```

### Écritures comptables

#### Écritures

```
GET /api/v1.0/acc/accounting-entries/
GET /api/v1.0/acc/accounting-entries/{id}/
POST /api/v1.0/acc/accounting-entries/
PUT /api/v1.0/acc/accounting-entries/{id}/
PATCH /api/v1.0/acc/accounting-entries/{id}/
DELETE /api/v1.0/acc/accounting-entries/{id}/
```

Exemple de requête de création d'une écriture avec ses lignes :
```json
{
  "reference": "VTE2023001",
  "date": "2023-05-15",
  "journal": "VEN",
  "fiscal_year": 2023,
  "description": "Vente de marchandises",
  "accounting_type": "GENE",
  "municipality": "75056",
  "accounting_entry_type": "VTE",
  "lines": [
    {
      "account": "411000",
      "debit_amount": "1200.00",
      "credit_amount": "0.00",
      "description": "Client ABC",
      "line_number": 1,
      "client_account_type": "PART"
    },
    {
      "account": "707000",
      "debit_amount": "0.00",
      "credit_amount": "1000.00",
      "description": "Vente de marchandises HT",
      "line_number": 2
    },
    {
      "account": "445710",
      "debit_amount": "0.00",
      "credit_amount": "200.00",
      "description": "TVA collectée (20%)",
      "line_number": 3
    }
  ]
}
```

#### Validation d'une écriture

```
POST /api/v1.0/acc/accounting-entries/{id}/validate/
```

Requête :
```json
{
  "validation_comment": "Écriture validée après vérification"
}
```

Réponse (HTTP 200) :
```json
{
  "id": "...",
  "reference": "VTE2023001",
  "status": "validated",
  "validated_by": {
    "id": "...",
    "username": "john.doe"
  },
  "validated_date": "2023-05-15T14:30:22Z",
  "validation_comment": "Écriture validée après vérification"
}
```

#### Comptabilisation d'une écriture

```
POST /api/v1.0/acc/accounting-entries/{id}/post/
```

#### Annulation d'une écriture

```
POST /api/v1.0/acc/accounting-entries/{id}/cancel/
```

Requête :
```json
{
  "cancellation_reason": "Erreur de saisie"
}
```

#### Extourne d'une écriture

```
POST /api/v1.0/acc/accounting-entries/{id}/reverse/
```

Requête :
```json
{
  "reversal_date": "2023-06-01",
  "reversal_reason": "Régularisation de fin de mois"
}
```

#### Lignes d'écritures (accès direct)

```
GET /api/v1.0/acc/accounting-entry-lines/
GET /api/v1.0/acc/accounting-entry-lines/{id}/
```

### Données de référence

Tous les types de données de référence suivent le même modèle d'API :

```
GET /api/v1.0/acc/{resource}/
GET /api/v1.0/acc/{resource}/{id}/
POST /api/v1.0/acc/{resource}/
PUT /api/v1.0/acc/{resource}/{id}/
PATCH /api/v1.0/acc/{resource}/{id}/
DELETE /api/v1.0/acc/{resource}/{id}/
```

Où `{resource}` peut être :
- `municipalities` - Municipalités
- `accounting-entry-types` - Types d'écritures
- `engagement-types` - Types d'engagement
- `reconciliation-types` - Types de lettrage
- `payer-types` - Types de payeurs
- `service-types` - Types de prestations
- `pricing-types` - Types de tarification
- `client-account-types` - Types de comptes clients

### Rapports financiers

#### Grand Livre

```
GET /api/v1.0/acc/reports/general-ledger/
```

Paramètres de requête :
- `fiscal_year` : ID de l'exercice fiscal (obligatoire)
- `account` : Numéro de compte (optionnel)
- `start_date` : Date de début (optionnel)
- `end_date` : Date de fin (optionnel)
- `journal` : Code du journal (optionnel)

#### Balance

```
GET /api/v1.0/acc/reports/trial-balance/
```

Paramètres de requête :
- `fiscal_year` : ID de l'exercice fiscal (obligatoire)
- `as_of_date` : Date de la balance (optionnel, par défaut = date actuelle)
- `level` : Niveau de détail ('account', 'section', 'chapter', 'class')
- `include_zero_balances` : Inclure les comptes à solde nul (true/false)

Exemple de réponse :
```json
{
  "fiscal_year": {
    "id": "2023",
    "name": "EXERCICE 2023"
  },
  "as_of_date": "2023-05-31",
  "generated_at": "2023-05-31T15:45:22Z",
  "balances": [
    {
      "account_number": "101000",
      "account_name": "Capital",
      "opening_debit": "0.00",
      "opening_credit": "50000.00",
      "period_debit": "0.00",
      "period_credit": "0.00",
      "closing_debit": "0.00",
      "closing_credit": "50000.00"
    },
    // ... autres comptes
  ],
  "totals": {
    "opening_debit": "75000.00",
    "opening_credit": "75000.00",
    "period_debit": "125000.00",
    "period_credit": "125000.00",
    "closing_debit": "145000.00",
    "closing_credit": "145000.00"
  }
}
```

#### Bilan

```
GET /api/v1.0/acc/reports/balance-sheet/
```

Paramètres de requête :
- `fiscal_year` : ID de l'exercice fiscal (obligatoire)
- `as_of_date` : Date du bilan (optionnel)
- `format` : Format de retour ('standard', 'detailed')

#### Compte de résultat

```
GET /api/v1.0/acc/reports/income-statement/
```

Paramètres de requête :
- `fiscal_year` : ID de l'exercice fiscal (obligatoire)
- `start_date` : Date de début (optionnel)
- `end_date` : Date de fin (optionnel)
- `format` : Format de retour ('standard', 'detailed')

## Pagination

Toutes les listes d'objets retournées par l'API sont paginées par défaut. La pagination utilise les paramètres standard :

- `page` : Numéro de la page demandée
- `page_size` : Nombre d'éléments par page (maximum 100)

Exemple :
```
GET /api/v1.0/acc/general-ledger-accounts/?page=2&page_size=50
```

## Filtrage

L'API permet de filtrer les résultats à l'aide de paramètres de requête. Les filtres disponibles dépendent de la ressource :

### Exemples de filtrage

1. Trouver tous les comptes contenant "client" dans leur nom :
   ```
   GET /api/v1.0/acc/general-ledger-accounts/?search=client
   ```

2. Obtenir toutes les écritures d'un journal spécifique :
   ```
   GET /api/v1.0/acc/accounting-entries/?journal=VEN
   ```

3. Trouver les écritures dans une plage de dates :
   ```
   GET /api/v1.0/acc/accounting-entries/?date_after=2023-01-01&date_before=2023-01-31
   ```

4. Filtrer les lignes d'écritures par compte :
   ```
   GET /api/v1.0/acc/accounting-entry-lines/?account=411000
   ```

## Tri

Les résultats peuvent être triés à l'aide du paramètre `ordering`. Le préfixe `-` indique un tri descendant.

Exemples :
- Tri des comptes par numéro :
  ```
  GET /api/v1.0/acc/general-ledger-accounts/?ordering=account_number
  ```

- Tri des écritures par date (plus récentes d'abord) :
  ```
  GET /api/v1.0/acc/accounting-entries/?ordering=-date
  ```

## Gestion des erreurs

L'API utilise les codes d'état HTTP standard pour indiquer le résultat des requêtes :

- `200 OK` : Requête réussie
- `201 Created` : Ressource créée avec succès
- `400 Bad Request` : Requête invalide (erreurs de validation)
- `401 Unauthorized` : Authentification requise
- `403 Forbidden` : Action non autorisée
- `404 Not Found` : Ressource non trouvée
- `500 Internal Server Error` : Erreur serveur

En cas d'erreur, le corps de la réponse contient des détails sur l'erreur :

```json
{
  "detail": "Message d'erreur général",
  "errors": {
    "field_name": ["Message d'erreur spécifique au champ"]
  }
}
```

## Exemples d'utilisation

### Création d'une écriture comptable complète

```python
import requests
import json

# Configuration
API_URL = "http://example.com/api/v1.0/acc"
AUTH_TOKEN = "your_auth_token"

headers = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json"
}

# Données de l'écriture
entry_data = {
    "reference": "ACH2023001",
    "date": "2023-05-20",
    "journal": "ACH",
    "fiscal_year": 2023,
    "description": "Achat de fournitures",
    "accounting_type": "GENE",
    "lines": [
        {
            "account": "606400",
            "debit_amount": "500.00",
            "credit_amount": "0.00",
            "description": "Fournitures administratives",
            "line_number": 1
        },
        {
            "account": "445620",
            "debit_amount": "100.00",
            "credit_amount": "0.00",
            "description": "TVA déductible sur biens et services (20%)",
            "line_number": 2
        },
        {
            "account": "401000",
            "debit_amount": "0.00",
            "credit_amount": "600.00",
            "description": "Fournisseur XYZ",
            "line_number": 3
        }
    ]
}

# Création de l'écriture
response = requests.post(
    f"{API_URL}/accounting-entries/",
    headers=headers,
    data=json.dumps(entry_data)
)

if response.status_code == 201:
    entry = response.json()
    print(f"Écriture créée avec l'ID: {entry['id']}")
    
    # Validation de l'écriture
    validate_response = requests.post(
        f"{API_URL}/accounting-entries/{entry['id']}/validate/",
        headers=headers,
        data=json.dumps({"validation_comment": "Écriture validée automatiquement"})
    )
    
    if validate_response.status_code == 200:
        print("Écriture validée avec succès")
    else:
        print(f"Erreur lors de la validation: {validate_response.json()}")
else:
    print(f"Erreur lors de la création: {response.json()}")
```

### Génération d'un rapport de balance

```python
import requests

# Configuration
API_URL = "http://example.com/api/v1.0/acc"
AUTH_TOKEN = "your_auth_token"

headers = {
    "Authorization": f"Bearer {AUTH_TOKEN}"
}

# Paramètres du rapport
params = {
    "fiscal_year": 2023,
    "as_of_date": "2023-05-31",
    "level": "account",
    "include_zero_balances": False
}

# Requête de rapport
response = requests.get(
    f"{API_URL}/reports/trial-balance/",
    headers=headers,
    params=params
)

if response.status_code == 200:
    balance_report = response.json()
    print(f"Balance au {balance_report['as_of_date']}")
    print(f"Exercice: {balance_report['fiscal_year']['name']}")
    
    print("\nComptes avec soldes:")
    for account in balance_report['balances']:
        print(f"{account['account_number']} - {account['account_name']}: " \
              f"Débit: {account['closing_debit']}, Crédit: {account['closing_credit']}")
    
    print("\nTotaux:")
    totals = balance_report['totals']
    print(f"Débit total: {totals['closing_debit']}")
    print(f"Crédit total: {totals['closing_credit']}")
else:
    print(f"Erreur lors de la génération du rapport: {response.json()}")
```

## Conclusion

L'API REST du module de comptabilité offre un accès complet et flexible à toutes les fonctionnalités du système. Elle permet l'intégration avec d'autres applications, l'automatisation des processus comptables et le développement d'interfaces utilisateur personnalisées.

Pour toute question ou suggestion concernant l'API, veuillez contacter l'équipe de développement.
