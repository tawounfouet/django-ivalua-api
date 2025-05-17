from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator, EmailValidator
from core.models import BaseModel, StatusChoices, YesNoChoices
from suppliers.models import Supplier


class OrderStatus(models.TextChoices):
    """
    Status choices for orders in the system.
    
    These statuses represent the lifecycle states of an order.
    """
    INITIAL = 'ini', _('Initial')
    DRAFT = 'dra', _('Draft')
    SUBMITTED = 'sub', _('Submitted')
    APPROVED = 'app', _('Approved')
    REJECTED = 'rej', _('Rejected')
    SENT = 'sen', _('Sent to supplier')
    ACKNOWLEDGED = 'ack', _('Acknowledged')
    PARTIALLY_RECEIVED = 'par', _('Partially received')
    RECEIVED = 'rec', _('Received')
    CANCELLED = 'can', _('Cancelled')
    CLOSED = 'clo', _('Closed')
    TERMINATED = 'end', _('Terminated')


class OrderType(models.TextChoices):
    """
    Types of orders in the system.
    """
    DEFAULT = 'default', _('Default')
    BLANKET = 'blanket', _('Blanket order')
    CONTRACT = 'contract', _('Contract-based')
    SPECIAL = 'special', _('Special order')


class Order(BaseModel):
    """
    Represents a purchase order in the system.
    
    A purchase order is a commercial document and first official offer issued by a buyer
    to a seller, indicating types, quantities, and agreed prices for products or services.
    
    Attributes:
        id (int): Primary key
        object_id (int): Object ID in the external system
        ord_id_origin (int): Original order ID in source system
        order_code (str): Unique code identifier for the order (e.g., PO000001)
        order_label (str): Label/description of the order
        order_type_code (str): Type classification code
        ord_ext_code (str): External reference code
        ord_ref (str): Reference number
        basket_id (int): Associated basket ID
        supplier (FK): Foreign key to supplier if assigned
        supplier_name (str): Supplier name for display purposes
        sup_nat_id (str): Supplier national ID
        sup_nat_id_type (str): Type of national ID
        created (date): Creation date 
        modified (date): Last modification date
        login_created (str): Username who created the order
        login_modified (str): Username who modified the order
        status_code (str): Current status code
        status_label (str): Descriptive status label
        order_date (date): Official order date
        items_total_amount (decimal): Total amount of order items
        currency_code (str): Currency code (e.g., EUR, USD)
        comment (str): Order comments
        inco_code (str): Incoterm code
        inco_place (str): Incoterm place
        payterm_code (str): Payment term code
        payterm_label (str): Payment term description
        payment_type_code (str): Payment type code
        payment_type_label (str): Payment type description
        free_budget (str): Yes/No field for free budget
        amendment_num (str): Amendment number
        track_timesheet (str): Yes/No field for timesheet tracking
        legal_comp_code (str): Legal company code
        legal_comp_legal_form (str): Legal form of company
        legal_comp_label (str): Legal company name
        orga_label (str): Organization label
        orga_level (str): Organization level
        orga_node (str): Organization node path
    """
    id = models.AutoField(
        primary_key=True,
        verbose_name=_("ID")
    )
    object_id = models.PositiveIntegerField(
        verbose_name=_("object ID"),
        help_text=_("Identifier in the external system")
    )
    ord_id_origin = models.PositiveIntegerField(
        verbose_name=_("origin ID"),
        help_text=_("Original order ID in the source system")
    )
    order_code = models.CharField(
        max_length=20, 
        verbose_name=_("order code"),
        help_text=_("Unique code identifier for the order (e.g., PO000001)")
    )
    order_label = models.CharField(
        max_length=255, 
        verbose_name=_("order label"),
        help_text=_("Label or description of the order")
    )
    order_type_code = models.CharField(
        max_length=20,
        choices=OrderType.choices,
        default=OrderType.DEFAULT,
        verbose_name=_("order type"),
        help_text=_("Type classification of the order")
    )
    ord_ext_code = models.CharField(
        max_length=50, 
        blank=True,
        verbose_name=_("external code"),
        help_text=_("External reference code")
    )
    ord_ref = models.CharField(
        max_length=50, 
        blank=True,
        verbose_name=_("reference"),
        help_text=_("Reference number")
    )
    basket_id = models.PositiveIntegerField(
        verbose_name=_("basket ID"),
        help_text=_("ID of the associated basket")
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name=_("supplier"),
        help_text=_("Associated supplier record")
    )
    order_sup_id = models.PositiveIntegerField(
        default=0,
        verbose_name=_("supplier ID"),
        help_text=_("ID of the supplier in the external system")
    )
    order_sup_name = models.CharField(
        max_length=255, 
        blank=True,
        verbose_name=_("supplier name"),
        help_text=_("Name of the supplier for display purposes")
    )
    sup_nat_id = models.CharField(
        max_length=30, 
        blank=True,
        verbose_name=_("national ID"),
        help_text=_("Supplier's national identification number")
    )
    sup_nat_id_type = models.CharField(
        max_length=2, 
        blank=True,
        verbose_name=_("national ID type"),
        help_text=_("Type of the national ID (e.g., SIRET, VAT)")
    )
    created = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("created date"),
        help_text=_("Date when the order was created")
    )
    modified = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("modified date"),
        help_text=_("Date when the order was last modified")
    )
    login_created = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name=_("created by"),
        help_text=_("Username of who created the order")
    )
    login_modified = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name=_("modified by"),
        help_text=_("Username of who last modified the order")
    )
    status_code = models.CharField(
        max_length=3,
        choices=OrderStatus.choices,
        default=OrderStatus.INITIAL,
        verbose_name=_("status"),
        help_text=_("Current status of the order")
    )
    status_label = models.CharField(
        max_length=50, 
        blank=True,
        verbose_name=_("status label"),
        help_text=_("Descriptive label for the status")
    )
    order_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("order date"),
        help_text=_("Official date of the order")
    )
    items_total_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        verbose_name=_("total amount"),
        help_text=_("Total amount of all order items")
    )
    currency_code = models.CharField(
        max_length=3, 
        default="EUR",
        verbose_name=_("currency"),
        help_text=_("Currency code (e.g., EUR, USD)")
    )
    comment = models.TextField(
        blank=True,
        verbose_name=_("comment"),
        help_text=_("Comments about the order")
    )
    inco_code = models.CharField(
        max_length=20, 
        blank=True,
        verbose_name=_("incoterm code"),
        help_text=_("International Commercial Terms code")
    )
    inco_place = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name=_("incoterm place"),
        help_text=_("Location specified in the Incoterm")
    )
    payterm_code = models.CharField(
        max_length=20, 
        blank=True,
        verbose_name=_("payment term code"),
        help_text=_("Code for the payment terms")
    )
    payterm_label = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name=_("payment term label"),
        help_text=_("Description of payment terms")
    )
    payment_type_code = models.CharField(
        max_length=20, 
        blank=True,
        verbose_name=_("payment type code"),
        help_text=_("Code for the payment type")
    )
    payment_type_label = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name=_("payment type label"),
        help_text=_("Description of payment type")
    )
    free_budget = models.CharField(
        max_length=3, 
        choices=YesNoChoices.choices,
        default=YesNoChoices.NO,
        verbose_name=_("free budget"),
        help_text=_("Whether the order is free from budget constraints")
    )
    amendment_num = models.CharField(
        max_length=10, 
        default="0",
        verbose_name=_("amendment number"),
        help_text=_("Sequential number of amendments to this order")
    )
    track_timesheet = models.CharField(
        max_length=3, 
        choices=YesNoChoices.choices,
        default=YesNoChoices.NO,
        verbose_name=_("track timesheet"),
        help_text=_("Whether the order requires timesheet tracking")
    )
    legal_comp_code = models.CharField(
        max_length=20, 
        blank=True,
        verbose_name=_("legal company code"),
        help_text=_("Code of the legal company")
    )
    legal_comp_legal_form = models.CharField(
        max_length=50, 
        blank=True,
        verbose_name=_("legal form"),
        help_text=_("Legal form of the company")
    )
    legal_comp_label = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name=_("legal company name"),
        help_text=_("Name of the legal company")
    )
    orga_label = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name=_("organization label"),
        help_text=_("Label of the organization")
    )
    orga_level = models.CharField(
        max_length=20, 
        blank=True,
        verbose_name=_("organization level"),
        help_text=_("Level of the organization (e.g., site, department)")
    )
    orga_node = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name=_("organization node"),
        help_text=_("Organization node path")
    )

    class Meta:
        verbose_name = _("order")
        verbose_name_plural = _("orders")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.order_code} - {self.order_label}"


