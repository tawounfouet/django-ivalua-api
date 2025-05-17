# Modèles de Données du Module de Comptabilité

Ce document décrit en détail tous les modèles de données utilisés dans le module de comptabilité du projet P2P Ivalua.

## Structure hiérarchique du Plan Comptable Général (PCG)

Le Plan Comptable Général est structuré de manière hiérarchique, du plus général au plus spécifique :

### AccountingClass

Représente les classes comptables (1 à 9) du PCG.

| Champ | Type | Description |
|-------|------|-------------|
| code | CharField | Code de la classe (1 chiffre de 1 à 9) |
| name | CharField | Nom de la classe (ex: "Comptes de capitaux") |

```python
class AccountingClass(BaseModel):
    """Représente une classe comptable du PCG (1-9)."""
    code = models.CharField(_("code"), max_length=1, unique=True)
    name = models.CharField(_("name"), max_length=255)
    
    def __str__(self):
        return f"{self.code} - {self.name}"
```

### AccountingChapter

Représente les chapitres comptables (subdivisions des classes).

| Champ | Type | Description |
|-------|------|-------------|
| code | CharField | Code du chapitre (2 chiffres, ex: 10, 11) |
| name | CharField | Nom du chapitre (ex: "Capital et réserves") |
| accounting_class | ForeignKey | Référence à la classe comptable parente |

```python
class AccountingChapter(BaseModel):
    """Représente un chapitre comptable du PCG (subdivision d'une classe)."""
    code = models.CharField(_("code"), max_length=2, unique=True)
    name = models.CharField(_("name"), max_length=255)
    accounting_class = models.ForeignKey(
        AccountingClass,
        on_delete=models.CASCADE,
        related_name="chapters",
        verbose_name=_("accounting class")
    )
    
    def __str__(self):
        return f"{self.code} - {self.name}"
```

### AccountingSection

Représente les sections comptables (subdivisions des chapitres).

| Champ | Type | Description |
|-------|------|-------------|
| code | CharField | Code de la section (3 chiffres, ex: 101, 106) |
| name | CharField | Nom de la section |
| chapter | ForeignKey | Référence au chapitre comptable parent |

```python
class AccountingSection(BaseModel):
    """Représente une section comptable du PCG (subdivision d'un chapitre)."""
    code = models.CharField(_("code"), max_length=3, unique=True)
    name = models.CharField(_("name"), max_length=255)
    chapter = models.ForeignKey(
        AccountingChapter,
        on_delete=models.CASCADE,
        related_name="sections",
        verbose_name=_("chapter")
    )
    
    def __str__(self):
        return f"{self.code} - {self.name}"
```

### GeneralLedgerAccount

Représente les comptes du Grand Livre comptable.

| Champ | Type | Description |
|-------|------|-------------|
| account_number | CharField | Numéro de compte complet |
| short_name | CharField | Nom abrégé du compte |
| full_name | CharField | Nom complet du compte |
| section | ForeignKey | Section comptable parente |
| is_balance_sheet | BooleanField | Indique si le compte apparaît au bilan (True) ou au compte de résultat (False) |
| budget_account_code | CharField | Code du compte budgétaire associé |
| recovery_status | CharField | Statut de récupération du compte |
| financial_statement_group | CharField | Groupe d'états financiers |

```python
class GeneralLedgerAccount(BaseModel):
    """Représente un compte du Grand Livre (compte détaillé du PCG)."""
    account_number = models.CharField(_("account number"), max_length=20, unique=True)
    short_name = models.CharField(_("short name"), max_length=50)
    full_name = models.TextField(_("full name"))
    section = models.ForeignKey(
        AccountingSection,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="accounts",
        verbose_name=_("section")
    )
    is_balance_sheet = models.BooleanField(
        _("is balance sheet account"),
        default=True,
        help_text=_("If True, this account appears in the balance sheet. If False, it appears in the income statement.")
    )
    budget_account_code = models.CharField(_("budget account code"), max_length=20, null=True, blank=True)
    recovery_status = models.CharField(_("recovery status"), max_length=50, null=True, blank=True)
    financial_statement_group = models.CharField(_("financial statement group"), max_length=50, null=True, blank=True)
    
    def __str__(self):
        return f"{self.account_number} - {self.short_name}"
```

## Bases comptables

### FiscalYear

Représente un exercice fiscal/comptable.

| Champ | Type | Description |
|-------|------|-------------|
| year | PositiveIntegerField | Année de l'exercice |
| name | CharField | Nom de l'exercice |
| start_date | DateField | Date de début |
| end_date | DateField | Date de fin |
| is_closed | BooleanField | Indique si l'exercice est clôturé |
| is_current | BooleanField | Indique s'il s'agit de l'exercice en cours |

