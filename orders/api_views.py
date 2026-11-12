from django.db import transaction

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
)

from notification.signals import create_notification

from .models import Order
from .serializers import (
    OrderSerializer,
    CreateOrderSerializer,
)
from .services import (
    create_order_from_cart,
    cancel_order,
    OrderCreationError,
)


# ============================================================
# CREATE ORDER
# ============================================================

class OrderCreateAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = CreateOrderSerializer(
            data=request.data,
            context={
                "request": request,
            }
        )

        serializer.is_valid(
            raise_exception=True
        )

        address = serializer.validated_data["address"]

        payment_method = serializer.validated_data[
            "payment_method"
        ]

        try:

            order = create_order_from_cart(

                user=request.user,

                address=address,

                payment_method=payment_method,

                payment_status="pending",
            )

        except OrderCreationError as error:

            return Response(
                {
                    "message": str(error)
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create notification after successful transaction.
        transaction.on_commit(
            lambda: create_notification(
                user=request.user,
                order=order,
                notification_type="order_placed",
                title="Order Placed",
                message=(
                    f"Your order #{str(order.id)[:8]} "
                    "has been placed successfully."
                ),
            )
        )

        return Response(
            {
                "message": "Order placed successfully.",
                "order": OrderSerializer(order).data,
            },
            status=status.HTTP_201_CREATED,
        )


# ============================================================
# ORDER HISTORY
# ============================================================

class OrderListAPIView(ListAPIView):

    serializer_class = OrderSerializer

    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        return (
            Order.objects
            .filter(
                user=self.request.user
            )
            .prefetch_related(
                "items"
            )
            .order_by(
                "-created_at"
            )
        )


# ============================================================
# ORDER DETAIL
# ============================================================

class OrderDetailAPIView(RetrieveAPIView):

    serializer_class = OrderSerializer

    permission_classes = [IsAuthenticated]

    lookup_field = "id"

    lookup_url_kwarg = "order_id"

    def get_queryset(self):

        return (
            Order.objects
            .filter(
                user=self.request.user
            )
            .prefetch_related(
                "items"
            )
        )


# ============================================================
# CANCEL ORDER
# ============================================================

class OrderCancelAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):

        order, error = cancel_order(
            order_id=order_id,
            user=request.user,
        )

        if error:

            response_status = (
                status.HTTP_404_NOT_FOUND
                if error == "Order not found."
                else status.HTTP_400_BAD_REQUEST
            )

            return Response(
                {
                    "message": error
                },
                status=response_status,
            )

        transaction.on_commit(
            lambda: create_notification(
                user=request.user,
                order=order,
                notification_type="order_cancelled",
                title="Order Cancelled",
                message=(
                    f"Your order #{str(order.id)[:8]} "
                    "has been cancelled successfully."
                ),
            )
        )

        return Response(
            {
                "message": "Order cancelled successfully.",
                "order": OrderSerializer(order).data,
            },
            status=status.HTTP_200_OK,
        )