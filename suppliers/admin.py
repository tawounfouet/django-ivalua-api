# apps/suppliers/admin.py
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from .models import (
    Supplier, SupplierAddress, BankingInformation, 
    Contact, ContactRole, SupplierPartner, SupplierRole
)


# Inlines
class SupplierAddressInline(admin.StackedInline):
    """Inline admin for supplier addresses."""
    model = SupplierAddress
    can_delete = False
    verbose_name = _("Address")
    verbose_name_plural = _("Address")
    fields = ('adr1', 'adr2', 'adr3', 'zip', 'city')


class BankingInformationInline(admin.TabularInline):
    """Inline admin for banking information."""
    model = BankingInformation
    extra = 0
    verbose_name = _("Banking Information")
    verbose_name_plural = _("Banking Information")
    fields = ('iban', 'bic', 'bank_label', 'country_code')


class ContactInline(admin.TabularInline):
    """Inline admin for contacts."""
    model = Contact
    extra = 0
    fields = ('first_name', 'last_name', 'email', 'is_internal')


class ContactRoleInline(admin.TabularInline):
    """Inline admin for contact roles."""
    model = ContactRole
    extra = 0
    fields = ('code', 'label')


class SupplierPartnerInline(admin.TabularInline):
    """Inline admin for supplier partners."""
    model = SupplierPartner
    extra = 0
    fields = ('orga_level', 'orga_node', 'num_part', 'status')


class SupplierRoleInline(admin.TabularInline):
    """Inline admin for supplier roles."""
    model = SupplierRole
    extra = 0
    fields = ('orga_level', 'orga_node', 'role_code', 'role_label', 'begin_date', 'end_date', 'status')


