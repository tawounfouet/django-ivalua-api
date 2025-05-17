# Guide de Développement et d'Extension du Module de Comptabilité

Ce document s'adresse aux développeurs qui souhaitent maintenir, améliorer ou étendre le module de comptabilité du projet P2P Ivalua.

## Architecture du code

### Structure des fichiers

```
accounting/
├── __init__.py              # Initialisation du module
├── admin.py                 # Configuration de l'interface d'administration
├── apps.py                  # Configuration de l'application Django
├── serializers.py           # Sérialiseurs pour l'API REST
├── urls.py                  # Routes de l'API
├── views.py                 # Vues et ViewSets de l'API
├── data/                    # Données statiques
├── docs/                    # Documentation
├── management/              # Commandes personnalisées
│   └── commands/            # Scripts d'importation et d'administration
├── migrations/              # Migrations de base de données
├── models/                  # Modèles de données
│   ├── __init__.py
│   ├── accounts.py          # Modèles du Plan Comptable Général
│   ├── entries.py           # Modèles des écritures comptables
│   ├── journals.py          # Modèles des journaux et exercices
│   └── reference_data.py    # Données de référence
└── utils/                   # Utilitaires et fonctions d'aide
    ├── __init__.py
    ├── financial_statements.py  # Génération d'états financiers
    ├── validators.py        # Validation des données comptables
    └── importers.py         # Fonctions d'importation
```

### Principes de conception

Le module suit plusieurs principes de conception essentiels :

1. **Séparation des responsabilités** : Les modèles, vues et logiques métier sont clairement séparés.

2. **Encapsulation** : La logique métier complexe est encapsulée dans des méthodes de modèle ou des fonctions d'utilitaire.

3. **Validation à plusieurs niveaux** : La validation s'effectue au niveau du modèle, des sérialiseurs et des vues.

4. **Traçabilité** : Toutes les opérations importantes sont journalisées pour l'audit.

5. **Extensibilité** : Le code est conçu pour faciliter l'ajout de nouvelles fonctionnalités.

## Guide de développement

### Configuration de l'environnement

Pour commencer à développer sur le module de comptabilité, suivez ces étapes :

1. Clonez le dépôt du projet :
   ```bash
   git clone https://github.com/your-organization/p2p-ivalua.git
   cd p2p-ivalua
   ```

2. Créez et activez un environnement virtuel :
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

4. Appliquez les migrations :
   ```bash
   python manage.py migrate
   ```

5. Lancez le serveur de développement :
   ```bash
   python manage.py runserver
   ```

### Conventions de codage

Suivez ces conventions lors du développement dans ce module :

1. **Style de code** : Respectez PEP 8 pour le style Python.

2. **Docstrings** : Utilisez le format Google pour la documentation du code.
   ```python
   def function_name(param1, param2):
       """Description de la fonction.
       
       Args:
           param1: Description du premier paramètre.
           param2: Description du second paramètre.
           
       Returns:
           Description de la valeur de retour.
           
       Raises:
           ExceptionType: Description de quand l'exception est levée.
       """
       # Code de la fonction
   ```

3. **Nommage** :
   - Classes : PascalCase (ex: `AccountingEntry`)
   - Fonctions et méthodes : snake_case (ex: `validate_balance`)
   - Variables : snake_case (ex: `total_debit`)
   - Constantes : MAJUSCULES_AVEC_UNDERSCORES (ex: `DEFAULT_DECIMAL_PLACES`)

4. **Internationalisation** : Encadrez tous les textes visibles par l'utilisateur avec la fonction `_()` pour permettre la traduction.
   ```python
   from django.utils.translation import gettext_lazy as _
   
   error_message = _("The accounting entry is not balanced.")
   ```

### Ajout de nouveaux modèles

Pour ajouter un nouveau modèle au module :

1. Déterminez le fichier approprié dans le dossier `models/` ou créez-en un nouveau si nécessaire.

2. Définissez votre classe de modèle en héritant de `BaseModel` :
   ```python
   from django.db import models
   from django.utils.translation import gettext_lazy as _
   from accounting.models.base import BaseModel
   
   class NewEntity(BaseModel):
       """Description de la nouvelle entité."""
       code = models.CharField(_("code"), max_length=10, unique=True)
       name = models.CharField(_("name"), max_length=100)
       description = models.TextField(_("description"), blank=True)
       
       class Meta:
           verbose_name = _("new entity")
           verbose_name_plural = _("new entities")
           ordering = ['code']
       
       def __str__(self):
           return self.name
   ```

3. Importez le nouveau modèle dans `models/__init__.py` pour le rendre accessible :
   ```python
   from accounting.models.your_file import NewEntity
   
   __all__ = [
       # Autres modèles...
       'NewEntity',
   ]
   ```

