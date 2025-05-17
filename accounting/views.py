from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from accounting.models import (
    AccountingClass,
    AccountingChapter,
    AccountingSection,
    GeneralLedgerAccount,
    FiscalYear,
    AccountingType,
    AccountingJournal,
    AccountingEntry,
    AccountingEntryLine
)
from accounting.models.reference_data import (
    ClientAccountType,
    AccountingEntryType,
    EngagementType,
    ReconciliationType,
    Activity,
    ServiceType,
    PricingType,
    PayerType,
    Municipality
)
from accounting.serializers import (
    AccountingClassSerializer,
    AccountingChapterSerializer,
    AccountingSectionSerializer,
    GeneralLedgerAccountSerializer,
    FiscalYearSerializer,
    AccountingTypeSerializer,
    AccountingJournalSerializer,
    AccountingEntrySerializer,
    AccountingEntryCreateUpdateSerializer,
    AccountingEntryLineSerializer,
    ClientAccountTypeSerializer,
    AccountingEntryTypeSerializer,
    EngagementTypeSerializer,
    ReconciliationTypeSerializer,
    ActivitySerializer,
    ServiceTypeSerializer,
    PricingTypeSerializer,
    PayerTypeSerializer,
    MunicipalitySerializer
)


class AccountingClassViewSet(viewsets.ModelViewSet):
    queryset = AccountingClass.objects.all()
    serializer_class = AccountingClassSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['code']
    search_fields = ['code', 'name']
    ordering_fields = ['code', 'name']
    ordering = ['code']


class AccountingChapterViewSet(viewsets.ModelViewSet):
    queryset = AccountingChapter.objects.all()
    serializer_class = AccountingChapterSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['code', 'accounting_class']
    search_fields = ['code', 'name']
    ordering_fields = ['code', 'name']
    ordering = ['code']


class AccountingSectionViewSet(viewsets.ModelViewSet):
    queryset = AccountingSection.objects.all()
    serializer_class = AccountingSectionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['code', 'chapter']
    search_fields = ['code', 'name']
    ordering_fields = ['code', 'name']
    ordering = ['code']


