from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import BaseModel
from django.utils import timezone


class FiscalYear(BaseModel):
    """
    Represents a fiscal or accounting year.
    
    A fiscal year is a period used for accounting purposes and preparing financial statements.
    """
    year = models.PositiveIntegerField(_("year"), unique=True, help_text=_("The numeric year (e.g., 2023)"))
    name = models.CharField(_("name"), max_length=255, help_text=_("Name of the fiscal year"))
    start_date = models.DateField(_("start date"), help_text=_("Start date of the fiscal year"))
    end_date = models.DateField(_("end date"), help_text=_("End date of the fiscal year"))
    is_closed = models.BooleanField(_("is closed"), default=False, help_text=_("Whether the fiscal year is closed for posting"))
    is_current = models.BooleanField(_("is current"), default=False, help_text=_("Whether this is the current fiscal year"))
    
    class Meta:
        verbose_name = _("Fiscal Year")
        verbose_name_plural = _("Fiscal Years")
        ordering = ["-year"]
    
    def __str__(self):
        return f"{self.name} ({self.year})"
    
    def save(self, *args, **kwargs):
        if self.is_current:
            # Ensure only one fiscal year is marked as current
            FiscalYear.objects.filter(is_current=True).exclude(pk=self.pk).update(is_current=False)
        super().save(*args, **kwargs)


class AccountingType(BaseModel):
    """
    Represents types of accounting (e.g., auxiliary accounting).
    """
    code = models.CharField(_("code"), max_length=3, unique=True, help_text=_("Unique code for the accounting type"))
    short_name = models.CharField(_("short name"), max_length=50, help_text=_("Short name of the accounting type"))
    full_name = models.CharField(_("full name"), max_length=255, help_text=_("Full name of the accounting type"))
    nature = models.CharField(_("nature"), max_length=50, null=True, blank=True, help_text=_("Nature of the accounting type"))
    
    class Meta:
        verbose_name = _("Accounting Type")
        verbose_name_plural = _("Accounting Types")
        ordering = ["code"]
    
    def __str__(self):
        return f"{self.code} - {self.full_name}"


class AccountingJournal(BaseModel):
    """
    Represents an accounting journal.
    
    In accounting, a journal is a record where transactions are recorded before being transferred
    to ledger accounts.
    """
    id_journal = models.CharField(_("journal ID"), max_length=10, unique=True, help_text=_("Unique journal identifier"))
    code = models.CharField(_("code"), max_length=3, help_text=_("Journal code"))
    short_name = models.CharField(_("short name"), max_length=10, help_text=_("Short name/description of the journal"))
    name = models.CharField(_("name"), max_length=255, help_text=_("Full name of the journal"))
    is_opening_balance = models.BooleanField(_("is opening balance"), default=False, help_text=_("Whether this journal is used for opening balance entries"))
    company_code = models.CharField(_("company code"), max_length=10, null=True, blank=True, help_text=_("Company code associated with this journal"))
    
    class Meta:
        verbose_name = _("Accounting Journal")
        verbose_name_plural = _("Accounting Journals")
        ordering = ["code"]
    
    def __str__(self):
        return f"{self.code} - {self.name}"
