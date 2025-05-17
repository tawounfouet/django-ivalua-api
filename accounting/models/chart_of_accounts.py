from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import BaseModel


class AccountingClass(BaseModel):
    """
    Represents a class in the chart of accounts (Plan Comptable Général - PCG).
    
    In French accounting, accounts are grouped into classes (1-9)
    Example: Class 1 - Capital accounts, Class 2 - Fixed asset accounts, etc.
    """
    code = models.CharField(_("code"), max_length=1, unique=True, help_text=_("Unique class code (1-9)"))
    name = models.CharField(_("name"), max_length=255, help_text=_("The name of the accounting class"))
    
    class Meta:
        verbose_name = _("Accounting Class")
        verbose_name_plural = _("Accounting Classes")
        ordering = ["code"]
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class AccountingChapter(BaseModel):
    """
    Represents a chapter in the chart of accounts (PCG).
    
    Chapters are subdivisions of classes, typically 2-digit codes.
    Example: 10 - Capital and reserves, 11 - Carry forward, etc.
    """
    accounting_class = models.ForeignKey(
        AccountingClass, 
        on_delete=models.CASCADE, 
        related_name="chapters",
        help_text=_("The accounting class this chapter belongs to")
    )
    code = models.CharField(_("code"), max_length=2, unique=True, help_text=_("Unique chapter code (e.g., 10, 11)"))
    name = models.CharField(_("name"), max_length=255, help_text=_("The name of the accounting chapter"))
    
    class Meta:
        verbose_name = _("Accounting Chapter")
        verbose_name_plural = _("Accounting Chapters")
        ordering = ["code"]
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class AccountingSection(BaseModel):
    """
    Represents a section in the chart of accounts (PCG).
    
    Sections are subdivisions of chapters, typically 3-digit codes.
    Example: 101 - Capital, 106 - Reserves, etc.
    """
    chapter = models.ForeignKey(
        AccountingChapter, 
        on_delete=models.CASCADE, 
        related_name="sections",
        help_text=_("The accounting chapter this section belongs to")
    )
    code = models.CharField(_("code"), max_length=3, unique=True, help_text=_("Unique section code (e.g., 101, 106)"))
    name = models.CharField(_("name"), max_length=255, help_text=_("The name of the accounting section"))
    
    class Meta:
        verbose_name = _("Accounting Section")
        verbose_name_plural = _("Accounting Sections")
        ordering = ["code"]
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class GeneralLedgerAccount(BaseModel):
    """
    Represents a general ledger account in the chart of accounts (PCG).
    
    This is the most detailed level in the chart of accounts hierarchy.
    """
    section = models.ForeignKey(
        AccountingSection, 
        on_delete=models.CASCADE, 
        related_name="accounts",
        help_text=_("The accounting section this account belongs to"),
        null=True,
        blank=True
    )
    account_number = models.CharField(_("account number"), max_length=6, unique=True, help_text=_("Unique account number"))
    short_name = models.CharField(_("short name"), max_length=50, help_text=_("Abbreviated account name"))
    full_name = models.CharField(_("full name"), max_length=255, help_text=_("Complete account name"))
    is_balance_sheet = models.BooleanField(_("is balance sheet"), default=True, help_text=_("True if this is a balance sheet account, False if it's an income statement account"))
    
    # Additional fields that might be useful based on your data
    budget_account_code = models.CharField(_("budget account code"), max_length=20, null=True, blank=True)
    recovery_status = models.CharField(_("recovery status"), max_length=50, null=True, blank=True)
    financial_statement_group = models.CharField(_("financial statement group"), max_length=50, null=True, blank=True)
    
    class Meta:
        verbose_name = _("General Ledger Account")
        verbose_name_plural = _("General Ledger Accounts")
        ordering = ["account_number"]
    
    def __str__(self):
        return f"{self.account_number} - {self.short_name}"

    @property
    def class_code(self):
        """Returns the accounting class code for this account"""
        return self.account_number[0] if self.account_number else None
    
    @property
    def chapter_code(self):
        """Returns the accounting chapter code for this account"""
        return self.account_number[:2] if self.account_number else None
    
    @property
    def section_code(self):
        """Returns the accounting section code for this account"""
        return self.account_number[:3] if self.account_number else None
