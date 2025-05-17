# FAQ et Dépannage du Module de Comptabilité

Ce document répond aux questions fréquemment posées et fournit des solutions aux problèmes courants rencontrés lors de l'utilisation du module de comptabilité du projet P2P Ivalua.

## Questions fréquentes

### Configuration et installation

#### Q: Comment mettre à jour le Plan Comptable Général (PCG) ?

**R:** Pour mettre à jour le Plan Comptable Général, suivez ces étapes :

1. Préparez un fichier CSV contenant les nouvelles définitions de comptes au format attendu par l'importateur.
2. Exécutez la commande d'import avec l'option de mise à jour :

```bash
$ python manage.py import_pcg path/to/updated_pcg.csv --update
```

Cette commande mettra à jour les comptes existants et en créera de nouveaux si nécessaire.

#### Q: Est-il possible d'avoir plusieurs exercices fiscaux ouverts simultanément ?

**R:** Oui, le système permet d'avoir plusieurs exercices fiscaux ouverts en même temps, ce qui est utile pour les périodes de transition. Cependant, un seul exercice peut être marqué comme "courant" (`is_current=True`).

Par défaut, le système autorise jusqu'à 2 exercices ouverts simultanément, mais cette valeur peut être configurée dans les paramètres :

```python
# settings.py
ACCOUNTING = {
    # Autres paramètres...
    'MAX_OPEN_FISCAL_YEARS': 2,
}
```

#### Q: Comment configurer les numéros de référence automatiques pour les écritures ?

**R:** Le système peut générer automatiquement des références pour les écritures comptables. Cette fonctionnalité se configure dans `settings.py` :

```python
# settings.py
ACCOUNTING = {
    # Autres paramètres...
    'ENTRY_REFERENCE_PREFIX': 'ACC',
    'ENTRY_REFERENCE_LENGTH': 10,
    'ENTRY_REFERENCE_SEQUENCE_BY_JOURNAL': True,
}
```

Avec ces paramètres, les références seront générées au format `ACC-JRN-00001` où `JRN` est le code du journal.

### Utilisation quotidienne

#### Q: Comment corriger une écriture déjà comptabilisée ?

**R:** Une fois qu'une écriture est comptabilisée, elle ne peut plus être modifiée directement afin de préserver l'intégrité de la piste d'audit. Pour corriger une écriture comptabilisée, vous devez :

1. Créer une écriture d'extourne (contre-passation) pour annuler l'effet de l'écriture originale :
   - Dans la liste des écritures, trouvez l'écriture à corriger
   - Cliquez sur le bouton "Extourner"
   - Spécifiez la date d'extourne et un motif
   - Validez l'opération

2. Créer une nouvelle écriture correcte :
   - Créez une nouvelle écriture avec les informations correctes
   - Dans la description, référencez l'écriture originale pour maintenir la traçabilité
   - Suivez le processus normal de validation et comptabilisation

#### Q: Comment effectuer une clôture mensuelle ?

**R:** Le processus de clôture mensuelle n'est pas un verrouillage technique dans le système, mais plutôt une série d'étapes à suivre :

1. Assurez-vous que toutes les écritures du mois sont comptabilisées
2. Générez et vérifiez la balance mensuelle
3. Créez les écritures d'ajustement nécessaires (provisions, régularisations, etc.)
4. Générez les rapports mensuels requis (balance, journaux, etc.)
5. Archivez ces rapports en utilisant la fonction d'export

Pour faciliter ce processus, vous pouvez utiliser la commande :

```bash
$ python manage.py monthly_closing --year=2023 --month=5
```

Cette commande vérifie que toutes les conditions sont remplies pour une clôture mensuelle et génère un rapport de clôture.

#### Q: Comment traiter une facture multidevise ?

**R:** Pour traiter une facture en devise étrangère, suivez ces étapes :

1. Créez l'écriture comptable normalement, mais spécifiez la devise dans les champs prévus à cet effet
2. Saisissez le montant en devise étrangère et le taux de change
3. Le système calculera automatiquement l'équivalent en devise locale
4. Ajoutez des lignes spécifiques pour enregistrer les écarts de change si nécessaire

Pour les écarts de change en fin de période, utilisez la fonction spéciale :

