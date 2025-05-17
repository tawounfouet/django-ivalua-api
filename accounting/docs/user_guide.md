# Guide d'Utilisation du Module de Comptabilité

Ce guide s'adresse aux utilisateurs finaux du module de comptabilité du projet P2P Ivalua. Il explique les concepts clés et les opérations quotidiennes à réaliser dans le système.

## Concepts fondamentaux

### Organisation de la comptabilité

Le module de comptabilité est structuré selon les principes du Plan Comptable Général (PCG) français, avec une organisation hiérarchique :

1. **Classes comptables** (1-9) : Les grandes catégories de comptes
   - Classe 1 : Comptes de capitaux
   - Classe 2 : Comptes d'immobilisations
   - Classe 3 : Comptes de stocks et en-cours
   - Classe 4 : Comptes de tiers
   - Classe 5 : Comptes financiers
   - Classe 6 : Comptes de charges
   - Classe 7 : Comptes de produits
   - Classes 8-9 : Comptes spéciaux et analytiques

2. **Chapitres comptables** : Subdivisions des classes (ex: 10, 11, 12...)

3. **Sections comptables** : Subdivisions des chapitres (ex: 101, 106...)

4. **Comptes du Grand Livre** : Comptes détaillés utilisés pour les écritures comptables

### Journaux comptables

Les journaux comptables permettent de catégoriser les écritures par type d'opération :

- **Journal des achats (ACH)** : Enregistrement des factures fournisseurs
- **Journal des ventes (VEN)** : Enregistrement des factures clients
- **Journal de banque (BAN)** : Opérations bancaires
- **Journal de caisse (CAI)** : Opérations de caisse
- **Journal des opérations diverses (OD)** : Écritures générales et ajustements
- **Journal des à-nouveaux (AN)** : Reports des soldes d'ouverture

### Exercices fiscaux

Les exercices fiscaux définissent les périodes comptables, généralement d'une année. Chaque exercice possède :

- Une année (ex: 2023)
- Des dates de début et de fin (ex: 01/01/2023 - 31/12/2023)
- Un statut (en cours, clôturé)

### Cycle de vie des écritures comptables

Chaque écriture comptable suit un cycle de vie précis :

1. **Brouillon** : L'écriture est créée mais pas encore validée
2. **Validée** : L'écriture a été vérifiée (équilibre débit/crédit) mais n'est pas encore définitive
3. **Comptabilisée** : L'écriture est définitivement enregistrée dans le Grand Livre
4. **Annulée** : L'écriture a été annulée (si elle était en brouillon ou validée)

Pour les écritures déjà comptabilisées, une opération d'**extourne** (contre-passation) peut être créée pour les corriger.

## Opérations quotidiennes

### Connexion au système

