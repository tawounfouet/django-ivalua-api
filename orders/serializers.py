from rest_framework import serializers
from .models import Order, OrderContact, OrderItem, OrderAddress


class OrderAddressSerializer(serializers.ModelSerializer):
    """
    Serializer for OrderAddress model.
    
    Handles address information associated with orders.
    """
    class Meta:
        model = OrderAddress
        fields = [
            'id', 'type', 'number', 'name_complement', 'street', 
            'street_complement', 'zip_code', 'city', 'country_code', 
            'country_label'
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for OrderItem model.
    
    Handles individual items within an order.
    """
    class Meta:
        model = OrderItem
        fields = [
            'id', 'item_id', 'label', 'family_label', 'family_node', 
            'family_level', 'quantity', 'total_amount'
        ]


class OrderContactSerializer(serializers.ModelSerializer):
    """
    Serializer for OrderContact model.
    
    Handles contact information associated with orders.
    """
    class Meta:
        model = OrderContact
        fields = [
            'id', 'requester_firstname', 'requester_lastname', 'requester_email',
            'billing_firstname', 'billing_lastname', 'billing_email',
            'delivery_firstname', 'delivery_lastname', 'delivery_email',
            'supplier_firstname', 'supplier_lastname', 'supplier_email'
        ]


class OrderListSerializer(serializers.ModelSerializer):
    """
    Serializer for Order model (list view).
    
    Provides basic order information for list displays.
    """
    supplier_name = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_code', 'order_label', 'supplier_name', 
            'items_total_amount', 'currency_code', 'status', 'order_date'
        ]
    
    def get_supplier_name(self, obj):
        """Return supplier name, either from related supplier or from order_sup_name field."""
        if obj.supplier:
            return obj.supplier.supplier_name
        return obj.order_sup_name
    
    def get_status(self, obj):
        """Return status label."""
        return obj.get_status_code_display()


class OrderDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for Order model (detail view).
    
    Provides full order information with nested related data.
    """
    contacts = OrderContactSerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    addresses = OrderAddressSerializer(many=True, read_only=True)
    supplier_name = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'object_id', 'ord_id_origin', 'order_code', 'order_label',
            'order_type_code', 'ord_ext_code', 'ord_ref', 'basket_id',
            'supplier', 'supplier_name', 'order_sup_id', 'order_sup_name',
            'sup_nat_id', 'sup_nat_id_type', 'created', 'modified',
            'login_created', 'login_modified', 'status_code', 'status',
            'order_date', 'items_total_amount', 'currency_code',
            'comment', 'inco_code', 'inco_place', 'payterm_code',
            'payterm_label', 'payment_type_code', 'payment_type_label',
            'free_budget', 'amendment_num', 'track_timesheet',
            'legal_comp_code', 'legal_comp_legal_form', 'legal_comp_label',
            'orga_label', 'orga_level', 'orga_node',
            'contacts', 'items', 'addresses'
        ]
    
    def get_supplier_name(self, obj):
        """Return supplier name, either from related supplier or from order_sup_name field."""
        if obj.supplier:
            return obj.supplier.supplier_name
        return obj.order_sup_name
    
    def get_status(self, obj):
        """Return status label."""
        return obj.get_status_code_display()