```bash
$ python manage.py generate_exchange_diff_entries --fiscal-year=2023 --as-of-date=2023-03-31
```

#### Q: Comment lettrer des écritures client ou fournisseur ?

**R:** Le lettrage permet de marquer les écritures qui se compensent (par exemple, une facture et son règlement) :

1. Accédez à la vue "Lettrage" dans le menu "Opérations"
2. Sélectionnez le compte à lettrer (client ou fournisseur)
3. Sélectionnez les écritures à lettrer ensemble (leur solde doit être nul)
4. Cliquez sur "Lettrer les écritures sélectionnées"
5. Spécifiez un code de lettrage ou laissez le système en générer un
6. Validez l'opération

Le lettrage peut aussi être fait automatiquement lors de l'import d'un relevé bancaire avec la commande :

```bash
$ python manage.py import_bank_statement path/to/statement.csv --auto-reconcile
```

### Reporting et états financiers

#### Q: Comment générer un bilan à une date intermédiaire ?

**R:** Pour générer un bilan à une date qui n'est pas la fin d'un exercice :

1. Accédez au menu "Rapports" et sélectionnez "Bilan"
2. Sélectionnez l'exercice fiscal concerné
3. Dans le champ "Date d'arrêté", spécifiez la date intermédiaire souhaitée
4. Cliquez sur "Générer le rapport"

Le système calculera automatiquement les soldes à cette date en prenant en compte :
- Les soldes d'ouverture de l'exercice
- Toutes les écritures comptabilisées jusqu'à la date spécifiée

#### Q: Comment exporter plusieurs états financiers en même temps ?

**R:** Pour exporter plusieurs rapports en une seule opération :

1. Accédez au menu "Rapports" et sélectionnez "Export groupé"
2. Sélectionnez les types de rapports à inclure dans l'export
3. Spécifiez les paramètres communs (exercice, période, etc.)
4. Choisissez le format d'export (PDF unique, fichiers séparés, archive ZIP)
5. Cliquez sur "Générer l'export"

Vous pouvez aussi utiliser la commande suivante :

```bash
$ python manage.py batch_export_reports --fiscal-year=2023 --period=Q1 --reports=balance,income,cashflow --format=pdf
```

#### Q: Les totaux de ma balance ne correspondent pas au Grand Livre. Pourquoi ?

**R:** Plusieurs raisons peuvent expliquer cette différence :

1. **Différence de période** : Vérifiez que les deux rapports couvrent exactement la même période.

2. **Statut des écritures** : La balance inclut parfois par défaut uniquement les écritures comptabilisées, tandis que le Grand Livre peut inclure aussi les écritures validées mais pas encore comptabilisées. Vérifiez les filtres appliqués.

3. **Problème de génération de rapport** : Essayez de vider le cache du système et de régénérer les rapports :

```bash
$ python manage.py clear_reports_cache
$ python manage.py rebuild_accounting_indices
```

4. **Écritures en attente** : Vérifiez s'il existe des écritures en brouillon ou validées qui devraient être comptabilisées.

## Résolution des problèmes courants

### Erreurs d'importation des données

#### Problème : "Le fichier CSV ne peut pas être lu correctement"

**Causes possibles et solutions :**

1. **Encodage incorrect** :
   - Le système attend des fichiers en Latin-1 (ISO-8859-1)
   - Solution : Convertissez votre fichier avec la commande :
     ```bash
     $ iconv -f UTF-8 -t ISO-8859-1 input.csv > output.csv
     ```

2. **Séparateur incorrect** :
   - Le système attend des points-virgules (;) comme séparateurs
   - Solution : Convertissez votre fichier avec la commande :
     ```bash
     $ sed 's/,/;/g' input.csv > output.csv
     ```

3. **Entêtes manquantes ou incorrectes** :
   - Vérifiez que la première ligne de votre fichier contient les noms de colonnes attendus
   - Solution : Comparez avec les exemples fournis dans la documentation d'import

#### Problème : "Erreur : too many SQL variables"

**Causes possibles et solutions :**

Cette erreur survient généralement lors de l'import d'un très grand nombre d'entrées en une seule fois.

Solution :
1. Utilisez la version mise à jour des scripts d'import qui prend en charge l'import par lots :
   ```bash
   $ python manage.py import_pcg_batched data/export_comptes_pcg.csv --batch-size=500
   ```