class OrderContact(BaseModel):
    """
    Represents contact information associated with an order.
    
    Each order can have various contacts for different purposes (requester, billing, delivery, supplier).
    
    Attributes:
        order (FK): The associated order
        requester_firstname (str): Requester's first name
        requester_lastname (str): Requester's last name
        requester_email (str): Requester's email
        billing_firstname (str): Billing contact's first name
        billing_lastname (str): Billing contact's last name
        billing_email (str): Billing contact's email
        delivery_firstname (str): Delivery contact's first name
        delivery_lastname (str): Delivery contact's last name
        delivery_email (str): Delivery contact's email
        supplier_firstname (str): Supplier contact's first name
        supplier_lastname (str): Supplier contact's last name
        supplier_email (str): Supplier contact's email
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="contacts",
        verbose_name=_("order"),
        help_text=_("Associated order")
    )
    requester_firstname = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name=_("requester first name"),
        help_text=_("First name of the person requesting the order")
    )
    requester_lastname = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name=_("requester last name"),
        help_text=_("Last name of the person requesting the order")
    )
    requester_email = models.EmailField(
        blank=True,
        verbose_name=_("requester email"),
        help_text=_("Email of the person requesting the order")
    )
    billing_firstname = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name=_("billing contact first name"),
        help_text=_("First name of the billing contact")
    )
    billing_lastname = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name=_("billing contact last name"),
        help_text=_("Last name of the billing contact")
    )
    billing_email = models.EmailField(
        blank=True,
        verbose_name=_("billing contact email"),
        help_text=_("Email of the billing contact")
    )
    delivery_firstname = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name=_("delivery contact first name"),
        help_text=_("First name of the delivery contact")
    )
    delivery_lastname = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name=_("delivery contact last name"),
        help_text=_("Last name of the delivery contact")
    )
    delivery_email = models.EmailField(
        blank=True,
        verbose_name=_("delivery contact email"),
        help_text=_("Email of the delivery contact")
    )
    supplier_firstname = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name=_("supplier contact first name"),
        help_text=_("First name of the supplier contact")
    )
    supplier_lastname = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name=_("supplier contact last name"),
        help_text=_("Last name of the supplier contact")
    )
    supplier_email = models.EmailField(
        blank=True,
        verbose_name=_("supplier contact email"),
        help_text=_("Email of the supplier contact")
    )

    class Meta:
        verbose_name = _("order contact")
        verbose_name_plural = _("order contacts")

    def __str__(self):
        return f"Contacts for {self.order.order_code}"


class OrderItem(BaseModel):
    """
    Represents an individual line item in an order.
    
    Each order can contain multiple items with different products/services.
    
    Attributes:
        order (FK): The associated order
        item_id (int): Item ID in the external system
        label (str): Description of the item
        family_label (str): Product family label
        family_node (str): Product family node
        family_level (str): Product family level
        quantity (Decimal): Quantity ordered
        total_amount (Decimal): Total amount for this item
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("order"),
        help_text=_("Associated order")
    )
    item_id = models.PositiveIntegerField(
        verbose_name=_("item ID"),
        help_text=_("ID of the item in the external system")
    )
    label = models.CharField(
        max_length=255, 
        verbose_name=_("item description"),
        help_text=_("Description of the item")
    )
    family_label = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name=_("family label"),
        help_text=_("Product family label")
    )
    family_node = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name=_("family node"),
        help_text=_("Product family node reference")
    )
    family_level = models.CharField(
        max_length=20, 
        blank=True,
        verbose_name=_("family level"),
        help_text=_("Product family level")
    )
    quantity = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        verbose_name=_("quantity"),
        help_text=_("Quantity ordered")
    )
    total_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        verbose_name=_("total amount"),
        help_text=_("Total amount for this item")
    )

    class Meta:
        verbose_name = _("order item")
        verbose_name_plural = _("order items")

    def __str__(self):
        return f"{self.label} ({self.order.order_code})"


