# Audit et Validation dans le Module de Comptabilité

Ce document décrit les mécanismes d'audit et de validation implémentés dans le module de comptabilité du projet P2P Ivalua.

## Principes d'audit

L'audit dans le module de comptabilité repose sur plusieurs principes fondamentaux :

1. **Traçabilité complète** : Toute action significative est enregistrée avec des informations détaillées
2. **Non-répudiation** : Les actions ne peuvent être niées grâce à l'identification claire des utilisateurs
3. **Immuabilité** : Une fois comptabilisées, les écritures ne peuvent plus être modifiées
4. **Piste d'audit** : Une piste d'audit claire est maintenue pour toutes les opérations financières

## Mécanismes de traçabilité

### Traçabilité des écritures comptables

Chaque écriture comptable conserve des informations complètes sur son cycle de vie :

| Champ | Description |
|-------|-------------|
| created_by | Utilisateur ayant créé l'écriture |
| created_at | Date et heure de création |
| validated_by | Utilisateur ayant validé l'écriture |
| validated_date | Date et heure de validation |
| posted_by | Utilisateur ayant comptabilisé l'écriture |
| posted_date | Date et heure de comptabilisation |
| canceled_by | Utilisateur ayant annulé l'écriture |
| canceled_date | Date et heure d'annulation |

Ces informations sont automatiquement enregistrées lors des changements d'état des écritures et ne peuvent être modifiées manuellement.

### Journal d'audit

En plus des champs de traçabilité intégrés aux modèles, le module utilise un journal d'audit centralisé qui enregistre toutes les actions significatives :

```python
# Exemple d'entrée dans le journal d'audit
{
    "timestamp": "2023-05-15T14:30:22Z",
    "user": "john.doe",
    "action": "validate_accounting_entry",
    "resource_type": "AccountingEntry",
    "resource_id": "VTE2023001",
    "details": {
        "previous_status": "draft",
        "new_status": "validated",
        "validation_comment": "Écriture validée après vérification"
    }
}
```

Les actions suivantes sont systématiquement journalisées :
- Création d'une écriture
- Modification d'une écriture (à l'état brouillon)
- Validation d'une écriture
- Comptabilisation d'une écriture
- Annulation d'une écriture
- Extourne d'une écriture
- Clôture d'un exercice fiscal
- Modification des paramètres comptables

### Horodatage et signatures numériques

Pour les environnements nécessitant un niveau d'audit encore plus élevé, le module peut être configuré pour utiliser un mécanisme d'horodatage qualifié et de signatures numériques :

```python
# Configuration du système de signature dans settings.py
ACCOUNTING = {
    # Autres paramètres...
    'ENABLE_DIGITAL_SIGNATURES': True,
    'SIGNATURE_SERVICE_URL': 'https://signature-service.example.com',
    'SIGNATURE_API_KEY': 'your-api-key',
}
```

Lorsque cette fonctionnalité est activée, chaque opération critique (comptabilisation d'écriture, clôture d'exercice) est horodatée et signée numériquement, créant une preuve cryptographique de son intégrité.

## Mécanismes de validation

### Validation des écritures comptables

Le module implémente plusieurs niveaux de validation pour garantir l'intégrité des données comptables :

#### 1. Validation de base (niveau modèle)

```python
def clean(self):
    """Validation au niveau du modèle pour AccountingEntryLine."""
    if self.debit_amount > 0 and self.credit_amount > 0:
        raise ValidationError(_("A line cannot have both debit and credit amounts."))
    
    if self.debit_amount == 0 and self.credit_amount == 0:
        raise ValidationError(_("A line must have either a debit or credit amount."))
```

#### 2. Validation métier (équilibre des écritures)

```python
def is_balanced(self):
    """Vérifie si l'écriture est équilibrée."""
    total_debit = sum(line.debit_amount for line in self.lines.all())
    total_credit = sum(line.credit_amount for line in self.lines.all())
    return total_debit == total_credit

def validate(self, user=None, validation_comment=None):
    """Valide une écriture comptable."""
    if self.status != self.DRAFT:
        raise ValidationError(_("Only draft entries can be validated."))
    
    if not self.is_balanced():
        raise ValidationError(_("Cannot validate an unbalanced entry."))
    
    # Autres validations métier...
    
    self.status = self.VALIDATED
    self.validated_by = user
    self.validated_date = timezone.now()
    self.save()
    
    # Enregistrement dans le journal d'audit
    log_accounting_event(
        user=user,
        action='validate_accounting_entry',
        entity=self,
        details={'validation_comment': validation_comment}
    )
```

#### 3. Validation au niveau de l'API (sérialiseurs)

```python
class AccountingEntrySerializer(serializers.ModelSerializer):
    """Sérialiseur pour les écritures comptables."""
    
    def validate(self, data):
        """Validation personnalisée au niveau du sérialiseur."""
        # Validation que les lignes existent
        if 'lines' not in data or not data['lines']:
            raise serializers.ValidationError(_("An accounting entry must have at least one line."))
        
        # Validation de la date (pas dans le futur)
        if data.get('date') and data['date'] > date.today():
            raise serializers.ValidationError(_("The entry date cannot be in the future."))
        
        # Validation que l'exercice fiscal est ouvert
        fiscal_year = data.get('fiscal_year')
        if fiscal_year and fiscal_year.is_closed:
            raise serializers.ValidationError(_("Cannot create an entry in a closed fiscal year."))
        
        return data
```

### Séparation des responsabilités

Le module implémente une séparation stricte des responsabilités conformément aux bonnes pratiques comptables :

