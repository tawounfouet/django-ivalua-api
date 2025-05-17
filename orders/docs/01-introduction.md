# Introduction à l'application Orders

## Présentation générale

L'application "Orders" est un module essentiel du système P2P Ivalua qui permet la gestion complète des bons de commande. Elle s'intègre étroitement avec les autres modules du système, notamment les modules "Suppliers" (fournisseurs) et "Authentication" (utilisateurs).

## Objectifs et raison d'être

Cette application a été développée pour répondre aux besoins suivants :

1. **Centralisation des commandes** : Disposer d'un référentiel central pour toutes les commandes du système
2. **Traçabilité** : Suivre l'historique complet des commandes, de leur création à leur clôture
3. **Intégration** : Faciliter l'échange de données avec les systèmes externes (ERP, systèmes fournisseurs)
4. **Reporting** : Permettre l'analyse des données de commandes pour le pilotage de l'activité

## Concepts clés

### Cycle de vie des commandes

Les commandes suivent un cycle de vie précis, matérialisé par différents statuts :

1. **Initial** : État initial lors de la création
2. **Brouillon** : Commande en cours d'élaboration
3. **Soumis** : Commande soumise pour approbation
4. **Approuvé** : Commande validée
5. **Rejeté** : Commande rejetée
6. **Envoyé au fournisseur** : Commande transmise au fournisseur
7. **Accusé de réception** : Le fournisseur a confirmé la réception
8. **Partiellement reçu** : Une partie des articles a été reçue
9. **Reçu** : Tous les articles ont été reçus
10. **Annulé** : Commande annulée
11. **Clôturé** : Commande finalisée
12. **Terminé** : Commande archivée

### Types de commandes

L'application prend en charge différents types de commandes :

- **Standard** : Commande classique
- **Commande ouverte** (Blanket order) : Commande cadre
- **Commande basée sur un contrat** : Commande liée à un contrat existant
- **Commande spéciale** : Commande avec traitement particulier

## Intégration dans l'écosystème

L'application Orders s'intègre avec :

- **Module Suppliers** : Pour associer les commandes aux fournisseurs
- **Module Authentication** : Pour la gestion des droits et des utilisateurs
- **API externes** : Pour l'échange de données avec les systèmes tiers

## Historique et évolution

Cette application a été développée en mai 2025 dans le cadre du projet P2P Ivalua. Elle a été conçue selon les principes de l'architecture Django, avec une séparation claire entre modèles, vues et API.

## Prérequis technologiques

Pour utiliser et développer l'application Orders, vous aurez besoin des éléments suivants :

- Django 5.2 ou supérieur
- Django REST Framework
- Base de données SQLite (développement) ou PostgreSQL (production)
- Python 3.10 ou supérieur

## Structure des fichiers

```
orders/
├── __init__.py
├── admin.py           # Configuration de l'interface d'administration
├── api_views.py       # Vues API (DRF ViewSets)
├── apps.py            # Configuration de l'application Django
├── models.py          # Modèles de données
├── serializers.py     # Sérialiseurs pour l'API
├── tests.py           # Tests unitaires (ancien fichier)
├── urls.py            # Configuration des URLs
├── views.py           # Vues Django traditionnelles
├── docs/              # Documentation
├── management/        # Commandes personnalisées Django
├── migrations/        # Migrations de base de données
└── tests/             # Tests unitaires et d'intégration
```
