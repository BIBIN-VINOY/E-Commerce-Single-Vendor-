from django.urls import path

from . import api_views


app_name = 'wishlist_api'


urlpatterns = [

    path(
        '',
        api_views.WishlistListAPIView.as_view(),
        name='wishlist-list'
    ),

    path(
        'items/',
        api_views.WishlistAddAPIView.as_view(),
        name='wishlist-add'
    ),

    path(
        'items/<uuid:variant_id>/',
        api_views.WishlistRemoveAPIView.as_view(),
        name='wishlist-remove'
    ),

    path(
        'clear/',
        api_views.WishlistClearAPIView.as_view(),
        name='wishlist-clear'
    ),

]