```python
class FiscalYear(BaseModel):
    """Représente un exercice fiscal/comptable."""
    year = models.PositiveIntegerField(_("year"), unique=True)
    name = models.CharField(_("name"), max_length=100)
    start_date = models.DateField(_("start date"))
    end_date = models.DateField(_("end date"))
    is_closed = models.BooleanField(_("is closed"), default=False)
    is_current = models.BooleanField(_("is current"), default=False)
    
    def __str__(self):
        return self.name
```

### AccountingType

Représente un type de comptabilité (générale, auxiliaire, analytique, etc.).

| Champ | Type | Description |
|-------|------|-------------|
| code | CharField | Code du type |
| short_name | CharField | Nom abrégé |
| full_name | CharField | Nom complet |
| nature | CharField | Nature de la comptabilité |

```python
class AccountingType(BaseModel):
    """Représente un type de comptabilité (générale, auxiliaire, etc.)."""
    code = models.CharField(_("code"), max_length=10, unique=True)
    short_name = models.CharField(_("short name"), max_length=50)
    full_name = models.CharField(_("full name"), max_length=255)
    nature = models.CharField(_("nature"), max_length=100, null=True, blank=True)
    
    def __str__(self):
        return self.short_name
```

### AccountingJournal

Représente un journal comptable.

| Champ | Type | Description |
|-------|------|-------------|
| id_journal | CharField | Identifiant unique du journal |
| code | CharField | Code du journal |
| short_name | CharField | Nom abrégé |
| name | CharField | Nom complet |
| is_opening_balance | BooleanField | Indique s'il s'agit d'un journal d'à-nouveaux |
| company_code | CharField | Code de la société associée |

```python
class AccountingJournal(BaseModel):
    """Représente un journal comptable."""
    id_journal = models.CharField(_("journal ID"), max_length=20, unique=True)
    code = models.CharField(_("code"), max_length=10)
    short_name = models.CharField(_("short name"), max_length=50)
    name = models.CharField(_("name"), max_length=255)
    is_opening_balance = models.BooleanField(
        _("is opening balance journal"),
        default=False,
        help_text=_("If True, this journal is used for opening balance entries.")
    )
    company_code = models.CharField(_("company code"), max_length=10, null=True, blank=True)
    
    def __str__(self):
        return self.short_name
```

## Écritures comptables

### AccountingEntry

Représente une écriture comptable.

| Champ | Type | Description |
|-------|------|-------------|
| reference | CharField | Référence unique de l'écriture |
| date | DateField | Date de l'écriture |
| journal | ForeignKey | Journal comptable associé |
| fiscal_year | ForeignKey | Exercice fiscal associé |
| description | TextField | Description de l'écriture |
| status | CharField | Statut de l'écriture (brouillon, validé, comptabilisé, annulé) |
| created_by | ForeignKey | Utilisateur ayant créé l'écriture |
| validated_by | ForeignKey | Utilisateur ayant validé l'écriture |
| validated_date | DateTimeField | Date de validation |
| posted_by | ForeignKey | Utilisateur ayant comptabilisé l'écriture |
| posted_date | DateTimeField | Date de comptabilisation |
| canceled_by | ForeignKey | Utilisateur ayant annulé l'écriture |
| canceled_date | DateTimeField | Date d'annulation |
| original_entry | ForeignKey | Écriture d'origine (pour les extournes) |
| municipality | ForeignKey | Municipalité concernée |
| accounting_type | ForeignKey | Type de comptabilité |
| accounting_entry_type | ForeignKey | Type d'écriture |
| engagement_type | ForeignKey | Type d'engagement |

