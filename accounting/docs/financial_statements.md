# États Financiers du Module de Comptabilité

Ce document détaille les fonctionnalités de génération d'états financiers disponibles dans le module de comptabilité du projet P2P Ivalua.

## Vue d'ensemble

Le module de comptabilité permet de générer plusieurs types d'états financiers standards, conformes aux exigences du Plan Comptable Général (PCG) français et aux pratiques recommandées par les cabinets d'audit des Big 4.

Les états financiers disponibles sont :

1. **Grand Livre** : Journal chronologique détaillé de toutes les écritures par compte
2. **Balance Générale** : Synthèse des soldes débiteurs et créditeurs de tous les comptes
3. **Bilan** : État de la situation financière à une date donnée (actif/passif)
4. **Compte de Résultat** : Synthèse des produits et charges d'une période

## Architecture technique

Les états financiers sont générés par un framework extensible défini dans le module `utils/financial_statements.py`. Ce framework utilise une architecture orientée objet avec des classes spécialisées pour chaque type d'état financier.

### Classe de base

```python
class BaseFinancialReport:
    """Classe de base pour tous les rapports financiers."""
    
    def __init__(self, fiscal_year, start_date=None, end_date=None, **kwargs):
        """
        Initialise un rapport financier.
        
        Args:
            fiscal_year: L'exercice fiscal concerné
            start_date: Date de début optionnelle (par défaut: début de l'exercice)
            end_date: Date de fin optionnelle (par défaut: fin de l'exercice ou aujourd'hui)
            **kwargs: Paramètres supplémentaires spécifiques au rapport
        """
        self.fiscal_year = fiscal_year
        self.start_date = start_date or fiscal_year.start_date
        self.end_date = end_date or (
            fiscal_year.end_date if fiscal_year.is_closed else date.today()
        )
        self.params = kwargs
    
    def generate(self):
        """
        Génère le rapport financier.
        
        Cette méthode doit être implémentée par les sous-classes.
        
        Returns:
            dict: Les données du rapport
        """
        raise NotImplementedError("Subclasses must implement generate()")
    
    def export_pdf(self, output_path=None):
        """Exporte le rapport au format PDF."""
        report_data = self.generate()
        # Logique d'export PDF...
        
    def export_excel(self, output_path=None):
        """Exporte le rapport au format Excel."""
        report_data = self.generate()
        # Logique d'export Excel...
        
    def export_csv(self, output_path=None):
        """Exporte le rapport au format CSV."""
        report_data = self.generate()
        # Logique d'export CSV...
```

## Grand Livre

Le Grand Livre est le rapport détaillé de toutes les écritures comptables, classées par compte. Il permet de suivre l'historique complet des opérations pour chaque compte.

### Fonctionnalités

- Filtrage par compte ou plage de comptes
- Filtrage par période
- Filtrage par journal
- Affichage des soldes d'ouverture, des mouvements et des soldes de clôture
- Calcul des soldes cumulés après chaque écriture

### Implémentation

