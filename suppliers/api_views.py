from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta

from .models import Supplier, Contact, SupplierAddress, BankingInformation, ContactRole, SupplierPartner, SupplierRole
from .serializers import (
    SupplierSerializer, SupplierDetailSerializer, SupplierCreateSerializer, 
    SupplierUpdateSerializer, ContactSerializer, BankingInformationSerializer,
    SupplierAddressSerializer, ContactRoleSerializer, SupplierPartnerSerializer,
    SupplierRoleSerializer
)


class SupplierViewSet(viewsets.ModelViewSet):
    """
    API endpoint for suppliers with full CRUD operations.
    
    This ViewSet provides complete operations for managing suppliers:
    - List all suppliers with filtering, searching and pagination
    - Retrieve a specific supplier by ID
    - Create new suppliers
    - Update existing suppliers
    - Delete suppliers (mark as deleted)
    - Additional custom endpoints for related data
    
    This endpoint follows the format defined in the Ivalua API specification.
    """
    queryset = Supplier.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'type_ikos_code', 'is_physical_person']
    search_fields = ['code', 'supplier_name', 'legal_name', 'nat_id', 'siret', 'siren']
    ordering_fields = ['code', 'supplier_name', 'creation_system_date', 'updated_at']
    ordering = ['-updated_at']
    
    def get_serializer_class(self):
        """
        Return the appropriate serializer based on the current action.
        
        Different actions require different serializers:
        - list: Basic serializer with minimal fields for listing
        - retrieve: Detailed serializer with all fields and related data
        - create: Serializer with validation specific to creation
        - update/partial_update: Serializer with validation specific to updates
        
        Returns:
            Serializer class appropriate for the current action
        """
        if self.action == 'list':
            return SupplierSerializer
        elif self.action == 'retrieve':
            return SupplierDetailSerializer
        elif self.action == 'create':
            return SupplierCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return SupplierUpdateSerializer
        return SupplierSerializer
    
    def list(self, request, *args, **kwargs):
        """
        List suppliers with filter options.
        
        This endpoint supports both 'full' and 'diff' modes:
        - 'full': Returns all suppliers
        - 'diff': Returns suppliers modified based on criteria
        
        Query parameters:
        - format: (Required) Response format ('json' or 'xml')
        - mode: (Required) Retrieval mode ('full' or 'diff')
        - sup_id: (Optional, diff mode) Filter by supplier ID
        - sup_code: (Optional, diff mode) Filter by supplier code
        - nat_id: (Optional, diff mode) Filter by national ID
        - nat_id_type: (Optional, diff mode) Filter by national ID type
        - date_from: (Optional, diff mode) Filter by modification date from
        - date_to: (Optional, diff mode) Filter by modification date to
        - search: (Optional) Search across multiple fields
        - ordering: (Optional) Field to order results by
        - page: (Optional) Page number for pagination
        - page_size: (Optional) Number of items per page
        
        Returns:
            Response: Formatted list of suppliers
        """
        # Get request parameters
        format_param = request.query_params.get('format', 'json')
        mode = request.query_params.get('mode', 'full')
        
        # Validate required parameters
        errors = []
        if format_param not in ['json', 'xml']:
            errors.append({
                'code': 'ERR-QUE-003',
                'message': _('The format must be either "json" or "xml".')
            })
            
        if mode not in ['full', 'diff']:
            errors.append({
                'code': 'ERR-QUE-002',
                'message': _('The mode must be either "full" or "diff".')
            })
            
        # Return errors if validation failed
        if errors:
            return Response({'erreurs': errors}, status=status.HTTP_400_BAD_REQUEST)
            
        # Process 'full' mode - return all suppliers
        if mode == 'full':
            queryset = self.filter_queryset(self.get_queryset())
            
        # Process 'diff' mode - apply filters
        else:  # mode == 'diff'
            # Get filter parameters
            sup_id = request.query_params.get('sup_id')
            sup_code = request.query_params.get('sup_code')
            nat_id = request.query_params.get('nat_id')
            nat_id_type = request.query_params.get('nat_id_type')
            date_from = request.query_params.get('date_from')
            date_to = request.query_params.get('date_to')
            
            # Validate at least one filter is provided
            if not any([sup_id, sup_code, nat_id, nat_id_type, date_from, date_to]):
                errors.append({
                    'code': 'ERR-QUE-004',
                    'message': _('At least one filter parameter must be provided in "diff" mode.')
                })
                return Response({'erreurs': errors}, status=status.HTTP_400_BAD_REQUEST)
                
            # Handle date validations
            if (date_from and not date_to) or (date_to and not date_from):
                errors.append({
                    'code': 'ERR-QUE-005',
                    'message': _('Both date_from and date_to are required when filtering by date.')
                })
                return Response({'erreurs': errors}, status=status.HTTP_400_BAD_REQUEST)
                
            if date_from and date_to:
                try:
                    from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
                    to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
                    
                    if from_date > to_date:
                        errors.append({
                            'code': 'ERR-QUE-006',
                            'message': _('date_from must be earlier than date_to.')
                        })
                        return Response({'erreurs': errors}, status=status.HTTP_400_BAD_REQUEST)
                        
                    # Check if date range is within limits (2 months)
                    if to_date - from_date > timedelta(days=62):  # ~2 months
                        errors.append({
                            'code': 'ERR-QUE-007',
                            'message': _('The interval between date_from and date_to cannot exceed 2 months.')
                        })
                        return Response({'erreurs': errors}, status=status.HTTP_400_BAD_REQUEST)
                except ValueError:
                    errors.append({
                        'code': 'ERR-QUE-008',
                        'message': _('Invalid date format. Use YYYY-MM-DD.')
                    })
                    return Response({'erreurs': errors}, status=status.HTTP_400_BAD_REQUEST)
            
            # Apply filters to queryset
            filter_kwargs = {}
            q_filters = Q()
            
            if sup_id:
                filter_kwargs['id'] = sup_id
                
            if sup_code:
                filter_kwargs['code'] = sup_code
                
            if nat_id:
                filter_kwargs['nat_id'] = nat_id
                
            if nat_id_type:
                filter_kwargs['nat_id_type'] = nat_id_type
                
            if date_from and date_to:
                q_filters |= Q(
                    latest_modification_date__gte=from_date,
                    latest_modification_date__lte=to_date
                )
                q_filters |= Q(
                    creation_system_date__gte=from_date,
                    creation_system_date__lte=to_date
                )
            
            queryset = self.filter_queryset(
                self.get_queryset().filter(**filter_kwargs).filter(q_filters)
            )
            
        # Paginate and serialize the results
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = self.get_paginated_response(serializer.data)
        else:
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data
            
        # Format response according to API spec
        response_data = {
            'header': {
                'apiName': 'suppliers',
                'format': format_param,
                'totalRow': len(data) if isinstance(data, list) else len(data['results']) if 'results' in data else 0
            },
            'suppliers': data if isinstance(data, list) else data.get('results', [])
        }
        
        return Response(response_data)
    
    def create(self, request, *args, **kwargs):
        """
        Create a new supplier.
        
        Validates the input data and creates a new supplier record with related
        data such as address and banking information if provided.
        
        Returns:
            Response: Created supplier data with status 201
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create supplier with validated data
        try:
            supplier = serializer.save()
            
            # Log the creation
            from django.utils import timezone
            supplier.creation_system_date = timezone.now().date()
            supplier.login_created = request.user.username if hasattr(request, 'user') and request.user.is_authenticated else None
            supplier.save()
            
            # Return created supplier with detail serializer
            detail_serializer = SupplierDetailSerializer(supplier, context={'request': request})
            headers = self.get_success_headers(serializer.data)
            return Response(detail_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            
        except Exception as e:
            return Response({
                'error': _('Failed to create supplier'),
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        """
        Update an existing supplier.
        
        Updates a supplier and its related data. For partial updates, use PATCH instead.
        
        Returns:
            Response: Updated supplier data
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        try:
            supplier = serializer.save()
            
            # Update modification info
            from django.utils import timezone
            supplier.modification_system_date = timezone.now().date()
            supplier.latest_modification_date = timezone.now().date()
            supplier.login_modified = request.user.username if hasattr(request, 'user') and request.user.is_authenticated else None
            supplier.save()
            
            # Return updated supplier with detail serializer
            detail_serializer = SupplierDetailSerializer(supplier, context={'request': request})
            return Response(detail_serializer.data)
            
        except Exception as e:
            return Response({
                'error': _('Failed to update supplier'),
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self, request, *args, **kwargs):
        """
        Partially update a supplier.
        
        Only the fields provided in the request will be updated.
        """
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """
        Soft delete a supplier.
        
        Instead of physically deleting the supplier record, this method marks
        it as deleted by setting the status to 'del' and recording the deletion date.
        
        Returns:
            Response: Empty response with status 204
        """
        supplier = self.get_object()
        
        # Mark as deleted instead of physical deletion
        from django.utils import timezone
        from .models import StatusChoices
        
        supplier.status = StatusChoices.DELETED
        supplier.deleted_system_date = timezone.now().date()
        supplier.save()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['get'])
    def banking(self, request, pk=None):
        """
        Get banking information for a specific supplier.
        
        Args:
            request: HTTP request
            pk: Supplier primary key
            
        Returns:
            Response: List of banking information for the supplier
        """
        supplier = self.get_object()
        banking_info = supplier.banking_informations.all()
        serializer = BankingInformationSerializer(banking_info, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_banking(self, request, pk=None):
        """
        Add banking information to a supplier.
        
        Args:
            request: HTTP request with banking data
            pk: Supplier primary key
            
        Returns:
            Response: Created banking information
        """
        supplier = self.get_object()
        serializer = BankingInformationSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(supplier=supplier)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def contacts(self, request, pk=None):
        """
        Get contacts for a specific supplier.
        
        Args:
            request: HTTP request
            pk: Supplier primary key
            
        Returns:
            Response: List of contacts for the supplier
        """
        supplier = self.get_object()
        contacts = supplier.contacts.all()
        serializer = ContactSerializer(contacts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_contact(self, request, pk=None):
        """
        Add a contact to a supplier.
        
        Args:
            request: HTTP request with contact data
            pk: Supplier primary key
            
        Returns:
            Response: Created contact information
        """
        supplier = self.get_object()
        serializer = ContactSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(supplier=supplier)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get', 'put'])
    def address(self, request, pk=None):
        """
        Get or update the address for a supplier.
        
        Args:
            request: HTTP request (GET or PUT with address data)
            pk: Supplier primary key
            
        Returns:
            Response: Supplier address information
        """
        supplier = self.get_object()
        
        # Get the supplier's address or create a new one if it doesn't exist
        try:
            address = supplier.address
        except SupplierAddress.DoesNotExist:
            if request.method == 'GET':
                return Response({'detail': _('No address found for this supplier')}, 
                                status=status.HTTP_404_NOT_FOUND)
            address = None
        
        if request.method == 'GET':
            serializer = SupplierAddressSerializer(address)
            return Response(serializer.data)
        
        # Update existing address or create new one
        if address:
            serializer = SupplierAddressSerializer(address, data=request.data, partial=True)
        else:
            serializer = SupplierAddressSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(supplier=supplier)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def roles(self, request, pk=None):
        """
        Get roles for a specific supplier.
        
        Args:
            request: HTTP request
            pk: Supplier primary key
            
        Returns:
            Response: List of roles for the supplier
        """
        supplier = self.get_object()
        roles = supplier.roles.all()
        serializer = SupplierRoleSerializer(roles, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_role(self, request, pk=None):
        """
        Add a role to a supplier.
        
        Args:
            request: HTTP request with role data
            pk: Supplier primary key
            
        Returns:
            Response: Created role information
        """
        supplier = self.get_object()
        serializer = SupplierRoleSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(supplier=supplier)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def partners(self, request, pk=None):
        """
        Get partners for a specific supplier.
        
        Args:
            request: HTTP request
            pk: Supplier primary key
            
        Returns:
            Response: List of partners for the supplier
        """
        supplier = self.get_object()
        partners = supplier.partners.all()
        serializer = SupplierPartnerSerializer(partners, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_partner(self, request, pk=None):
        """
        Add a partner to a supplier.
        
        Args:
            request: HTTP request with partner data
            pk: Supplier primary key
            
        Returns:
            Response: Created partner information
        """
        supplier = self.get_object()
        serializer = SupplierPartnerSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(supplier=supplier)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContactViewSet(viewsets.ModelViewSet):
    """
    API endpoint for supplier contacts.
    
    Provides CRUD operations for contacts associated with suppliers.
    """
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['supplier', 'is_internal']
    search_fields = ['first_name', 'last_name', 'email']
    
    @action(detail=True, methods=['get'])
    def roles(self, request, pk=None):
        """Get roles for a specific contact."""
        contact = self.get_object()
        roles = contact.roles.all()
        serializer = ContactRoleSerializer(roles, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_role(self, request, pk=None):
        """Add a role to a contact."""
        contact = self.get_object()
        serializer = ContactRoleSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(contact=contact)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BankingInformationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for banking information.
    
    Provides CRUD operations for banking information associated with suppliers.
    """
    queryset = BankingInformation.objects.all()
    serializer_class = BankingInformationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['supplier', 'country_code']
    search_fields = ['iban', 'bic', 'bank_label']
    
    def perform_create(self, serializer):
        """Add creation date on new banking information."""
        from django.utils import timezone
        serializer.save(creation_account_date=timezone.now().date())
    
    def perform_update(self, serializer):
        """Add modification date on banking information update."""
        from django.utils import timezone
        serializer.save(modification_account_date=timezone.now().date())


class SupplierRoleViewSet(viewsets.ModelViewSet):
    """
    API endpoint for supplier roles.
    
    Provides CRUD operations for roles associated with suppliers.
    """
    queryset = SupplierRole.objects.all()
    serializer_class = SupplierRoleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['supplier', 'orga_level', 'orga_node', 'role_code', 'status']
    search_fields = ['role_label']


class SupplierPartnerViewSet(viewsets.ModelViewSet):
    """
    API endpoint for supplier partners.
    
    Provides CRUD operations for partners associated with suppliers.
    """
    queryset = SupplierPartner.objects.all()
    serializer_class = SupplierPartnerSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['supplier', 'orga_level', 'orga_node', 'status']