```python
class AccountingEntry(BaseModel):
    """Représente une écriture comptable."""
    DRAFT = 'draft'
    VALIDATED = 'validated'
    POSTED = 'posted'
    CANCELED = 'canceled'
    
    STATUS_CHOICES = [
        (DRAFT, _("Draft")),
        (VALIDATED, _("Validated")),
        (POSTED, _("Posted")),
        (CANCELED, _("Canceled")),
    ]
    
    reference = models.CharField(_("reference"), max_length=50, unique=True)
    date = models.DateField(_("date"))
    journal = models.ForeignKey(
        AccountingJournal,
        on_delete=models.PROTECT,
        related_name="entries",
        verbose_name=_("journal")
    )
    fiscal_year = models.ForeignKey(
        FiscalYear,
        on_delete=models.PROTECT,
        related_name="entries",
        verbose_name=_("fiscal year")
    )
    description = models.TextField(_("description"))
    status = models.CharField(
        _("status"),
        max_length=10,
        choices=STATUS_CHOICES,
        default=DRAFT
    )
    
    # Champs de traçabilité
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_entries",
        verbose_name=_("created by")
    )
    validated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name="validated_entries",
        verbose_name=_("validated by")
    )
    validated_date = models.DateTimeField(_("validated date"), null=True, blank=True)
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name="posted_entries",
        verbose_name=_("posted by")
    )
    posted_date = models.DateTimeField(_("posted date"), null=True, blank=True)
    canceled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name="canceled_entries",
        verbose_name=_("canceled by")
    )
    canceled_date = models.DateTimeField(_("canceled date"), null=True, blank=True)
    
    # Relations avec d'autres écritures
    original_entry = models.ForeignKey(
        'self',
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name="reversed_entries",
        verbose_name=_("original entry")
    )
    
    # Relations avec les données de référence
    municipality = models.ForeignKey(
        'Municipality',
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name="accounting_entries",
        verbose_name=_("municipality")
    )
    accounting_type = models.ForeignKey(
        AccountingType,
        on_delete=models.PROTECT,
        related_name="entries",
        verbose_name=_("accounting type")
    )
    accounting_entry_type = models.ForeignKey(
        'AccountingEntryType',
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name="entries",
        verbose_name=_("entry type")
    )
    engagement_type = models.ForeignKey(
        'EngagementType',
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name="entries",
        verbose_name=_("engagement type")
    )
    
    def __str__(self):
        return f"{self.reference} ({self.get_status_display()})"
    
    def is_balanced(self):
        """Vérifie si l'écriture est équilibrée (somme des débits = somme des crédits)."""
        total_debit = sum(line.debit_amount for line in self.lines.all())
        total_credit = sum(line.credit_amount for line in self.lines.all())
        return total_debit == total_credit
```

### AccountingEntryLine

Représente une ligne d'écriture comptable.

| Champ | Type | Description |
|-------|------|-------------|
| entry | ForeignKey | Écriture comptable parente |
| account | ForeignKey | Compte comptable associé |
| debit_amount | DecimalField | Montant au débit |
| credit_amount | DecimalField | Montant au crédit |
| description | TextField | Description de la ligne |
| line_number | PositiveIntegerField | Numéro de ligne |
| client_account_type | ForeignKey | Type de compte client |
| reconciliation_type | ForeignKey | Type de lettrage |
| payer_type | ForeignKey | Type de payeur |
| service_type | ForeignKey | Type de prestation |
| pricing_type | ForeignKey | Type de tarification |

```python
class AccountingEntryLine(BaseModel):
    """Représente une ligne d'écriture comptable."""
    entry = models.ForeignKey(
        AccountingEntry,
        on_delete=models.CASCADE,
        related_name="lines",
        verbose_name=_("accounting entry")
    )
    account = models.ForeignKey(
        GeneralLedgerAccount,
        on_delete=models.PROTECT,
        related_name="entry_lines",
        verbose_name=_("account")
    )
    debit_amount = models.DecimalField(
        _("debit amount"),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    credit_amount = models.DecimalField(
        _("credit amount"),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    description = models.TextField(_("description"), blank=True)
    line_number = models.PositiveIntegerField(_("line number"))
    
    # Relations avec les données de référence
    client_account_type = models.ForeignKey(
        'ClientAccountType',
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name="entry_lines",
        verbose_name=_("client account type")
    )
    reconciliation_type = models.ForeignKey(
        'ReconciliationType',
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name="entry_lines",
        verbose_name=_("reconciliation type")
    )
    payer_type = models.ForeignKey(
        'PayerType',
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name="entry_lines",
        verbose_name=_("payer type")
    )
    service_type = models.ForeignKey(
        'ServiceType',
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name="entry_lines",
        verbose_name=_("service type")
    )
    pricing_type = models.ForeignKey(
        'PricingType',
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name="entry_lines",
        verbose_name=_("pricing type")
    )
    
    class Meta:
        ordering = ['entry', 'line_number']
    
    def __str__(self):
        return f"{self.entry.reference} - Line {self.line_number}"
    
    def save(self, *args, **kwargs):
        # Vérifier que soit debit_amount soit credit_amount est égal à zéro
        if self.debit_amount > 0 and self.credit_amount > 0:
            raise ValidationError(_("A line cannot have both debit and credit amounts."))
        super().save(*args, **kwargs)
```

## Données de référence

### Municipality

Représente une municipalité (commune).

| Champ | Type | Description |
|-------|------|-------------|
| insee_code | CharField | Code INSEE de la commune |
| name | CharField | Nom de la commune |
| postal_code | CharField | Code postal |
| department_code | CharField | Code du département |
| region_code | CharField | Code de la région |

