from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from .models import Order


@login_required
def order_list(request):
    """
    Display all orders belonging to the logged-in user.
    """

    orders = (
        Order.objects
        .filter(user=request.user)
        .prefetch_related("items")
        .order_by("-created_at")
    )

    return render(
        request,
        "orders/orders.html",
        {
            "orders": orders,
        },
    )


@login_required
def order_detail(request, order_id):
    """
    Display a single order.

    The user can only access their own orders.
    """

    order = get_object_or_404(
        Order.objects.prefetch_related("items"),
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