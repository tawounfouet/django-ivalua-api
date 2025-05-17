from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Sum
from .models import (
    Order, OrderContact, OrderItem, OrderAddress
)


# Inlines
class OrderContactInline(admin.StackedInline):
    """Inline admin for order contacts."""
    model = OrderContact
    can_delete = False
    verbose_name = _("Contacts")
    verbose_name_plural = _("Contacts")
    max_num = 1
    fields = (
        ('requester_firstname', 'requester_lastname', 'requester_email'),
        ('billing_firstname', 'billing_lastname', 'billing_email'),
        ('delivery_firstname', 'delivery_lastname', 'delivery_email'),
        ('supplier_firstname', 'supplier_lastname', 'supplier_email'),
    )


class OrderItemInline(admin.TabularInline):
    """Inline admin for order items."""
    model = OrderItem
    extra = 0
    verbose_name = _("Item")
    verbose_name_plural = _("Items")
    fields = ('item_id', 'label', 'family_label', 'quantity', 'total_amount')
    readonly_fields = ('item_id',)


class OrderAddressInline(admin.TabularInline):
    """Inline admin for order addresses."""
    model = OrderAddress
    extra = 0
    verbose_name = _("Address")
    verbose_name_plural = _("Addresses")
    fields = ('type', 'street', 'zip_code', 'city', 'country_label')


# Main Admin Models
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin configuration for orders."""
    list_display = ('order_code', 'order_label', 'order_sup_name', 'formatted_amount', 'status_badge', 'order_date')
    list_filter = ('status_code', 'order_type_code', 'created', 'order_date', 'currency_code')
    search_fields = ('order_code', 'order_label', 'order_sup_name', 'legal_comp_label')
    readonly_fields = ('created_at', 'updated_at', 'supplier_link', 'items_count', 'items_total_amount')
    list_per_page = 25
    date_hierarchy = 'created'
    save_on_top = True
    inlines = [OrderContactInline, OrderItemInline, OrderAddressInline]
    actions = ['mark_as_approved', 'mark_as_sent', 'mark_as_received', 'export_orders']
    
    fieldsets = (
        (_('Order Information'), {
            'fields': (
                'order_code', 'order_label', 'order_type_code', 'ord_ext_code', 
                'ord_ref', 'basket_id', 'status_code', 'status_label', 'order_date'
            )
        }),
        (_('Supplier Information'), {
            'fields': (
                'supplier', 'supplier_link', 'order_sup_id', 'order_sup_name', 
                'sup_nat_id', 'sup_nat_id_type'
            )
        }),
        (_('Financial Information'), {
            'fields': (
                'items_count', 'items_total_amount', 'currency_code', 
                'free_budget', 'payterm_code', 'payterm_label',
                'payment_type_code', 'payment_type_label'
            )
        }),
        (_('Shipping Information'), {
            'fields': ('inco_code', 'inco_place'),
            'classes': ('collapse',)
        }),
        (_('Organization Information'), {
            'fields': (
                'legal_comp_code', 'legal_comp_legal_form', 'legal_comp_label',
                'orga_label', 'orga_level', 'orga_node'
            ),
            'classes': ('collapse',)
        }),
        (_('Additional Information'), {
            'fields': (
                'comment', 'amendment_num', 'track_timesheet'
            ),
            'classes': ('collapse',)
        }),
        (_('System Information'), {
            'fields': (
                'object_id', 'ord_id_origin', 'created', 'modified',
                'login_created', 'login_modified', 'created_at', 'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        """Enhance the queryset with annotations."""
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _items_count=Count('items', distinct=True)
        )
        return queryset

    def items_count(self, obj):
        """Return the number of items in this order."""
        return obj._items_count if hasattr(obj, '_items_count') else obj.items.count()
    items_count.short_description = _("Items Count")

    def formatted_amount(self, obj):
        """Format the total amount with currency."""
        return f"{obj.items_total_amount} {obj.currency_code}"
    formatted_amount.short_description = _("Total Amount")

    def status_badge(self, obj):
        """Display a colored badge for status."""
        status_colors = {
            'ini': 'secondary',
            'dra': 'info',
            'sub': 'primary',
            'app': 'success',
            'rej': 'danger',
            'sen': 'warning',
            'ack': 'info',
            'par': 'info',
            'rec': 'success',
            'can': 'danger',
            'clo': 'dark',
            'end': 'dark',
        }
        color = status_colors.get(obj.status_code, 'secondary')
        return format_html(
            '<span class="badge badge-pill badge-{}">{}</span>',
            color, obj.get_status_code_display()
        )
    status_badge.short_description = _("Status")

    def supplier_link(self, obj):
        """Create a link to the associated supplier."""
        if obj.supplier:
            url = reverse('admin:suppliers_supplier_change', args=[obj.supplier.pk])
            return format_html('<a href="{}">{}</a>', url, obj.supplier.supplier_name)
        elif obj.order_sup_name:
            return obj.order_sup_name
        return "-"
    supplier_link.short_description = _("Supplier")

    def mark_as_approved(self, request, queryset):
        """Mark selected orders as approved."""
        updated = queryset.update(status_code='app', status_label=_('Approved'))
        self.message_user(request, _(f"{updated} orders were successfully marked as approved."))
    mark_as_approved.short_description = _("Mark selected orders as approved")

    def mark_as_sent(self, request, queryset):
        """Mark selected orders as sent to supplier."""
        updated = queryset.update(status_code='sen', status_label=_('Sent to supplier'))
        self.message_user(request, _(f"{updated} orders were successfully marked as sent to supplier."))
    mark_as_sent.short_description = _("Mark selected orders as sent to supplier")

    def mark_as_received(self, request, queryset):
        """Mark selected orders as received."""
        updated = queryset.update(status_code='rec', status_label=_('Received'))
        self.message_user(request, _(f"{updated} orders were successfully marked as received."))
    mark_as_received.short_description = _("Mark selected orders as received")

    def export_orders(self, request, queryset):
        """Export selected orders to CSV."""
        # This would be implemented with custom export logic
        self.message_user(request, _("Export functionality will be implemented in the future."))
    export_orders.short_description = _("Export selected orders to CSV")


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin configuration for order items."""
    list_display = ('label', 'order_link', 'quantity', 'total_amount', 'family_label')
    list_filter = ('family_level',)
    search_fields = ('label', 'order__order_code', 'family_label')
    
    def order_link(self, obj):
        """Create a link to the associated order."""
        url = reverse('admin:orders_order_change', args=[obj.order.pk])
        return format_html('<a href="{}">{}</a>', url, obj.order.order_code)
    order_link.short_description = _("Order")


@admin.register(OrderAddress)
class OrderAddressAdmin(admin.ModelAdmin):
    """Admin configuration for order addresses."""
    list_display = ('type', 'order_link', 'street', 'zip_code', 'city', 'country_label')
    list_filter = ('type', 'country_code')
    search_fields = ('street', 'city', 'order__order_code')
    
    def order_link(self, obj):
        """Create a link to the associated order."""
        url = reverse('admin:orders_order_change', args=[obj.order.pk])
        return format_html('<a href="{}">{}</a>', url, obj.order.order_code)
    order_link.short_description = _("Order")
