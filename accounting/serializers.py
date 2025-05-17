from rest_framework import serializers
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


class AccountingClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountingClass
        fields = '__all__'


class AccountingChapterSerializer(serializers.ModelSerializer):
    accounting_class_details = AccountingClassSerializer(source='accounting_class', read_only=True)
    
    class Meta:
        model = AccountingChapter
        fields = '__all__'


class AccountingSectionSerializer(serializers.ModelSerializer):
    chapter_details = AccountingChapterSerializer(source='chapter', read_only=True)
    
    class Meta:
        model = AccountingSection
        fields = '__all__'


class GeneralLedgerAccountSerializer(serializers.ModelSerializer):
    section_details = AccountingSectionSerializer(source='section', read_only=True)
    
    class Meta:
        model = GeneralLedgerAccount
        fields = '__all__'
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['class_code'] = instance.class_code
        representation['chapter_code'] = instance.chapter_code
        representation['section_code'] = instance.section_code
        return representation


class FiscalYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = FiscalYear
        fields = '__all__'


class AccountingTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountingType
        fields = '__all__'


class AccountingJournalSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountingJournal
        fields = '__all__'


class AccountingEntryLineSerializer(serializers.ModelSerializer):
    account_details = GeneralLedgerAccountSerializer(source='account', read_only=True)
    auxiliary_account_type_details = serializers.SerializerMethodField()
    client_account_type_details = serializers.SerializerMethodField()
    reconciliation_type_details = serializers.SerializerMethodField()
    payer_type_details = serializers.SerializerMethodField()
    pricing_type_details = serializers.SerializerMethodField()
    municipality_details = serializers.SerializerMethodField()
    
    class Meta:
        model = AccountingEntryLine
        fields = '__all__'
    
    def get_auxiliary_account_type_details(self, obj):
        if (obj.auxiliary_account_type):
            return {
                'id': obj.auxiliary_account_type.id,
                'code': obj.auxiliary_account_type.code,
                'name': obj.auxiliary_account_type.name
            }
        return None
    
    def get_client_account_type_details(self, obj):
        if (obj.client_account_type):
            return {
                'id': obj.client_account_type.id,
                'code': obj.client_account_type.code,
                'name': obj.client_account_type.name
            }
        return None
    
    def get_reconciliation_type_details(self, obj):
        if (obj.reconciliation_type):
            return {
                'id': obj.reconciliation_type.id,
                'code': obj.reconciliation_type.code,
                'name': obj.reconciliation_type.name
            }
        return None
    
    def get_payer_type_details(self, obj):
        if (obj.payer_type):
            return {
                'id': obj.payer_type.id,
                'code': obj.payer_type.code,
                'name': obj.payer_type.name
            }
        return None
    
    def get_pricing_type_details(self, obj):
        if (obj.pricing_type):
            return {
                'id': obj.pricing_type.id,
                'code': obj.pricing_type.code,
                'name': obj.pricing_type.name
            }
        return None
    
    def get_municipality_details(self, obj):
        if (obj.municipality):
            return {
                'id': obj.municipality.id,
                'insee_code': obj.municipality.insee_code,
                'name': obj.municipality.name,
                'postal_code': obj.municipality.postal_code
            }
        return None


# Reference data serializers
class ClientAccountTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientAccountType
        fields = '__all__'


class AccountingEntryTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountingEntryType
        fields = '__all__'


class EngagementTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EngagementType
        fields = '__all__'


class ReconciliationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReconciliationType
        fields = '__all__'


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = '__all__'


class ServiceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceType
        fields = '__all__'


class PricingTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PricingType
        fields = '__all__'


class PayerTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayerType
        fields = '__all__'


class MunicipalitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Municipality
        fields = '__all__'


class AccountingEntrySerializer(serializers.ModelSerializer):
    journal_details = AccountingJournalSerializer(source='journal', read_only=True)
    fiscal_year_details = FiscalYearSerializer(source='fiscal_year', read_only=True)
    lines = AccountingEntryLineSerializer(many=True, read_only=True)
    total_debit = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    total_credit = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    is_balanced = serializers.BooleanField(read_only=True)
    entry_type_details = AccountingEntryTypeSerializer(source='entry_type', read_only=True)
    engagement_type_details = EngagementTypeSerializer(source='engagement_type', read_only=True)
    activity_details = ActivitySerializer(source='activity', read_only=True)
    service_type_details = ServiceTypeSerializer(source='service_type', read_only=True)
    
    class Meta:
        model = AccountingEntry
        fields = '__all__'


class AccountingEntryCreateUpdateSerializer(serializers.ModelSerializer):
    lines = AccountingEntryLineSerializer(many=True)
    
    class Meta:
        model = AccountingEntry
        fields = '__all__'
    
    def create(self, validated_data):
        lines_data = validated_data.pop('lines')
        accounting_entry = AccountingEntry.objects.create(**validated_data)
        
        for i, line_data in enumerate(lines_data):
            line_data['line_number'] = i + 1
            AccountingEntryLine.objects.create(entry=accounting_entry, **line_data)
        
        return accounting_entry
    
    def update(self, instance, validated_data):
        lines_data = validated_data.pop('lines', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if lines_data is not None:
            instance.lines.all().delete()
            for i, line_data in enumerate(lines_data):
                line_data['line_number'] = i + 1
                AccountingEntryLine.objects.create(entry=instance, **line_data)
        
        return instance
