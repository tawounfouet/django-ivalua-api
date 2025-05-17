from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .api_views import UserViewSet, EmailTokenObtainPairView
from .views import EmailLoginView, RegisterView

# Configuration du routeur DRF pour les endpoints API
router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    # Endpoints d'authentification JWT personnalisés pour email
    path('api/token/', EmailTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Endpoints API REST
    path('api/', include(router.urls)),
    
    # URLs pour les vues traditionnelles
    path('login/', EmailLoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
]