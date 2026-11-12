from rest_framework import serializers

from .models import Wishlist

from products.serializers import (
    ProductVariantDetailSerializer,
)


class WishlistSerializer(serializers.ModelSerializer):

    variant = ProductVariantDetailSerializer(read_only=True)

    class Meta:
        model = Wishlist
        fields = [
            'id',
            'variant',
            'added_at',
        ]


class WishlistAddSerializer(serializers.Serializer):

    variant_id = serializers.UUIDField()