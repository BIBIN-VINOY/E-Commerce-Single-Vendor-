from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from products.models import ProductVariant

from .models import Wishlist

from .serializers import (
    WishlistSerializer,
    WishlistAddSerializer,
)


def get_wishlist_queryset(user):

    return (
        Wishlist.objects
        .filter(user=user)
        .select_related(
            'variant',
            'variant__product',
            'variant__color',
            'variant__product__category',
            'variant__product__brand',
        )
        .prefetch_related(
            'variant__images'
        )
    )


# --------------------------------
# VIEW WISHLIST
# --------------------------------

class WishlistListAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        wishlist_items = get_wishlist_queryset(request.user)

        serializer = WishlistSerializer(
            wishlist_items,
            many=True,
            context={'request': request}
        )

        return Response({
            'count': wishlist_items.count(),
            'items': serializer.data,
        })


# --------------------------------
# ADD TO WISHLIST
# --------------------------------

class WishlistAddAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = WishlistAddSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        variant_id = serializer.validated_data['variant_id']

        variant = get_object_or_404(
            ProductVariant.objects.select_related('product'),
            id=variant_id,
            is_active=True,
            product__is_deleted=False,
            product__status__in=['published', 'out_of_stock'],
        )

        wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user,
            variant=variant,
        )

        return Response({
            'message': (
                'Added to wishlist.'
                if created
                else 'Item already exists in wishlist.'
            ),
            'created': created,
            'item': WishlistSerializer(
                wishlist_item,
                context={'request': request}
            ).data,
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


# --------------------------------
# REMOVE FROM WISHLIST
# --------------------------------

class WishlistRemoveAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def delete(self, request, variant_id):

        deleted_count, _ = Wishlist.objects.filter(
            user=request.user,
            variant_id=variant_id,
        ).delete()

        if not deleted_count:

            return Response({
                'message': 'Wishlist item not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'message': 'Removed from wishlist.',
        })


# --------------------------------
# CLEAR WISHLIST
# --------------------------------

class WishlistClearAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def delete(self, request):

        Wishlist.objects.filter(
            user=request.user
        ).delete()

        return Response({
            'message': 'Wishlist cleared successfully.'
        })