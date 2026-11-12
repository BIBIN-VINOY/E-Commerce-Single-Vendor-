from rest_framework import serializers

from .models import Cart
from products.models import ProductImage


class CartProductSerializer(serializers.Serializer):

    id = serializers.UUIDField()
    name = serializers.CharField()
    slug = serializers.CharField()


class CartColorSerializer(serializers.Serializer):

    name = serializers.CharField()
    hex_code = serializers.CharField()


class CartImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductImage
        fields = [
            'id',
            'image',
            'is_primary',
        ]


class CartVariantSerializer(serializers.Serializer):

    id = serializers.UUIDField()

    product = CartProductSerializer(read_only=True)

    color = CartColorSerializer(read_only=True)

    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    stock = serializers.IntegerField()

    is_active = serializers.BooleanField()

    images = CartImageSerializer(many=True, read_only=True)


class CartItemSerializer(serializers.ModelSerializer):

    variant = CartVariantSerializer(read_only=True)

    subtotal = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = Cart
        fields = [
            'id',
            'variant',
            'quantity',
            'subtotal',
            'added_at',
            'updated_at',
        ]


class CartAddSerializer(serializers.Serializer):

    variant_id = serializers.UUIDField()

    quantity = serializers.IntegerField(
        min_value=1,
        default=1
    )


class CartUpdateSerializer(serializers.Serializer):

    quantity = serializers.IntegerField(
        min_value=1
    )