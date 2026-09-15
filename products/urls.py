from django.urls import path
from . import views
app_name = 'products'
urlpatterns=[
    path('<slug:slug>/', views.product_detail, name='product_detail'),
    path('search/', views.product_search, name='product_search'),

]