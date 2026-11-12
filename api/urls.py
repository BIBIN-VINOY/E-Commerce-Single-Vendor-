from django.urls import include, path
from .views import ProtectedTestView

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)


urlpatterns = [

    # Login / Obtain JWT tokens
    path(
        'auth/token/',
        TokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),

    # Refresh access token
    path(
        'auth/token/refresh/',
        TokenRefreshView.as_view(),
        name='token_refresh'
    ),

    # Verify token
    path(
        'auth/token/verify/',
        TokenVerifyView.as_view(),
        name='token_verify'
    ),

    path(
    'test/protected/',
    ProtectedTestView.as_view(),
    name='protected_test'
),

path(
    'accounts/',
    include('accounts.api_urls')
),

path(
        'products/',
        include('products.api_urls')
    ),

path('cart/', include('cart.api_urls')),
path('wishlist/', include('wishlist.api_urls')),

path(
        "orders/",
        include("orders.api_urls"),
    ),

]