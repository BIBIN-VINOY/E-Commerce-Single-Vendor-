import django_filters

from django.db.models import Exists, OuterRef

from .models import Product, ProductVariant


class ProductFilter(django_filters.FilterSet):

    category = django_filters.CharFilter(
        field_name='category__slug',
        lookup_expr='iexact'
    )

    brand = django_filters.CharFilter(
        field_name='brand__slug',
        lookup_expr='iexact'
    )

    is_featured = django_filters.BooleanFilter()

    min_price = django_filters.NumberFilter(method='filter_noop')

    max_price = django_filters.NumberFilter(method='filter_noop')

    color = django_filters.CharFilter(method='filter_noop')

    in_stock = django_filters.BooleanFilter(method='filter_noop')

    class Meta:
        model = Product
        fields = []

    def filter_noop(self, queryset, name, value):
        return queryset

    def filter_queryset(self, queryset):

        queryset = super().filter_queryset(queryset)

        min_price = self.form.cleaned_data.get('min_price')
        max_price = self.form.cleaned_data.get('max_price')
        color = self.form.cleaned_data.get('color')
        in_stock = self.form.cleaned_data.get('in_stock')

        variant_queryset = ProductVariant.objects.filter(
            product=OuterRef('pk'),
            is_active=True
        )

        if min_price is not None:
            variant_queryset = variant_queryset.filter(
                price__gte=min_price
            )

        if max_price is not None:
            variant_queryset = variant_queryset.filter(
                price__lte=max_price
            )

        if color:
            variant_queryset = variant_queryset.filter(
                color__name__iexact=color
            )

        if in_stock is True:
            variant_queryset = variant_queryset.filter(
                stock__gt=0
            )

        elif in_stock is False:
            variant_queryset = variant_queryset.filter(
                stock=0
            )

        if (
            min_price is not None
            or max_price is not None
            or color
            or in_stock is not None
        ):
            queryset = queryset.filter(
                Exists(variant_queryset)
            )

        return queryset