```python
class Municipality(BaseModel):
    """Représente une municipalité (commune)."""
    insee_code = models.CharField(_("INSEE code"), max_length=5, unique=True)
    name = models.CharField(_("name"), max_length=255)
    postal_code = models.CharField(_("postal code"), max_length=5)
    department_code = models.CharField(_("department code"), max_length=3)
    region_code = models.CharField(_("region code"), max_length=3)
    
    def __str__(self):
        return f"{self.name} ({self.insee_code})"
```

### AccountingEntryType

Représente un type d'écriture comptable.

| Champ | Type | Description |
|-------|------|-------------|
| code | CharField | Code du type d'écriture |
| name | CharField | Nom du type d'écriture |
| description | TextField | Description du type d'écriture |

```python
class AccountingEntryType(BaseModel):
    """Représente un type d'écriture comptable."""
    code = models.CharField(_("code"), max_length=10, unique=True)
    name = models.CharField(_("name"), max_length=100)
    description = models.TextField(_("description"), blank=True)
    
    def __str__(self):
        return self.name
```

### EngagementType

Représente un type d'engagement.

| Champ | Type | Description |
|-------|------|-------------|
| code | CharField | Code du type d'engagement |
| name | CharField | Nom du type d'engagement |
| description | TextField | Description du type d'engagement |

```python
class EngagementType(BaseModel):
    """Représente un type d'engagement."""
    code = models.CharField(_("code"), max_length=10, unique=True)
    name = models.CharField(_("name"), max_length=100)
    description = models.TextField(_("description"), blank=True)
    
    def __str__(self):
        return self.name
```

### ReconciliationType

Représente un type de lettrage pour la réconciliation des comptes.

| Champ | Type | Description |
|-------|------|-------------|
| code | CharField | Code du type de lettrage |
| name | CharField | Nom du type de lettrage |
| description | TextField | Description du type de lettrage |

```python
class ReconciliationType(BaseModel):
    """Représente un type de lettrage pour la réconciliation des comptes."""
    code = models.CharField(_("code"), max_length=10, unique=True)
    name = models.CharField(_("name"), max_length=100)
    description = models.TextField(_("description"), blank=True)
    
    def __str__(self):
        return self.name
```

### PayerType

Représente un type de payeur.

| Champ | Type | Description |
|-------|------|-------------|
| code | CharField | Code du type de payeur |
| name | CharField | Nom du type de payeur |
| description | TextField | Description du type de payeur |

```python
class PayerType(BaseModel):
    """Représente un type de payeur."""
    code = models.CharField(_("code"), max_length=10, unique=True)
    name = models.CharField(_("name"), max_length=100)
    description = models.TextField(_("description"), blank=True)
    
    def __str__(self):
        return self.name
```

### ServiceType

Représente un type de prestation.

| Champ | Type | Description |
|-------|------|-------------|
| code | CharField | Code du type de prestation |
| name | CharField | Nom du type de prestation |
| description | TextField | Description du type de prestation |

```python
class ServiceType(BaseModel):
    """Représente un type de prestation."""
    code = models.CharField(_("code"), max_length=10, unique=True)
    name = models.CharField(_("name"), max_length=100)
    description = models.TextField(_("description"), blank=True)
    
    def __str__(self):
        return self.name
```

### PricingType

Représente un type de tarification.

| Champ | Type | Description |
|-------|------|-------------|
| code | CharField | Code du type de tarification |
| name | CharField | Nom du type de tarification |
| description | TextField | Description du type de tarification |

```python
class PricingType(BaseModel):
    """Représente un type de tarification."""
    code = models.CharField(_("code"), max_length=10, unique=True)
    name = models.CharField(_("name"), max_length=100)
    description = models.TextField(_("description"), blank=True)
    
    def __str__(self):
        return self.name
```

### ClientAccountType

Représente un type de compte client.

| Champ | Type | Description |
|-------|------|-------------|
| code | CharField | Code du type de compte client |
| name | CharField | Nom du type de compte client |
| description | TextField | Description du type de compte client |

```python
class ClientAccountType(BaseModel):
    """Représente un type de compte client."""
    code = models.CharField(_("code"), max_length=10, unique=True)
    name = models.CharField(_("name"), max_length=100)
    description = models.TextField(_("description"), blank=True)
    
    def __str__(self):
        return self.name
```

## Héritage et structure commune

Tous les modèles héritent d'une classe de base qui fournit des champs communs :

```python
class BaseModel(models.Model):
    """Classe de base pour tous les modèles comptables."""
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)
    
    class Meta:
        abstract = True
```

## Modèle ER (Entity-Relationship)

Le diagramme ER complet du module de comptabilité est disponible dans le fichier `accounting/docs/diagrams/entity_relationship.png`.
