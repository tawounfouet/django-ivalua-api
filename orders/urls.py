from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import OrderViewSet, OrderItemViewSet, OrderAddressViewSet

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'orders', OrderViewSet)
router.register(r'order-items', OrderItemViewSet)
router.register(r'order-addresses', OrderAddressViewSet)

# The API URLs are determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]