2. Divisez votre fichier d'import en plusieurs fichiers plus petits :
   ```bash
   $ split -l 1000 large_file.csv split_file_
   ```

### Erreurs lors de la création d'écritures

#### Problème : "L'écriture n'est pas équilibrée"

**Causes possibles et solutions :**

1. **Erreur de saisie** :
   - Vérifiez tous les montants saisis, recherchez les erreurs de frappe
   - Assurez-vous que la somme des débits est exactement égale à la somme des crédits

2. **Problème d'arrondi** :
   - Les écarts d'arrondi peuvent causer des déséquilibres minimes
   - Solution : Utilisez l'outil d'ajustement automatique :
     ```
     Menu : Outils > Corriger les arrondis
     ```

3. **Montants en devise étrangère** :
   - Vérifiez que les taux de change sont correctement appliqués
   - Solution : Utilisez la fonction de conversion intégrée plutôt que des calculs manuels

#### Problème : "Impossible de comptabiliser l'écriture"

**Causes possibles et solutions :**

1. **Exercice fermé** :
   - Vérifiez que l'exercice fiscal associé à l'écriture est encore ouvert
   - Solution : Si l'écriture doit être enregistrée dans un exercice clôturé, contactez un administrateur

2. **Droits insuffisants** :
   - Vérifiez que vous disposez des permissions nécessaires pour comptabiliser
   - Solution : Contactez votre administrateur pour obtenir les droits appropriés

3. **Journal fermé** :
   - Certains journaux peuvent être verrouillés pour certaines périodes
   - Solution : Vérifiez les règles de verrouillage des journaux dans l'administration

4. **Validation manquante** :
   - L'écriture doit être à l'état "validée" avant d'être comptabilisée
   - Solution : Validez d'abord l'écriture, puis comptabilisez-la

### Problèmes de performance

#### Problème : "La génération des rapports est très lente"

**Causes possibles et solutions :**

1. **Volume de données important** :
   - La génération de rapports sur plusieurs années peut être lente
   - Solution : Limitez la période ou utilisez des rapports agrégés

2. **Indices manquants** :
   - Les performances peuvent être affectées par des indices manquants
   - Solution : Exécutez la commande de maintenance :
     ```bash
     $ python manage.py optimize_accounting_indices
     ```

3. **Cache non utilisé** :
   - Vérifiez que le système de cache est correctement configuré
   - Solution : Configurez un cache efficace dans `settings.py` :
     ```python
     CACHES = {
         'default': {
             'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
             'LOCATION': '127.0.0.1:11211',
         }
     }
     ```

4. **Requêtes non optimisées** :
   - Des requêtes complexes peuvent ralentir le système
   - Solution : Utilisez l'outil de profilage pour identifier les goulots d'étranglement :
     ```bash
     $ python manage.py profile_accounting_queries
     ```

#### Problème : "L'interface devient lente avec beaucoup d'écritures"

**Causes possibles et solutions :**

1. **Pagination inadéquate** :
   - Ajustez les paramètres de pagination dans l'interface
   - Solution : Réduisez le nombre d'éléments par page ou utilisez des filtres plus précis

2. **Ressources système insuffisantes** :
   - Vérifiez l'utilisation des ressources sur le serveur
   - Solution : Augmentez la RAM ou les capacités CPU si nécessaire

3. **Base de données non optimisée** :
   - Les performances peuvent se dégrader avec le temps
   - Solution : Exécutez les commandes de maintenance régulièrement :
     ```bash
     $ python manage.py vacuum_analyze_accounting
     ```

### Problèmes d'intégration

#### Problème : "Les écritures générées automatiquement sont incorrectes"

**Causes possibles et solutions :**

1. **Règles de génération mal configurées** :
   - Vérifiez les règles de génération automatique dans l'administration
   - Solution : Mettez à jour les modèles d'écritures avec les bonnes règles comptables

2. **Données sources incomplètes** :
   - Les écritures peuvent être incorrectes si les données sources manquent d'informations
   - Solution : Complétez les informations manquantes dans le système source

3. **Problème de synchronisation** :
   - Les modifications dans le système source peuvent ne pas être reflétées immédiatement
   - Solution : Forcez une synchronisation manuelle :
     ```bash
     $ python manage.py sync_accounting_entries --source=invoices
     ```