# Main Admin Models
@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    """Admin configuration for suppliers."""
    list_display = ('code', 'supplier_name', 'supplier_type', 'nat_id', 'has_banking_info', 'status', 'creation_system_date')
    list_filter = ('status', 'type_ikos_code', 'is_physical_person', 'creation_system_date')
    search_fields = ('code', 'supplier_name', 'legal_name', 'nat_id', 'siret', 'siren')
    readonly_fields = ('created_at', 'updated_at', 'address_link', 'banking_count', 'contacts_count', 'roles_count')
    list_per_page = 25
    date_hierarchy = 'creation_system_date'
    save_on_top = True
    actions = ['mark_as_valid', 'mark_as_archived', 'export_suppliers']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                'code', 'erp_code', 'supplier_name', 'legal_name', 'website', 
                'status', 'type_ikos_code'
            )
        }),
        (_('Identification'), {
            'fields': (
                'nat_id_type', 'nat_id', 'siret', 'siren', 'duns', 'tva_intracom',
                'ape_naf'
            )
        }),
        (_('Person Details'), {
            'fields': ('is_physical_person', 'title', 'first_name', 'last_name'),
            'classes': ('collapse',),
            'description': _("Only applicable if the supplier is a physical person")
        }),
        (_('Legal Information'), {
            'fields': ('legal_code', 'legal_structure', 'creation_year'),
            'classes': ('collapse',)
        }),
        (_('Related Information'), {
            'fields': ('address_link', 'banking_count', 'contacts_count', 'roles_count'),
        }),
        (_('System Information'), {
            'fields': (
                'object_id', 'creation_system_date', 'modification_system_date',
                'deleted_system_date', 'latest_modification_date', 'created_at', 'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    inlines = [SupplierAddressInline, BankingInformationInline, ContactInline, SupplierPartnerInline, SupplierRoleInline]
    
    def get_queryset(self, request):
        """Optimize the queryset by prefetching related data."""
        return super().get_queryset(request).prefetch_related(
            'address', 'banking_informations', 'contacts', 'roles'
        ).annotate(
            bank_count=Count('banking_informations', distinct=True),
            contact_count=Count('contacts', distinct=True),
            role_count=Count('roles', distinct=True)
        )
    
    def supplier_type(self, obj):
        """Format the supplier type."""
        return obj.get_type_ikos_code_display()
    supplier_type.short_description = _("Type")
    supplier_type.admin_order_field = 'type_ikos_code'
    
    def has_banking_info(self, obj):
        """Check if supplier has banking information."""
        return bool(obj.banking_informations.exists())
    has_banking_info.boolean = True
    has_banking_info.short_description = _("Banking Info")
    
    def address_link(self, obj):
        """Create a link to the supplier's address if it exists."""
        if hasattr(obj, 'address'):
            return format_html(
                '<a href="{}">{}</a>',
                reverse('admin:suppliers_supplieraddress_change', args=[obj.address.id]),
                str(obj.address)
            )
        return _("No address")
    address_link.short_description = _("Address")
    
    def banking_count(self, obj):
        """Get number of banking information records."""
        if hasattr(obj, 'bank_count'):
            count = obj.bank_count
        else:
            count = obj.banking_informations.count()
        
        if count > 0:
            return format_html(
                '<a href="{}?supplier__id__exact={}">{} banking records</a>',
                reverse('admin:suppliers_bankinginformation_changelist'),
                obj.id,
                count
            )
        return _("No banking information")
    banking_count.short_description = _("Banking Information")
    
    def contacts_count(self, obj):
        """Get number of contacts."""
        if hasattr(obj, 'contact_count'):
            count = obj.contact_count
        else:
            count = obj.contacts.count()
        
        if count > 0:
            return format_html(
                '<a href="{}?supplier__id__exact={}">{} contacts</a>',
                reverse('admin:suppliers_contact_changelist'),
                obj.id,
                count
            )
        return _("No contacts")
    contacts_count.short_description = _("Contacts")
    
    def roles_count(self, obj):
        """Get number of roles."""
        if hasattr(obj, 'role_count'):
            count = obj.role_count
        else:
            count = obj.roles.count()
        
        if count > 0:
            return format_html(
                '<a href="{}?supplier__id__exact={}">{} roles</a>',
                reverse('admin:suppliers_supplierrole_changelist'),
                obj.id,
                count
            )
        return _("No roles")
    roles_count.short_description = _("Roles")
    
    # Custom actions
    def mark_as_valid(self, request, queryset):
        """Mark selected suppliers as valid."""
        from core.models import StatusChoices
        updated = queryset.update(status=StatusChoices.VALID)
        self.message_user(request, _("%(count)d suppliers were successfully marked as valid.") % {'count': updated})
    mark_as_valid.short_description = _("Mark selected suppliers as valid")
    
    def mark_as_archived(self, request, queryset):
        """Mark selected suppliers as archived."""
        from core.models import StatusChoices
        updated = queryset.update(status=StatusChoices.ARCHIVED)
        self.message_user(request, _("%(count)d suppliers were successfully archived.") % {'count': updated})
    mark_as_archived.short_description = _("Mark selected suppliers as archived")
    
    def export_suppliers(self, request, queryset):
        """Export selected suppliers to CSV."""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="suppliers.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Code', 'Name', 'Type', 'National ID', 'SIRET', 'SIREN', 
            'Status', 'Creation Date', 'Address'
        ])
        
        for supplier in queryset:
            address = getattr(supplier, 'address', None)
            address_str = f"{address.zip} {address.city}" if address else ""
            
            writer.writerow([
                supplier.code,
                supplier.supplier_name,
                supplier.get_type_ikos_code_display(),
                supplier.nat_id,
                supplier.siret,
                supplier.siren,
                supplier.get_status_display(),
                supplier.creation_system_date,
                address_str
            ])
        
        return response
    export_suppliers.short_description = _("Export selected suppliers to CSV")


@admin.register(BankingInformation)
class BankingInformationAdmin(admin.ModelAdmin):
    """Admin configuration for banking information."""
    list_display = ('supplier_link', 'bank_label', 'masked_iban', 'bic', 'country_code')
    list_filter = ('country_code', 'creation_account_date')
    search_fields = ('supplier__code', 'supplier__supplier_name', 'iban', 'bic', 'bank_label')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (_('Supplier'), {
            'fields': ('supplier',)
        }),
        (_('Banking Details'), {
            'fields': (
                'account_number', 'bank_code', 'counter_code', 'rib_key',
                'iban', 'bic', 'bank_label', 'country_code'
            )
        }),
        (_('Additional Information'), {
            'fields': (
                'international_pay_id', 'bban', 
                'creation_account_date', 'modification_account_date'
            ),
            'classes': ('collapse',)
        }),
        (_('System Information'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def supplier_link(self, obj):
        """Create a link to the supplier."""
        return format_html(
            '<a href="{}">{} - {}</a>',
            reverse('admin:suppliers_supplier_change', args=[obj.supplier.id]),
            obj.supplier.code,
            obj.supplier.supplier_name
        )
    supplier_link.short_description = _("Supplier")
    supplier_link.admin_order_field = 'supplier__supplier_name'
    
    def masked_iban(self, obj):
        """Display a masked version of the IBAN for security."""
        if not obj.iban:
            return ""
        return f"{'*' * (len(obj.iban) - 4)}{obj.iban[-4:]}"
    masked_iban.short_description = _("IBAN")


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """Admin configuration for contacts."""
    list_display = ('get_full_name', 'supplier_link', 'email', 'is_internal', 'roles_list')
    list_filter = ('is_internal', 'supplier__type_ikos_code')
    search_fields = ('first_name', 'last_name', 'email', 'supplier__supplier_name', 'supplier__code')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (_('Contact Information'), {
            'fields': (
                'first_name', 'last_name', 'email', 'is_internal', 'login'
            )
        }),
        (_('Supplier'), {
            'fields': ('supplier',)
        }),
        (_('System Information'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    inlines = [ContactRoleInline]
    
    def supplier_link(self, obj):
        """Create a link to the supplier."""
        return format_html(
            '<a href="{}">{} - {}</a>',
            reverse('admin:suppliers_supplier_change', args=[obj.supplier.id]),
            obj.supplier.code,
            obj.supplier.supplier_name
        )
    supplier_link.short_description = _("Supplier")
    
    def get_full_name(self, obj):
        """Get the contact's full name."""
        return obj.get_full_name()
    get_full_name.short_description = _("Name")
    
    def roles_list(self, obj):
        """List the contact's roles."""
        roles = obj.roles.all()
        if not roles:
            return _("No roles")
        
        roles_html = ", ".join(f"{role.label}" for role in roles[:3])
        if len(roles) > 3:
            roles_html += ", ..."
        return roles_html
    roles_list.short_description = _("Roles")


@admin.register(ContactRole)
class ContactRoleAdmin(admin.ModelAdmin):
    """Admin configuration for contact roles."""
    list_display = ('label', 'code', 'contact_link')
    list_filter = ('code',)
    search_fields = ('label', 'code', 'contact__first_name', 'contact__last_name')
    
    def contact_link(self, obj):
        """Create a link to the contact."""
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:suppliers_contact_change', args=[obj.contact.id]),
            obj.contact.get_full_name()
        )
    contact_link.short_description = _("Contact")


@admin.register(SupplierPartner)
class SupplierPartnerAdmin(admin.ModelAdmin):
    """Admin configuration for supplier partners."""
    list_display = ('supplier_link', 'orga_level', 'orga_node', 'num_part', 'status')
    list_filter = ('orga_level', 'status')
    search_fields = ('supplier__code', 'supplier__supplier_name', 'orga_node')
    
    def supplier_link(self, obj):
        """Create a link to the supplier."""
        return format_html(
            '<a href="{}">{} - {}</a>',
            reverse('admin:suppliers_supplier_change', args=[obj.supplier.id]),
            obj.supplier.code,
            obj.supplier.supplier_name
        )
    supplier_link.short_description = _("Supplier")


@admin.register(SupplierRole)
class SupplierRoleAdmin(admin.ModelAdmin):
    """Admin configuration for supplier roles."""
    list_display = ('supplier_link', 'role_label', 'orga_level', 'orga_node', 'begin_date', 'end_date', 'is_active_status')
    list_filter = ('role_code', 'orga_level', 'status', 'begin_date')
    search_fields = ('supplier__code', 'supplier__supplier_name', 'role_label', 'orga_node')
    date_hierarchy = 'begin_date'
    
    def supplier_link(self, obj):
        """Create a link to the supplier."""
        return format_html(
            '<a href="{}">{} - {}</a>',
            reverse('admin:suppliers_supplier_change', args=[obj.supplier.id]),
            obj.supplier.code,
            obj.supplier.supplier_name
        )
    supplier_link.short_description = _("Supplier")
    
    def is_active_status(self, obj):
        """Check if the role is active."""
        return obj.is_active()
    is_active_status.boolean = True
    is_active_status.short_description = _("Active")