```python
class GeneralLedgerReport(BaseFinancialReport):
    """Rapport du Grand Livre."""
    
    def __init__(self, fiscal_year, start_date=None, end_date=None, account=None, journal=None):
        """
        Initialise un rapport de Grand Livre.
        
        Args:
            fiscal_year: L'exercice fiscal
            start_date: Date de début (optionnelle)
            end_date: Date de fin (optionnelle)
            account: Compte spécifique (optionnel)
            journal: Journal spécifique (optionnel)
        """
        super().__init__(fiscal_year, start_date, end_date)
        self.account = account
        self.journal = journal
    
    def generate(self):
        """Génère le rapport du Grand Livre."""
        # Récupération des écritures
        entries_query = AccountingEntryLine.objects.filter(
            entry__fiscal_year=self.fiscal_year,
            entry__date__gte=self.start_date,
            entry__date__lte=self.end_date,
            entry__status=AccountingEntry.POSTED
        ).select_related('entry', 'account')
        
        if self.account:
            entries_query = entries_query.filter(account=self.account)
        
        if self.journal:
            entries_query = entries_query.filter(entry__journal=self.journal)
        
        # Organisation par compte
        accounts_data = {}
        
        # Calcul des soldes d'ouverture
        # ...
        
        # Organisation des écritures par compte
        for line in entries_query.order_by('account', 'entry__date', 'entry__id'):
            account_number = line.account.account_number
            
            if account_number not in accounts_data:
                accounts_data[account_number] = {
                    'account': line.account,
                    'opening_balance': self._calculate_opening_balance(line.account),
                    'entries': [],
                    'closing_balance': 0,
                }
            
            accounts_data[account_number]['entries'].append({
                'date': line.entry.date,
                'reference': line.entry.reference,
                'description': line.description or line.entry.description,
                'debit': line.debit_amount,
                'credit': line.credit_amount,
                'journal': line.entry.journal.code,
            })
        
        # Calcul des soldes de clôture
        for account_number, data in accounts_data.items():
            opening_balance = data['opening_balance']
            total_debit = sum(entry['debit'] for entry in data['entries'])
            total_credit = sum(entry['credit'] for entry in data['entries'])
            
            data['total_debit'] = total_debit
            data['total_credit'] = total_credit
            data['closing_balance'] = opening_balance + (total_debit - total_credit)
        
        return {
            'title': 'Grand Livre',
            'fiscal_year': self.fiscal_year.name,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'generated_at': timezone.now(),
            'accounts': accounts_data,
        }
```

### Exemple de sortie

```json
{
  "title": "Grand Livre",
  "fiscal_year": "EXERCICE 2023",
  "start_date": "2023-01-01",
  "end_date": "2023-03-31",
  "generated_at": "2023-04-05T14:22:16Z",
  "accounts": {
    "411000": {
      "account": {
        "account_number": "411000",
        "short_name": "Clients",
        "full_name": "Clients - ventes de biens ou prestations de services"
      },
      "opening_balance": 0.0,
      "entries": [
        {
          "date": "2023-01-15",
          "reference": "VTE2023001",
          "description": "Facture client ABC",
          "debit": 1200.0,
          "credit": 0.0,
          "journal": "VEN"
        },
        {
          "date": "2023-02-28",
          "reference": "ENC2023001",
          "description": "Règlement facture VTE2023001",
          "debit": 0.0,
          "credit": 1200.0,
          "journal": "BAN"
        }
      ],
      "total_debit": 1200.0,
      "total_credit": 1200.0,
      "closing_balance": 0.0
    },
    "707000": {
      "account": {
        "account_number": "707000",
        "short_name": "Ventes de marchandises",
        "full_name": "Ventes de marchandises"
      },
      "opening_balance": 0.0,
      "entries": [
        {
          "date": "2023-01-15",
          "reference": "VTE2023001",
          "description": "Facture client ABC - Vente HT",
          "debit": 0.0,
          "credit": 1000.0,
          "journal": "VEN"
        }
      ],
      "total_debit": 0.0,
      "total_credit": 1000.0,
      "closing_balance": -1000.0
    }
  }
}
```

## Balance Générale

La Balance Générale est un état récapitulatif des soldes de tous les comptes à une date donnée. Elle permet de vérifier l'équilibre global du système comptable.

### Fonctionnalités

- Filtrage par niveau de détail (compte, section, chapitre, classe)
- Option pour inclure ou exclure les comptes à solde nul
- Calcul des totaux par classe comptable
- Vérification automatique de l'équilibre global

### Implémentation

