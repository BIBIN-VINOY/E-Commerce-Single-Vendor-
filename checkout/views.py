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


# ============================================================
# CALCULATE CHECKOUT TOTALS
# ============================================================

def calculate_checkout_totals(cart_items):
    """
    Calculate checkout totals on the server.

    Never trust prices or totals sent by JavaScript.
    """

    subtotal = sum(
        (
            item.variant.price * item.quantity
            for item in cart_items
        ),
        Decimal("0.00"),
    )

    tax = (
        subtotal * TAX_RATE
    ).quantize(Decimal("0.01"))

    if subtotal >= FREE_SHIPPING_THRESHOLD:
        shipping_cost = Decimal("0.00")
    else:
        shipping_cost = SHIPPING_COST

    total = (
        subtotal
        + tax
        + shipping_cost
    )

    return (
        subtotal,
        tax,
        shipping_cost,
        total,
    )


# ============================================================
# CREATE ORDER
# ============================================================

def create_order_from_cart(
    user,
    address,
    payment_method,
    payment_status,
):
    """
    Create Order + OrderItems,
    reduce stock and clear cart.

    This function should only be called after
    the payment requirements have been satisfied.
    """

    with transaction.atomic():

        # ----------------------------------------------------
        # Lock cart items
        # ----------------------------------------------------

        cart_items = list(
            Cart.objects
            .select_for_update()
            .filter(user=user)
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
            return None, "Your cart is empty."

        # ----------------------------------------------------
        # Calculate totals again
        # ----------------------------------------------------

        (
            subtotal,
            tax,
            shipping_cost,
            total,
        ) = calculate_checkout_totals(
            cart_items
        )

        # ----------------------------------------------------
        # Check stock
        # ----------------------------------------------------

        for cart_item in cart_items:

            variant = cart_item.variant

            if not variant.is_active:
                return (
                    None,
                    f"{variant.product.name} is no longer available.",
                )

            if variant.stock < cart_item.quantity:
                return (
                    None,
                    (
                        f"Only {variant.stock} unit(s) of "
                        f"{variant.product.name} are available."
                    ),
                )

        # ----------------------------------------------------
        # Create Order
        # ----------------------------------------------------

        order = Order.objects.create(
            user=user,

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

        # ----------------------------------------------------
        # Create OrderItems
        # ----------------------------------------------------

        for cart_item in cart_items:

            variant = cart_item.variant

            # -----------------------------------------------
            # Get primary image
            # -----------------------------------------------

            primary_image = (
                variant.images
                .filter(is_primary=True)
                .first()
            )

            if primary_image:

                image_url = (
                    primary_image.image.url
                )

            else:

                first_image = (
                    variant.images.first()
                )

                image_url = (
                    first_image.image.url
                    if first_image
                    else ""
                )

            # -----------------------------------------------
            # Calculate item subtotal
            # -----------------------------------------------

            item_subtotal = (
                variant.price
                * cart_item.quantity
            )

            # -----------------------------------------------
            # Create OrderItem
            # -----------------------------------------------

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

            # -----------------------------------------------
            # Reduce stock
            # -----------------------------------------------

            variant.stock -= cart_item.quantity

            variant.save(
                update_fields=["stock"]
            )

        # ----------------------------------------------------
        # Clear cart
        # ----------------------------------------------------

        Cart.objects.filter(
            user=user
        ).delete()

    return order, None


# ============================================================
# CHECKOUT PAGE
# ============================================================

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

    # --------------------------------------------------------
    # Empty cart
    # --------------------------------------------------------

    if not cart_items.exists():

        messages.warning(
            request,
            "Your cart is empty.",
        )

        return redirect(
            "cart:cart"
        )

    # --------------------------------------------------------
    # Addresses
    # --------------------------------------------------------

    addresses = (
        Address.objects
        .filter(user=request.user)
        .order_by(
            "-is_default",
            "-id",
        )
    )

    # --------------------------------------------------------
    # Calculate totals
    # --------------------------------------------------------

    (
        subtotal,
        tax,
        shipping_cost,
        total,
    ) = calculate_checkout_totals(
        cart_items
    )

    # ========================================================
    # POST
    # ========================================================

    if request.method == "POST":

        address_id = request.POST.get(
            "address_id"
        )

        payment_method = request.POST.get(
            "payment_method"
        )

        # ----------------------------------------------------
        # Validate address
        # ----------------------------------------------------

        if not address_id:

            messages.error(
                request,
                "Please select a delivery address.",
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

        address = get_object_or_404(
            Address,
            id=address_id,
            user=request.user,
        )

        # ----------------------------------------------------
        # Validate payment method
        # ----------------------------------------------------

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

        # ====================================================
        # CARD
        # ====================================================

        if payment_method == "card":

            # Store only checkout information.
            #
            # NEVER store card number, CVV,
            # expiry date, etc.

            request.session[
                "checkout_address_id"
            ] = address.id

            request.session[
                "checkout_payment_method"
            ] = "card"

            return redirect(
                "checkout:card_payment"
            )

        # ====================================================
        # UPI
        # ====================================================

        if payment_method == "upi":

            messages.info(
                request,
                "UPI payment will be available soon.",
            )

            return redirect(
                "checkout:checkout"
            )

        # ====================================================
        # COD
        # ====================================================

        if payment_method == "cod":

            order, error = (
                create_order_from_cart(
                    user=request.user,
                    address=address,
                    payment_method="cod",
                    payment_status="pending",
                )
            )

            if error:

                messages.error(
                    request,
                    error,
                )

                return redirect(
                    "cart:cart"
                )

            messages.success(
                request,
                "Your order has been placed successfully!",
            )

            return redirect(
                "orders:order_detail",
                order_id=order.id,
            )

    # ========================================================
    # GET
    # ========================================================

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


# ============================================================
# CARD PAYMENT PAGE
# ============================================================

@login_required
def card_payment(request):

    address_id = request.session.get(
        "checkout_address_id"
    )

    payment_method = request.session.get(
        "checkout_payment_method"
    )

    # --------------------------------------------------------
    # Validate checkout session
    # --------------------------------------------------------

    if (
        not address_id
        or payment_method != "card"
    ):

        messages.error(
            request,
            "Your checkout session has expired. Please try again.",
        )

        return redirect(
            "checkout:checkout"
        )

    # --------------------------------------------------------
    # Address
    # --------------------------------------------------------

    address = get_object_or_404(
        Address,
        id=address_id,
        user=request.user,
    )

    # --------------------------------------------------------
    # Cart
    # --------------------------------------------------------

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

    if not cart_items.exists():

        messages.warning(
            request,
            "Your cart is empty.",
        )

        return redirect(
            "cart:cart"
        )

    # --------------------------------------------------------
    # Totals
    # --------------------------------------------------------

    (
        subtotal,
        tax,
        shipping_cost,
        total,
    ) = calculate_checkout_totals(
        cart_items
    )

    # ========================================================
    # POST
    # ========================================================

    if request.method == "POST":

        card_number = request.POST.get(
            "card_number",
            "",
        ).strip()

        card_holder = request.POST.get(
            "card_holder",
            "",
        ).strip()

        expiry = request.POST.get(
            "expiry",
            "",
        ).strip()

        cvv = request.POST.get(
            "cvv",
            "",
        ).strip()

        # ----------------------------------------------------
        # Basic validation
        # ----------------------------------------------------

        if (
            not card_number
            or not card_holder
            or not expiry
            or not cvv
        ):

            messages.error(
                request,
                "Please enter all card details.",
            )

            return render(
                request,
                "checkout/card_payment.html",
                {
                    "address": address,
                    "cart_items": cart_items,
                    "subtotal": subtotal,
                    "tax": tax,
                    "shipping_cost": shipping_cost,
                    "total": total,
                },
            )

        # ----------------------------------------------------
        # DEVELOPMENT ONLY
        # ----------------------------------------------------
        #
        # This simulates successful card payment.
        #
        # In production:
        #
        # Card details should be handled by
        # a payment gateway.
        #
        # NEVER store:
        # - card number
        # - CVV
        # - expiry
        #
        # ----------------------------------------------------

        request.session[
            "card_payment_success"
        ] = True

        return redirect(
            "checkout:complete_card_payment"
        )

    # ========================================================
    # GET
    # ========================================================

    return render(
        request,
        "checkout/card_payment.html",
        {
            "address": address,
            "cart_items": cart_items,
            "subtotal": subtotal,
            "tax": tax,
            "shipping_cost": shipping_cost,
            "total": total,
        },
    )


# ============================================================
# COMPLETE CARD PAYMENT
# ============================================================

@login_required
def complete_card_payment(request):

    payment_success = request.session.get(
        "card_payment_success"
    )

    # --------------------------------------------------------
    # Payment verification
    # --------------------------------------------------------

    if not payment_success:

        messages.error(
            request,
            "Payment was not completed.",
        )

        return redirect(
            "checkout:checkout"
        )

    # --------------------------------------------------------
    # Get address
    # --------------------------------------------------------

    address_id = request.session.get(
        "checkout_address_id"
    )

    if not address_id:

        messages.error(
            request,
            "Your checkout session has expired.",
        )

        return redirect(
            "checkout:checkout"
        )

    address = get_object_or_404(
        Address,
        id=address_id,
        user=request.user,
    )

    # --------------------------------------------------------
    # Create order
    # --------------------------------------------------------

    order, error = create_order_from_cart(
        user=request.user,
        address=address,
        payment_method="card",
        payment_status="paid",
    )

    if error:

        messages.error(
            request,
            error,
        )

        return redirect(
            "cart:cart"
        )

    # --------------------------------------------------------
    # Clear checkout session
    # --------------------------------------------------------

    request.session.pop(
        "checkout_address_id",
        None,
    )

    request.session.pop(
        "checkout_payment_method",
        None,
    )

    request.session.pop(
        "card_payment_success",
        None,
    )

    # --------------------------------------------------------
    # Success
    # --------------------------------------------------------

    messages.success(
        request,
        "Payment successful! Your order has been placed.",
    )

    return redirect(
        "orders:order_detail",
        order_id=order.id,
    )