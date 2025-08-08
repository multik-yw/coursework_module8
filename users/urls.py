from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    CustomTokenObtainPairView,
    UserViewSet
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # Users endpoints
    path("users/", UserViewSet.as_view({'get': 'list'}), name="user-list"),
    path("users/<int:pk>/", UserViewSet.as_view({
        'get': 'retrieve',
        'patch': 'update',
        'delete': 'destroy'
    }), name="user-detail"),
    path("users/set_telegram_id/", UserViewSet.as_view({'patch': 'set_telegram_id'}),
         name="user-set-telegram-id"),
]