#### Problème : "L'API REST renvoie des erreurs"

**Causes possibles et solutions :**

1. **Authentification invalide** :
   - Vérifiez que le jeton d'authentification est valide et non expiré
   - Solution : Renouvelez le jeton d'authentification

2. **Format de requête incorrect** :
   - Vérifiez que votre requête respecte le format attendu par l'API
   - Solution : Consultez la documentation de l'API et validez votre JSON

3. **Permissions insuffisantes** :
   - L'utilisateur de l'API peut ne pas avoir les droits nécessaires
   - Solution : Vérifiez et ajustez les permissions de l'utilisateur

4. **Validation des données** :
   - Les données envoyées peuvent ne pas respecter les règles de validation
   - Solution : Corrigez les données selon les règles de validation décrites dans la documentation

## Outils de diagnostic

Le module de comptabilité fournit plusieurs outils de diagnostic pour vous aider à résoudre les problèmes :

### Vérificateur de cohérence

Cet outil vérifie la cohérence globale des données comptables :

```bash
$ python manage.py check_accounting_consistency
```

Il vérifie notamment :
- L'équilibre de toutes les écritures comptabilisées
- La cohérence entre les soldes calculés et les soldes stockés
- L'intégrité des références entre les différentes entités
- La validité des dates d'écritures par rapport aux exercices fiscaux

### Journaux de diagnostic

Les journaux de diagnostic contiennent des informations détaillées sur le fonctionnement du module :

```bash
$ python manage.py show_accounting_logs --level=DEBUG --days=7
```

Cela affiche les journaux de diagnostic des 7 derniers jours avec un niveau de détail DEBUG.

### Analyseur de performances

L'analyseur de performances aide à identifier les goulots d'étranglement :

```bash
$ python manage.py analyze_accounting_performance
```

Il fournit des statistiques sur :
- Les requêtes les plus longues
- Les fonctions les plus consommatrices en ressources
- Les opérations fréquentes qui pourraient bénéficier d'optimisations

### Testeur de configuration

Cet outil vérifie que la configuration du module est correcte et optimale :

```bash
$ python manage.py test_accounting_config
```

Il détecte les problèmes potentiels comme :
- Les paramètres manquants ou incorrects
- Les configurations sous-optimales
- Les incompatibilités entre différents paramètres

## Contacter le support

Si vous ne parvenez pas à résoudre un problème avec les informations fournies dans ce document, vous pouvez contacter le support technique :

- **Email** : support-comptabilite@ivalua.com
- **Téléphone** : +33 (0)1 23 45 67 89
- **Portail de support** : https://support.ivalua.com (créez un ticket avec la catégorie "Module Comptabilité")

Lorsque vous contactez le support, fournissez les informations suivantes pour accélérer la résolution :

1. Description détaillée du problème
2. Étapes précises pour reproduire le problème
3. Captures d'écran ou extraits de code si pertinent
4. Journaux d'erreur (disponibles dans `logs/accounting.log`)
5. Version du module et de la plateforme
6. Nom de l'environnement (production, test, développement)

## Annexe : Codes d'erreur courants

| Code d'erreur | Description | Solution |
|---------------|-------------|----------|
| ACC-E001 | Écriture non équilibrée | Vérifiez que la somme des débits égale la somme des crédits |
| ACC-E002 | Compte comptable invalide | Vérifiez que le compte existe et est actif |
| ACC-E003 | Période comptable fermée | Utilisez une période ouverte ou demandez la réouverture |
| ACC-E004 | Référence d'écriture dupliquée | Utilisez une référence unique |
| ACC-E005 | Droits insuffisants | Demandez les permissions nécessaires |
| ACC-E006 | Données d'import invalides | Corrigez le format du fichier d'import |
| ACC-E007 | Erreur de calcul de solde | Exécutez la commande de recalcul des soldes |
| ACC-E008 | Configuration incomplète | Complétez la configuration requise dans l'administration |
| ACC-E009 | Erreur d'intégration externe | Vérifiez la connectivité et les paramètres d'intégration |
| ACC-E010 | Limite système dépassée | Optimisez votre requête ou augmentez les limites système |