class AddressType(models.TextChoices):
    """
    Types of addresses that can be associated with an order.
    """
    BILLING = 'billing', _('Billing address')
    DELIVERY = 'delivery', _('Delivery address')
    SUPPLIER = 'supplier', _('Supplier address')


class OrderAddress(BaseModel):
    """
    Represents an address associated with an order.
    
    Each order can have different addresses for billing, delivery, etc.
    
    Attributes:
        order (FK): The associated order
        type (str): Type of address (billing, delivery, etc.)
        number (str): Street number
        name_complement (str): Name complement
        street (str): Street name
        street_complement (str): Additional street information
        zip_code (str): Postal/ZIP code
        city (str): City name
        country_code (str): Country code
        country_label (str): Country name
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="addresses",
        verbose_name=_("order"),
        help_text=_("Associated order")
    )
    type = models.CharField(
        max_length=20,
        choices=AddressType.choices,
        verbose_name=_("address type"),
        help_text=_("Type of address (billing, delivery, etc.)")
    )
    number = models.CharField(
        max_length=10, 
        blank=True,
        verbose_name=_("street number"),
        help_text=_("Street number")
    )
    name_complement = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name=_("name complement"),
        help_text=_("Additional name information")
    )
    street = models.CharField(
        max_length=255, 
        verbose_name=_("street"),
        help_text=_("Street name")
    )
    street_complement = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name=_("street complement"),
        help_text=_("Additional street information")
    )
    zip_code = models.CharField(
        max_length=20, 
        verbose_name=_("ZIP code"),
        help_text=_("Postal/ZIP code")
    )
    city = models.CharField(
        max_length=100, 
        verbose_name=_("city"),
        help_text=_("City name")
    )
    country_code = models.CharField(
        max_length=2, 
        blank=True,
        verbose_name=_("country code"),
        help_text=_("ISO country code")
    )
    country_label = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name=_("country"),
        help_text=_("Country name")
    )

    class Meta:
        verbose_name = _("order address")
        verbose_name_plural = _("order addresses")
        unique_together = ['order', 'type']

    def __str__(self):
        return f"{self.get_type_display()} for {self.order.order_code}"