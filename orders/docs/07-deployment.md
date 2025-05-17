# Guide de déploiement et configuration

Ce guide explique comment déployer et configurer l'application Orders dans différents environnements.

## Prérequis de déploiement

### Environnement système
- Python 3.10 ou supérieur
- Base de données PostgreSQL 13+ (production) ou SQLite (développement)
- Serveur web compatible WSGI (Gunicorn, uWSGI, etc.)
- Serveur HTTP en frontal (Nginx, Apache)

### Packages Python requis
Tous les packages nécessaires sont listés dans le fichier `requirements.txt` à la racine du projet :

```
Django==5.2.1
djangorestframework==3.14.0
django-filter==23.2
django-admin-interface==0.26.0
gunicorn==21.2.0
psycopg2-binary==2.9.6
whitenoise==6.5.0
python-dotenv==1.0.0
dj-database-url==2.1.0
```

## Options de déploiement

### 1. Déploiement local pour développement

Pour un déploiement local de développement, suivez ces étapes :

1. **Cloner le dépôt**
   ```bash
   git clone <url-du-repo>
   cd django-ivalua-api
   ```

2. **Créer un environnement virtuel**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # ou
   .venv\Scripts\activate     # Windows
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurer les variables d'environnement**
   Créez un fichier `.env` à la racine du projet avec le contenu suivant :
   ```
   DEBUG=True
   SECRET_KEY=your-secret-key-for-development
   DATABASE_URL=sqlite:///db.sqlite3
   ALLOWED_HOSTS=localhost,127.0.0.1
   ```

5. **Appliquer les migrations**
   ```bash
   python manage.py migrate
   ```

6. **Créer un superutilisateur**
   ```bash
   python manage.py createsuperuser
   ```

7. **Lancer le serveur de développement**
   ```bash
   python manage.py runserver
   ```

### 2. Déploiement en production avec Gunicorn et Nginx

Pour un déploiement en production, suivez ces étapes supplémentaires :

1. **Configurer les variables d'environnement**
   Créez un fichier `.env` à la racine du projet avec des paramètres de production :
   ```
   DEBUG=False
   SECRET_KEY=votre-clé-secrète-sécurisée
   DATABASE_URL=postgres://user:password@localhost:5432/ivalua_db
   ALLOWED_HOSTS=votredomaine.com,www.votredomaine.com
   CSRF_TRUSTED_ORIGINS=https://votredomaine.com
   SECURE_SSL_REDIRECT=True
   SESSION_COOKIE_SECURE=True
   CSRF_COOKIE_SECURE=True
   SECURE_HSTS_SECONDS=31536000
   ```

2. **Collecter les fichiers statiques**
   ```bash
   python manage.py collectstatic
   ```

3. **Configurer Gunicorn**
   Créez un fichier `gunicorn_start.sh` :
   ```bash
   #!/bin/bash
   NAME="ivalua_api"
   DIR=/chemin/vers/django-ivalua-api
   USER=utilisateur
   GROUP=groupe
   WORKERS=3
   BIND=unix:${DIR}/run/gunicorn.sock
   DJANGO_SETTINGS_MODULE=project.settings
   DJANGO_WSGI_MODULE=project.wsgi
   LOG_LEVEL=error

   cd $DIR
   source ${DIR}/.venv/bin/activate

   exec ${DIR}/.venv/bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
     --name $NAME \
     --workers $WORKERS \
     --user=$USER \
     --group=$GROUP \
     --bind=$BIND \
     --log-level=$LOG_LEVEL \
     --log-file=-
   ```
   
   Puis rendez-le exécutable :
   ```bash
   chmod +x gunicorn_start.sh
   ```

4. **Configurer Nginx**
   Créez un fichier de configuration pour Nginx :
   ```nginx
   server {
       listen 80;
       server_name votredomaine.com www.votredomaine.com;
       return 301 https://$host$request_uri;
   }

   server {
       listen 443 ssl;
       server_name votredomaine.com www.votredomaine.com;

       ssl_certificate /chemin/vers/certificat.pem;
       ssl_certificate_key /chemin/vers/clé-privée.pem;

       location = /favicon.ico { access_log off; log_not_found off; }
       
       location /static/ {
           root /chemin/vers/django-ivalua-api;
       }

       location /media/ {
           root /chemin/vers/django-ivalua-api;
       }

       location / {
           include proxy_params;
           proxy_pass http://unix:/chemin/vers/django-ivalua-api/run/gunicorn.sock;
       }
   }
   ```

5. **Configurer un service systemd**
   Créez un fichier `/etc/systemd/system/ivalua-api.service` :
   ```ini
   [Unit]
   Description=Ivalua API Gunicorn daemon
   After=network.target

   [Service]
   User=utilisateur
   Group=groupe
   WorkingDirectory=/chemin/vers/django-ivalua-api
   ExecStart=/chemin/vers/django-ivalua-api/gunicorn_start.sh
   Restart=on-failure

   [Install]
   WantedBy=multi-user.target
   ```

   Activez et démarrez le service :
   ```bash
   sudo systemctl enable ivalua-api
   sudo systemctl start ivalua-api
   ```

### 3. Déploiement avec Docker

Pour un déploiement avec Docker, suivez ces étapes :

1. **Créer un Dockerfile**
   ```dockerfile
   FROM python:3.10-slim

   ENV PYTHONDONTWRITEBYTECODE 1
   ENV PYTHONUNBUFFERED 1

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY . .

   RUN python manage.py collectstatic --noinput

   EXPOSE 8000

   CMD ["gunicorn", "--bind", "0.0.0.0:8000", "project.wsgi:application"]
   ```