```python
class TrialBalanceReport(BaseFinancialReport):
    """Rapport de la Balance Générale."""
    
    LEVEL_ACCOUNT = 'account'
    LEVEL_SECTION = 'section'
    LEVEL_CHAPTER = 'chapter'
    LEVEL_CLASS = 'class'
    
    def __init__(self, fiscal_year, as_of_date=None, level=LEVEL_ACCOUNT, include_zero_balances=False):
        """
        Initialise un rapport de Balance.
        
        Args:
            fiscal_year: L'exercice fiscal
            as_of_date: Date d'arrêté (optionnelle, par défaut: aujourd'hui)
            level: Niveau de détail (account, section, chapter, class)
            include_zero_balances: Inclure les comptes à solde nul
        """
        super().__init__(fiscal_year, fiscal_year.start_date, as_of_date or date.today())
        self.level = level
        self.include_zero_balances = include_zero_balances
    
    def generate(self):
        """Génère le rapport de Balance."""
        # Récupération des soldes d'ouverture
        opening_balances = self._calculate_opening_balances()
        
        # Récupération des mouvements de la période
        period_movements = self._calculate_period_movements()
        
        # Calcul des soldes finaux
        balances = []
        totals = {
            'opening_debit': Decimal('0.00'),
            'opening_credit': Decimal('0.00'),
            'period_debit': Decimal('0.00'),
            'period_credit': Decimal('0.00'),
            'closing_debit': Decimal('0.00'),
            'closing_credit': Decimal('0.00'),
        }
        
        # Organisation des données selon le niveau demandé
        if self.level == self.LEVEL_ACCOUNT:
            accounts = GeneralLedgerAccount.objects.all()
            for account in accounts:
                account_number = account.account_number
                
                opening_debit = opening_balances.get(account_number, {}).get('debit', Decimal('0.00'))
                opening_credit = opening_balances.get(account_number, {}).get('credit', Decimal('0.00'))
                
                period_debit = period_movements.get(account_number, {}).get('debit', Decimal('0.00'))
                period_credit = period_movements.get(account_number, {}).get('credit', Decimal('0.00'))
                
                # Calcul des soldes de clôture
                closing_balance = (opening_debit - opening_credit) + (period_debit - period_credit)
                closing_debit = closing_balance if closing_balance > 0 else Decimal('0.00')
                closing_credit = -closing_balance if closing_balance < 0 else Decimal('0.00')
                
                # Vérifier si on inclut les comptes à solde nul
                if not self.include_zero_balances and closing_debit == 0 and closing_credit == 0 and period_debit == 0 and period_credit == 0:
                    continue
                
                balances.append({
                    'account_number': account_number,
                    'account_name': account.short_name,
                    'opening_debit': opening_debit,
                    'opening_credit': opening_credit,
                    'period_debit': period_debit,
                    'period_credit': period_credit,
                    'closing_debit': closing_debit,
                    'closing_credit': closing_credit,
                })
                
                # Mise à jour des totaux
                totals['opening_debit'] += opening_debit
                totals['opening_credit'] += opening_credit
                totals['period_debit'] += period_debit
                totals['period_credit'] += period_credit
                totals['closing_debit'] += closing_debit
                totals['closing_credit'] += closing_credit
        
        # Regroupement par section, chapitre ou classe si nécessaire
        # ...
        
        return {
            'title': 'Balance Générale',
            'fiscal_year': self.fiscal_year.name,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'level': self.level,
            'generated_at': timezone.now(),
            'balances': balances,
            'totals': totals,
        }
    
    def _calculate_opening_balances(self):
        """Calcule les soldes d'ouverture pour tous les comptes."""
        # ...
    
    def _calculate_period_movements(self):
        """Calcule les mouvements de la période pour tous les comptes."""
        # ...
```

### Exemple de sortie

```json
{
  "title": "Balance Générale",
  "fiscal_year": "EXERCICE 2023",
  "start_date": "2023-01-01",
  "end_date": "2023-03-31",
  "level": "account",
  "generated_at": "2023-04-05T14:30:22Z",
  "balances": [
    {
      "account_number": "101000",
      "account_name": "Capital",
      "opening_debit": "0.00",
      "opening_credit": "50000.00",
      "period_debit": "0.00",
      "period_credit": "0.00",
      "closing_debit": "0.00",
      "closing_credit": "50000.00"
    },
    {
      "account_number": "401000",
      "account_name": "Fournisseurs",
      "opening_debit": "0.00",
      "opening_credit": "5000.00",
      "period_debit": "3000.00",
      "period_credit": "4000.00",
      "closing_debit": "0.00",
      "closing_credit": "6000.00"
    },
    {
      "account_number": "411000",
      "account_name": "Clients",
      "opening_debit": "7000.00",
      "opening_credit": "0.00",
      "period_debit": "15000.00",
      "period_credit": "12000.00",
      "closing_debit": "10000.00",
      "closing_credit": "0.00"
    }
  ],
  "totals": {
    "opening_debit": "75000.00",
    "opening_credit": "75000.00",
    "period_debit": "125000.00",
    "period_credit": "125000.00",
    "closing_debit": "145000.00",
    "closing_credit": "145000.00"
  }
}
```