4. Créez et appliquez les migrations :
   ```bash
   python manage.py makemigrations accounting
   python manage.py migrate accounting
   ```

### Extension de l'API REST

Pour exposer un nouveau modèle via l'API REST :

1. Créez un sérialiseur dans `serializers.py` :
   ```python
   from rest_framework import serializers
   from accounting.models import NewEntity
   
   class NewEntitySerializer(serializers.ModelSerializer):
       class Meta:
           model = NewEntity
           fields = ['id', 'code', 'name', 'description', 'created_at', 'updated_at']
           read_only_fields = ['created_at', 'updated_at']
   ```

2. Créez un ViewSet dans `views.py` :
   ```python
   from rest_framework import viewsets
   from accounting.models import NewEntity
   from accounting.serializers import NewEntitySerializer
   
   class NewEntityViewSet(viewsets.ModelViewSet):
       """API endpoint for managing new entities."""
       queryset = NewEntity.objects.all()
       serializer_class = NewEntitySerializer
       filterset_fields = ['code', 'name']
       search_fields = ['code', 'name', 'description']
       ordering_fields = ['code', 'name', 'created_at', 'updated_at']
   ```

3. Ajoutez le ViewSet aux routes dans `urls.py` :
   ```python
   from rest_framework.routers import DefaultRouter
   from accounting.views import NewEntityViewSet
   
   router = DefaultRouter()
   # Autres routes...
   router.register(r'new-entities', NewEntityViewSet)
   
   urlpatterns = router.urls
   ```

### Ajout de nouvelles commandes

Pour ajouter une nouvelle commande de gestion Django :

1. Créez un fichier Python dans le dossier `management/commands/` :
   ```python
   # accounting/management/commands/your_command.py
   from django.core.management.base import BaseCommand
   
   class Command(BaseCommand):
       help = 'Description de la commande'
       
       def add_arguments(self, parser):
           parser.add_argument('arg1', type=str, help='Description de l\'argument 1')
           parser.add_argument('--option1', type=int, default=10, help='Description de l\'option 1')
       
       def handle(self, *args, **options):
           arg1 = options['arg1']
           option1 = options['option1']
           
           # Logique de la commande
           self.stdout.write(self.style.SUCCESS('Commande exécutée avec succès !'))
   ```

2. La commande peut ensuite être exécutée avec :
   ```bash
   python manage.py your_command value_for_arg1 --option1=20
   ```

### Extension des rapports financiers

Le module fournit un framework extensible pour les rapports financiers dans `utils/financial_statements.py`. Pour ajouter un nouveau type de rapport :

1. Créez une nouvelle classe de rapport héritant de `BaseFinancialReport` :
   ```python
   from accounting.utils.financial_statements import BaseFinancialReport
   
   class CustomReport(BaseFinancialReport):
       """Implémentation d'un rapport financier personnalisé."""
       
       def __init__(self, fiscal_year, start_date=None, end_date=None, **kwargs):
           super().__init__(fiscal_year, start_date, end_date, **kwargs)
           # Initialisation spécifique
       
       def generate(self):
           """Génère le rapport personnalisé."""
           # Logique de génération du rapport
           result = {
               'title': 'Rapport personnalisé',
               'fiscal_year': self.fiscal_year.name,
               'generated_at': timezone.now(),
               'data': self._compute_data(),
           }
           return result
       
       def _compute_data(self):
           """Calcule les données du rapport."""
           # Logique de calcul spécifique
           return data
   ```

2. Exposez le nouveau rapport via l'API en ajoutant une vue dans `views.py` :
   ```python
   from rest_framework.decorators import api_view
   from rest_framework.response import Response
   from accounting.utils.financial_statements import CustomReport
   
   @api_view(['GET'])
   def custom_report_view(request):
       """API endpoint pour le rapport personnalisé."""
       fiscal_year_id = request.GET.get('fiscal_year')
       start_date = request.GET.get('start_date')
       end_date = request.GET.get('end_date')
       
       try:
           fiscal_year = FiscalYear.objects.get(pk=fiscal_year_id)
       except FiscalYear.DoesNotExist:
           return Response({'error': 'Fiscal year not found'}, status=404)
       
       report = CustomReport(fiscal_year, start_date, end_date)
       report_data = report.generate()
       
       return Response(report_data)
   ```

3. Ajoutez la vue aux URLs dans `urls.py` :
   ```python
   from django.urls import path
   from accounting.views import custom_report_view
   
   urlpatterns = [
       # Autres URLs...
       path('reports/custom-report/', custom_report_view, name='custom-report'),
   ]
   ```

## Tests

### Écriture de tests

Le module utilise le framework de test Django. Les tests doivent être placés dans un dossier `tests/` :

```
accounting/
└── tests/
    ├── __init__.py
    ├── test_models.py
    ├── test_api.py
    └── test_reports.py
```

