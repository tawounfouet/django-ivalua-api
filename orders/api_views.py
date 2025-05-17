from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta

from .models import Order, OrderContact, OrderItem, OrderAddress
from .serializers import (
    OrderListSerializer, OrderDetailSerializer, 
    OrderContactSerializer, OrderItemSerializer, OrderAddressSerializer
)


class OrderViewSet(viewsets.ModelViewSet):
    """
    API endpoint for orders with full CRUD operations.
    
    This ViewSet provides complete operations for managing orders:
    - List all orders with filtering, searching and pagination
    - Retrieve a specific order by ID
    - Create new orders
    - Update existing orders
    - Delete orders (mark as deleted)
    - Additional custom endpoints for related data
    
    This endpoint follows the format defined in the Ivalua API specification.
    """
    queryset = Order.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status_code', 'order_type_code', 'created', 'order_date']
    search_fields = ['order_code', 'order_label', 'order_sup_name', 'legal_comp_label']
    ordering_fields = ['order_code', 'order_date', 'created', 'updated_at', 'items_total_amount']
    ordering = ['-created']
    
    def get_serializer_class(self):
        """
        Return the appropriate serializer based on the current action.
        
        Different actions require different serializers:
        - list: Basic serializer with minimal fields for listing
        - retrieve: Detailed serializer with all fields and related data
        
        Returns:
            Serializer class appropriate for the current action
        """
        if self.action == 'list':
            return OrderListSerializer
        elif self.action == 'retrieve':
            return OrderDetailSerializer
        return OrderListSerializer
    
    def list(self, request, *args, **kwargs):
        """
        List orders with filter options.
        
        This endpoint supports both 'full' and 'diff' modes:
        - 'full': Returns all orders
        - 'diff': Returns orders modified based on criteria
        
        Query parameters:
        - format: (Optional) Response format ('json')
        - mode: (Optional) Retrieval mode ('full' or 'diff')
        - order_id: (Optional) Filter by order ID
        - order_code: (Optional) Filter by order code
        - sup_id: (Optional) Filter by supplier ID
        - sup_name: (Optional) Filter by supplier name
        - date_from: (Optional) Filter by creation date from
        - date_to: (Optional) Filter by creation date to
        - status: (Optional) Filter by order status
        - search: (Optional) Search across multiple fields
        - ordering: (Optional) Field to order results by
        
        Returns:
            Response: Formatted list of orders
        """
        # Get request parameters
        format_param = request.query_params.get('format', 'json')
        mode = request.query_params.get('mode', 'full')
        
        # Apply filters
        queryset = self.filter_queryset(self.get_queryset())
        
        # Apply specific filters based on query parameters
        order_id = request.query_params.get('order_id')
        order_code = request.query_params.get('order_code')
        sup_id = request.query_params.get('sup_id')
        sup_name = request.query_params.get('sup_name')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        status = request.query_params.get('status')
        
        if order_id:
            queryset = queryset.filter(Q(id=order_id) | Q(object_id=order_id))
        
        if order_code:
            queryset = queryset.filter(order_code=order_code)
        
        if sup_id:
            queryset = queryset.filter(Q(supplier_id=sup_id) | Q(order_sup_id=sup_id))
        
        if sup_name:
            queryset = queryset.filter(Q(supplier__supplier_name__icontains=sup_name) | 
                                     Q(order_sup_name__icontains=sup_name))
        
        if status:
            queryset = queryset.filter(status_code=status)
        
        if date_from:
            try:
                date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(created__gte=date_from)
            except ValueError:
                pass
        
        if date_to:
            try:
                date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
                queryset = queryset.filter(created__lte=date_to)
            except ValueError:
                pass
        
        # Apply pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(self.format_orders_response(serializer.data))
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(self.format_orders_response(serializer.data))
    
    def format_orders_response(self, data):
        """
        Format the response to match the Ivalua API structure.
        
        Args:
            data: Serialized order data
            
        Returns:
            dict: Formatted response with header and orders list
        """
        count = len(data)
        return {
            'header': {
                'apiName': 'Orders',
                'format': 'json',
                'totalRow': count
            },
            'orders': data
        }
    
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a single order with detailed information.
        
        Returns:
            Response: Detailed order data with nested related objects
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        # Format the response to match the Ivalua API structure
        return Response({
            'header': {
                'apiName': 'Orders',
                'format': 'json',
                'totalRow': 1
            },
            'order': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def items(self, request, pk=None):
        """
        List all items for a specific order.
        
        Args:
            pk: Primary key of the order
            
        Returns:
            Response: List of order items
        """
        order = self.get_object()
        items = order.items.all()
        serializer = OrderItemSerializer(items, many=True)
        
        return Response({
            'header': {
                'apiName': 'OrderItems',
                'format': 'json',
                'totalRow': items.count()
            },
            'items': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def contacts(self, request, pk=None):
        """
        Get contact information for a specific order.
        
        Args:
            pk: Primary key of the order
            
        Returns:
            Response: Order contact information
        """
        order = self.get_object()
        try:
            contact = order.contacts.get()
            serializer = OrderContactSerializer(contact)
            
            return Response({
                'header': {
                    'apiName': 'OrderContacts',
                    'format': 'json',
                    'totalRow': 1
                },
                'contact': serializer.data
            })
        except OrderContact.DoesNotExist:
            return Response({
                'header': {
                    'apiName': 'OrderContacts',
                    'format': 'json',
                    'totalRow': 0
                },
                'contact': None
            })
    
    @action(detail=True, methods=['get'])
    def addresses(self, request, pk=None):
        """
        List all addresses for a specific order.
        
        Args:
            pk: Primary key of the order
            
        Returns:
            Response: List of order addresses
        """
        order = self.get_object()
        addresses = order.addresses.all()
        serializer = OrderAddressSerializer(addresses, many=True)
        
        return Response({
            'header': {
                'apiName': 'OrderAddresses',
                'format': 'json',
                'totalRow': addresses.count()
            },
            'addresses': serializer.data
        })


class OrderItemViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows order items to be viewed.
    
    This endpoint is read-only and provides list and retrieve operations.
    """
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['order', 'family_level']
    search_fields = ['label', 'family_label']


class OrderAddressViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows order addresses to be viewed.
    
    This endpoint is read-only and provides list and retrieve operations.
    """
    queryset = OrderAddress.objects.all()
    serializer_class = OrderAddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['order', 'type']
    search_fields = ['street', 'city', 'country_label']