## Bilan

Le Bilan est un état financier qui présente la situation patrimoniale d'une entité à une date donnée, en distinguant l'Actif (emplois/ressources) et le Passif (origines des ressources).

### Fonctionnalités

- Présentation standard selon le PCG français
- Option pour un format détaillé ou simplifié
- Calcul automatique des totaux et sous-totaux
- Comparaison avec l'exercice précédent (optionnel)

### Implémentation

```python
class BalanceSheetReport(BaseFinancialReport):
    """Rapport du Bilan."""
    
    FORMAT_STANDARD = 'standard'
    FORMAT_DETAILED = 'detailed'
    
    def __init__(self, fiscal_year, as_of_date=None, format=FORMAT_STANDARD, compare_with_previous=False):
        """
        Initialise un rapport de Bilan.
        
        Args:
            fiscal_year: L'exercice fiscal
            as_of_date: Date d'arrêté (optionnelle)
            format: Format du rapport (standard ou détaillé)
            compare_with_previous: Comparer avec l'exercice précédent
        """
        super().__init__(fiscal_year, fiscal_year.start_date, as_of_date or date.today())
        self.format = format
        self.compare_with_previous = compare_with_previous
    
    def generate(self):
        """Génère le rapport de Bilan."""
        # Structure du bilan selon le PCG
        structure = {
            'assets': {
                'fixed_assets': {
                    'intangible': self._get_accounts_balance(['20%', '280%']),
                    'tangible': self._get_accounts_balance(['21%', '22%', '23%', '281%', '282%']),
                    'financial': self._get_accounts_balance(['26%', '27%', '296%', '297%']),
                },
                'current_assets': {
                    'inventory': self._get_accounts_balance(['3%', '39%']),
                    'receivables': self._get_accounts_balance(['41%', '42%', '43%', '44%', '45%', '46%', '47%', '49%']),
                    'investments': self._get_accounts_balance(['50%', '59%']),
                    'cash': self._get_accounts_balance(['51%', '52%', '53%', '54%', '58%']),
                },
                'accruals': self._get_accounts_balance(['48%']),
            },
            'liabilities': {
                'equity': {
                    'capital': self._get_accounts_balance(['10%']),
                    'reserves': self._get_accounts_balance(['11%']),
                    'retained_earnings': self._get_accounts_balance(['12%']),
                    'net_income': self._calculate_net_income(),
                },
                'provisions': self._get_accounts_balance(['15%']),
                'liabilities': {
                    'loans': self._get_accounts_balance(['16%']),
                    'payables': self._get_accounts_balance(['40%', '41%', '42%', '43%', '44%', '45%', '46%', '47%']),
                },
                'accruals': self._get_accounts_balance(['48%']),
            }
        }
        
        # Calcul des totaux et sous-totaux
        self._calculate_totals(structure)
        
        # Comparaison avec l'exercice précédent si demandé
        previous_year_data = None
        if self.compare_with_previous:
            previous_year = FiscalYear.objects.filter(year=self.fiscal_year.year - 1).first()
            if previous_year:
                previous_report = BalanceSheetReport(
                    previous_year,
                    previous_year.end_date,
                    self.format
                )
                previous_year_data = previous_report.generate()
        
        return {
            'title': 'Bilan',
            'fiscal_year': self.fiscal_year.name,
            'as_of_date': self.end_date,
            'format': self.format,
            'generated_at': timezone.now(),
            'structure': structure,
            'previous_year': previous_year_data,
        }
    
    def _get_accounts_balance(self, account_patterns):
        """Calcule le solde des comptes correspondant aux motifs spécifiés."""
        # ...
    
    def _calculate_net_income(self):
        """Calcule le résultat net (classe 7 - classe 6)."""
        # ...
    
    def _calculate_totals(self, structure):
        """Calcule les totaux et sous-totaux du bilan."""
        # ...
```

