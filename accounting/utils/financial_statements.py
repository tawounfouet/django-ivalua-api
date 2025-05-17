from django.db import models
from django.db.models import Sum, Case, When, Q, F, Value, DecimalField
from django.db.models.functions import Coalesce
from decimal import Decimal
from .models import GeneralLedgerAccount, AccountingEntry, AccountingEntryLine


def calculate_account_balance(account, fiscal_year=None, as_of_date=None, journal_code=None):
    """
    Calculate the balance of a general ledger account.
    
    Parameters:
    - account: GeneralLedgerAccount instance or account_number
    - fiscal_year: Optional FiscalYear instance to filter entries by fiscal year
    - as_of_date: Optional date to calculate balance as of a specific date
    - journal_code: Optional journal code to filter entries by journal
    
    Returns:
    - Decimal: The account balance (positive for debit balance, negative for credit balance)
    """
    if isinstance(account, str):
        try:
            account = GeneralLedgerAccount.objects.get(account_number=account)
        except GeneralLedgerAccount.DoesNotExist:
            return Decimal('0.00')
    
    # Start with all entry lines for this account
    query = AccountingEntryLine.objects.filter(account=account)
    
    # Filter by fiscal year if provided
    if fiscal_year:
        query = query.filter(entry__fiscal_year=fiscal_year)
    
    # Filter by date if provided
    if as_of_date:
        query = query.filter(entry__entry_date__lte=as_of_date)
    
    # Filter by journal if provided
    if journal_code:
        query = query.filter(entry__journal__code=journal_code)
    
    # Only include posted entries
    query = query.filter(entry__status='posted')
    
    # Calculate balance
    result = query.aggregate(
        balance=Sum(
            Case(
                When(is_debit=True, then=F('amount')),
                When(is_debit=False, then=-F('amount')),
                default=Value(0),
                output_field=DecimalField()
            )
        )
    )
    
    return result['balance'] or Decimal('0.00')


def generate_trial_balance(fiscal_year, as_of_date=None, include_zero_balances=False):
    """
    Generate a trial balance for a given fiscal year.
    
    Parameters:
    - fiscal_year: FiscalYear instance
    - as_of_date: Optional date to calculate balance as of a specific date
    - include_zero_balances: Whether to include accounts with zero balance
    
    Returns:
    - Dict with debit and credit totals, and a list of accounts with their balances
    """
    accounts = GeneralLedgerAccount.objects.all().order_by('account_number')
    trial_balance = []
    total_debit = Decimal('0.00')
    total_credit = Decimal('0.00')
    
    for account in accounts:
        balance = calculate_account_balance(account, fiscal_year, as_of_date)
        
        if balance == Decimal('0.00') and not include_zero_balances:
            continue
        
        debit_amount = balance if balance > Decimal('0.00') else Decimal('0.00')
        credit_amount = -balance if balance < Decimal('0.00') else Decimal('0.00')
        
        total_debit += debit_amount
        total_credit += credit_amount
        
        trial_balance.append({
            'account_number': account.account_number,
            'account_name': account.full_name,
            'debit': debit_amount,
            'credit': credit_amount
        })
    
    return {
        'total_debit': total_debit,
        'total_credit': total_credit,
        'accounts': trial_balance,
        'is_balanced': total_debit == total_credit
    }


def generate_general_ledger(fiscal_year, account=None, start_date=None, end_date=None):
    """
    Generate a general ledger report for a given fiscal year.
    
    Parameters:
    - fiscal_year: FiscalYear instance
    - account: Optional GeneralLedgerAccount instance or account_number to filter by account
    - start_date: Optional start date for the report
    - end_date: Optional end date for the report
    
    Returns:
    - Dict with list of entries and their details
    """
    # Start with entries from the fiscal year
    entries = AccountingEntry.objects.filter(
        fiscal_year=fiscal_year,
        status='posted'
    ).order_by('entry_date', 'entry_number')
    
    # Apply date filters if provided
    if start_date:
        entries = entries.filter(entry_date__gte=start_date)
    if end_date:
        entries = entries.filter(entry_date__lte=end_date)
    
    # Get all lines for these entries
    lines = AccountingEntryLine.objects.filter(
        entry__in=entries
    ).select_related('entry', 'account')
    
    # If account is provided, filter lines by account
    if account:
        if isinstance(account, str):
            try:
                account = GeneralLedgerAccount.objects.get(account_number=account)
            except GeneralLedgerAccount.DoesNotExist:
                return {'entries': []}
        lines = lines.filter(account=account)
    
    # Organize by entry
    gl_entries = {}
    for line in lines:
        entry_id = line.entry.id
        if entry_id not in gl_entries:
            gl_entries[entry_id] = {
                'entry_number': line.entry.entry_number,
                'entry_date': line.entry.entry_date,
                'journal_code': line.entry.journal.code,
                'description': line.entry.reference,
                'lines': []
            }
        
        gl_entries[entry_id]['lines'].append({
            'account_number': line.account.account_number,
            'account_name': line.account.short_name,
            'is_debit': line.is_debit,
            'amount': line.amount,
            'description': line.description or '',
            'line_number': line.line_number
        })
    
    return {'entries': list(gl_entries.values())}


