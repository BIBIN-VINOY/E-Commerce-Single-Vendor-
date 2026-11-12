from rest_framework import serializers

from accounts.models import Address
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):

    variant_id = serializers.UUIDField(
        read_only=True
    )

    class Meta:
        model = OrderItem

        fields = [
            "id",
            "variant_id",
            "product_name",
            "color_name",
            "image_url",
            "price",
            "quantity",
            "subtotal",
        ]

        read_only_fields = fields


class OrderSerializer(serializers.ModelSerializer):

    items = OrderItemSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Order

        fields = [
            "id",
            "status",
            "payment_method",
            "payment_status",

            # Delivery address snapshot
            "full_name",
            "address_line_1",
            "address_line_2",
            "city",
            "state",
            "postal_code",
            "country",
            "phone_number",

            # Pricing
            "subtotal",
            "tax",
            "shipping_cost",
            "total_amount",

            # Order items
            "items",

            # Timestamps
            "created_at",
            "updated_at",
        ]

        read_only_fields = fields


class CreateOrderSerializer(serializers.Serializer):

    address_id = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.all(),
        source="address"
    )

    payment_method = serializers.ChoiceField(
        choices=[
            ("cod", "Cash on Delivery"),
        ]
    )

    def validate_address(self, address):

        user = self.context["request"].user

        if address.user != user:
            raise serializers.ValidationError(
                "You cannot use another user's address."
            )

        return address