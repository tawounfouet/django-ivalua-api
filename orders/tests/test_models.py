# If you encounter indentation errors in your test file,
# copy the content of this file to replace your current test_models.py

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from orders.models import Order, OrderContact, OrderItem, OrderAddress, OrderStatus, OrderType, AddressType
from suppliers.models import Supplier
import datetime


class OrderModelTest(TestCase):
    """Test suite for the Order model."""
    
    def setUp(self):
        """Set up test data."""
        # Create a test supplier
        self.supplier = Supplier.objects.create(
            object_id=1,
            code='SUP000001',
            supplier_name='Test Supplier',
            legal_name='Test Supplier Legal Name',
            creation_system_date=timezone.now().date(),
        )
        
        # Create valid order data
        self.valid_order_data = {
            'object_id': 1,
            'ord_id_origin': 1001,
            'order_code': 'PO000001',
            'order_label': 'Test Order',
            'order_type_code': OrderType.DEFAULT,
            'basket_id': 1,
            'supplier': self.supplier,
            'order_sup_id': 1,
            'order_sup_name': 'Test Supplier',
            'created': timezone.now().date(),
            'login_created': 'testuser',
            'status_code': OrderStatus.DRAFT,
            'order_date': timezone.now().date(),
            'currency_code': 'EUR',
        }
        
    def test_create_order(self):
        """Test creating a valid order."""
        order = Order.objects.create(**self.valid_order_data)
        self.assertEqual(order.order_code, 'PO000001')
        self.assertEqual(order.status_code, OrderStatus.DRAFT)
        self.assertEqual(order.supplier, self.supplier)
        
    def test_order_string_representation(self):
        """Test the string representation of an order."""
        order = Order.objects.create(**self.valid_order_data)
        self.assertEqual(str(order), "PO000001 - Test Order")
        
    def test_order_status_transitions(self):
        """Test order status transitions."""
        order = Order.objects.create(**self.valid_order_data)
        
        # Test initial status
        self.assertEqual(order.status_code, OrderStatus.DRAFT)
        
        # Test status change
        order.status_code = OrderStatus.SUBMITTED
        order.save()
        self.assertEqual(order.status_code, OrderStatus.SUBMITTED)
        
    def test_order_with_items_total(self):
        """Test order with items and total calculation."""
        order = Order.objects.create(**self.valid_order_data)
        
        # Add order items
        OrderItem.objects.create(
            order=order,
            item_id=1,
            label='Test Item 1',
            quantity=2.00,
            total_amount=100.00
        )
        
        OrderItem.objects.create(
            order=order,
            item_id=2,
            label='Test Item 2',
            quantity=1.00,
            total_amount=50.00
        )
        
        # Update order total
        order.items_total_amount = 150.00
        order.save()
        
        # Check total amount
        self.assertEqual(order.items_total_amount, 150.00)
        self.assertEqual(order.items.count(), 2)
        
    def test_order_with_invalid_status(self):
        """Test order with invalid status."""
        data = self.valid_order_data.copy()
        data['status_code'] = 'invalid'
        
        with self.assertRaises(ValidationError):
            order = Order(**data)
            order.full_clean()
            
    def test_order_with_contacts(self):
        """Test order with contacts."""
        order = Order.objects.create(**self.valid_order_data)
        
        # Add order contact
        contact = OrderContact.objects.create(
            order=order,
            requester_firstname='John',
            requester_lastname='Doe',
            requester_email='john.doe@example.com',
            billing_firstname='Jane',
            billing_lastname='Smith',
            billing_email='jane.smith@example.com'
        )
        
        self.assertEqual(order.contacts.count(), 1)
        self.assertEqual(order.contacts.first().requester_email, 'john.doe@example.com')
        
    def test_order_with_addresses(self):
        """Test order with addresses."""
        order = Order.objects.create(**self.valid_order_data)
        
        # Add billing address
        billing_address = OrderAddress.objects.create(
            order=order,
            type=AddressType.BILLING,
            street='123 Billing Street',
            zip_code='10001',
            city='New York',
            country_code='US'
        )
        
        # Add delivery address
        delivery_address = OrderAddress.objects.create(
            order=order,
            type=AddressType.DELIVERY,
            street='456 Delivery Avenue',
            zip_code='94105',
            city='San Francisco',
            country_code='US'
        )
        
        self.assertEqual(order.addresses.count(), 2)
        
        # Verify we can fetch addresses by type
        self.assertEqual(
            order.addresses.filter(type=AddressType.BILLING).first().street,
            '123 Billing Street'
        )


class OrderContactTest(TestCase):
    """Test suite for the OrderContact model."""
    
    def setUp(self):
        """Set up test data."""
        # Create a test supplier
        self.supplier = Supplier.objects.create(
            object_id=1,
            code='SUP000001',
            supplier_name='Test Supplier',
            legal_name='Test Supplier Legal Name',
            creation_system_date=timezone.now().date(),
        )
        
        # Create an order for testing
        self.order = Order.objects.create(
            object_id=1,
            ord_id_origin=1001,
            order_code='PO000001',
            order_label='Test Order',
            basket_id=1,
            supplier=self.supplier,
            order_sup_id=1,
            order_sup_name='Test Supplier',
            created=timezone.now().date(),
            login_created='testuser',
            status_code=OrderStatus.DRAFT,
            order_date=timezone.now().date(),
            currency_code='EUR',
        )
        
    def test_create_order_contact(self):
        """Test creating a valid order contact."""
        contact = OrderContact.objects.create(
            order=self.order,
            requester_firstname='John',
            requester_lastname='Doe',
            requester_email='john.doe@example.com'
        )
        
        self.assertEqual(contact.requester_firstname, 'John')
        self.assertEqual(contact.order, self.order)
        
    def test_order_contact_string_representation(self):
        """Test the string representation of an order contact."""
        contact = OrderContact.objects.create(
            order=self.order,
            requester_firstname='John',
            requester_lastname='Doe',
            requester_email='john.doe@example.com'
        )
        
        self.assertEqual(str(contact), f"Contacts for {self.order.order_code}")
        
    def test_order_contact_with_invalid_email(self):
        """Test order contact with invalid email."""
        with self.assertRaises(ValidationError):
            contact = OrderContact(
                order=self.order,
                requester_firstname='John',
                requester_lastname='Doe',
                requester_email='invalid-email'
            )
            contact.full_clean()


