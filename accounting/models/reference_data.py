from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import BaseModel


class ClientAccountType(BaseModel):
    """
    Represents client account types used in accounting.
    
    This classification is important for reporting and analysis of client accounts.
    """
    code = models.CharField(_("code"), max_length=5, unique=True, help_text=_("Unique code for client account type"))
    name = models.CharField(_("name"), max_length=255, help_text=_("Name of client account type"))
    
    class Meta:
        verbose_name = _("Client Account Type")
        verbose_name_plural = _("Client Account Types")
        ordering = ["code"]
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Activity(BaseModel):
    """
    Represents accounting activity types.
    
    Activities categorize accounting operations, which is important for management accounting.
    """
    code = models.CharField(_("code"), max_length=5, unique=True, help_text=_("Unique code for activity"))
    name = models.CharField(_("name"), max_length=255, help_text=_("Name of activity"))
    
    class Meta:
        verbose_name = _("Activity")
        verbose_name_plural = _("Activities")
        ordering = ["code"]
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class AccountingEntryType(BaseModel):
    """
    Represents types of accounting entries.
    
    Different entry types (e.g., budget, analytical, general) serve specific accounting purposes.
    """
    code = models.CharField(_("code"), max_length=5, unique=True, help_text=_("Unique code for accounting entry type"))
    name = models.CharField(_("name"), max_length=255, help_text=_("Name of accounting entry type"))
    indicator_code = models.CharField(_("indicator code"), max_length=5, help_text=_("Indicator code for accounting entry type"))
    indicator_name = models.CharField(_("indicator name"), max_length=255, help_text=_("Indicator name for accounting entry type"))
    
    class Meta:
        verbose_name = _("Accounting Entry Type")
        verbose_name_plural = _("Accounting Entry Types")
        ordering = ["code"]
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class EngagementType(BaseModel):
    """
    Represents types of financial engagements.
    
    Engagements can be contracts, orders, financing, etc.
    """
    code = models.CharField(_("code"), max_length=5, unique=True, help_text=_("Unique code for engagement type"))
    name = models.CharField(_("name"), max_length=255, help_text=_("Name of engagement type"))
    
    class Meta:
        verbose_name = _("Engagement Type")
        verbose_name_plural = _("Engagement Types")
        ordering = ["code"]
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class ReconciliationType(BaseModel):
    """
    Represents types of account reconciliation (lettrage).
    
    Reconciliation is the process of matching transactions to identify open items.
    """
    code = models.CharField(_("code"), max_length=5, unique=True, help_text=_("Unique code for reconciliation type"))
    name = models.CharField(_("name"), max_length=255, help_text=_("Name of reconciliation type"))
    
    class Meta:
        verbose_name = _("Reconciliation Type")
        verbose_name_plural = _("Reconciliation Types")
        ordering = ["code"]
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class PayerType(BaseModel):
    """
    Represents types of payers.
    
    Payers can be occupants, partners, third-party payers, etc.
    """
    code = models.CharField(_("code"), max_length=5, unique=True, help_text=_("Unique code for payer type"))
    name = models.CharField(_("name"), max_length=255, help_text=_("Name of payer type"))
    
    class Meta:
        verbose_name = _("Payer Type")
        verbose_name_plural = _("Payer Types")
        ordering = ["code"]
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class ServiceType(BaseModel):
    """
    Represents types of services provided.
    
    Services can be categorized for better reporting and analysis.
    """
    id_service_type = models.CharField(_("service type ID"), max_length=10, unique=True, help_text=_("Unique ID for service type"))
    code = models.CharField(_("code"), max_length=5, help_text=_("Code for service type"))
    name = models.CharField(_("name"), max_length=255, help_text=_("Name of service type"))
    category_code = models.CharField(_("category code"), max_length=5, help_text=_("Category code"))
    category_name = models.CharField(_("category name"), max_length=255, help_text=_("Category name"))
    
    class Meta:
        verbose_name = _("Service Type")
        verbose_name_plural = _("Service Types")
        ordering = ["code"]
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class PricingType(BaseModel):
    """
    Represents types of pricing used.
    
    Different pricing types apply to different business contexts.
    """
    code = models.CharField(_("code"), max_length=5, unique=True, help_text=_("Unique code for pricing type"))
    name = models.CharField(_("name"), max_length=255, help_text=_("Name of pricing type"))
    
    class Meta:
        verbose_name = _("Pricing Type")
        verbose_name_plural = _("Pricing Types")
        ordering = ["code"]
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Municipality(BaseModel):
    """
    Represents municipalities (communes) in which accounting operations occur.
    
    Municipalities are relevant for territorial accounting and reporting.
    """
    insee_code = models.CharField(_("INSEE code"), max_length=5, unique=True, help_text=_("Official INSEE identification code for municipality"))
    name = models.CharField(_("name"), max_length=255, help_text=_("Name of municipality"))
    postal_code = models.CharField(_("postal code"), max_length=5, help_text=_("Postal code of municipality"))
    department_code = models.CharField(_("department code"), max_length=3, help_text=_("Department code"))
    region_code = models.CharField(_("region code"), max_length=3, help_text=_("Region code"))
    
    class Meta:
        verbose_name = _("Municipality")
        verbose_name_plural = _("Municipalities")
        ordering = ["insee_code"]
    
    def __str__(self):
        return f"{self.insee_code} - {self.name} ({self.postal_code})"
