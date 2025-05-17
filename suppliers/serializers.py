from rest_framework import serializers
from .models import (
    Supplier, SupplierAddress, BankingInformation, Contact,
    ContactRole, SupplierPartner, SupplierRole
)
from django.utils.translation import gettext_lazy as _


class SupplierAddressSerializer(serializers.ModelSerializer):
    """Serializer for the SupplierAddress model."""
    
    class Meta:
        model = SupplierAddress
        fields = ('adr1', 'adr2', 'adr3', 'zip', 'city')


class BankingInformationSerializer(serializers.ModelSerializer):
    """Serializer for the BankingInformation model."""
    
    class Meta:
        model = BankingInformation
        fields = (
            'id', 'international_pay_id', 'account_number', 'bank_code',
            'counter_code', 'rib_key', 'bban', 'iban', 'bic', 'country_code',
            'bank_label', 'creation_account_date', 'modification_account_date'
        )
        read_only_fields = ('creation_account_date', 'modification_account_date')


class ContactRoleSerializer(serializers.ModelSerializer):
    """Serializer for the ContactRole model."""
    
    class Meta:
        model = ContactRole
        fields = ('id', 'code', 'label')


class ContactSerializer(serializers.ModelSerializer):
    """Serializer for the Contact model."""
    roles = ContactRoleSerializer(many=True, read_only=True)
    
    class Meta:
        model = Contact
        fields = ('id', 'is_internal', 'first_name', 'last_name', 'email', 'login', 'roles')


class SupplierPartnerSerializer(serializers.ModelSerializer):
    """Serializer for the SupplierPartner model."""
    
    class Meta:
        model = SupplierPartner
        fields = ('id', 'orga_level', 'orga_node', 'num_part', 'status')


class SupplierRoleSerializer(serializers.ModelSerializer):
    """Serializer for the SupplierRole model."""
    
    class Meta:
        model = SupplierRole
        fields = (
            'id', 'orga_level', 'orga_node', 'role_code', 'role_label',
            'begin_date', 'end_date', 'status'
        )


class SupplierSerializer(serializers.ModelSerializer):
    """
    Basic serializer for listing suppliers.
    """
    class Meta:
        model = Supplier
        fields = (
            'id', 'code', 'supplier_name', 'legal_name', 'nat_id', 
            'nat_id_type', 'status', 'creation_system_date'
        )


class SupplierDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for retrieving a single supplier with all related data.
    """
    address = SupplierAddressSerializer(read_only=True)
    banking_informations = BankingInformationSerializer(many=True, read_only=True)
    contacts = ContactSerializer(many=True, read_only=True)
    partners = SupplierPartnerSerializer(many=True, read_only=True)
    roles = SupplierRoleSerializer(many=True, read_only=True)
    
    class Meta:
        model = Supplier
        fields = '__all__'


class SupplierCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new supplier.
    """
    address = SupplierAddressSerializer(required=False)
    
    class Meta:
        model = Supplier
        exclude = ('created_at', 'updated_at', 'deleted_system_date', 
                  'modification_system_date', 'latest_modification_date')
    
    def create(self, validated_data):
        address_data = validated_data.pop('address', None)
        
        # Create the supplier
        supplier = Supplier.objects.create(**validated_data)
        
        # Create address if provided
        if address_data:
            SupplierAddress.objects.create(supplier=supplier, **address_data)
            
        return supplier


class SupplierUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating an existing supplier.
    """
    address = SupplierAddressSerializer(required=False)
    
    class Meta:
        model = Supplier
        exclude = ('created_at', 'updated_at')
    
    def update(self, instance, validated_data):
        address_data = validated_data.pop('address', None)
        
        # Update supplier fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update address if provided
        if address_data:
            address, created = SupplierAddress.objects.get_or_create(supplier=instance)
            for attr, value in address_data.items():
                setattr(address, attr, value)
            address.save()
            
        return instance