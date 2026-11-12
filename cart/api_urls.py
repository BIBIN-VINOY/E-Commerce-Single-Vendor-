from django.urls import path

from . import api_views


app_name = 'cart_api'


urlpatterns = [

    path(
        '',
        api_views.CartListAPIView.as_view(),
        name='cart-list'
    ),

    path(
        'items/',
        api_views.CartAddAPIView.as_view(),
        name='cart-add'
    ),

    path(
        'items/<uuid:variant_id>/',
        api_views.CartUpdateAPIView.as_view(),
        name='cart-update'
    ),

    path(
        'items/<uuid:variant_id>/remove/',
        api_views.CartRemoveAPIView.as_view(),
        name='cart-remove'
    ),

    path(
        'clear/',
        api_views.CartClearAPIView.as_view(),
        name='cart-clear'
    ),

]