1. **Création** : Un utilisateur peut créer des écritures en brouillon
2. **Validation** : Un utilisateur différent (avec les permissions appropriées) peut valider les écritures
3. **Comptabilisation** : Seuls les utilisateurs avec des droits spécifiques peuvent comptabiliser les écritures validées

Cette séparation est mise en œuvre via le système de permissions Django :

```python
class AccountingPermissions:
    """Permissions spécifiques au module de comptabilité."""
    CREATE_ENTRY = 'accounting.add_accountingentry'
    VALIDATE_ENTRY = 'accounting.validate_accountingentry'
    POST_ENTRY = 'accounting.post_accountingentry'
    REVERSE_ENTRY = 'accounting.reverse_accountingentry'
    CLOSE_FISCAL_YEAR = 'accounting.close_fiscalyear'
```

## Contrôles de cohérence

### Contrôles automatiques

Le module effectue plusieurs contrôles automatiques pour garantir la cohérence des données :

1. **Vérification des références uniques** : Les références d'écritures sont vérifiées pour s'assurer qu'elles sont uniques.

2. **Validation des exercices fiscaux** : Les écritures ne peuvent être créées que dans des exercices ouverts.

3. **Contrôle des journaux comptables** : Certains journaux (comme les à-nouveaux) ont des règles spécifiques qui sont vérifiées automatiquement.

4. **Validation des comptes** : Les comptes utilisés dans les écritures sont vérifiés pour s'assurer qu'ils sont actifs.

### Rapports de contrôle

Le module fournit plusieurs rapports pour faciliter les contrôles manuels :

1. **Journal des événements comptables** : Liste chronologique de toutes les actions comptables.

2. **Rapport d'écritures non équilibrées** : Identifie les écritures en brouillon qui ne sont pas équilibrées.

3. **Analyse des écritures par utilisateur** : Permet d'examiner les écritures créées, validées ou comptabilisées par un utilisateur spécifique.

4. **Rapport d'audit de clôture** : Détaille les opérations effectuées lors de la clôture d'un exercice.

## Archivage et conservation

### Politique de conservation des données

Le module permet de définir des politiques de conservation des données conformément aux exigences légales :

```python
# Configuration de la politique de conservation dans settings.py
ACCOUNTING = {
    # Autres paramètres...
    'DATA_RETENTION': {
        'ACCOUNTING_ENTRIES': {
            'ACTIVE_PERIOD': 10,  # Années de conservation active
            'ARCHIVE_PERIOD': 5,  # Années supplémentaires en archive
        },
        'AUDIT_LOGS': {
            'ACTIVE_PERIOD': 5,  # Années de conservation active
            'ARCHIVE_PERIOD': 10,  # Années supplémentaires en archive
        }
    }
}
```

### Archivage des exercices clôturés

Lorsqu'un exercice fiscal est clôturé, plusieurs opérations sont effectuées :

1. **Gel des données** : Toutes les écritures de l'exercice sont verrouillées et ne peuvent plus être modifiées.

2. **Génération d'archives** : Des fichiers d'archive (PDF, XML) sont générés pour tous les documents comptables importants.

3. **Calcul des soldes de clôture** : Les soldes finaux sont calculés et enregistrés pour référence future.

4. **Création des à-nouveaux** : Les écritures d'à-nouveaux sont automatiquement générées pour le nouvel exercice.

## Conformité réglementaire

### Exigences légales françaises

Le module est conçu pour respecter les exigences légales françaises en matière de comptabilité :

1. **Tenue des comptes** : Conformité avec le Plan Comptable Général (PCG).

2. **Permanence des méthodes** : Maintien de la cohérence des méthodes comptables.

3. **Conservation des données** : Respect des durées légales de conservation (10 ans).

4. **Piste d'audit fiable** : Conformité avec les exigences de traçabilité.

### Préparation aux audits

Pour faciliter les audits externes, le module fournit :

1. **Exports normalisés** : Génération de fichiers d'export au format standard FEC (Fichier des Écritures Comptables).

2. **Rapports d'audit prédéfinis** : Des rapports spécifiquement conçus pour les besoins des auditeurs.

3. **Traçabilité complète** : Possibilité de reconstituer l'historique de toutes les opérations.

4. **Extraction de données** : Outils d'extraction ciblée pour répondre aux demandes spécifiques des auditeurs.

## Configuration des règles d'audit

Les règles d'audit et de validation peuvent être configurées selon les besoins spécifiques de l'organisation :

```python
# Exemple de configuration des règles d'audit dans settings.py
ACCOUNTING = {
    # Autres paramètres...
    'AUDIT_RULES': {
        # Règle des 4 yeux (validation obligatoire par un autre utilisateur)
        'ENFORCE_FOUR_EYES_PRINCIPLE': True,
        
        # Niveau de journalisation (MINIMAL, STANDARD, DETAILED)
        'LOGGING_LEVEL': 'DETAILED',
        
        # Journalisation des consultations (lecture seule)
        'LOG_READ_ACCESS': False,
        
        # Signature électronique des rapports
        'SIGN_REPORTS': True,
        
        # Notification des actions sensibles
        'NOTIFY_ON_SENSITIVE_ACTIONS': True,
        'NOTIFICATION_EMAIL': 'accounting-alerts@example.com'
    }
}
```

## Conclusion

Les mécanismes d'audit et de validation du module de comptabilité assurent l'intégrité, la traçabilité et la fiabilité des données financières. Ils permettent de répondre aux exigences légales et réglementaires tout en offrant une sécurité et une transparence optimales pour les opérations comptables.

Pour plus d'informations sur l'utilisation pratique de ces fonctionnalités, consultez le [Guide d'utilisation](./user_guide.md). Pour des informations sur l'extension de ces mécanismes, consultez le [Guide de développement](./development.md).
