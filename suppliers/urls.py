# apps/suppliers/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    SupplierViewSet, ContactViewSet, BankingInformationViewSet,
    SupplierRoleViewSet, SupplierPartnerViewSet
)

# Configuration du routeur DRF pour les endpoints API
router = DefaultRouter()
router.register(r'suppliers', SupplierViewSet)
router.register(r'contacts', ContactViewSet)
router.register(r'banking', BankingInformationViewSet)
router.register(r'roles', SupplierRoleViewSet)
router.register(r'partners', SupplierPartnerViewSet)

urlpatterns = [
    # Endpoints API
    path('', include(router.urls)),
    
    # Si vous ajoutez plus tard des vues Django classiques, vous pourrez les ajouter ici
    # path('', views.supplier_list, name='supplier-list'),
    # path('<int:pk>/', views.supplier_detail, name='supplier-detail'),
]