def generate_income_statement(fiscal_year, as_of_date=None):
    """
    Generate an income statement for a given fiscal year.
    
    Parameters:
    - fiscal_year: FiscalYear instance
    - as_of_date: Optional date to calculate statement as of a specific date
    
    Returns:
    - Dict with revenue, expenses, and net income figures
    """
    # Get revenue accounts (class 7 in French accounting)
    revenue_accounts = GeneralLedgerAccount.objects.filter(account_number__startswith='7')
    
    # Get expense accounts (class 6 in French accounting)
    expense_accounts = GeneralLedgerAccount.objects.filter(account_number__startswith='6')
    
    # Calculate total revenue
    total_revenue = Decimal('0.00')
    revenues = []
    for account in revenue_accounts:
        # Revenue accounts normally have credit balances, so we negate the result
        balance = -calculate_account_balance(account, fiscal_year, as_of_date)
        if balance != Decimal('0.00'):
            revenues.append({
                'account_number': account.account_number,
                'account_name': account.full_name,
                'amount': balance
            })
            total_revenue += balance
    
    # Calculate total expenses
    total_expenses = Decimal('0.00')
    expenses = []
    for account in expense_accounts:
        # Expense accounts normally have debit balances
        balance = calculate_account_balance(account, fiscal_year, as_of_date)
        if balance != Decimal('0.00'):
            expenses.append({
                'account_number': account.account_number,
                'account_name': account.full_name,
                'amount': balance
            })
            total_expenses += balance
    
    # Calculate net income
    net_income = total_revenue - total_expenses
    
    return {
        'revenues': sorted(revenues, key=lambda x: x['account_number']),
        'expenses': sorted(expenses, key=lambda x: x['account_number']),
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'net_income': net_income
    }


def generate_balance_sheet(fiscal_year, as_of_date=None):
    """
    Generate a balance sheet for a given fiscal year.
    
    Parameters:
    - fiscal_year: FiscalYear instance
    - as_of_date: Optional date to calculate balance sheet as of a specific date
    
    Returns:
    - Dict with assets, liabilities, and equity figures
    """
    # Get asset accounts (class 1-5 in French accounting)
    asset_accounts = GeneralLedgerAccount.objects.filter(
        Q(account_number__startswith='1') |
        Q(account_number__startswith='2') |
        Q(account_number__startswith='3') |
        Q(account_number__startswith='4') |
        Q(account_number__startswith='5'),
        is_balance_sheet=True
    )
    
    # Get liability accounts (class 1, 4, 5 in French accounting)
    liability_accounts = GeneralLedgerAccount.objects.filter(
        Q(account_number__startswith='1') |
        Q(account_number__startswith='4') |
        Q(account_number__startswith='5'),
        is_balance_sheet=True
    )
    
    # Get equity accounts (class 1 in French accounting)
    equity_accounts = GeneralLedgerAccount.objects.filter(
        account_number__startswith='1',
        is_balance_sheet=True
    )
    
    # Calculate total assets
    total_assets = Decimal('0.00')
    assets = []
    for account in asset_accounts:
        # Asset accounts normally have debit balances
        balance = calculate_account_balance(account, fiscal_year, as_of_date)
        if balance > Decimal('0.00'):
            assets.append({
                'account_number': account.account_number,
                'account_name': account.full_name,
                'amount': balance
            })
            total_assets += balance
    
    # Calculate total liabilities
    total_liabilities = Decimal('0.00')
    liabilities = []
    for account in liability_accounts:
        # Liability accounts normally have credit balances, so we negate the result
        balance = -calculate_account_balance(account, fiscal_year, as_of_date)
        if balance > Decimal('0.00'):
            liabilities.append({
                'account_number': account.account_number,
                'account_name': account.full_name,
                'amount': balance
            })
            total_liabilities += balance
    
    # Calculate total equity
    total_equity = Decimal('0.00')
    equity = []
    for account in equity_accounts:
        # Equity accounts normally have credit balances, so we negate the result
        balance = -calculate_account_balance(account, fiscal_year, as_of_date)
        if balance != Decimal('0.00'):
            equity.append({
                'account_number': account.account_number,
                'account_name': account.full_name,
                'amount': balance
            })
            total_equity += balance
    
    # Calculate retained earnings if not as of the end of the fiscal year
    income_statement = generate_income_statement(fiscal_year, as_of_date)
    retained_earnings = income_statement['net_income']
    
    # Total equity including current year earnings
    total_equity_with_earnings = total_equity + retained_earnings
    
    return {
        'assets': sorted(assets, key=lambda x: x['account_number']),
        'liabilities': sorted(liabilities, key=lambda x: x['account_number']),
        'equity': sorted(equity, key=lambda x: x['account_number']),
        'total_assets': total_assets,
        'total_liabilities': total_liabilities,
        'total_equity': total_equity,
        'retained_earnings': retained_earnings,
        'total_equity_with_earnings': total_equity_with_earnings,
        'is_balanced': total_assets == (total_liabilities + total_equity_with_earnings)
    }