1. Accédez à l'URL du système (fournie par votre administrateur)
2. Saisissez vos identifiants (nom d'utilisateur et mot de passe)
3. Naviguez vers le module Comptabilité

### Consultation du Plan Comptable

1. Dans le menu principal, sélectionnez "Plan Comptable"
2. Utilisez les filtres pour trouver des comptes spécifiques :
   - Par numéro de compte
   - Par nom de compte
   - Par classe/chapitre/section
3. Cliquez sur un compte pour voir ses détails et son historique

### Création d'une écriture comptable

1. Dans le menu "Écritures comptables", cliquez sur "Nouvelle écriture"
2. Remplissez les informations générales :
   - Journal : sélectionnez le journal approprié
   - Date : saisissez la date de l'écriture
   - Référence : le système peut suggérer une référence automatique
   - Description : saisissez une description claire de l'opération
   - Exercice fiscal : sélectionnez l'exercice concerné

3. Ajoutez les lignes d'écriture :
   - Cliquez sur "Ajouter une ligne"
   - Sélectionnez le compte (vous pouvez rechercher par numéro ou nom)
   - Saisissez le montant au débit ou au crédit (jamais les deux)
   - Ajoutez une description spécifique à la ligne si nécessaire
   - Complétez les informations de classement (type de client, prestations, etc.)
   - Répétez pour toutes les lignes nécessaires

4. Vérifiez l'équilibre de l'écriture :
   - Le total des débits doit être égal au total des crédits
   - Le système affiche la différence éventuelle

5. Enregistrez l'écriture en brouillon :
   - Cliquez sur "Enregistrer" pour sauvegarder en brouillon
   - Ou cliquez sur "Enregistrer et valider" pour passer directement à l'étape de validation

### Validation d'une écriture

1. Dans la liste des écritures, filtrez par statut "Brouillon"
2. Ouvrez l'écriture à valider
3. Vérifiez toutes les informations (journal, date, lignes, équilibre)
4. Cliquez sur "Valider"
5. Ajoutez un commentaire de validation si nécessaire
6. Confirmez la validation

### Comptabilisation d'une écriture

1. Dans la liste des écritures, filtrez par statut "Validée"
2. Sélectionnez une ou plusieurs écritures à comptabiliser
3. Cliquez sur "Comptabiliser"
4. Confirmez l'opération

Une fois comptabilisée, l'écriture ne peut plus être modifiée directement.

### Annulation d'une écriture

Pour les écritures en statut "Brouillon" ou "Validée" :

1. Ouvrez l'écriture concernée
2. Cliquez sur "Annuler"
3. Saisissez un motif d'annulation
4. Confirmez l'opération

### Extourne d'une écriture comptabilisée

Pour corriger une écriture déjà comptabilisée :

1. Ouvrez l'écriture concernée
2. Cliquez sur "Créer une extourne"
3. Sélectionnez la date de l'extourne
4. Saisissez un motif d'extourne
5. Confirmez l'opération

Le système créera automatiquement une nouvelle écriture inversant tous les débits et crédits.

### Recherche et filtrage des écritures

1. Accédez à la liste des écritures comptables
2. Utilisez les filtres disponibles :
   - Par journal
   - Par période (date de début et de fin)
   - Par référence
   - Par statut
   - Par compte impliqué
   - Par montant
3. Cliquez sur "Rechercher" pour afficher les résultats
4. Utilisez les options d'export pour télécharger les résultats (Excel, CSV, PDF)

## États financiers et rapports

### Consultation du Grand Livre

1. Dans le menu "Rapports", sélectionnez "Grand Livre"
2. Définissez les paramètres :
   - Exercice fiscal
   - Période (dates de début et de fin)
   - Compte ou intervalle de comptes
   - Journal (optionnel)
3. Cliquez sur "Générer le rapport"
4. Consultez le Grand Livre à l'écran ou exportez-le (PDF, Excel)

### Génération de la balance

1. Dans le menu "Rapports", sélectionnez "Balance"
2. Définissez les paramètres :
   - Exercice fiscal
   - Date d'arrêté
   - Niveau de détail (compte, section, chapitre, classe)
   - Inclure ou non les comptes à solde nul
3. Cliquez sur "Générer le rapport"
4. Consultez la balance, avec les colonnes standard :
   - Soldes d'ouverture (débits/crédits)
   - Mouvements de la période (débits/crédits)
   - Soldes de clôture (débits/crédits)

### Consultation du bilan

1. Dans le menu "Rapports", sélectionnez "Bilan"
2. Définissez les paramètres :
   - Exercice fiscal
   - Date d'arrêté
   - Format (standard ou détaillé)
3. Générez le rapport
4. Consultez le bilan avec l'Actif et le Passif

### Consultation du compte de résultat

1. Dans le menu "Rapports", sélectionnez "Compte de résultat"
2. Définissez les paramètres :
   - Exercice fiscal
   - Période (optionnel)
   - Format (standard ou détaillé)
3. Générez le rapport
4. Consultez le compte de résultat avec les Charges et les Produits

## Opérations périodiques

### Clôture mensuelle

1. Assurez-vous que toutes les écritures du mois sont comptabilisées
2. Générez et vérifiez la balance mensuelle
3. Effectuez les écritures d'ajustement nécessaires
4. Générez les rapports mensuels requis

### Clôture annuelle

1. Complétez toutes les opérations de fin d'exercice :
   - Écritures d'amortissement
   - Provisions
   - Régularisations diverses
2. Vérifiez l'équilibre global de l'exercice
3. Générez et vérifiez les états financiers annuels
4. Demandez à l'administrateur de clôturer l'exercice
5. Assurez-vous que les écritures d'à-nouveaux sont générées pour le nouvel exercice

## Bonnes pratiques

### Organisation des références

Utilisez un système cohérent pour les références d'écritures, par exemple :
- `ACH2023001` : Première écriture d'achat de 2023
- `VEN2023001` : Première écriture de vente de 2023
- `OD2023001` : Première écriture diverse de 2023

### Descriptions claires

- Utilisez des descriptions précises et standardisées
- Incluez les références externes (numéros de facture, commande, etc.)
- Pour les écritures complexes, ajoutez des détails dans chaque ligne

### Vérifications régulières

- Contrôlez régulièrement la balance pour vous assurer de l'équilibre du système
- Réconciliez les comptes clients et fournisseurs
- Vérifiez les comptes d'attente et assurez-vous qu'ils sont soldés régulièrement

### Sauvegarde des preuves

Chaque écriture doit être justifiée par un document source :
- Factures
- Relevés bancaires
- Contrats
- Notes de frais
- Etc.

Attachez ou référencez ces documents dans le système lorsque c'est possible.

## Résolution des problèmes courants

### Écriture déséquilibrée

**Problème** : L'écriture ne peut pas être validée car la somme des débits ne correspond pas à la somme des crédits.

**Solution** :
1. Vérifiez chaque ligne pour vous assurer que les montants sont correctement saisis
2. Assurez-vous qu'aucune ligne n'a à la fois un montant au débit et au crédit
3. Vérifiez les arrondis et les décimales
4. Ajoutez ou modifiez les lignes pour équilibrer l'écriture

### Compte non trouvé

**Problème** : Vous ne trouvez pas le compte approprié pour une opération.

**Solution** :
1. Utilisez la recherche par mot-clé dans le plan comptable
2. Consultez la documentation du PCG pour identifier le compte correct
3. Si nécessaire, contactez votre responsable comptable pour déterminer le compte à utiliser

### Modification d'une écriture comptabilisée

**Problème** : Vous devez corriger une écriture déjà comptabilisée.

**Solution** :
1. Créez une extourne de l'écriture originale
2. Créez une nouvelle écriture avec les informations correctes
3. Assurez-vous que les deux écritures (extourne et correction) sont clairement référencées

### Erreurs sur les rapports

**Problème** : Les montants sur les rapports financiers semblent incorrects.

**Solution** :
1. Vérifiez les paramètres de filtrage (dates, comptes, exercice)
2. Assurez-vous que toutes les écritures pertinentes sont comptabilisées
3. Vérifiez s'il existe des écritures en brouillon ou validées qui devraient être comptabilisées
4. Générez une balance détaillée pour identifier les comptes problématiques

## Conclusion

Ce guide d'utilisation couvre les opérations de base du module de comptabilité. Pour des fonctionnalités plus avancées ou des questions spécifiques, n'hésitez pas à consulter l'équipe de support ou votre administrateur système.

Le module de comptabilité est conçu pour être intuitif tout en respectant les principes rigoureux de la comptabilité. Avec une utilisation régulière et méthodique, il deviendra un outil essentiel pour la gestion financière de votre organisation.