class GeneralLedgerAccountViewSet(viewsets.ModelViewSet):
    queryset = GeneralLedgerAccount.objects.all()
    serializer_class = GeneralLedgerAccountSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['account_number', 'section', 'is_balance_sheet']
    search_fields = ['account_number', 'short_name', 'full_name']
    ordering_fields = ['account_number', 'short_name']
    ordering = ['account_number']
    
    @action(detail=False, methods=['get'])
    def balance_sheet_accounts(self, request):
        """Get only balance sheet accounts."""
        accounts = self.queryset.filter(is_balance_sheet=True)
        page = self.paginate_queryset(accounts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(accounts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def income_statement_accounts(self, request):
        """Get only income statement accounts."""
        accounts = self.queryset.filter(is_balance_sheet=False)
        page = self.paginate_queryset(accounts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(accounts, many=True)
        return Response(serializer.data)


class FiscalYearViewSet(viewsets.ModelViewSet):
    queryset = FiscalYear.objects.all()
    serializer_class = FiscalYearSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['year', 'is_closed', 'is_current']
    search_fields = ['year', 'name']
    ordering_fields = ['year', 'name']
    ordering = ['-year']
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get the current fiscal year."""
        try:
            fiscal_year = FiscalYear.objects.get(is_current=True)
            serializer = self.get_serializer(fiscal_year)
            return Response(serializer.data)
        except FiscalYear.DoesNotExist:
            return Response(
                {"detail": "No current fiscal year found."},
                status=status.HTTP_404_NOT_FOUND
            )


class AccountingTypeViewSet(viewsets.ModelViewSet):
    queryset = AccountingType.objects.all()
    serializer_class = AccountingTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['code', 'nature']
    search_fields = ['code', 'short_name', 'full_name', 'nature']
    ordering_fields = ['code', 'short_name']
    ordering = ['code']


class AccountingJournalViewSet(viewsets.ModelViewSet):
    queryset = AccountingJournal.objects.all()
    serializer_class = AccountingJournalSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['code', 'is_opening_balance', 'company_code']
    search_fields = ['code', 'short_name', 'name']
    ordering_fields = ['code', 'name']
    ordering = ['code']


class AccountingEntryViewSet(viewsets.ModelViewSet):
    queryset = AccountingEntry.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['journal', 'fiscal_year', 'entry_date', 'status', 'is_opening_balance', 'is_closing_entry']
    search_fields = ['entry_number', 'reference', 'source_document', 'source_document_id']
    ordering_fields = ['entry_date', 'entry_number', 'posting_date']
    ordering = ['-entry_date', '-entry_number']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return AccountingEntryCreateUpdateSerializer
        return AccountingEntrySerializer
    
    @action(detail=True, methods=['post'])
    def validate(self, request, pk=None):
        """Validate an accounting entry."""
        entry = self.get_object()
        
        # Check if entry is balanced
        if not entry.is_balanced:
            return Response(
                {"detail": "Entry is not balanced. Total debits must equal total credits."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update status to validated
        entry.status = 'validated'
        entry.save()
        
        serializer = self.get_serializer(entry)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def post_to_ledger(self, request, pk=None):
        """Post a validated entry to the ledger."""
        entry = self.get_object()
        
        # Check if entry is in validated status
        if entry.status != 'validated':
            return Response(
                {"detail": "Only validated entries can be posted to the ledger."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update status to posted
        entry.status = 'posted'
        entry.posting_date = request.data.get('posting_date', None) or timezone.now().date()
        entry.save()
        
        serializer = self.get_serializer(entry)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an accounting entry."""
        entry = self.get_object()
        
        # Check if entry can be cancelled
        if entry.status == 'posted':
            return Response(
                {"detail": "Posted entries cannot be cancelled. Create a reversing entry instead."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update status to cancelled
        entry.status = 'cancelled'
        entry.save()
        
        serializer = self.get_serializer(entry)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def create_reversing_entry(self, request, pk=None):
        """Create a reversing entry for a posted entry."""
        original_entry = self.get_object()
        
        # Check if the entry is posted
        if original_entry.status != 'posted':
            return Response(
                {"detail": "Only posted entries can be reversed."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create reversing entry
        reversing_entry = AccountingEntry.objects.create(
            journal=original_entry.journal,
            fiscal_year=original_entry.fiscal_year,
            entry_date=request.data.get('entry_date', None) or timezone.now().date(),
            reference=f"Reversal of {original_entry.entry_number}: {original_entry.reference}",
            status='draft',
            is_reversing_entry=True,
            original_entry=original_entry,
            source_document=original_entry.source_document,
            source_document_id=original_entry.source_document_id
        )
        
        # Create reversed lines
        for line in original_entry.lines.all():
            AccountingEntryLine.objects.create(
                entry=reversing_entry,
                account=line.account,
                line_number=line.line_number,
                description=f"Reversal of {original_entry.entry_number}-{line.line_number}: {line.description}",
                is_debit=not line.is_debit,  # Reverse debit/credit
                amount=line.amount,
                auxiliary_account_type=line.auxiliary_account_type,
                auxiliary_account_id=line.auxiliary_account_id
            )
        
        serializer = self.get_serializer(reversing_entry)
        return Response(serializer.data)


# Reference data ViewSets
class ClientAccountTypeViewSet(viewsets.ModelViewSet):
    queryset = ClientAccountType.objects.all()
    serializer_class = ClientAccountTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['code']
    search_fields = ['code', 'name']
    ordering_fields = ['code', 'name']
    ordering = ['code']


class AccountingEntryTypeViewSet(viewsets.ModelViewSet):
    queryset = AccountingEntryType.objects.all()
    serializer_class = AccountingEntryTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['code']
    search_fields = ['code', 'name', 'indicator_code', 'indicator_name']
    ordering_fields = ['code', 'name']
    ordering = ['code']


class EngagementTypeViewSet(viewsets.ModelViewSet):
    queryset = EngagementType.objects.all()
    serializer_class = EngagementTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['code']
    search_fields = ['code', 'name']
    ordering_fields = ['code', 'name']
    ordering = ['code']


class ReconciliationTypeViewSet(viewsets.ModelViewSet):
    queryset = ReconciliationType.objects.all()
    serializer_class = ReconciliationTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['code']
    search_fields = ['code', 'name']
    ordering_fields = ['code', 'name']
    ordering = ['code']


class ActivityViewSet(viewsets.ModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['code']
    search_fields = ['code', 'name']
    ordering_fields = ['code', 'name']
    ordering = ['code']


class ServiceTypeViewSet(viewsets.ModelViewSet):
    queryset = ServiceType.objects.all()
    serializer_class = ServiceTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['code', 'id_service_type', 'category_code']
    search_fields = ['code', 'name', 'category_name']
    ordering_fields = ['code', 'name']
    ordering = ['code']


class PricingTypeViewSet(viewsets.ModelViewSet):
    queryset = PricingType.objects.all()
    serializer_class = PricingTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['code']
    search_fields = ['code', 'name']
    ordering_fields = ['code', 'name']
    ordering = ['code']


class PayerTypeViewSet(viewsets.ModelViewSet):
    queryset = PayerType.objects.all()
    serializer_class = PayerTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['code']
    search_fields = ['code', 'name']
    ordering_fields = ['code', 'name']
    ordering = ['code']


class MunicipalityViewSet(viewsets.ModelViewSet):
    queryset = Municipality.objects.all()
    serializer_class = MunicipalitySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['insee_code', 'postal_code']
    search_fields = ['insee_code', 'name', 'postal_code']
    ordering_fields = ['insee_code', 'name']
    ordering = ['insee_code']


class AccountingReportViewSet(viewsets.ViewSet):
    """
    ViewSet for generating accounting reports and financial statements.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def trial_balance(self, request):
        """Generate a trial balance report."""
        from accounting.utils.financial_statements import generate_trial_balance
        
        fiscal_year_id = request.query_params.get('fiscal_year')
        as_of_date = request.query_params.get('as_of_date')
        include_zero_balances = request.query_params.get('include_zero_balances', 'false').lower() == 'true'
        
        if not fiscal_year_id:
            return Response({"error": "fiscal_year parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            fiscal_year = FiscalYear.objects.get(pk=fiscal_year_id)
        except FiscalYear.DoesNotExist:
            return Response({"error": "Fiscal year not found"}, status=status.HTTP_404_NOT_FOUND)
        
        trial_balance = generate_trial_balance(fiscal_year, as_of_date, include_zero_balances)
        return Response(trial_balance)
    
    @action(detail=False, methods=['get'])
    def general_ledger(self, request):
        """Generate a general ledger report."""
        from accounting.utils.financial_statements import generate_general_ledger
        
        fiscal_year_id = request.query_params.get('fiscal_year')
        account_number = request.query_params.get('account')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not fiscal_year_id:
            return Response({"error": "fiscal_year parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            fiscal_year = FiscalYear.objects.get(pk=fiscal_year_id)
        except FiscalYear.DoesNotExist:
            return Response({"error": "Fiscal year not found"}, status=status.HTTP_404_NOT_FOUND)
        
        general_ledger = generate_general_ledger(fiscal_year, account_number, start_date, end_date)
        return Response(general_ledger)
    
    @action(detail=False, methods=['get'])
    def income_statement(self, request):
        """Generate an income statement."""
        from accounting.utils.financial_statements import generate_income_statement
        
        fiscal_year_id = request.query_params.get('fiscal_year')
        as_of_date = request.query_params.get('as_of_date')
        
        if not fiscal_year_id:
            return Response({"error": "fiscal_year parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            fiscal_year = FiscalYear.objects.get(pk=fiscal_year_id)
        except FiscalYear.DoesNotExist:
            return Response({"error": "Fiscal year not found"}, status=status.HTTP_404_NOT_FOUND)
        
        income_statement = generate_income_statement(fiscal_year, as_of_date)
        return Response(income_statement)
    
    @action(detail=False, methods=['get'])
    def balance_sheet(self, request):
        """Generate a balance sheet."""
        from accounting.utils.financial_statements import generate_balance_sheet
        
        fiscal_year_id = request.query_params.get('fiscal_year')
        as_of_date = request.query_params.get('as_of_date')
        
        if not fiscal_year_id:
            return Response({"error": "fiscal_year parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            fiscal_year = FiscalYear.objects.get(pk=fiscal_year_id)
        except FiscalYear.DoesNotExist:
            return Response({"error": "Fiscal year not found"}, status=status.HTTP_404_NOT_FOUND)
        
        balance_sheet = generate_balance_sheet(fiscal_year, as_of_date)
        return Response(balance_sheet)
    
    @action(detail=False, methods=['get'])
    def account_balance(self, request):
        """Get the balance for a specific account."""
        from accounting.utils.financial_statements import calculate_account_balance
        from decimal import Decimal
        
        account_number = request.query_params.get('account')
        fiscal_year_id = request.query_params.get('fiscal_year')
        as_of_date = request.query_params.get('as_of_date')
        journal_code = request.query_params.get('journal')
        
        if not account_number:
            return Response({"error": "account parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        fiscal_year = None
        if fiscal_year_id:
            try:
                fiscal_year = FiscalYear.objects.get(pk=fiscal_year_id)
            except FiscalYear.DoesNotExist:
                return Response({"error": "Fiscal year not found"}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            account = GeneralLedgerAccount.objects.get(account_number=account_number)
        except GeneralLedgerAccount.DoesNotExist:
            return Response({"error": "Account not found"}, status=status.HTTP_404_NOT_FOUND)
        
        balance = calculate_account_balance(account, fiscal_year, as_of_date, journal_code)
        
        return Response({
            'account_number': account_number,
            'account_name': account.full_name,
            'balance': balance,
            'is_debit': balance > Decimal('0.00'),
            'formatted_balance': f"{abs(balance):,.2f} {'DR' if balance > Decimal('0.00') else 'CR'}"
        })
