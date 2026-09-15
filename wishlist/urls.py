from django.urls import path
from . import views
app_name='wishlist'
urlpatterns=[
    path('',views.wishlist,name='wishlist'),
    path('add/<uuid:pk>/', views.add_to_wishlist,name='add_to_wishlist'),
    path('product_search/',views.product_search,name='product_search'),
    path('wishlist_remove/<uuid:variant_id>/',views.wishlist_remove,name='wishlist_remove'),
]

