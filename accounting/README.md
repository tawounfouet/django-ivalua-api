# Module de Comptabilité - P2P Ivalua

## Description
Module de comptabilité pour le projet P2P Ivalua, intégrant le Plan Comptable Général (PCG) et permettant la gestion des écritures comptables, des journaux et des exercices fiscaux.

## Structure du module

### Modèles de données

#### Plan Comptable Général (PCG)
- **AccountingClass**: Classes comptables (1-9)
- **AccountingChapter**: Chapitres comptables (sous-divisions des classes, ex: 10, 11)
- **AccountingSection**: Sections comptables (sous-divisions des chapitres, ex: 101, 106)
- **GeneralLedgerAccount**: Comptes du Grand Livre (comptes détaillés du PCG)

#### Bases comptables
- **FiscalYear**: Exercices comptables
- **AccountingType**: Types de comptabilité (auxiliaire, etc.)
- **AccountingJournal**: Journaux comptables

#### Écritures comptables
- **AccountingEntry**: Écritures comptables (avec statut : brouillon, validé, comptabilisé, annulé)
- **AccountingEntryLine**: Lignes d'écritures comptables (débit/crédit)

### API REST
Toutes les ressources sont accessibles via l'API REST au point d'entrée `/api/v1.0/acc/`.

Endpoints disponibles:
- `/api/v1.0/acc/accounting-classes/`
- `/api/v1.0/acc/accounting-chapters/`
- `/api/v1.0/acc/accounting-sections/`
- `/api/v1.0/acc/general-ledger-accounts/`
- `/api/v1.0/acc/fiscal-years/`
- `/api/v1.0/acc/accounting-types/`
- `/api/v1.0/acc/accounting-journals/`
- `/api/v1.0/acc/accounting-entries/`

### Commandes d'importation
Le module fournit des commandes Django pour importer les données comptables à partir de fichiers CSV:

- `import_pcg`: Importe le Plan Comptable Général
- `import_fiscal_years`: Importe les exercices comptables
- `import_journals`: Importe les journaux comptables
- `import_accounting_types`: Importe les types de comptabilité
- `import_all_accounting_data`: Importe toutes les données comptables en une seule commande

Pour importer toutes les données:
```bash
python manage.py import_all_accounting_data path/to/data/directory
```

## Utilisation

### Interface d'administration
L'interface d'administration Django permet de:
- Gérer les comptes du Plan Comptable Général
- Configurer les journaux comptables
- Définir les exercices fiscaux
- Saisir et valider les écritures comptables

### API REST
L'API REST permet:
- De consulter le Plan Comptable Général
- De gérer les écritures comptables
- D'obtenir des informations sur les journaux et exercices

### Opérations sur les écritures comptables
Les écritures comptables suivent un processus:
1. Création (brouillon)
2. Validation (vérification de l'équilibre débit/crédit)
3. Comptabilisation (écriture définitive au Grand Livre)

Des actions spéciales sont disponibles:
- Annulation d'écritures (pour les brouillons et validés)
- Création d'écritures d'extourne (pour les écritures comptabilisées)

## Modèle comptable
Le module implémente un modèle comptable classique:
- Les comptes sont organisés selon le Plan Comptable Général français
- Chaque écriture doit être équilibrée (somme des débits = somme des crédits)
- Les écritures comptables sont regroupées par journaux (ventes, achats, etc.)
- Les périodes comptables sont définies par des exercices fiscaux
