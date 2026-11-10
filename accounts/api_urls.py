from django.urls import path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .api_views import (
    RegisterAPIView,
    UserProfileAPIView,
    LogoutAPIView,
    AddressListCreateAPIView,
    AddressDetailAPIView,
    SetDefaultAddressAPIView,
)


urlpatterns = [

    # Authentication

    path(
        'register/',
        RegisterAPIView.as_view(),
        name='api_register'
    ),

    path(
        'login/',
        TokenObtainPairView.as_view(),
        name='api_login'
    ),

    path(
        'token/refresh/',
        TokenRefreshView.as_view(),
        name='api_token_refresh'
    ),

    path(
        'logout/',
        LogoutAPIView.as_view(),
        name='api_logout'
    ),

    # Profile

    path(
        'profile/',
        UserProfileAPIView.as_view(),
        name='api_profile'
    ),

    # Addresses

    path(
        'addresses/',
        AddressListCreateAPIView.as_view(),
        name='address_list_create'
    ),

    path(
        'addresses/<int:pk>/',
        AddressDetailAPIView.as_view(),
        name='address_detail'
    ),

    path(
        'addresses/<int:pk>/set-default/',
        SetDefaultAddressAPIView.as_view(),
        name='set_default_address'
    ),

]