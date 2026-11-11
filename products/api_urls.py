from django.urls import path

from . import api_views


app_name = 'products_api'


urlpatterns = [

    # Categories
    path(
        'categories/',
        api_views.CategoryListAPIView.as_view(),
        name='category-list'
    ),

    path(
        'categories/<slug:slug>/',
        api_views.CategoryDetailAPIView.as_view(),
        name='category-detail'
    ),

    # Brands
    path(
        'brands/',
        api_views.BrandListAPIView.as_view(),
        name='brand-list'
    ),

    path(
        'brands/<slug:slug>/',
        api_views.BrandDetailAPIView.as_view(),
        name='brand-detail'
    ),

    # Featured products - keep before the product slug route
    path(
        'featured/',
        api_views.FeaturedProductListAPIView.as_view(),
        name='featured-products'
    ),

    # Products
    path(
        '',
        api_views.ProductListAPIView.as_view(),
        name='product-list'
    ),

    path(
        '<slug:slug>/',
        api_views.ProductDetailAPIView.as_view(),
        name='product-detail'
    ),

]