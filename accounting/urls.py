from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AccountingClassViewSet,
    AccountingChapterViewSet,
    AccountingSectionViewSet,
    GeneralLedgerAccountViewSet,
    FiscalYearViewSet,
    AccountingTypeViewSet,
    AccountingJournalViewSet,
    AccountingEntryViewSet,
    AccountingReportViewSet,
    ClientAccountTypeViewSet,
    AccountingEntryTypeViewSet,
    EngagementTypeViewSet,
    ReconciliationTypeViewSet,
    ActivityViewSet,
    ServiceTypeViewSet,
    PricingTypeViewSet,
    PayerTypeViewSet,
    MunicipalityViewSet
)

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'accounting-classes', AccountingClassViewSet)
router.register(r'accounting-chapters', AccountingChapterViewSet)
router.register(r'accounting-sections', AccountingSectionViewSet)
router.register(r'general-ledger-accounts', GeneralLedgerAccountViewSet)
router.register(r'fiscal-years', FiscalYearViewSet)
router.register(r'accounting-types', AccountingTypeViewSet)
router.register(r'accounting-journals', AccountingJournalViewSet)
router.register(r'accounting-entries', AccountingEntryViewSet)
router.register(r'reports', AccountingReportViewSet, basename='reports')

# Reference data endpoints
router.register(r'client-account-types', ClientAccountTypeViewSet)
router.register(r'accounting-entry-types', AccountingEntryTypeViewSet)
router.register(r'engagement-types', EngagementTypeViewSet)
router.register(r'reconciliation-types', ReconciliationTypeViewSet)
router.register(r'activities', ActivityViewSet)
router.register(r'service-types', ServiceTypeViewSet)
router.register(r'pricing-types', PricingTypeViewSet)
router.register(r'payer-types', PayerTypeViewSet)
router.register(r'municipalities', MunicipalityViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
