# apps/suppliers/tests/test_models.py
from django.test import TestCase
from django.core.exceptions import ValidationError
from suppliers.models import Supplier, SupplierAddress, BankingInformation
from django.utils import timezone
import datetime


class SupplierModelTest(TestCase):
    """Test suite for the Supplier model."""
    
    def setUp(self):
        """Set up test data."""
        self.valid_supplier_data = {
            'object_id': 1,
            'code': 'SUP000001',
            'supplier_name': 'Test Company',
            'legal_name': 'Test Company Legal Name',
            'creation_system_date': timezone.now().date(),
        }
        
    def test_create_supplier(self):
        """Test creating a valid supplier."""
        supplier = Supplier.objects.create(**self.valid_supplier_data)
        self.assertEqual(supplier.code, 'SUP000001')
        self.assertEqual(supplier.status, 'ini')
        
    def test_create_physical_person_supplier(self):
        """Test creating a supplier as a physical person."""
        data = self.valid_supplier_data.copy()
        data.update({
            'is_physical_person': True,
            'first_name': 'John',
            'last_name': 'Doe',
            'title': 'Mr.',
        })
        supplier = Supplier.objects.create(**data)
        self.assertTrue(supplier.is_physical_person)
        self.assertEqual(supplier.first_name, 'John')
        
    def test_validate_physical_person_without_names(self):
        """Test validation fails for physical person without names."""
        data = self.valid_supplier_data.copy()
        data['is_physical_person'] = True
        
        supplier = Supplier(**data)
        with self.assertRaises(ValidationError):
            supplier.full_clean()
            
    def test_validate_non_physical_person_with_names(self):
        """Test validation fails for non-physical person with personal info."""
        data = self.valid_supplier_data.copy()
        data.update({
            'is_physical_person': False,
            'first_name': 'John',
        })
        
        supplier = Supplier(**data)
        with self.assertRaises(ValidationError):
            supplier.full_clean()
            
    def test_siret_validation(self):
        """Test SIRET validation."""
        data = self.valid_supplier_data.copy()
        data.update({
            'nat_id_type': '01',  # SIRET
            'nat_id': '12345678901234',  # Valid 14 digits
        })
        
        supplier = Supplier.objects.create(**data)
        self.assertEqual(supplier.nat_id, '12345678901234')
        
        # Test invalid SIRET
        data['nat_id'] = '123456'  # Too short
        supplier = Supplier(**data)
        with self.assertRaises(ValidationError):
            supplier.full_clean()
            
    def test_auto_siren_from_siret(self):
        """Test automatic SIREN derivation from SIRET."""
        data = self.valid_supplier_data.copy()
        data['siret'] = '12345678901234'
        
        supplier = Supplier.objects.create(**data)
        self.assertEqual(supplier.siren, '123456789')
        
    def test_get_full_address(self):
        """Test getting full address."""
        supplier = Supplier.objects.create(**self.valid_supplier_data)
        
        # Without address
        self.assertEqual(supplier.get_full_address(), "")
        
        # With address
        SupplierAddress.objects.create(
            supplier=supplier,
            adr1='FR',
            adr2='123 Test Street',
            zip='75001',
            city='Paris'
        )
        
        self.assertEqual(
            supplier.get_full_address(),
            "FR, 123 Test Street, 75001, Paris"
        )


class BankingInformationTest(TestCase):
    """Test suite for the BankingInformation model."""
    
    def setUp(self):
        """Set up test data."""
        self.supplier = Supplier.objects.create(
            object_id=1,
            code='SUP000001',
            supplier_name='Test Company',
            legal_name='Test Company Legal Name',
            creation_system_date=timezone.now().date(),
        )
        
        self.valid_banking_data = {
            'supplier': self.supplier,
            'account_number': '00020419401',
            'iban': 'FR7610278021310002041940126',
            'bic': 'CMCIFR2A',
            'country_code': 'FR',
            'bank_label': 'Test Bank',
        }
        
    def test_create_banking_info(self):
        """Test creating valid banking information."""
        banking_info = BankingInformation.objects.create(**self.valid_banking_data)
        self.assertEqual(banking_info.iban, 'FR7610278021310002041940126')
        self.assertEqual(banking_info.supplier, self.supplier)
        
    def test_iban_validation(self):
        """Test IBAN validation."""
        # Valid IBAN
        banking_info = BankingInformation.objects.create(**self.valid_banking_data)
        self.assertTrue(banking_info.is_valid_iban())
        
        # Invalid format
        data = self.valid_banking_data.copy()
        data['iban'] = 'INVALID'
        banking_info = BankingInformation(**data)
        with self.assertRaises(ValidationError):
            banking_info.full_clean()
            
    def test_get_primary_banking_info(self):
        """Test getting primary banking info."""
        # No banking info yet
        self.assertIsNone(self.supplier.get_primary_banking_info())
        
        # Add banking info
        banking_info = BankingInformation.objects.create(**self.valid_banking_data)
        self.assertEqual(self.supplier.get_primary_banking_info(), banking_info)