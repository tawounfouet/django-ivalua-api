import random
from decimal import Decimal
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from faker import Faker
from django.utils.translation import gettext_lazy as _

from orders.models import Order, OrderContact, OrderItem, OrderAddress, OrderStatus, OrderType, AddressType
from suppliers.models import Supplier


class Command(BaseCommand):
    """
    Management command to generate fake order data for development and testing.
    
    This command creates realistic-looking orders with related contacts, items, and addresses.
    It provides options to specify the number of orders to create and whether to clear existing data.
    
    Usage:
        python manage.py generate_fake_orders
        python manage.py generate_fake_orders --count 50
        python manage.py generate_fake_orders --clear
    """
    help = _('Generate fake order data for development and testing')

    def add_arguments(self, parser):
        parser.add_argument(
            '--count', 
            type=int, 
            default=20,
            help=_('Number of orders to generate (default: 20)')
        )
        parser.add_argument(
            '--clear', 
            action='store_true',
            help=_('Clear existing order data before generating new data')
        )

    def handle(self, *args, **options):
        fake = Faker(['fr_FR'])
        count = options['count']
        clear = options['clear']
        
        # Fonction de remplacement pour secondary_address qui manque dans la locale fr_FR
        def get_secondary_address():
            """Génère une adresse secondaire compatible avec fr_FR"""
            options = [
                f"Bâtiment {random.choice('ABCDEFGH')}", 
                f"Étage {random.randint(1, 10)}", 
                f"Appartement {random.randint(1, 100)}",
                f"Boîte postale {random.randint(1000, 9999)}",
                f"ZI {fake.word().capitalize()}",
                f"ZA {fake.word().capitalize()}"
            ]
            return random.choice(options)
        
        # Get supplier IDs for random assignment
        supplier_ids = list(Supplier.objects.values_list('id', flat=True))
        if not supplier_ids:
            self.stdout.write(self.style.WARNING(
                'No suppliers found in the database. Orders will be created without suppliers.'
            ))
            supplier_ids = [None]
        
        with transaction.atomic():
            # Clear existing data if requested
            if clear:
                self.stdout.write(self.style.WARNING('Clearing existing order data...'))
                OrderAddress.objects.all().delete()
                OrderItem.objects.all().delete()
                OrderContact.objects.all().delete()
                Order.objects.all().delete()
                self.stdout.write(self.style.SUCCESS('Existing order data cleared successfully.'))
            
            # Create new orders
            self.stdout.write(f'Generating {count} fake orders...')
            orders_created = 0
            
            for i in range(1, count + 1):
                # Create order
                supplier_id = random.choice(supplier_ids)
                supplier = None if supplier_id is None else Supplier.objects.get(id=supplier_id)
                
                created_date = fake.date_between(start_date='-6m', end_date='today')
                order_date = fake.date_between(start_date=created_date, end_date='+2w')
                
                # Randomly choose order status based on dates
                if order_date > datetime.now().date():
                    status = random.choice([
                        OrderStatus.INITIAL, OrderStatus.DRAFT, OrderStatus.SUBMITTED
                    ])
                else:
                    days_diff = (datetime.now().date() - order_date).days
                    if days_diff < 7:
                        status = random.choice([
                            OrderStatus.APPROVED, OrderStatus.SENT, OrderStatus.ACKNOWLEDGED
                        ])
                    elif days_diff < 14:
                        status = random.choice([
                            OrderStatus.SENT, OrderStatus.ACKNOWLEDGED, OrderStatus.PARTIALLY_RECEIVED
                        ])
                    else:
                        status = random.choice([
                            OrderStatus.RECEIVED, OrderStatus.CLOSED, OrderStatus.TERMINATED
                        ])
                
                # Calculate modified date based on status
                modified_date = None
                if status not in [OrderStatus.INITIAL, OrderStatus.DRAFT]:
                    modified_date = fake.date_between(start_date=created_date, end_date='today')
                
                # Get status label
                status_label = dict(OrderStatus.choices)[status]
                
                order = Order.objects.create(
                    object_id=i,
                    ord_id_origin=i,
                    order_code=f"PO{i:06d}",
                    order_label=fake.sentence(nb_words=5),
                    order_type_code=random.choice(list(OrderType.values)),
                    ord_ext_code=f"EXT{i:06d}" if random.random() > 0.7 else "",
                    ord_ref=f"REF{i:06d}" if random.random() > 0.5 else "",
                    basket_id=i,
                    supplier=supplier,
                    order_sup_id=0 if supplier is None else supplier.id,
                    order_sup_name="" if supplier is None else supplier.supplier_name,
                    sup_nat_id="" if supplier is None else supplier.nat_id,
                    sup_nat_id_type="" if supplier is None else supplier.nat_id_type,
                    created=created_date,
                    modified=modified_date,
                    login_created=f"user{random.randint(1, 10)}",
                    login_modified=f"user{random.randint(1, 10)}" if modified_date else "",
                    status_code=status,
                    status_label=status_label,
                    order_date=order_date,
                    items_total_amount=Decimal(random.uniform(100, 100000)).quantize(Decimal('0.01')),
                    currency_code=random.choice(['EUR', 'USD']),
                    comment=fake.paragraph() if random.random() > 0.7 else "",
                    inco_code=random.choice(['EXW', 'FOB', 'CIF', '']) if random.random() > 0.7 else "",
                    inco_place=fake.city() if random.random() > 0.7 else "",
                    payterm_code=random.choice(['30D', '60D', '90D']) if random.random() > 0.5 else "",
                    payterm_label=f"{random.choice(['30', '60', '90'])} jours fin de mois" if random.random() > 0.5 else "",
                    payment_type_code=random.choice(['VIR', 'CHQ']) if random.random() > 0.5 else "",
                    payment_type_label=random.choice(['Virement', 'Chèque']) if random.random() > 0.5 else "",
                    free_budget='Yes' if random.random() > 0.8 else 'No',
                    amendment_num=str(random.randint(0, 3)),
                    track_timesheet='Yes' if random.random() > 0.8 else 'No',
                    legal_comp_code=random.choice(['ADL', 'SQS']),
                    legal_comp_legal_form=random.choice(['SAS', 'SA', 'SARL', '']),
                    legal_comp_label=random.choice(['Adlis', 'SEQENS']),
                    orga_label=fake.company_suffix(),
                    orga_level=random.choice(['site', 'division', 'department']),
                    orga_node=f"{random.choice(['ADL', 'SQS'])}_{random.choice(['DIR', 'DEV', 'FIN'])}_{random.randint(1000, 9999)}"
                )
                
                # Create order contact
                OrderContact.objects.create(
                    order=order,
                    requester_firstname=fake.first_name(),
                    requester_lastname=fake.last_name(),
                    requester_email=fake.email(),
                    billing_firstname=fake.first_name() if random.random() > 0.5 else "",
                    billing_lastname=fake.last_name() if random.random() > 0.5 else "",
                    billing_email=fake.email() if random.random() > 0.5 else "",
                    delivery_firstname=fake.first_name() if random.random() > 0.5 else "",
                    delivery_lastname=fake.last_name() if random.random() > 0.5 else "",
                    delivery_email=fake.email() if random.random() > 0.5 else "",
                    supplier_firstname=fake.first_name() if random.random() > 0.5 else "",
                    supplier_lastname=fake.last_name() if random.random() > 0.5 else "",
                    supplier_email=fake.email() if random.random() > 0.5 else ""
                )
                
                # Create order items (1-5 per order)
                items_count = random.randint(1, 5)
                total_amount = Decimal('0.00')
                
                for j in range(1, items_count + 1):
                    item_qty = Decimal(random.randint(1, 100))
                    item_price = Decimal(random.uniform(100, 10000)).quantize(Decimal('0.01'))
                    item_total = item_qty * item_price
                    total_amount += item_total
                    
                    OrderItem.objects.create(
                        order=order,
                        item_id=j,
                        label=fake.sentence(nb_words=4),
                        family_label=random.choice([
                            'Services informatiques', 'Matériel informatique', 
                            'Fournitures de bureau', 'Mobilier', 'Prestations de service'
                        ]),
                        family_node=str(random.randint(1, 5)),
                        family_level=random.choice(['cat', 'ssfam', 'fam']),
                        quantity=item_qty,
                        total_amount=item_total
                    )
                
                # Update order total amount to match items
                order.items_total_amount = total_amount
                order.save(update_fields=['items_total_amount'])
                
                # Create order addresses
                # Billing address
                OrderAddress.objects.create(
                    order=order,
                    type=AddressType.BILLING,
                    number=str(random.randint(1, 150)) if random.random() > 0.5 else "",
                    name_complement=fake.company() if random.random() > 0.7 else "",
                    street=fake.street_name(),
                    street_complement=get_secondary_address() if random.random() > 0.7 else "",
                    zip_code=fake.postcode(),
                    city=fake.city(),
                    country_code="FR",
                    country_label="France"
                )
                
                # Delivery address (sometimes same as billing)
                if random.random() > 0.3:  # 70% chance of different delivery address
                    OrderAddress.objects.create(
                        order=order,
                        type=AddressType.DELIVERY,
                        number=str(random.randint(1, 150)) if random.random() > 0.5 else "",
                        name_complement=fake.company() if random.random() > 0.7 else "",
                        street=fake.street_name(),
                        street_complement=get_secondary_address() if random.random() > 0.7 else "",
                        zip_code=fake.postcode(),
                        city=fake.city(),
                        country_code="FR",
                        country_label="France"
                    )
                else:
                    # Copy billing address for delivery
                    billing_address = order.addresses.filter(type=AddressType.BILLING).first()
                    if billing_address:
                        OrderAddress.objects.create(
                            order=order,
                            type=AddressType.DELIVERY,
                            number=billing_address.number,
                            name_complement=billing_address.name_complement,
                            street=billing_address.street,
                            street_complement=billing_address.street_complement,
                            zip_code=billing_address.zip_code,
                            city=billing_address.city,
                            country_code=billing_address.country_code,
                            country_label=billing_address.country_label
                        )
                
                orders_created += 1
                if orders_created % 10 == 0:
                    self.stdout.write(f'Created {orders_created} orders so far...')
            
            self.stdout.write(self.style.SUCCESS(
                f'Successfully generated {orders_created} fake orders with related data.'
            ))