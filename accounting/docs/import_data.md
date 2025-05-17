# Import de Données Comptables

Ce document détaille les procédures d'import des données comptables dans le module de comptabilité du projet P2P Ivalua.

## Vue d'ensemble

Le module de comptabilité nécessite plusieurs jeux de données initiales pour fonctionner correctement :

1. Le **Plan Comptable Général (PCG)** - structure hiérarchique des comptes
2. Les **exercices fiscaux** - définition des périodes comptables
3. Les **journaux comptables** - catégorisation des écritures
4. Les **municipalités** - données de localisation pour les opérations comptables
5. Les **données de référence** - typologies diverses pour la classification des opérations

Le module fournit des commandes Django dédiées pour importer ces données à partir de fichiers CSV.

## Prérequis

Avant de commencer l'import des données, assurez-vous de disposer des éléments suivants :

- Fichiers CSV contenant les données à importer
- Accès à une instance du projet avec le module de comptabilité installé
- Droits d'accès suffisants pour exécuter les commandes Django ou Docker

## Format des fichiers CSV

Tous les fichiers CSV doivent respecter le format suivant :
- Séparateur : point-virgule (`;`)
- Encodage : Latin-1 (ISO-8859-1)
- Première ligne : en-têtes des colonnes
- Pas de guillemets autour des champs (sauf si nécessaire pour les champs contenant des séparateurs)

Exemple de fichier CSV valide (extrait de `exercice_comptable.csv`) :
```
NO_EXERCICE;LIB_EXERCICE_
2020;EXERCICE 2020
2021;EXERCICE 2021
2022;EXERCICE 2022
2023;EXERCICE 2023
2024;EXERCICE 2024
```

## Scripts d'import disponibles

Le module fournit plusieurs scripts d'import spécialisés :

| Commande | Description | Fichier CSV attendu |
|----------|-------------|---------------------|
| `import_pcg` | Importe le Plan Comptable Général | `export_comptes_pcg.csv` |
| `import_fiscal_years` | Importe les exercices comptables | `exercice_comptable.csv` |
| `import_journals` | Importe les journaux comptables | `journal_comptable.csv` |
| `import_accounting_types` | Importe les types de comptabilité | `type-de-comptabilite.csv` |
| `import_municipalities` | Importe les municipalités | `commune_insee.csv` |
| `import_accounting_entry_types` | Importe les types d'écritures | `type_d_ecrirture_comptable.csv` |
| `import_engagement_types` | Importe les types d'engagement | `type_d_engagement.csv` |
| `import_reconciliation_types` | Importe les types de lettrage | `type_lettrage.csv` |
| `import_payer_types` | Importe les types de payeurs | `type_payeur.csv` |
| `import_service_types` | Importe les types de prestations | `type_prestation.csv` |
| `import_pricing_types` | Importe les types de tarification | `type_tarification.csv` |
| `import_client_account_types` | Importe les types de comptes clients | `type-de-compte-client.csv` |
| `import_activities` | Importe les activités | `activite.csv` |

Ces commandes peuvent être exécutées individuellement ou via des scripts d'automatisation.

## Exécution des imports

### Import complet via script shell

Pour importer toutes les données en une seule opération, utilisez le script `import_all_fixed.sh` (version Linux/Unix) ou `import_all_fixed.ps1` (version Windows) :

```bash
# Linux/Unix
$ ./import_all_fixed.sh

# Windows PowerShell
$ .\import_all_fixed.ps1
```

### Import complet via Docker

Si vous utilisez Docker, utilisez les scripts adaptés :

```bash
# Linux/Unix
$ ./docker_import_all.sh

# Windows PowerShell
$ .\docker_import_all.ps1
```

### Import manuel des données individuelles

Pour importer chaque type de données séparément, exécutez les commandes Django individuelles :

```bash
# Sans Docker
$ python manage.py import_pcg data/export_comptes_pcg.csv
$ python manage.py import_fiscal_years data/exercice_comptable.csv
$ python manage.py import_journals data/journal_comptable.csv
# etc.

# Avec Docker
$ docker-compose exec web python manage.py import_pcg data/export_comptes_pcg.csv
$ docker-compose exec web python manage.py import_fiscal_years data/exercice_comptable.csv
$ docker-compose exec web python manage.py import_journals data/journal_comptable.csv
# etc.
```

## Structure des fichiers CSV attendus

### Plan Comptable Général (`export_comptes_pcg.csv`)

| Colonne | Description | Exemple |
|---------|-------------|---------|
| NO_CPT_COMPTABLE_GENERAL | Numéro de compte | 101000 |
| LIB_CHAPITRE_COMPTABLE | Nom du chapitre | CAPITAL ET RESERVES |
| LIB_SECTION_COMPTABLE | Nom de la section | CAPITAL |
| LIB_RED_CPT_COMPTABLE_GENERAL | Nom abrégé | Capital |
| LIB_CPT_COMPTABLE_GENERAL | Nom complet | Capital social |
| INDIC_BILAN_RESULTAT | Indicateur bilan/résultat | BILAN |
| CODE_CPT_BUDG_THEO | Code compte budgétaire | 1010 |
| STATUT_RECUP_CPT | Statut récupération | ACTIF |
| CODE_REGRP_ETATS_FINANC_CPT | Groupe états financiers | CAPITAUX |

