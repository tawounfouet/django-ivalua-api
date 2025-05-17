from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
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
from .models.reference_data import (
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


class AccountingChapterInline(admin.TabularInline):
    model = AccountingChapter
    extra = 0
    show_change_link = True


@admin.register(AccountingClass)
class AccountingClassAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'created_at', 'updated_at')
    search_fields = ('code', 'name')
    inlines = [AccountingChapterInline]


class AccountingSectionInline(admin.TabularInline):
    model = AccountingSection
    extra = 0
    show_change_link = True


@admin.register(AccountingChapter)
class AccountingChapterAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'accounting_class', 'created_at', 'updated_at')
    list_filter = ('accounting_class',)
    search_fields = ('code', 'name')
    inlines = [AccountingSectionInline]


class GeneralLedgerAccountInline(admin.TabularInline):
    model = GeneralLedgerAccount
    extra = 0
    show_change_link = True
    fields = ('account_number', 'short_name', 'full_name', 'is_balance_sheet')


@admin.register(AccountingSection)
class AccountingSectionAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'chapter', 'created_at', 'updated_at')
    list_filter = ('chapter', 'chapter__accounting_class')
    search_fields = ('code', 'name')
    inlines = [GeneralLedgerAccountInline]


@admin.register(GeneralLedgerAccount)
class GeneralLedgerAccountAdmin(admin.ModelAdmin):
    list_display = ('account_number', 'short_name', 'full_name', 'section', 'is_balance_sheet', 'created_at', 'updated_at')
    list_filter = ('is_balance_sheet', 'section', 'section__chapter', 'section__chapter__accounting_class')
    search_fields = ('account_number', 'short_name', 'full_name')
    fieldsets = (
        (None, {
            'fields': ('account_number', 'short_name', 'full_name', 'section', 'is_balance_sheet')
        }),
        (_('Additional Information'), {
            'fields': ('budget_account_code', 'recovery_status', 'financial_statement_group'),
            'classes': ('collapse',),
        }),
        (_('Metadata'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(FiscalYear)
class FiscalYearAdmin(admin.ModelAdmin):
    list_display = ('year', 'name', 'start_date', 'end_date', 'is_current', 'is_closed', 'created_at', 'updated_at')
    list_filter = ('is_current', 'is_closed')
    search_fields = ('year', 'name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(AccountingType)
class AccountingTypeAdmin(admin.ModelAdmin):
    list_display = ('code', 'short_name', 'full_name', 'nature', 'created_at', 'updated_at')
    list_filter = ('nature',)
    search_fields = ('code', 'short_name', 'full_name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(AccountingJournal)
class AccountingJournalAdmin(admin.ModelAdmin):
    list_display = ('code', 'short_name', 'name', 'is_opening_balance', 'company_code', 'created_at', 'updated_at')
    list_filter = ('is_opening_balance', 'company_code')
    search_fields = ('code', 'short_name', 'name', 'id_journal')
    readonly_fields = ('created_at', 'updated_at')


class AccountingEntryLineInline(admin.TabularInline):
    model = AccountingEntryLine
    extra = 0
    fields = ('line_number', 'account', 'is_debit', 'amount', 'description', 'auxiliary_account_type', 'auxiliary_account_id')
    readonly_fields = ('line_number',)


@admin.register(AccountingEntry)
class AccountingEntryAdmin(admin.ModelAdmin):
    list_display = ('entry_number', 'journal', 'fiscal_year', 'entry_date', 'status', 'total_debit', 'total_credit', 'is_balanced', 'created_at', 'updated_at')
    list_filter = ('status', 'journal', 'fiscal_year', 'entry_date', 'is_opening_balance', 'is_closing_entry', 'is_reversing_entry')
    search_fields = ('entry_number', 'reference', 'source_document', 'source_document_id')
    readonly_fields = ('created_at', 'updated_at', 'total_debit', 'total_credit', 'is_balanced')
    inlines = [AccountingEntryLineInline]
    fieldsets = (
        (None, {
            'fields': ('entry_number', 'journal', 'fiscal_year', 'entry_date', 'status', 'reference')
        }),
        (_('Additional Information'), {
            'fields': ('is_opening_balance', 'is_closing_entry', 'is_reversing_entry', 'original_entry', 'source_document', 'source_document_id', 'posting_date'),
        }),
        (_('Balances'), {
            'fields': ('total_debit', 'total_credit', 'is_balanced'),
        }),
        (_('Metadata'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    actions = ['validate_entries', 'post_to_ledger', 'cancel_entries']
    
    def validate_entries(self, request, queryset):
        for entry in queryset.filter(status='draft'):
            if entry.is_balanced:
                entry.status = 'validated'
                entry.save()
    validate_entries.short_description = _("Validate selected entries")
    
    def post_to_ledger(self, request, queryset):
        for entry in queryset.filter(status='validated'):
            if entry.is_balanced:
                entry.status = 'posted'
                entry.posting_date = timezone.now().date()
                entry.save()
    post_to_ledger.short_description = _("Post selected entries to ledger")
    
    def cancel_entries(self, request, queryset):
        for entry in queryset.filter(status__in=['draft', 'validated']):
            entry.status = 'cancelled'
            entry.save()
    cancel_entries.short_description = _("Cancel selected entries")


# Reference data admin classes
@admin.register(ClientAccountType)
class ClientAccountTypeAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'created_at', 'updated_at')
    search_fields = ('code', 'name')
    list_filter = ('created_at',)


@admin.register(AccountingEntryType)
class AccountingEntryTypeAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'indicator_code', 'indicator_name', 'created_at', 'updated_at')
    search_fields = ('code', 'name', 'indicator_code', 'indicator_name')
    list_filter = ('created_at',)


@admin.register(EngagementType)
class EngagementTypeAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'created_at', 'updated_at')
    search_fields = ('code', 'name')
    list_filter = ('created_at',)


@admin.register(ReconciliationType)
class ReconciliationTypeAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'created_at', 'updated_at')
    search_fields = ('code', 'name')
    list_filter = ('created_at',)


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'created_at', 'updated_at')
    search_fields = ('code', 'name')
    list_filter = ('created_at',)


@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ('id_service_type', 'code', 'name', 'category_code', 'category_name', 'created_at', 'updated_at')
    search_fields = ('id_service_type', 'code', 'name', 'category_code', 'category_name')
    list_filter = ('category_code', 'created_at')


@admin.register(PricingType)
class PricingTypeAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'created_at', 'updated_at')
    search_fields = ('code', 'name')
    list_filter = ('created_at',)


@admin.register(PayerType)
class PayerTypeAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'created_at', 'updated_at')
    search_fields = ('code', 'name')
    list_filter = ('created_at',)


@admin.register(Municipality)
class MunicipalityAdmin(admin.ModelAdmin):
    list_display = ('insee_code', 'name', 'postal_code', 'created_at', 'updated_at')
    search_fields = ('insee_code', 'name', 'postal_code')
    list_filter = ('created_at', 'postal_code')
