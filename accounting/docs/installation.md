# Guide d'Installation du Module de Comptabilité

Ce guide vous explique comment installer et configurer le module de comptabilité dans le projet P2P Ivalua.

## Prérequis

Avant d'installer le module de comptabilité, assurez-vous de disposer des éléments suivants :

- Python 3.10 ou supérieur
- Django 4.0 ou supérieur
- Une base de données compatible (PostgreSQL recommandé pour la production)
- Accès aux fichiers de données de référence (PCG, municipalités, etc.)

## Installation dans un environnement existant

Le module de comptabilité est conçu pour s'intégrer à un projet Django existant. Si vous travaillez dans le projet P2P Ivalua, le module est déjà inclus et vous pouvez passer directement à la section Configuration.

Si vous souhaitez ajouter le module à un autre projet Django, suivez ces étapes :

1. Copiez le dossier `accounting` à la racine de votre projet Django.

2. Ajoutez l'application à la liste des applications installées dans votre fichier `settings.py` :

```python
INSTALLED_APPS = [
    # ...
    'accounting',
    # ...
]
```

3. Incluez les URLs du module dans votre fichier `urls.py` principal :

```python
from django.urls import path, include

urlpatterns = [
    # ...
    path('api/v1.0/acc/', include('accounting.urls')),
    # ...
]
```

## Configuration

### Configuration de la base de données

Le module utilise la configuration de base de données de votre projet Django. Pour de meilleures performances, nous recommandons d'utiliser PostgreSQL :

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ivalua_db',
        'USER': 'ivalua',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

Pour SQLite (recommandé uniquement en développement) :

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### Configuration des paramètres spécifiques

Ajoutez les paramètres suivants à votre fichier `settings.py` pour configurer le comportement du module de comptabilité :

```python
# Configuration comptable
ACCOUNTING = {
    # Longueur de la référence des écritures comptables
    'ENTRY_REFERENCE_LENGTH': 10,
    
    # Préfixe pour les références d'écritures
    'ENTRY_REFERENCE_PREFIX': 'ACC',
    
    # Activer la validation automatique des écritures équilibrées
    'AUTO_VALIDATE_BALANCED_ENTRIES': False,
    
    # Nombre d'exercices fiscaux ouverts maximum
    'MAX_OPEN_FISCAL_YEARS': 2,
}
```

## Migration de la base de données

Une fois le module configuré, vous devez créer et appliquer les migrations de la base de données :

```bash
# Générer les migrations
$ python manage.py makemigrations accounting

# Appliquer les migrations
$ python manage.py migrate accounting
```

## Installation avec Docker

Si vous utilisez Docker pour votre environnement de développement ou de production, le module est déjà inclus dans l'image Docker du projet P2P Ivalua.

Pour démarrer l'application avec Docker :

```bash
# Construire l'image
$ docker-compose build

# Démarrer les services
$ docker-compose up -d

# Appliquer les migrations
$ docker-compose exec web python manage.py migrate accounting
```

## Installation des données initiales

Le module nécessite certaines données de référence pour fonctionner correctement. Suivez ces étapes pour importer les données initiales :

### Préparation des fichiers de données

Assurez-vous que vos fichiers CSV sont disponibles dans un dossier accessible. Par défaut, le module cherche les fichiers dans le dossier `data` à la racine du projet :

```
projet/
├── data/
│   ├── commune_insee.csv
│   ├── exercice_comptable.csv
│   ├── export_comptes_pcg.csv
│   ├── journal_comptable.csv
│   ├── type-de-comptabilite.csv
│   └── ... (autres fichiers de données)
```

### Vérification de l'encodage des fichiers

Les fichiers CSV doivent être encodés en Latin-1 (ISO-8859-1) pour une compatibilité optimale. Vous pouvez vérifier et convertir l'encodage à l'aide du script `check_encoding.sh` :

```bash
$ ./check_encoding.sh
```

### Import des données

Utilisez le script `import_all.sh` (ou `import_all_fixed.sh`) pour importer toutes les données de référence en une seule opération :

```bash
# Sans Docker
$ ./import_all_fixed.sh

# Avec Docker
$ ./docker_import_all.sh
```

Pour importer uniquement certaines données, vous pouvez utiliser les commandes spécifiques :

```bash
# Import du Plan Comptable Général
$ python manage.py import_pcg data/export_comptes_pcg.csv

# Import des exercices comptables
$ python manage.py import_fiscal_years data/exercice_comptable.csv

# Import des journaux comptables
$ python manage.py import_journals data/journal_comptable.csv

# Import des municipalités
$ python manage.py import_municipalities data/commune_insee.csv
```

## Vérification de l'installation

Pour vérifier que le module est correctement installé et configuré, vous pouvez exécuter les tests unitaires :

```bash
$ python manage.py test accounting
```

Vous pouvez également vérifier l'accès à l'API REST en visitant l'URL suivante dans votre navigateur :

```
http://localhost:8000/api/v1.0/acc/
```

Vous devriez voir la liste des points d'entrée de l'API pour le module de comptabilité.

## Interface d'administration

Pour accéder à l'interface d'administration Django et gérer les données comptables :

1. Créez un superutilisateur si vous n'en avez pas déjà un :

```bash
$ python manage.py createsuperuser
```

2. Accédez à l'interface d'administration à l'URL suivante :

```
http://localhost:8000/admin/
```

3. Connectez-vous avec les identifiants du superutilisateur.

4. Naviguez vers la section "Accounting" pour gérer les données comptables.

## Résolution des problèmes courants

### Erreur d'import des données

Si vous rencontrez des erreurs lors de l'import des données, vérifiez les points suivants :

1. **Encodage des fichiers** : Les fichiers CSV doivent être encodés en Latin-1 (ISO-8859-1).

   ```bash
   $ iconv -f UTF-8 -t ISO-8859-1 input.csv > output.csv
   ```

2. **Format des fichiers CSV** : Vérifiez que le séparateur est bien un point-virgule (;).

3. **Noms des colonnes** : Les scripts d'import s'attendent à des noms de colonnes spécifiques. Vérifiez que les noms correspondent aux attentes des scripts.

4. **Trop de variables SQL** : Si vous obtenez l'erreur "too many SQL variables", c'est généralement lié à un grand nombre d'entrées dans un fichier. La solution est d'utiliser l'import par lots comme implémenté dans les scripts mis à jour.

### Erreurs de migration

Si vous rencontrez des erreurs lors des migrations, essayez les solutions suivantes :

1. Réinitialisez les migrations si vous êtes en environnement de développement :

   ```bash
   $ python manage.py migrate accounting zero
   $ rm accounting/migrations/0*.py
   $ python manage.py makemigrations accounting
   $ python manage.py migrate accounting
   ```

2. Pour les erreurs de dépendance, assurez-vous que toutes les migrations des autres applications dont dépend le module de comptabilité ont été appliquées.

## Conclusion

Vous avez maintenant installé et configuré le module de comptabilité. Vous pouvez commencer à l'utiliser pour gérer vos opérations comptables dans le projet P2P Ivalua.

Pour plus d'informations sur l'utilisation du module, consultez le [Guide d'utilisation](./user_guide.md).
