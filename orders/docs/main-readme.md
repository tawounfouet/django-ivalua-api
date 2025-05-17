# Application Orders - Documentation

## Aperçu de la documentation

Cette documentation couvre tous les aspects de l'application "Orders" dans le système P2P Ivalua. Elle est organisée en plusieurs sections pour faciliter la navigation et la maintenance.

## Structure de la documentation

1. [Introduction et aperçu](./01-introduction.md)
2. [Architecture et modèles de données](./02-architecture.md)
3. [API et intégrations](./03-api.md)
4. [Interface d'administration](./04-admin-interface.md)
5. [Guides de développement](./05-development.md)
6. [Tests et qualité du code](./06-testing.md)
7. [Déploiement et configuration](./07-deployment.md)
8. [Guide d'utilisation](./08-user-guide.md)

## À propos de l'application Orders

L'application "Orders" est un composant central du système P2P (Procure-to-Pay) Ivalua. Elle gère le cycle de vie complet des commandes, depuis leur création jusqu'à leur clôture, en passant par les différentes étapes d'approbation, d'envoi aux fournisseurs et de réception.

## Fonctionnalités principales

- Gestion complète du cycle de vie des commandes
- Suivi des statuts de commande (brouillon, soumis, approuvé, etc.)
- Association avec les fournisseurs
- Gestion des contacts (demandeur, livraison, facturation)
- Suivi des adresses multiples (livraison, facturation)
- Interface d'administration complète
- API REST pour l'intégration avec d'autres systèmes

## Technologies utilisées

- Django (backend)
- Django REST Framework (API)
- SQLite/PostgreSQL (base de données)
- Interface d'administration Django personnalisée

## Date de dernière mise à jour

15 mai 2025
