from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from .models import Order


# ============================================================
# ORDER LIST
# ============================================================

@login_required
def order_list(request):

    orders = (
        Order.objects
        .filter(user=request.user)
        .prefetch_related("items")
        .order_by("-created_at")
    )

    return render(
        request,
        "orders/order_list.html",
        {
            "orders": orders,
        },
    )


# ============================================================
# ORDER DETAIL
# ============================================================

@login_required
def order_detail(request, order_id):

    order = get_object_or_404(
        Order.objects.prefetch_related(
            "items",
        ),
        id=order_id,
        user=request.user,
    )

    return render(
        request,
        "orders/order_detail.html",
        {
            "order": order,
        },
    )


# ============================================================
# ORDER TRACKING
# ============================================================

@login_required
def order_tracking(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user,
    )

    # Status steps shown on the tracking page.
    tracking_steps = [
        {
            "status": "confirmed",
            "label": "Order Confirmed",
            "description": "Your order has been confirmed.",
        },
        {
            "status": "processing",
            "label": "Processing",
            "description": "Your order is being prepared.",
        },
        {
            "status": "shipped",
            "label": "Shipped",
            "description": "Your order has been shipped.",
        },
        {
            "status": "delivered",
            "label": "Delivered",
            "description": "Your order has been delivered.",
        },
    ]

    status_order = [
        "confirmed",
        "processing",
        "shipped",
        "delivered",
    ]

    current_status = order.status

    if current_status in status_order:
        current_index = status_order.index(
            current_status
        )
    else:
        current_index = -1

    for index, step in enumerate(tracking_steps):

        step["completed"] = (
            current_index >= index
        )

        step["current"] = (
            current_index == index
        )

    return render(
        request,
        "orders/order_tracking.html",
        {
            "order": order,
            "tracking_steps": tracking_steps,
        },
    )


# ============================================================
# CANCEL ORDER
# ============================================================

@login_required
def cancel_order(request, order_id):

    if request.method != "POST":
        return redirect(
            "orders:order_detail",
            order_id=order_id,
        )

    with transaction.atomic():

        order = get_object_or_404(
            Order.objects.select_for_update(),
            id=order_id,
            user=request.user,
        )

        cancellable_statuses = [
            "pending",
            "confirmed",
            "processing",
        ]

        if order.status not in cancellable_statuses:

            messages.error(
                request,
                "This order can no longer be cancelled.",
            )

            return redirect(
                "orders:order_detail",
                order_id=order.id,
            )

        # ----------------------------------------------------
        # Restore stock
        # ----------------------------------------------------

        order_items = (
            order.items
            .select_related("variant")
            .select_for_update()
        )

        for item in order_items:

            variant = item.variant

            variant.stock += item.quantity

            variant.save(
                update_fields=["stock"]
            )

        # ----------------------------------------------------
        # Cancel order
        # ----------------------------------------------------

        order.status = "cancelled"

        order.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

    messages.success(
        request,
        "Your order has been cancelled successfully.",
    )

    return redirect(
        "orders:order_detail",
        order_id=order.id,
    )


# ============================================================
# DELETE / REMOVE ORDER FROM HISTORY
# ============================================================

@login_required
def delete_order(request, order_id):

    if request.method != "POST":
        return redirect(
            "orders:order_list"
        )

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user,
    )

    # --------------------------------------------------------
    # Only cancelled orders can be removed
    # --------------------------------------------------------

    if order.status != "cancelled":

        messages.error(
            request,
            "Only cancelled orders can be removed from your order history.",
        )

        return redirect(
            "orders:order_list"
        )

    order.delete()

    messages.success(
        request,
        "Order removed from your order history.",
    )

    return redirect(
        "orders:order_list"
    )