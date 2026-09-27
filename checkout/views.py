from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import Address
from cart.models import Cart
from orders.models import Order, OrderItem


TAX_RATE = Decimal("0.05")
FREE_SHIPPING_THRESHOLD = Decimal("1000.00")
SHIPPING_COST = Decimal("50.00")


def calculate_checkout_totals(cart_items):
    """
    Calculate checkout totals on the server.
    Never trust prices or totals sent by JavaScript.
    """

    subtotal = sum(
        (item.variant.price * item.quantity for item in cart_items),
        Decimal("0.00"),
    )

    tax = (subtotal * TAX_RATE).quantize(Decimal("0.01"))

    if subtotal >= FREE_SHIPPING_THRESHOLD:
        shipping_cost = Decimal("0.00")
    else:
        shipping_cost = SHIPPING_COST

    total = subtotal + tax + shipping_cost

    return subtotal, tax, shipping_cost, total


@login_required
def checkout(request):

    cart_items = (
        Cart.objects
        .filter(user=request.user)
        .select_related(
            "variant",
            "variant__product",
            "variant__color",
        )
        .prefetch_related(
            "variant__images",
        )
    )

    # Empty cart
    if not cart_items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect("cart:cart")

    addresses = Address.objects.filter(
        user=request.user
    ).order_by(
        "-is_default",
        "-id",
    )

    subtotal, tax, shipping_cost, total = calculate_checkout_totals(
        cart_items
    )

    if request.method == "POST":

        address_id = request.POST.get("address_id")
        payment_method = request.POST.get("payment_method")

        # -----------------------------------
        # Validate address
        # -----------------------------------

        if not address_id:
            messages.error(request, "Please select a delivery address.")
            return render(
                request,
                "checkout/checkout.html",
                {
                    "cart_items": cart_items,
                    "addresses": addresses,
                    "subtotal": subtotal,
                    "tax": tax,
                    "shipping_cost": shipping_cost,
                    "total": total,
                },
            )

        address = get_object_or_404(
            Address,
            id=address_id,
            user=request.user,
        )

        # -----------------------------------
        # Validate payment method
        # -----------------------------------

        allowed_payment_methods = {
            "card",
            "upi",
            "cod",
        }

        if payment_method not in allowed_payment_methods:
            messages.error(
                request,
                "Please select a valid payment method.",
            )

            return render(
                request,
                "checkout/checkout.html",
                {
                    "cart_items": cart_items,
                    "addresses": addresses,
                    "subtotal": subtotal,
                    "tax": tax,
                    "shipping_cost": shipping_cost,
                    "total": total,
                },
            )

        # -----------------------------------
        # Create order safely
        # -----------------------------------

        with transaction.atomic():

            # Re-fetch cart items inside transaction
            cart_items = list(
                Cart.objects
                .select_for_update()
                .filter(user=request.user)
                .select_related(
                    "variant",
                    "variant__product",
                    "variant__color",
                )
                .prefetch_related(
                    "variant__images",
                )
            )

            if not cart_items:
                messages.error(
                    request,
                    "Your cart is empty.",
                )
                return redirect("cart:cart")

            # Recalculate prices
            subtotal, tax, shipping_cost, total = (
                calculate_checkout_totals(cart_items)
            )

            # -----------------------------------
            # Check stock
            # -----------------------------------

            for cart_item in cart_items:

                variant = cart_item.variant

                if not variant.is_active:
                    messages.error(
                        request,
                        f"{variant.product.name} is no longer available.",
                    )
                    return redirect("cart:cart")

                if variant.stock < cart_item.quantity:
                    messages.error(
                        request,
                        (
                            f"Only {variant.stock} unit(s) of "
                            f"{variant.product.name} are available."
                        ),
                    )
                    return redirect("cart:cart")

            # -----------------------------------
            # Payment status
            # -----------------------------------

            if payment_method == "cod":
                payment_status = "pending"
            else:
                # Card / UPI will remain pending until
                # a real payment gateway is integrated.
                payment_status = "pending"

            # -----------------------------------
            # Create Order
            # -----------------------------------

            order = Order.objects.create(
                user=request.user,

                status="confirmed",

                payment_method=payment_method,
                payment_status=payment_status,

                # Address snapshot
                full_name=address.full_name,
                address_line_1=address.address_line_1,
                address_line_2=address.address_line_2,
                city=address.city,
                state=address.state,
                postal_code=address.postal_code,
                country=address.country,
                phone_number=address.phone_number,

                # Price snapshot
                subtotal=subtotal,
                tax=tax,
                shipping_cost=shipping_cost,
                total_amount=total,
            )

            # -----------------------------------
            # Create OrderItems
            # -----------------------------------

            for cart_item in cart_items:

                variant = cart_item.variant

                primary_image = (
                    variant.images
                    .filter(is_primary=True)
                    .first()
                )

                if primary_image:
                    image_url = primary_image.image.url
                else:
                    first_image = variant.images.first()

                    image_url = (
                        first_image.image.url
                        if first_image
                        else ""
                    )

                item_subtotal = (
                    variant.price * cart_item.quantity
                )

                OrderItem.objects.create(
                    order=order,
                    variant=variant,

                    product_name=variant.product.name,
                    color_name=variant.color.name,
                    image_url=image_url,

                    price=variant.price,
                    quantity=cart_item.quantity,
                    subtotal=item_subtotal,
                )

                # -----------------------------------
                # Reduce stock
                # -----------------------------------

                variant.stock -= cart_item.quantity
                variant.save(update_fields=["stock"])

            # -----------------------------------
            # Clear cart
            # -----------------------------------

            Cart.objects.filter(
                user=request.user
            ).delete()

        messages.success(
            request,
            "Your order has been placed successfully!",
        )

        # We'll create this page next.
        return redirect(
            "orders:order_detail",
            order_id=order.id,
        )

    return render(
        request,
        "checkout/checkout.html",
        {
            "cart_items": cart_items,
            "addresses": addresses,
            "subtotal": subtotal,
            "tax": tax,
            "shipping_cost": shipping_cost,
            "total": total,
        },
    )