### Exemple de sortie

```json
{
  "title": "Bilan",
  "fiscal_year": "EXERCICE 2023",
  "as_of_date": "2023-03-31",
  "format": "standard",
  "generated_at": "2023-04-05T14:45:18Z",
  "structure": {
    "assets": {
      "fixed_assets": {
        "intangible": 25000.00,
        "tangible": 150000.00,
        "financial": 10000.00,
        "total": 185000.00
      },
      "current_assets": {
        "inventory": 45000.00,
        "receivables": 75000.00,
        "investments": 0.00,
        "cash": 65000.00,
        "total": 185000.00
      },
      "accruals": 5000.00,
      "total": 375000.00
    },
    "liabilities": {
      "equity": {
        "capital": 150000.00,
        "reserves": 30000.00,
        "retained_earnings": 25000.00,
        "net_income": 45000.00,
        "total": 250000.00
      },
      "provisions": 15000.00,
      "liabilities": {
        "loans": 50000.00,
        "payables": 55000.00,
        "total": 105000.00
      },
      "accruals": 5000.00,
      "total": 375000.00
    }
  }
}
```

## Compte de Résultat

Le Compte de Résultat est un état financier qui récapitule l'ensemble des charges et des produits d'une entité sur une période donnée, permettant de déterminer le résultat net (bénéfice ou perte).

### Fonctionnalités

- Présentation par nature ou par fonction (selon le PCG)
- Option pour un format détaillé ou simplifié
- Calcul automatique des résultats intermédiaires
- Comparaison avec l'exercice précédent (optionnel)

### Implémentation

