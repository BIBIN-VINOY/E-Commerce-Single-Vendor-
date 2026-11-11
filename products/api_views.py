from django.db.models import (
    Min,
    Q,
    Prefetch,
)

from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.filters import SearchFilter, OrderingFilter

from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    Category,
    Brand,
    Product,
    ProductVariant,
)

from .serializers import (
    CategorySerializer,
    BrandSerializer,
    ProductListSerializer,
    ProductDetailSerializer,
)

from .filters import ProductFilter
from .pagination import ProductPagination


# -------------------------
# COMMON PRODUCT QUERYSET
# -------------------------

def get_product_queryset():

    active_variants = (
        ProductVariant.objects
        .filter(is_active=True)
        .select_related('color')
        .prefetch_related('images')
    )

    return (
        Product.objects
        .filter(
            is_deleted=False,
            status__in=['published', 'out_of_stock']
        )
        .select_related(
            'category',
            'brand'
        )
        .prefetch_related(
            Prefetch(
                'variants',
                queryset=active_variants
            )
        )
        .annotate(
            price=Min(
                'variants__price',
                filter=Q(variants__is_active=True)
            )
        )
    )


# -------------------------
# CATEGORY API
# -------------------------

class CategoryListAPIView(generics.ListAPIView):

    serializer_class = CategorySerializer

    permission_classes = [AllowAny]

    queryset = (
        Category.objects
        .filter(is_active=True)
        .select_related('parent')
        .prefetch_related('subcategories')
    )


class CategoryDetailAPIView(generics.RetrieveAPIView):

    serializer_class = CategorySerializer

    permission_classes = [AllowAny]

    lookup_field = 'slug'

    queryset = (
        Category.objects
        .filter(is_active=True)
        .select_related('parent')
        .prefetch_related('subcategories')
    )


# -------------------------
# BRAND API
# -------------------------

class BrandListAPIView(generics.ListAPIView):

    serializer_class = BrandSerializer

    permission_classes = [AllowAny]

    queryset = Brand.objects.filter(
        is_active=True
    )


class BrandDetailAPIView(generics.RetrieveAPIView):

    serializer_class = BrandSerializer

    permission_classes = [AllowAny]

    lookup_field = 'slug'

    queryset = Brand.objects.filter(
        is_active=True
    )


# -------------------------
# PRODUCT LIST API
# -------------------------

class ProductListAPIView(generics.ListAPIView):

    serializer_class = ProductListSerializer

    permission_classes = [AllowAny]

    pagination_class = ProductPagination

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_class = ProductFilter

    search_fields = [
        'name',
        'description',
        'category__name',
        'brand__name',
    ]

    ordering_fields = [
        'created_at',
        'name',
        'price',
    ]

    ordering = ['-created_at']

    def get_queryset(self):

        return get_product_queryset()


# -------------------------
# PRODUCT DETAIL API
# -------------------------

class ProductDetailAPIView(generics.RetrieveAPIView):

    serializer_class = ProductDetailSerializer

    permission_classes = [AllowAny]

    lookup_field = 'slug'

    def get_queryset(self):

        return get_product_queryset()


# -------------------------
# FEATURED PRODUCTS API
# -------------------------

class FeaturedProductListAPIView(generics.ListAPIView):

    serializer_class = ProductListSerializer

    permission_classes = [AllowAny]

    pagination_class = ProductPagination

    def get_queryset(self):

        return get_product_queryset().filter(
            is_featured=True
        )