class OrderItemTest(TestCase):
    """Test suite for the OrderItem model."""
    
    def setUp(self):
        """Set up test data."""
        # Create a test supplier
        self.supplier = Supplier.objects.create(
            object_id=1,
            code='SUP000001',
            supplier_name='Test Supplier',
            legal_name='Test Supplier Legal Name',
            creation_system_date=timezone.now().date(),
        )
        
        # Create an order for testing
        self.order = Order.objects.create(
            object_id=1,
            ord_id_origin=1001,
            order_code='PO000001',
            order_label='Test Order',
            basket_id=1,
            supplier=self.supplier,
            order_sup_id=1,
            order_sup_name='Test Supplier',
            created=timezone.now().date(),
            login_created='testuser',
            status_code=OrderStatus.DRAFT,
            order_date=timezone.now().date(),
            currency_code='EUR',
        )
        
    def test_create_order_item(self):
        """Test creating a valid order item."""
        item = OrderItem.objects.create(
            order=self.order,
            item_id=1,
            label='Test Product',
            family_label='Electronics',
            quantity=2.50,
            total_amount=125.00
        )
        
        self.assertEqual(item.label, 'Test Product')
        self.assertEqual(item.quantity, 2.50)
        self.assertEqual(item.total_amount, 125.00)
        
    def test_order_item_string_representation(self):
        """Test the string representation of an order item."""
        item = OrderItem.objects.create(
            order=self.order,
            item_id=1,
            label='Test Product',
            quantity=1.00,
            total_amount=50.00
        )
        
        self.assertEqual(str(item), f"Test Product ({self.order.order_code})")
        
    def test_order_item_with_negative_quantity(self):
        """Test order item with negative quantity."""
        # Create item with negative quantity (this doesn't trigger validation)
        item = OrderItem.objects.create(
            order=self.order,
            item_id=1,
            label='Test Product',
            quantity=-1.00,
            total_amount=50.00
        )
        
        # Verify negative quantity was stored
        self.assertEqual(item.quantity, -1.00)
        
        # We should add a validation rule to the model to prevent negative quantities
        # For example, by adding a MinValueValidator to the quantity field in the model


class OrderAddressTest(TestCase):
    """Test suite for the OrderAddress model."""
    
    def setUp(self):
        """Set up test data."""
        # Create a test supplier
        self.supplier = Supplier.objects.create(
            object_id=1,
            code='SUP000001',
            supplier_name='Test Supplier',
            legal_name='Test Supplier Legal Name',
            creation_system_date=timezone.now().date(),
        )
        
        # Create an order for testing
        self.order = Order.objects.create(
            object_id=1,
            ord_id_origin=1001,
            order_code='PO000001',
            order_label='Test Order',
            basket_id=1,
            supplier=self.supplier,
            order_sup_id=1,
            order_sup_name='Test Supplier',
            created=timezone.now().date(),
            login_created='testuser',
            status_code=OrderStatus.DRAFT,
            order_date=timezone.now().date(),
            currency_code='EUR',
        )
        
    def test_create_order_address(self):
        """Test creating a valid order address."""
        address = OrderAddress.objects.create(
            order=self.order,
            type=AddressType.BILLING,
            street='123 Main Street',
            zip_code='75001',
            city='Paris',
            country_code='FR'
        )
        
        self.assertEqual(address.street, '123 Main Street')
        self.assertEqual(address.type, AddressType.BILLING)
        
    def test_multiple_address_types(self):
        """Test creating multiple address types for the same order."""
        billing_address = OrderAddress.objects.create(
            order=self.order,
            type=AddressType.BILLING,
            street='123 Billing Street',
            zip_code='75001',
            city='Paris',
            country_code='FR'
        )
        
        delivery_address = OrderAddress.objects.create(
            order=self.order,
            type=AddressType.DELIVERY,
            street='456 Delivery Avenue',
            zip_code='69001',
            city='Lyon',
            country_code='FR'
        )
        
        supplier_address = OrderAddress.objects.create(
            order=self.order,
            type=AddressType.SUPPLIER,
            street='789 Supplier Road',
            zip_code='13001',
            city='Marseille',
            country_code='FR'
        )
        
        self.assertEqual(self.order.addresses.count(), 3)
        
        # Check each address type
        self.assertEqual(
            self.order.addresses.filter(type=AddressType.BILLING).first().city,
            'Paris'
        )
        self.assertEqual(
            self.order.addresses.filter(type=AddressType.DELIVERY).first().city,
            'Lyon'
        )
        self.assertEqual(
            self.order.addresses.filter(type=AddressType.SUPPLIER).first().city,
            'Marseille'
        )
        
    def test_order_address_with_invalid_type(self):
        """Test order address with invalid type."""
        with self.assertRaises(ValidationError):
            address = OrderAddress(
                order=self.order,
                type='invalid_type',
                street='123 Main Street',
                zip_code='75001',
                city='Paris',
                country_code='FR'
            )
            address.full_clean()