```python
class IncomeStatementReport(BaseFinancialReport):
    """Rapport du Compte de Résultat."""
    
    FORMAT_STANDARD = 'standard'
    FORMAT_DETAILED = 'detailed'
    PRESENTATION_BY_NATURE = 'by_nature'
    PRESENTATION_BY_FUNCTION = 'by_function'
    
    def __init__(self, fiscal_year, start_date=None, end_date=None, format=FORMAT_STANDARD, 
                 presentation=PRESENTATION_BY_NATURE, compare_with_previous=False):
        """
        Initialise un rapport de Compte de Résultat.
        
        Args:
            fiscal_year: L'exercice fiscal
            start_date: Date de début (optionnelle)
            end_date: Date de fin (optionnelle)
            format: Format du rapport (standard ou détaillé)
            presentation: Type de présentation (par nature ou par fonction)
            compare_with_previous: Comparer avec la même période de l'exercice précédent
        """
        super().__init__(fiscal_year, start_date, end_date)
        self.format = format
        self.presentation = presentation
        self.compare_with_previous = compare_with_previous
    
    def generate(self):
        """Génère le rapport de Compte de Résultat."""
        if self.presentation == self.PRESENTATION_BY_NATURE:
            structure = self._generate_by_nature()
        else:
            structure = self._generate_by_function()
        
        # Comparaison avec l'exercice précédent si demandé
        previous_period_data = None
        if self.compare_with_previous:
            previous_year = FiscalYear.objects.filter(year=self.fiscal_year.year - 1).first()
            if previous_year:
                previous_start = self.start_date.replace(year=self.start_date.year - 1)
                previous_end = self.end_date.replace(year=self.end_date.year - 1)
                
                # Ajustement si l'année précédente est déjà clôturée
                if previous_end > previous_year.end_date:
                    previous_end = previous_year.end_date
                
                previous_report = IncomeStatementReport(
                    previous_year,
                    previous_start,
                    previous_end,
                    self.format,
                    self.presentation
                )
                previous_period_data = previous_report.generate()
        
        return {
            'title': 'Compte de Résultat',
            'fiscal_year': self.fiscal_year.name,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'format': self.format,
            'presentation': self.presentation,
            'generated_at': timezone.now(),
            'structure': structure,
            'previous_period': previous_period_data,
        }
    
    def _generate_by_nature(self):
        """Génère le compte de résultat par nature."""
        structure = {
            'operating_income': {
                'sales': self._get_accounts_balance(['70%']),
                'stored_production': self._get_accounts_balance(['71%']),
                'capitalized_production': self._get_accounts_balance(['72%']),
                'operating_subsidies': self._get_accounts_balance(['74%']),
                'other_operating_income': self._get_accounts_balance(['75%', '781%', '791%']),
                'total': 0
            },
            'operating_expenses': {
                'purchases': self._get_accounts_balance(['60%']),
                'inventory_change': self._get_accounts_balance(['603%']),
                'external_services': self._get_accounts_balance(['61%', '62%']),
                'taxes': self._get_accounts_balance(['63%']),
                'personnel': self._get_accounts_balance(['64%']),
                'depreciation_amortization': self._get_accounts_balance(['681%']),
                'other_operating_expenses': self._get_accounts_balance(['65%']),
                'total': 0
            },
            'financial_income': self._get_accounts_balance(['76%', '786%', '796%']),
            'financial_expenses': self._get_accounts_balance(['66%', '686%']),
            'extraordinary_income': self._get_accounts_balance(['77%', '787%', '797%']),
            'extraordinary_expenses': self._get_accounts_balance(['67%', '687%']),
            'income_tax': self._get_accounts_balance(['69%']),
        }
        
        # Calcul des totaux et résultats
        structure['operating_income']['total'] = sum(v for k, v in structure['operating_income'].items() if k != 'total')
        structure['operating_expenses']['total'] = sum(v for k, v in structure['operating_expenses'].items() if k != 'total')
        
        structure['operating_result'] = structure['operating_income']['total'] - structure['operating_expenses']['total']
        structure['financial_result'] = structure['financial_income'] - structure['financial_expenses']
        structure['extraordinary_result'] = structure['extraordinary_income'] - structure['extraordinary_expenses']
        
        structure['net_income_before_tax'] = structure['operating_result'] + structure['financial_result'] + structure['extraordinary_result']
        structure['net_income'] = structure['net_income_before_tax'] - structure['income_tax']
        
        return structure
    
    def _generate_by_function(self):
        """Génère le compte de résultat par fonction."""
        # Implémentation similaire mais avec regroupement par fonction
        # ...
    
    def _get_accounts_balance(self, account_patterns):
        """Calcule le solde des comptes correspondant aux motifs spécifiés pour la période."""
        # ...
```

### Exemple de sortie

```json
{
  "title": "Compte de Résultat",
  "fiscal_year": "EXERCICE 2023",
  "start_date": "2023-01-01",
  "end_date": "2023-03-31",
  "format": "standard",
  "presentation": "by_nature",
  "generated_at": "2023-04-05T15:00:42Z",
  "structure": {
    "operating_income": {
      "sales": 250000.00,
      "stored_production": 0.00,
      "capitalized_production": 0.00,
      "operating_subsidies": 15000.00,
      "other_operating_income": 5000.00,
      "total": 270000.00
    },
    "operating_expenses": {
      "purchases": 120000.00,
      "inventory_change": -5000.00,
      "external_services": 35000.00,
      "taxes": 10000.00,
      "personnel": 50000.00,
      "depreciation_amortization": 15000.00,
      "other_operating_expenses": 5000.00,
      "total": 230000.00
    },
    "operating_result": 40000.00,
    "financial_income": 2000.00,
    "financial_expenses": 5000.00,
    "financial_result": -3000.00,
    "extraordinary_income": 10000.00,
    "extraordinary_expenses": 2000.00,
    "extraordinary_result": 8000.00,
    "income_tax": 15000.00,
    "net_income_before_tax": 45000.00,
    "net_income": 30000.00
  }
}
```

## Export des états financiers

Le module permet d'exporter les états financiers dans différents formats pour faciliter leur distribution et leur analyse.

### Formats d'export disponibles

