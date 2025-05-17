from django.db import models

# Create your models here.
# apps/core/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from typing import Optional, Union, Dict, Any


class BaseModel(models.Model):
    """
    Base abstract model that provides common fields for all models.
    
    This base model provides created and modified timestamps that are 
    automatically set when the model is saved.
    
    Attributes:
        created_at (datetime): When the record was created
        updated_at (datetime): When the record was last updated
    """
    created_at = models.DateTimeField(
        _("created at"),
        default=timezone.now,
        editable=False,
        help_text=_("Date and time when the record was created")
    )
    updated_at = models.DateTimeField(_("updated at"), auto_now=True, help_text=_("Date and time when the record was last updated"))
    #updated_at = models.DateTimeField(null=True, auto_now=True)


    class Meta:
        abstract = True
        
    def update_fields(self, **kwargs: Any) -> None:
        """
        Update model fields and save the instance.
        
        Args:
            **kwargs: Field names and values to update
            
        Example:
            >>> user = User.objects.get(id=1)
            >>> user.update_fields(first_name="John", last_name="Doe")
        """
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.save(update_fields=list(kwargs.keys()) + ['updated_at'])


class StatusChoices(models.TextChoices):
    """
    Common status choices used across multiple models.
    
    These statuses represent the lifecycle states of various entities in the system.
    """
    VALID = 'val', _('Valid')
    DELETED = 'del', _('Deleted')
    INITIAL = 'ini', _('Initial')
    DRAFT = 'dra', _('Draft')
    
    
class YesNoChoices(models.TextChoices):
    """
    Yes/No choices for boolean-like fields stored as strings.
    
    Some external systems expect "Yes"/"No" values instead of boolean True/False.
    """
    YES = 'Yes', _('Yes')
    NO = 'No', _('No')