### Exercices comptables (`exercice_comptable.csv`)

| Colonne | Description | Exemple |
|---------|-------------|---------|
| NO_EXERCICE | Année de l'exercice | 2023 |
| LIB_EXERCICE_ | Nom de l'exercice | EXERCICE 2023 |

### Journaux comptables (`journal_comptable.csv`)

| Colonne | Description | Exemple |
|---------|-------------|---------|
| ID_JOURNAL_COMPTABLE | Identifiant unique | JVE001 |
| CODE_JOURNAL_COMPTABLE | Code du journal | VEN |
| LIB_RED_JOURNAL_COMPTABLE | Nom abrégé | Ventes |
| LIB_JOURNAL_COMPTABLE | Nom complet | Journal des ventes |
| CODE_SOCIETE | Code société | IVALUA |

### Municipalités (`commune_insee.csv`)

| Colonne | Description | Exemple |
|---------|-------------|---------|
| CODE_COMMUNE_INSEE | Code INSEE | 75056 |
| LIB_COMMUNE_INSEE | Nom de la commune | PARIS |
| CODE_POSTAL | Code postal | 75000 |
| CODE_DEPT_COMMUNE_INSEE | Code département | 75 |
| INDIC_EPCI | Code région | IDF |

## Gestion des erreurs d'import

### Vérification préalable des fichiers

Avant d'importer les données, vous pouvez vérifier l'encodage et la structure des fichiers à l'aide des scripts fournis :

```bash
# Vérifier l'encodage des fichiers
$ ./check_encoding.sh

# Vérifier l'ouverture des fichiers CSV
$ ./check_csv_files.sh
```

Ces scripts vous aideront à identifier les problèmes potentiels avant de lancer l'import.

### Résolution des problèmes courants

1. **Erreur d'encodage** : Convertissez les fichiers au format Latin-1 :

   ```bash
   $ iconv -f UTF-8 -t ISO-8859-1 input.csv > output.csv
   ```

2. **"Too many SQL variables"** : Cette erreur survient lors de l'import de grandes quantités de données. La solution est d'utiliser l'import par lots :

   ```python
   # Import avec traitement par lots
   def _import_with_batching(data, batch_size=500):
       batches = [data[i:i+batch_size] for i in range(0, len(data), batch_size)]
       for batch in batches:
           Model.objects.bulk_create(batch)
   ```

   Cette approche est déjà implémentée dans les scripts d'import mis à jour.

3. **Noms de colonnes incorrects** : Vérifiez que les noms des colonnes dans vos fichiers CSV correspondent à ceux attendus par les scripts d'import. En cas de différence, vous pouvez soit modifier les fichiers CSV, soit adapter les scripts d'import.

## Import programmé

Pour automatiser l'import régulier de données comptables (par exemple, mise à jour mensuelle), vous pouvez créer un job cron ou une tâche planifiée :

### Linux/Unix (Cron)

```bash
# Éditer la table cron
$ crontab -e

# Ajouter une tâche mensuelle (premier jour du mois à 2h00)
0 2 1 * * cd /chemin/vers/projet && ./import_all_fixed.sh >> /var/log/accounting_import.log 2>&1
```

### Windows (Task Scheduler)

1. Ouvrez le Planificateur de tâches Windows
2. Créez une nouvelle tâche planifiée qui exécute le script PowerShell :
   ```
   powershell.exe -ExecutionPolicy Bypass -File C:\chemin\vers\projet\import_all_fixed.ps1
   ```
3. Définissez la planification selon vos besoins (par exemple, mensuelle)

## Maintenance des données

Après l'import initial, vous pourriez avoir besoin de mettre à jour les données régulièrement. Voici quelques recommandations :

1. **Sauvegarde préalable** : Avant tout import massif, effectuez une sauvegarde de la base de données.

2. **Environnement de test** : Testez vos imports sur un environnement de test avant de les appliquer en production.

3. **Logs d'import** : Conservez les logs d'import pour pouvoir identifier la source des problèmes éventuels.

4. **Vérification post-import** : Après l'import, vérifiez un échantillon de données pour vous assurer de leur intégrité.

## Conclusion

L'import de données est une étape cruciale dans la mise en place du module de comptabilité. En suivant les procédures décrites dans ce document, vous pourrez initialiser votre système avec toutes les données de référence nécessaires à son bon fonctionnement.

Pour toute question ou problème relatif à l'import de données, consultez la section [FAQ et dépannage](./troubleshooting.md) ou contactez l'équipe de développement.