- **PDF** : Format de document portable, idéal pour l'impression et la distribution
- **Excel** : Format tableur, idéal pour l'analyse et les manipulations supplémentaires
- **CSV** : Format texte simple, idéal pour l'intégration avec d'autres systèmes
- **JSON** : Format de données structuré, idéal pour l'intégration avec des applications web

### Personnalisation des exports

Les exports peuvent être personnalisés selon plusieurs critères :

- En-têtes et pieds de page (logo, informations de l'entreprise)
- Niveaux de détail (complet, résumé)
- Mise en forme (couleurs, styles)
- Langue (français, anglais)

### Exemple d'utilisation

```python
# Génération d'un bilan au format PDF
report = BalanceSheetReport(
    fiscal_year=FiscalYear.objects.get(year=2023),
    as_of_date=date(2023, 3, 31),
    format='detailed'
)
report.export_pdf('/path/to/bilan_2023_q1.pdf')

# Génération d'une balance au format Excel
report = TrialBalanceReport(
    fiscal_year=FiscalYear.objects.get(year=2023),
    as_of_date=date(2023, 3, 31),
    level='account'
)
report.export_excel('/path/to/balance_2023_q1.xlsx')
```

## Configuration et personnalisation

Le système d'états financiers peut être configuré et personnalisé selon les besoins spécifiques de l'organisation.

### Configuration dans settings.py

```python
# Configuration du module d'états financiers
ACCOUNTING = {
    # Autres paramètres...
    'FINANCIAL_STATEMENTS': {
        # Format par défaut pour les exports PDF
        'DEFAULT_PDF_TEMPLATE': 'accounting/reports/templates/default.html',
        
        # En-tête et pied de page
        'REPORT_HEADER': {
            'LOGO': '/path/to/logo.png',
            'COMPANY_NAME': 'P2P Ivalua',
            'ADDRESS': '123 rue de la Comptabilité, 75000 Paris'
        },
        
        # Couleurs et styles
        'STYLES': {
            'PRIMARY_COLOR': '#336699',
            'SECONDARY_COLOR': '#CCDDEE',
            'FONT_FAMILY': 'Arial, sans-serif'
        },
        
        # Options avancées
        'DECIMAL_PLACES': 2,
        'THOUSAND_SEPARATOR': ' ',
        'DECIMAL_SEPARATOR': ',',
        'CURRENCY_SYMBOL': '€',
        
        # Comportement
        'AUTO_SAVE_REPORTS': True,
        'REPORTS_DIRECTORY': '/path/to/saved/reports/',
    }
}
```

### Création de rapports personnalisés

Le framework peut être étendu pour créer des rapports personnalisés spécifiques aux besoins de l'organisation :

```python
from accounting.utils.financial_statements import BaseFinancialReport

class CustomAnalyticalReport(BaseFinancialReport):
    """Rapport analytique personnalisé."""
    
    def __init__(self, fiscal_year, dimension, **kwargs):
        """
        Initialise un rapport analytique personnalisé.
        
        Args:
            fiscal_year: L'exercice fiscal
            dimension: La dimension analytique (ex: 'project', 'department')
            **kwargs: Paramètres supplémentaires
        """
        super().__init__(fiscal_year, **kwargs)
        self.dimension = dimension
    
    def generate(self):
        """Génère le rapport personnalisé."""
        # Logique de génération du rapport analytique
        # ...
        
        return {
            'title': f'Rapport analytique par {self.dimension}',
            'fiscal_year': self.fiscal_year.name,
            'dimension': self.dimension,
            'data': dimension_data,
            'generated_at': timezone.now(),
        }
```

## Conclusion

Le module d'états financiers du système de comptabilité offre une solution complète et flexible pour générer les rapports comptables et financiers nécessaires à la gestion et à la conformité réglementaire.

Grâce à son architecture extensible, il peut être adapté pour répondre aux besoins spécifiques de différentes organisations tout en maintenant la cohérence et la fiabilité des données financières.

Pour plus d'informations sur l'utilisation de ces fonctionnalités dans l'interface utilisateur, consultez le [Guide d'utilisation](./user_guide.md). Pour des détails sur l'extension de ces fonctionnalités, consultez le [Guide de développement](./development.md).
