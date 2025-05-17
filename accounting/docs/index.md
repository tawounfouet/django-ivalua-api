# Documentation du Module de Comptabilité - P2P Ivalua

## Introduction

Le module de comptabilité est une composante essentielle du projet P2P Ivalua, conçu pour gérer tous les aspects financiers et comptables de l'application. Il s'appuie sur les principes comptables du Plan Comptable Général (PCG) français et implémente les meilleures pratiques recommandées par les cabinets d'audit des Big 4.

Ce module permet de :
- Gérer le plan comptable complet (classes, chapitres, sections, comptes)
- Enregistrer et traiter les écritures comptables
- Gérer les journaux comptables et les exercices fiscaux
- Produire des états financiers (grand livre, balance, compte de résultat, bilan)
- Assurer la traçabilité et l'audit des opérations financières

## Structure de la documentation

Cette documentation est organisée en plusieurs sections pour vous aider à comprendre, utiliser et maintenir le module de comptabilité :

1. [Architecture et conception](./architecture.md) - Vue d'ensemble de l'architecture du module
2. [Modèles de données](./models.md) - Description détaillée des modèles de données
3. [Guide d'installation](./installation.md) - Instructions pour installer et configurer le module
4. [Import de données](./import_data.md) - Procédures pour importer des données comptables
5. [API REST](./api.md) - Documentation de l'API REST exposée par le module
6. [Guide d'utilisation](./user_guide.md) - Manuel d'utilisation du module
7. [Développement et extension](./development.md) - Guide pour les développeurs souhaitant étendre le module
8. [Meilleures pratiques](./best_practices.md) - Conventions, tests et considérations de sécurité
9. [Validation et audit](./audit.md) - Fonctionnalités de validation et d'audit des opérations comptables
10. [États financiers](./financial_statements.md) - Génération et interprétation des états financiers
11. [FAQ et dépannage](./troubleshooting.md) - Questions fréquentes et résolution de problèmes

## Public cible

Cette documentation s'adresse à différents publics :

- **Utilisateurs finaux** : Comptables et financiers utilisant le système
- **Administrateurs système** : Responsables de la mise en place et de la maintenance
- **Développeurs** : Équipe technique travaillant sur le code source
- **Auditeurs** : Professionnels vérifiant la conformité du système

Chaque section de la documentation est conçue pour répondre aux besoins spécifiques de ces différents publics.

## Conventions de la documentation

Dans l'ensemble de cette documentation, les conventions suivantes sont utilisées :

- Les noms de modèles sont en **gras** (exemple : **AccountingEntry**)
- Les chemins de fichiers sont en `monospace` (exemple : `accounting/models/entries.py`)
- Les extraits de code sont encadrés comme suit :

```python
# Exemple de code Python
def validate_accounting_entry(entry):
    # Vérification de l'équilibre débit/crédit
    total_debit = sum(line.debit_amount for line in entry.lines.all())
    total_credit = sum(line.credit_amount for line in entry.lines.all())
    return total_debit == total_credit
```

Les commandes shell sont précédées d'un symbole $ :

```bash
$ python manage.py import_pcg data/export_comptes_pcg.csv
```

## À propos de ce module

Le module de comptabilité a été développé dans le cadre du projet P2P Ivalua pour répondre aux exigences comptables et financières des utilisateurs. Il s'intègre parfaitement au reste de l'application tout en offrant une API robuste pour les intégrations externes.

En cas de questions ou problèmes non couverts par cette documentation, veuillez contacter l'équipe de développement.