Exemple de test pour un modèle :

```python
from django.test import TestCase
from accounting.models import AccountingEntry, AccountingEntryLine, GeneralLedgerAccount

class AccountingEntryTests(TestCase):
    def setUp(self):
        # Configuration commune pour tous les tests
        self.account1 = GeneralLedgerAccount.objects.create(
            account_number='411000',
            short_name='Clients',
            full_name='Clients'
        )
        self.account2 = GeneralLedgerAccount.objects.create(
            account_number='707000',
            short_name='Ventes de marchandises',
            full_name='Ventes de marchandises'
        )
    
    def test_is_balanced(self):
        """Test si la méthode is_balanced fonctionne correctement."""
        # Créer une écriture équilibrée
        entry = AccountingEntry.objects.create(
            reference='TEST001',
            date='2023-01-01',
            description='Test entry'
        )
        
        # Ajouter des lignes qui s'équilibrent
        AccountingEntryLine.objects.create(
            entry=entry,
            account=self.account1,
            debit_amount=100,
            credit_amount=0,
            line_number=1
        )
        AccountingEntryLine.objects.create(
            entry=entry,
            account=self.account2,
            debit_amount=0,
            credit_amount=100,
            line_number=2
        )
        
        # Vérifier que l'écriture est équilibrée
        self.assertTrue(entry.is_balanced())
        
        # Modifier une ligne pour déséquilibrer
        line = entry.lines.first()
        line.debit_amount = 200
        line.save()
        
        # Vérifier que l'écriture n'est plus équilibrée
        self.assertFalse(entry.is_balanced())
```

### Exécution des tests

Pour exécuter tous les tests du module :

```bash
python manage.py test accounting
```

Pour exécuter une classe de test spécifique :

```bash
python manage.py test accounting.tests.test_models.AccountingEntryTests
```

Pour exécuter un test spécifique :

```bash
python manage.py test accounting.tests.test_models.AccountingEntryTests.test_is_balanced
```

## Déploiement

### Préparation au déploiement

Avant de déployer des modifications, assurez-vous de :

1. Exécuter tous les tests et vérifier qu'ils passent :
   ```bash
   python manage.py test accounting
   ```

2. Générer et vérifier les migrations :
   ```bash
   python manage.py makemigrations accounting --check
   ```

3. Mettre à jour la documentation si nécessaire

4. Vérifier que le code respecte les conventions de style :
   ```bash
   flake8 accounting
   ```

### Stratégie de migration en production

Pour déployer des modifications en production :

1. **Sauvegarde** : Effectuez toujours une sauvegarde complète de la base de données avant d'appliquer des migrations.

2. **Migrations incrémentales** : Préférez plusieurs petites migrations plutôt qu'une seule grande pour faciliter les rollbacks si nécessaire.

3. **Tests en préproduction** : Testez toujours les migrations sur un environnement de préproduction avant la production.

4. **Fenêtre de maintenance** : Planifiez les migrations importantes pendant une fenêtre de maintenance pour minimiser l'impact sur les utilisateurs.

5. **Procédure de rollback** : Préparez toujours une procédure de rollback en cas de problème.

## Intégration avec d'autres modules

Le module de comptabilité peut interagir avec d'autres modules du système P2P Ivalua. Voici comment implémenter ces intégrations :

### Génération d'écritures comptables depuis d'autres modules

Pour générer des écritures comptables depuis un autre module (par exemple, le module Factures) :

```python
from accounting.models import AccountingEntry, AccountingEntryLine, GeneralLedgerAccount, AccountingJournal, FiscalYear

def create_invoice_accounting_entry(invoice):
    """Crée une écriture comptable à partir d'une facture."""
    # Récupérer les références nécessaires
    journal = AccountingJournal.objects.get(code='VEN')
    fiscal_year = FiscalYear.objects.get(is_current=True)
    client_account = GeneralLedgerAccount.objects.get(account_number='411000')
    revenue_account = GeneralLedgerAccount.objects.get(account_number='707000')
    tax_account = GeneralLedgerAccount.objects.get(account_number='445710')
    
    # Créer l'en-tête de l'écriture
    entry = AccountingEntry.objects.create(
        reference=f"VTE{invoice.number}",
        date=invoice.date,
        journal=journal,
        fiscal_year=fiscal_year,
        description=f"Facture client {invoice.number} - {invoice.client.name}",
        created_by=invoice.created_by
    )
    
    # Créer les lignes d'écriture
    # 1. Ligne client (débit)
    AccountingEntryLine.objects.create(
        entry=entry,
        account=client_account,
        debit_amount=invoice.total_amount,
        credit_amount=0,
        description=f"Facture {invoice.number}",
        line_number=1
    )
    
    # 2. Ligne revenus (crédit)
    AccountingEntryLine.objects.create(
        entry=entry,
        account=revenue_account,
        debit_amount=0,
        credit_amount=invoice.net_amount,
        description=f"Facture {invoice.number} - Montant HT",
        line_number=2
    )
    
    # 3. Ligne TVA (crédit)
    AccountingEntryLine.objects.create(
        entry=entry,
        account=tax_account,
        debit_amount=0,
        credit_amount=invoice.tax_amount,
        description=f"Facture {invoice.number} - TVA",
        line_number=3
    )
    
    return entry
```

