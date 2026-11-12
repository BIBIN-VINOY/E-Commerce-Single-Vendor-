from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from products.models import ProductVariant

from .models import Cart

from .serializers import (
    CartItemSerializer,
    CartAddSerializer,
    CartUpdateSerializer,
)


def get_cart_queryset(user):

    return (
        Cart.objects
        .filter(user=user)
        .select_related(
            'variant',
            'variant__product',
            'variant__color',
        )
        .prefetch_related(
            'variant__images'
        )
    )


def get_cart_summary(user):

    items = Cart.objects.filter(user=user)

    total_quantity = items.aggregate(
        total=Sum('quantity')
    )['total'] or 0

    cart_items = get_cart_queryset(user)

    total = sum(
        (item.subtotal for item in cart_items),
        Decimal('0.00')
    )

    return {
        'item_count': items.count(),
        'total_quantity': total_quantity,
        'total': total,
    }


# --------------------------------
# VIEW CART
# --------------------------------

class CartListAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        cart_items = get_cart_queryset(request.user)

        summary = get_cart_summary(request.user)

        serializer = CartItemSerializer(
            cart_items,
            many=True,
            context={'request': request}
        )

        return Response({
            'items': serializer.data,
            'summary': summary,
        })


# --------------------------------
# ADD TO CART
# --------------------------------

class CartAddAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = CartAddSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        variant_id = serializer.validated_data['variant_id']

        quantity = serializer.validated_data['quantity']

        with transaction.atomic():

            variant = get_object_or_404(
                ProductVariant.objects
                .select_for_update()
                .select_related('product'),
                id=variant_id,
                is_active=True,
                product__is_deleted=False,
                product__status='published',
            )

            if quantity > variant.stock:

                return Response({
                    'message': f'Only {variant.stock} item(s) available.'
                }, status=status.HTTP_400_BAD_REQUEST)

            cart_item, created = Cart.objects.update_or_create(
                user=request.user,
                variant=variant,
                defaults={
                    'quantity': quantity
                }
            )

        cart_item = get_cart_queryset(request.user).get(
            id=cart_item.id
        )

        return Response({
            'message': (
                'Item added to cart.'
                if created
                else 'Cart quantity updated.'
            ),
            'item': CartItemSerializer(
                cart_item,
                context={'request': request}
            ).data,
            'summary': get_cart_summary(request.user),
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


# --------------------------------
# UPDATE CART QUANTITY
# --------------------------------

class CartUpdateAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self, request, variant_id):

        serializer = CartUpdateSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        quantity = serializer.validated_data['quantity']

        with transaction.atomic():

            cart_item = get_object_or_404(
                Cart.objects
                .select_for_update()
                .select_related('variant'),
                user=request.user,
                variant_id=variant_id,
            )

            variant = cart_item.variant

            if not variant.is_active:

                return Response({
                    'message': 'This product variant is no longer available.'
                }, status=status.HTTP_400_BAD_REQUEST)

            if quantity > variant.stock:

                return Response({
                    'message': f'Only {variant.stock} item(s) available.'
                }, status=status.HTTP_400_BAD_REQUEST)

            cart_item.quantity = quantity

            cart_item.save(update_fields=[
                'quantity',
                'updated_at'
            ])

        cart_item = get_cart_queryset(request.user).get(
            id=cart_item.id
        )

        return Response({
            'message': 'Cart quantity updated.',
            'item': CartItemSerializer(
                cart_item,
                context={'request': request}
            ).data,
            'summary': get_cart_summary(request.user),
        })


# --------------------------------
# REMOVE CART ITEM
# --------------------------------

class CartRemoveAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def delete(self, request, variant_id):

        deleted_count, _ = Cart.objects.filter(
            user=request.user,
            variant_id=variant_id,
        ).delete()

        if not deleted_count:

            return Response({
                'message': 'Cart item not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'message': 'Item removed from cart.',
            'summary': get_cart_summary(request.user),
        })


# --------------------------------
# CLEAR CART
# --------------------------------

class CartClearAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def delete(self, request):

        Cart.objects.filter(
            user=request.user
        ).delete()

        return Response({
            'message': 'Cart cleared successfully.',
            'summary': get_cart_summary(request.user),
        })