2. **Créer un docker-compose.yml**
   ```yaml
   version: '3.8'

   services:
     db:
       image: postgres:13
       volumes:
         - postgres_data:/var/lib/postgresql/data/
       env_file:
         - ./.env
       environment:
         - POSTGRES_PASSWORD=${DB_PASSWORD}
         - POSTGRES_USER=${DB_USER}
         - POSTGRES_DB=${DB_NAME}

     web:
       build: .
       restart: always
       depends_on:
         - db
       env_file:
         - ./.env
       volumes:
         - static_volume:/app/staticfiles
         - media_volume:/app/media
       expose:
         - 8000

     nginx:
       image: nginx:1.21
       ports:
         - "80:80"
         - "443:443"
       volumes:
         - ./nginx/conf.d:/etc/nginx/conf.d
         - ./nginx/ssl:/etc/nginx/ssl
         - static_volume:/app/staticfiles
         - media_volume:/app/media
       depends_on:
         - web

   volumes:
     postgres_data:
     static_volume:
     media_volume:
   ```

3. **Lancer l'application avec Docker Compose**
   ```bash
   docker-compose up -d
   ```

## Configuration de l'application

### Configuration des paramètres dans settings.py

Voici les paramètres principaux à configurer dans le fichier `settings.py` :

#### 1. Base de données
```python
import dj_database_url
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

# ...

DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL', 'sqlite:///db.sqlite3'),
        conn_max_age=600
    )
}
```

#### 2. Cache
Pour une application en production, configurez le cache :
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/1'),
    }
}
```

#### 3. Internationalisation
```python
LANGUAGE_CODE = 'fr'
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_L10N = True
USE_TZ = True

MIDDLEWARE = [
    # ...
    'django.middleware.locale.LocaleMiddleware',  # Pour l'internationalisation
    # ...
]

LANGUAGES = [
    ('fr', 'Français'),
    ('en', 'English'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]
```

#### 4. Logging
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'orders': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### Configuration des éléments d'administration

#### 1. Personnalisation de l'interface d'administration

Vous pouvez personnaliser l'apparence de l'interface d'administration via l'application `admin_interface` :

1. Accédez à l'administration Django : `/admin/`
2. Naviguez vers "Admin Interface" > "Themes"
3. Modifiez le thème existant ou créez-en un nouveau
4. Personnalisez les couleurs, logos et autres éléments visuels

#### 2. Préchargement de données de référence

Pour charger des données initiales (fixtures) :
```bash
python manage.py loaddata orders/fixtures/initial_data.json
```

## Maintenance et sauvegardes

### Sauvegardes de la base de données

1. **PostgreSQL (dump)**
   ```bash
   pg_dump -U utilisateur -d ivalua_db -F c -f backup.dump
   ```

2. **Restauration depuis une sauvegarde**
   ```bash
   pg_restore -U utilisateur -d ivalua_db -c backup.dump
   ```

3. **Automatisation des sauvegardes**
   Créez un script dans `/etc/cron.daily/backup-ivalua-db` :
   ```bash
   #!/bin/bash
   DATE=$(date +%Y-%m-%d)
   BACKUP_DIR=/path/to/backups
   
   pg_dump -U utilisateur -d ivalua_db -F c -f $BACKUP_DIR/ivalua_db_$DATE.dump
   
   # Supprimer les sauvegardes de plus de 30 jours
   find $BACKUP_DIR -type f -name "ivalua_db_*.dump" -mtime +30 -delete
   ```
   
   Rendez-le exécutable:
   ```bash
   chmod +x /etc/cron.daily/backup-ivalua-db
   ```

## Sécurité

### Bonnes pratiques de sécurité

1. **Utiliser HTTPS** - Toujours activer HTTPS en production
2. **Protection des clés sensibles** - Utilisez des variables d'environnement
3. **Mise à jour régulière** - Gardez Django et les dépendances à jour
4. **Analyse de sécurité** - Utilisez des outils comme `bandit` pour auditer le code Python
5. **Limiter les accès à l'administration** - Restreindre l'accès à des IPs spécifiques

### Entêtes de sécurité

Ajoutez ces paramètres à votre fichier settings.py en production :

```python
# Sécurité
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

## Surveillance et supervision

### Mise en place de supervision

1. **Heartbeat**
   Créez une vue simple de santé à l'URL `/health/` qui retourne un code 200 si tout fonctionne correctement.

2. **Intégration avec Prometheus**
   Utilisez le package `django-prometheus` pour exposer des métriques.

3. **Alerting**
   Configurez des alertes sur les temps de réponse, les erreurs et l'utilisation des ressources.

## Résolution de problèmes courants

### Problèmes courants et solutions

1. **Erreurs de migration**
   ```bash
   # Vérifier l'état des migrations
   python manage.py showmigrations
   
   # Remettre à zéro les migrations problématiques
   python manage.py migrate orders zero
   
   # Recréer les migrations
   python manage.py makemigrations orders
   python manage.py migrate orders
   ```

2. **Problèmes de performance**
   - Vérifiez les requêtes lentes avec le debug toolbar
   - Optimisez les modèles avec des index appropriés
   - Utilisez le caching pour les données fréquemment accédées

3. **Erreurs 500 en production**
   - Consultez les logs dans `/var/log/nginx/error.log`
   - Vérifiez les logs Django dans le dossier configuré
   - Vérifiez les permissions des fichiers et dossiers

4. **Erreurs de connexion à la base de données**
   - Vérifiez que PostgreSQL est en cours d'exécution
   - Vérifiez les informations de connexion dans les variables d'environnement
   - Vérifiez les règles de pare-feu