### Enregistrement des événements comptables

Pour enregistrer des événements comptables importants dans le système d'audit :

```python
from django.utils import timezone
from your_project.audit.models import AuditLog

def log_accounting_event(user, action, entity, details=None):
    """Enregistre un événement comptable dans le journal d'audit."""
    AuditLog.objects.create(
        timestamp=timezone.now(),
        user=user,
        module='accounting',
        action=action,
        entity_type=entity.__class__.__name__,
        entity_id=entity.id,
        details=details or {}
    )
```

## Bonnes pratiques et recommandations

### Patterns de conception recommandés

1. **Repository Pattern** : Encapsulez la logique d'accès aux données dans des classes dédiées pour faciliter les tests et la réutilisation.

2. **Service Layer** : Isolez la logique métier complexe dans des services pour éviter de surcharger les modèles ou les vues.

3. **Factory Pattern** : Utilisez des factories pour créer des objets complexes comme les différents types de rapports financiers.

### Optimisation des performances

1. **Requêtes efficientes** : Utilisez `select_related` et `prefetch_related` pour réduire le nombre de requêtes SQL.
   ```python
   # Inefficient
   entries = AccountingEntry.objects.all()
   for entry in entries:
       print(entry.journal.name)  # Requête SQL pour chaque entrée
   
   # Efficient
   entries = AccountingEntry.objects.select_related('journal').all()
   for entry in entries:
       print(entry.journal.name)  # Pas de requête SQL supplémentaire
   ```

2. **Opérations en masse** : Utilisez `bulk_create` et `bulk_update` pour les opérations sur de nombreux objets.
   ```python
   # Créer de nombreux objets efficacement
   objects = [Model(attr=value) for value in values]
   Model.objects.bulk_create(objects)
   ```

3. **Pagination** : Implémentez la pagination pour toutes les API retournant potentiellement de grandes quantités de données.

4. **Caching** : Utilisez le système de cache de Django pour les données fréquemment accédées et qui changent peu.
   ```python
   from django.core.cache import cache
   
   def get_fiscal_year_settings():
       cache_key = 'fiscal_year_settings'
       result = cache.get(cache_key)
       if result is None:
           result = compute_expensive_fiscal_year_settings()
           cache.set(cache_key, result, 3600)  # Cache pour 1 heure
       return result
   ```

### Sécurité

1. **Validation des entrées** : Validez toutes les entrées utilisateur à plusieurs niveaux (formulaires, sérialiseurs, modèles).

2. **Autorisations** : Utilisez le système de permissions de Django pour contrôler l'accès aux fonctionnalités sensibles.
   ```python
   from rest_framework.permissions import BasePermission
   
   class CanPostAccountingEntries(BasePermission):
       """Permission pour comptabiliser des écritures."""
       def has_permission(self, request, view):
           return request.user.has_perm('accounting.post_accountingentry')
   ```

3. **Protection contre les injections SQL** : Utilisez les ORM et les requêtes paramétrées plutôt que des requêtes SQL brutes.

4. **Audit des opérations sensibles** : Journalisez toutes les opérations financières importantes pour l'audit.

## Ressources supplémentaires

### Documentation de référence

- [Documentation Django](https://docs.djangoproject.com/)
- [Documentation Django REST framework](https://www.django-rest-framework.org/)
- [Plan Comptable Général](https://www.economie.gouv.fr/dgfip/plan-comptable-general)

### Outils de développement recommandés

- **Visual Studio Code** avec les extensions :
  - Python
  - Django
  - Django Template
  - ESLint
  - GitLens

- **PyCharm Professional** avec son support Django intégré

### Tutoriels et guides

- [Real Python - Django Tutorials](https://realpython.com/tutorials/django/)
- [Django REST framework Tutorial](https://www.django-rest-framework.org/tutorial/quickstart/)
- [Test-Driven Development with Django](https://testdriven.io/courses/tdd-django/)

## Conclusion

Ce guide vous a fourni les bases pour développer et étendre le module de comptabilité du projet P2P Ivalua. En suivant ces pratiques et principes, vous pourrez maintenir et améliorer le module de manière efficace et fiable.

N'hésitez pas à contribuer à cette documentation en proposant des améliorations ou des clarifications si nécessaire.
