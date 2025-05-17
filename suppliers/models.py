# apps/suppliers/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from core.models import BaseModel, StatusChoices
from typing import List, Dict, Any, Optional


class SupplierType(models.TextChoices):
    """
    Types of suppliers in the system.
    
    These types correspond to the IKOS supplier classification system.
    """
    SUPPLIER = 'FRS', _('Supplier')
    COOP_SYNDICATE_SEQENS = 'IBE', _('SEQENS Co-ownership Syndicate')
    COOP_SYNDICATE = 'SYN', _('Co-ownership Syndicate')


class NationalIdType(models.TextChoices):
    """
    Types of national identification for suppliers.
    
    Different countries and organizations use different ID systems.
    """
    SIRET = '01', _('SIRET')
    VAT = '05', _('VAT')
    NON_EU = '06', _('Non-EU')
    TAHITI = '07', _('TAHITI')
    RIDET = '08', _('RIDET')
    FR_NO_SIRET = '09', _('French supplier without SIRET')
    FRWF = '10', _('FRWF')
    IREP = '11', _('IREP')


class Supplier(BaseModel):
    """
    Represents a supplier (vendor) entity in the system.
    
    Suppliers can be companies or individuals who provide goods or services.
    Each supplier has identification, contact information, and categorization.
    
    Attributes:
        id (int): Primary key
        object_id (int): Object ID in the external system
        code (str): Internal supplier code (e.g., SUP000001)
        erp_code (str): External ERP system code
        supplier_name (str): Name of the supplier
        is_physical_person (bool): Whether the supplier is an individual person
        title (str): Title for individuals (Mr, Mrs, etc.)
        first_name (str): First name for individuals
        last_name (str): Last name for individuals
        legal_name (str): Legal business name
        website (str): Supplier's website URL
        nat_id_type (str): Type of national identifier
        nat_id (str): National identifier value
        type_ikos_code (str): IKOS system supplier type code
        siret (str): SIRET number (French company ID)
        siren (str): SIREN number (French company base ID)
        duns (str): DUNS number (international company ID)
        tva_intracom (str): Intra-community VAT number
        ape_naf (str): APE/NAF code (French activity code)
        creation_year (str): Year the supplier company was created
        creation_system_date (date): Date the supplier was created in the system
        modification_system_date (date): Date of last modification
        deleted_system_date (date): Date when the supplier was deleted
        latest_modification_date (date): Date of the latest modification
        status (str): Current status of the supplier record
        legal_code (str): Legal form code
        legal_structure (str): Description of legal structure
        
    Examples:
        >>> supplier = Supplier.objects.create(
        ...     object_id=1,
        ...     code="SUP000001",
        ...     supplier_name="ACME Inc.",
        ...     legal_name="ACME Incorporated",
        ...     creation_system_date="2023-01-01"
        ... )
        >>> supplier.status
        'ini'
        >>> supplier.update_fields(status=StatusChoices.VALID)
        >>> supplier.status
        'val'
    """
    id = models.AutoField(
        primary_key=True,
        verbose_name=_("ID")
    )
    object_id = models.PositiveIntegerField(
        verbose_name=_("object ID"),
        help_text=_("Identifier in the external system")
    )
    code = models.CharField(
        max_length=20,
        verbose_name=_("code"),
        help_text=_("Internal Ivalua code (e.g., SUP000001)")
    )
    erp_code = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("ERP code"),
        help_text=_("External IKOS code")
    )
    supplier_name = models.CharField(
        max_length=255,
        verbose_name=_("supplier name"),
        help_text=_("Commercial or common name of the supplier")
    )
    is_physical_person = models.BooleanField(
        default=False,
        verbose_name=_("physical person"),
        help_text=_("Whether the supplier is an individual rather than a company")
    )
    title = models.CharField(
        max_length=10,
        blank=True,
        verbose_name=_("title"),
        help_text=_("Personal title (Mr., Mrs., etc.)")
    )
    first_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("first name"),
        help_text=_("First name if the supplier is a person")
    )
    last_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("last name"),
        help_text=_("Last name if the supplier is a person")
    )
    legal_name = models.CharField(
        max_length=255,
        verbose_name=_("legal name"),
        help_text=_("Official registered name of the company")
    )
    website = models.URLField(
        blank=True,
        verbose_name=_("website"),
        help_text=_("Company website URL")
    )
    nat_id_type = models.CharField(
        max_length=2,
        choices=NationalIdType.choices,
        blank=True,
        verbose_name=_("national ID type"),
        help_text=_("Type of national identifier")
    )
    nat_id = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("national ID"),
        help_text=_("National identifier value")
    )
    type_ikos_code = models.CharField(
        max_length=3,
        choices=SupplierType.choices,
        default=SupplierType.SUPPLIER,
        verbose_name=_("IKOS type code"),
        help_text=_("Code for the IKOS supplier type")
    )
    siret = models.CharField(
        max_length=14,
        blank=True,
        verbose_name=_("SIRET"),
        validators=[
            RegexValidator(
                regex=r'^\d{14}$',
                message=_("SIRET must be exactly 14 digits")
            )
        ],
        help_text=_("French company identifier (14 digits)")
    )
    siren = models.CharField(
        max_length=9,
        blank=True,
        verbose_name=_("SIREN"),
        validators=[
            RegexValidator(
                regex=r'^\d{9}$',
                message=_("SIREN must be exactly 9 digits")
            )
        ],
        help_text=_("French company base identifier (9 digits)")
    )
    duns = models.CharField(
        max_length=9,
        blank=True,
        verbose_name=_("DUNS"),
        help_text=_("Dun & Bradstreet unique identifier")
    )
    tva_intracom = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("intra-EU VAT"),
        help_text=_("Intra-community VAT number")
    )
    ape_naf = models.CharField(
        max_length=10,
        blank=True,
        verbose_name=_("APE/NAF"),
        help_text=_("French activity code (format: 00.00X)")
    )
    creation_year = models.CharField(
        max_length=4,
        blank=True,
        verbose_name=_("creation year"),
        help_text=_("Year the supplier company was created")
    )
    creation_system_date = models.DateField(
        verbose_name=_("creation date"),
        help_text=_("Date when the supplier was created in the system")
    )
    modification_system_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("modification date"),
        help_text=_("Date of last modification")
    )
    deleted_system_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("deletion date"),
        help_text=_("Date when the supplier was deleted")
    )
    latest_modification_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("latest modification date"),
        help_text=_("Date of the latest modification of any supplier data")
    )
    status = models.CharField(
        max_length=3,
        choices=StatusChoices.choices,
        default=StatusChoices.INITIAL,
        verbose_name=_("status"),
        help_text=_("Current status of the supplier record")
    )
    legal_code = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("legal code"),
        help_text=_("Legal form code")
    )
    legal_structure = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("legal structure"),
        help_text=_("Description of legal structure")
    )

    class Meta:
        verbose_name = _("supplier")
        verbose_name_plural = _("suppliers")
        ordering = ['code', 'supplier_name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['nat_id']),
            models.Index(fields=['siret']),
            models.Index(fields=['siren']),
        ]

    def __str__(self) -> str:
        """Return a string representation of the supplier."""
        return f"{self.code} - {self.supplier_name}"
    
    def clean(self) -> None:
        """
        Validate the model before saving.
        
        Ensures that personal information is only set when supplier is a physical person,
        and validates national ID formats based on type.
        
        Raises:
            ValidationError: If validation fails
        """
        super().clean()
        
        # Validate personal information
        if self.is_physical_person:
            if not self.first_name or not self.last_name:
                raise ValidationError({
                    'first_name': _("First name is required for physical persons"),
                    'last_name': _("Last name is required for physical persons")
                })
        else:
            if self.first_name or self.last_name or self.title:
                raise ValidationError(_("Personal information should not be set for organizational suppliers"))
        
        # Validate national ID format based on type
        if self.nat_id_type == NationalIdType.SIRET and self.nat_id:
            if not self.nat_id.isdigit() or len(self.nat_id) != 14:
                raise ValidationError({'nat_id': _("SIRET must be exactly 14 digits")})
        
    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        Save the supplier instance.
        
        Updates the siren field automatically from siret when possible.
        
        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
        """
        # Auto-derive SIREN from SIRET if possible
        if self.siret and len(self.siret) == 14 and not self.siren:
            self.siren = self.siret[:9]
            
        self.full_clean()
        super().save(*args, **kwargs)

    def get_full_address(self) -> str:
        """
        Get the full formatted address of the supplier.
        
        Returns:
            str: Formatted full address
        """
        address = getattr(self, 'address', None)
        if not address:
            return ""
            
        parts = []
        if address.adr1:
            parts.append(address.adr1)
        if address.adr2:
            parts.append(address.adr2)
        if address.adr3:
            parts.append(address.adr3)
        if address.zip:
            parts.append(f"{address.zip}")
        if address.city:
            parts.append(address.city)
            
        return ", ".join(parts)
        
    def get_primary_banking_info(self) -> Optional['BankingInformation']:
        """
        Get the primary banking information record for this supplier.
        
        Returns:
            BankingInformation or None: The primary banking information if available
        """
        return self.banking_informations.first()
    



# apps/suppliers/models.py (suite)
class SupplierAddress(BaseModel):
    """
    Represents a supplier's address.
    
    Each supplier has one main address stored in this model.
    
    Attributes:
        supplier (Supplier): Associated supplier
        adr1 (str): Address line 1, typically country code
        adr2 (str): Address line 2, typically street address
        adr3 (str): Address line 3, additional address information
        zip (str): ZIP or postal code
        city (str): City name
    """
    supplier = models.OneToOneField(
        Supplier,
        on_delete=models.CASCADE,
        related_name='address',
        verbose_name=_("supplier"),
        help_text=_("The supplier this address belongs to")
    )
    adr1 = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("address line 1"),
        help_text=_("First line of address, typically country code")
    )
    adr2 = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("address line 2"),
        help_text=_("Second line of address, typically street address")
    )
    adr3 = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("address line 3"),
        help_text=_("Third line of address, additional information")
    )
    zip = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("ZIP/postal code"),
        help_text=_("ZIP or postal code")
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("city"),
        help_text=_("City name")
    )

    class Meta:
        verbose_name = _("supplier address")
        verbose_name_plural = _("supplier addresses")

    def __str__(self) -> str:
        """Return a string representation of the address."""
        return f"{self.zip} {self.city}" if self.zip and self.city else _("Address for {supplier}").format(
            supplier=self.supplier
        )

class BankingInformation(BaseModel):
    """
    Banking information for a supplier.
    
    Stores payment details necessary for electronic transfers.
    A supplier can have multiple banking information records.
    
    Attributes:
        supplier (Supplier): Associated supplier
        international_pay_id (str): International payment identifier
        account_number (str): Bank account number
        bank_code (str): Bank identifier code
        counter_code (str): Bank counter code
        rib_key (str): RIB key for validation
        bban (str): Basic Bank Account Number
        iban (str): International Bank Account Number
        bic (str): Bank Identifier Code (SWIFT code)
        country_code (str): ISO country code
        bank_label (str): Bank name/label
        creation_account_date (date): Date when the account was created
        modification_account_date (date): Date when the account was last modified
    
    Example:
        >>> bank_info = BankingInformation.objects.create(
        ...     supplier=supplier,
        ...     iban="FR7610278021310002041940126",
        ...     bic="CMCIFR2A",
        ...     country_code="FR",
        ...     bank_label="Credit Mutuel",
        ...     account_number="00020419401"
        ... )
        >>> bank_info.is_valid_iban()
        True
    """
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='banking_informations',
        verbose_name=_("supplier"),
        help_text=_("The supplier this banking information belongs to")
    )
    international_pay_id = models.CharField(
        max_length=10,
        blank=True,
        verbose_name=_("international payment ID"),
        help_text=_("International payment identifier")
    )
    account_number = models.CharField(
        max_length=50,
        verbose_name=_("account number"),
        help_text=_("Bank account number")
    )
    bank_code = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("bank code"),
        help_text=_("Bank identifier code")
    )
    counter_code = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("counter code"),
        help_text=_("Bank counter code")
    )
    rib_key = models.CharField(
        max_length=10,
        blank=True,
        verbose_name=_("RIB key"),
        help_text=_("RIB key for validation")
    )
    bban = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("BBAN"),
        help_text=_("Basic Bank Account Number")
    )
    iban = models.CharField(
        max_length=34,
        verbose_name=_("IBAN"),
        validators=[
            RegexValidator(
                regex=r'^[A-Z]{2}\d{2}[A-Z0-9]{10,30}$',
                message=_("IBAN must be in the correct format (e.g., FR7610278021310002041940126)")
            )
        ],
        help_text=_("International Bank Account Number")
    )
    bic = models.CharField(
        max_length=11,
        blank=True,
        verbose_name=_("BIC"),
        validators=[
            RegexValidator(
                regex=r'^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$',
                message=_("BIC must be 8 or 11 characters (e.g., CMCIFR2A)")
            )
        ],
        help_text=_("Bank Identifier Code (SWIFT code)")
    )
    country_code = models.CharField(
        max_length=2,
        verbose_name=_("country code"),
        help_text=_("ISO country code")
    )
    bank_label = models.CharField(
        max_length=255,
        verbose_name=_("bank name"),
        help_text=_("Name of the bank")
    )
    creation_account_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("creation date"),
        help_text=_("Date when the account was created")
    )
    modification_account_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("modification date"),
        help_text=_("Date when the account was last modified")
    )

    class Meta:
        verbose_name = _("banking information")
        verbose_name_plural = _("banking information")
        indexes = [
            models.Index(fields=['iban']),
            models.Index(fields=['bic']),
        ]

    def __str__(self) -> str:
        """Return a string representation of the banking information."""
        masked_iban = f"{'*' * (len(self.iban) - 4)}{self.iban[-4:]}" if self.iban else ""
        return f"{self.bank_label} - {masked_iban}"
    
    def is_valid_iban(self) -> bool:
        """
        Check if the IBAN is valid according to the checksum rules.
        
        Returns:
            bool: True if the IBAN is valid, False otherwise
        """
        if not self.iban:
            return False
            
        # This is a simplified validation - in a real app you would use a library
        # like 'schwifty' for complete IBAN validation
        iban = self.iban.replace(' ', '').upper()
        if len(iban) < 4:
            return False
            
        # Move first 4 chars to end and convert letters to numbers
        iban = iban[4:] + iban[:4]
        iban_digits = ''
        for ch in iban:
            if ch.isdigit():
                iban_digits += ch
            elif 'A' <= ch <= 'Z':
                iban_digits += str(ord(ch) - ord('A') + 10)
            else:
                return False
                
        # Check if the remainder when divided by 97 equals 1
        return int(iban_digits) % 97 == 1
    


class Contact(BaseModel):
    """
    Represents a contact person associated with a supplier.
    
    Contacts can be either internal (from the organization) or external 
    (from the supplier company). Each contact has personal information and
    can have multiple roles assigned.
    
    Attributes:
        supplier (Supplier): Associated supplier
        is_internal (bool): Whether the contact is internal to the organization
        first_name (str): First name of the contact
        last_name (str): Last name of the contact
        email (str): Email address of the contact
        login (str): Login username in the system, if applicable
        
    Examples:
        >>> supplier = Supplier.objects.get(code="SUP000001")
        >>> contact = Contact.objects.create(
        ...     supplier=supplier,
        ...     first_name="John",
        ...     last_name="Doe",
        ...     email="john.doe@example.com",
        ...     is_internal=False
        ... )
        >>> contact.get_full_name()
        'John Doe'
    """
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='contacts',
        verbose_name=_("supplier"),
        help_text=_("The supplier this contact is associated with")
    )
    is_internal = models.BooleanField(
        default=False,
        verbose_name=_("internal contact"),
        help_text=_("Whether the contact belongs to the organization rather than the supplier")
    )
    first_name = models.CharField(
        max_length=100,
        verbose_name=_("first name"),
        help_text=_("First name of the contact")
    )
    last_name = models.CharField(
        max_length=100,
        verbose_name=_("last name"),
        help_text=_("Last name of the contact")
    )
    email = models.EmailField(
        verbose_name=_("email"),
        help_text=_("Email address of the contact")
    )
    login = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("login"),
        help_text=_("System login username, if applicable")
    )

    class Meta:
        verbose_name = _("contact")
        verbose_name_plural = _("contacts")
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['email']),
        ]

    def __str__(self) -> str:
        """Return a string representation of the contact."""
        return f"{self.first_name} {self.last_name}"
    
    def get_full_name(self) -> str:
        """
        Get the contact's full name.
        
        Returns:
            str: Full name (first name + last name)
        """
        return f"{self.first_name} {self.last_name}"
    
    def clean(self) -> None:
        """
        Validate the contact before saving.
        
        Ensures that email is in a valid format and that internal contacts have login info.
        
        Raises:
            ValidationError: If validation fails
        """
        super().clean()
        
        # Internal contacts should have a login
        if self.is_internal and not self.login:
            raise ValidationError({
                'login': _("Login is required for internal contacts")
            })


class ContactRole(BaseModel):
    """
    Represents a role assigned to a supplier contact.
    
    Each contact can have multiple roles within the supplier relationship,
    such as 'Commercial Contact', 'Technical Contact', 'Administrative Contact', etc.
    
    Attributes:
        contact (Contact): Associated contact person
        code (str): Role code identifier
        label (str): Human-readable role name/description
        
    Examples:
        >>> contact = Contact.objects.get(email="john.doe@example.com")
        >>> role = ContactRole.objects.create(
        ...     contact=contact,
        ...     code="COM",
        ...     label="Commercial Contact"
        ... )
    """
    contact = models.ForeignKey(
        Contact,
        on_delete=models.CASCADE,
        related_name='roles',
        verbose_name=_("contact"),
        help_text=_("The contact this role is assigned to")
    )
    code = models.CharField(
        max_length=20,
        verbose_name=_("role code"),
        help_text=_("Code identifier for the role")
    )
    label = models.CharField(
        max_length=100,
        verbose_name=_("role label"),
        help_text=_("Human-readable name or description of the role")
    )

    class Meta:
        verbose_name = _("contact role")
        verbose_name_plural = _("contact roles")
        ordering = ['code']
        unique_together = ['contact', 'code']

    def __str__(self) -> str:
        """Return a string representation of the contact role."""
        return self.label


class SupplierPartner(BaseModel):
    """
    Represents a partner organization associated with a supplier.
    
    This model links suppliers to specific organizational units (departments, 
    subsidiaries, etc.) with which they have a partnership relationship.
    
    Attributes:
        supplier (Supplier): Associated supplier
        orga_level (str): Organization level code
        orga_node (str): Organization node identifier
        num_part (int): Partner number or identifier
        status (str): Status of the partnership
        
    Examples:
        >>> supplier = Supplier.objects.get(code="SUP000001")
        >>> partner = SupplierPartner.objects.create(
        ...     supplier=supplier,
        ...     orga_level="DIV",
        ...     orga_node="DIV001",
        ...     num_part=1,
        ...     status=StatusChoices.VALID
        ... )
    """
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='partners',
        verbose_name=_("supplier"),
        help_text=_("The supplier this partnership is associated with")
    )
    orga_level = models.CharField(
        max_length=10,
        verbose_name=_("organization level"),
        help_text=_("Code representing the level in the organization hierarchy")
    )
    orga_node = models.CharField(
        max_length=20,
        verbose_name=_("organization node"),
        help_text=_("Identifier for the specific organizational unit")
    )
    num_part = models.PositiveIntegerField(
        verbose_name=_("partner number"),
        help_text=_("Numeric identifier for the partnership")
    )
    status = models.CharField(
        max_length=3,
        choices=StatusChoices.choices,
        default=StatusChoices.VALID,
        verbose_name=_("status"),
        help_text=_("Current status of the partnership")
    )

    class Meta:
        verbose_name = _("supplier partner")
        verbose_name_plural = _("supplier partners")
        ordering = ['orga_level', 'orga_node']
        unique_together = ['supplier', 'orga_level', 'orga_node']

    def __str__(self) -> str:
        """Return a string representation of the supplier partner."""
        return f"{self.orga_level} - {self.orga_node}"
    
    def get_organization_display(self) -> str:
        """
        Get a display string for the partner organization.
        
        Returns:
            str: Formatted organization identifier
        """
        return f"{self.orga_level}:{self.orga_node} (#{self.num_part})"


class SupplierRole(BaseModel):
    """
    Represents a role assigned to a supplier within an organization.
    
    This model defines the specific roles a supplier plays within different
    parts of the organization, such as 'Preferred Supplier', 'Approved Vendor',
    'Strategic Partner', etc.
    
    Attributes:
        supplier (Supplier): Associated supplier
        orga_level (str): Organization level code
        orga_node (str): Organization node identifier
        role_code (str): Role type code
        role_label (str): Human-readable role description
        begin_date (date): Date when the role became effective
        end_date (date): Date when the role expires/ended
        status (str): Current status of the role assignment
        
    Examples:
        >>> supplier = Supplier.objects.get(code="SUP000001")
        >>> from datetime import date
        >>> role = SupplierRole.objects.create(
        ...     supplier=supplier,
        ...     orga_level="DIV",
        ...     orga_node="DIV001",
        ...     role_code="PREF",
        ...     role_label="Preferred Supplier",
        ...     begin_date=date(2023, 1, 1),
        ...     status=StatusChoices.VALID
        ... )
        >>> role.is_active()
        True
    """
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='roles',
        verbose_name=_("supplier"),
        help_text=_("The supplier this role is assigned to")
    )
    orga_level = models.CharField(
        max_length=10,
        verbose_name=_("organization level"),
        help_text=_("Code representing the level in the organization hierarchy")
    )
    orga_node = models.CharField(
        max_length=20,
        verbose_name=_("organization node"),
        help_text=_("Identifier for the specific organizational unit")
    )
    role_code = models.CharField(
        max_length=10,
        verbose_name=_("role code"),
        help_text=_("Code identifier for the role type")
    )
    role_label = models.CharField(
        max_length=100,
        verbose_name=_("role description"),
        help_text=_("Human-readable description of the role")
    )
    begin_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("start date"),
        help_text=_("Date when the role became effective")
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("end date"),
        help_text=_("Date when the role expires or ended")
    )
    status = models.CharField(
        max_length=3,
        choices=StatusChoices.choices,
        default=StatusChoices.VALID,
        verbose_name=_("status"),
        help_text=_("Current status of the role assignment")
    )

    class Meta:
        verbose_name = _("supplier role")
        verbose_name_plural = _("supplier roles")
        ordering = ['orga_level', 'orga_node', 'role_code']
        unique_together = ['supplier', 'orga_level', 'orga_node', 'role_code']

    def __str__(self) -> str:
        """Return a string representation of the supplier role."""
        return f"{self.role_code} - {self.role_label}"
    
    def clean(self) -> None:
        """
        Validate the supplier role before saving.
        
        Ensures that date ranges are valid (end date is after begin date).
        
        Raises:
            ValidationError: If validation fails
        """
        super().clean()
        
        # Validate date range
        if self.begin_date and self.end_date and self.begin_date > self.end_date:
            raise ValidationError({
                'end_date': _("End date cannot be earlier than begin date")
            })
    
    def is_active(self) -> bool:
        """
        Check if the role is currently active.
        
        A role is considered active if:
        - Its status is VALID
        - Current date is after begin_date (if specified)
        - Current date is before end_date (if specified)
        
        Returns:
            bool: True if the role is active, False otherwise
        """
        from django.utils import timezone
        
        if self.status != StatusChoices.VALID:
            return False
            
        today = timezone.now().date()
        
        if self.begin_date and today < self.begin_date:
            return False
            
        if self.end_date and today > self.end_date:
            return False
            
        return True