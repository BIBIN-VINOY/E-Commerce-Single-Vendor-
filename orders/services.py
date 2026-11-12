from django.db import transaction

from cart.models import Cart
from products.models import ProductVariant

from .models import Order, OrderItem

from checkout.views import calculate_checkout_totals


class OrderCreationError(Exception):
    pass


def create_order_from_cart(
    user,
    address,
    payment_method,
    payment_status,
):

    with transaction.atomic():

        # ------------------------------------------------
        # 1. Lock cart items
        # ------------------------------------------------

        cart_items = list(
            Cart.objects
            .select_for_update()
            .filter(user=user)
            .order_by("variant_id")
        )

        if not cart_items:
            raise OrderCreationError(
                "Your cart is empty."
            )

        # ------------------------------------------------
        # 2. Lock the actual product variants
        # ------------------------------------------------

        variant_ids = [
            item.variant_id
            for item in cart_items
        ]

        variants = list(
            ProductVariant.objects
            .select_for_update()
            .filter(id__in=variant_ids)
            .select_related(
                "product",
                "color",
            )
            .prefetch_related(
                "images",
            )
            .order_by("id")
        )

        variant_map = {
            variant.id: variant
            for variant in variants
        }

        # ------------------------------------------------
        # 3. Verify all variants exist and are available
        # ------------------------------------------------

        for cart_item in cart_items:

            variant = variant_map.get(
                cart_item.variant_id
            )

            if variant is None:

                raise OrderCreationError(
                    "A product in your cart is no longer available."
                )

            if (
                not variant.is_active
                or variant.product.is_deleted
                or variant.product.status != "published"
            ):

                raise OrderCreationError(
                    f"{variant.product.name} is no longer available."
                )

            if variant.stock < cart_item.quantity:

                raise OrderCreationError(
                    (
                        f"Only {variant.stock} unit(s) of "
                        f"{variant.product.name} are available."
                    )
                )

        # ------------------------------------------------
        # 4. Calculate checkout totals
        # ------------------------------------------------

        (
            subtotal,
            tax,
            shipping_cost,
            total,
        ) = calculate_checkout_totals(
            cart_items
        )

        # ------------------------------------------------
        # 5. Create Order
        # ------------------------------------------------

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

        # ------------------------------------------------
        # 6. Create OrderItems and reduce stock
        # ------------------------------------------------

        for cart_item in cart_items:

            variant = variant_map[
                cart_item.variant_id
            ]

            primary_image = (
                variant.images
                .filter(is_primary=True)
                .first()
            )

            if not primary_image:

                primary_image = (
                    variant.images.first()
                )

            image_url = ""

            if primary_image:

                try:
                    image_url = primary_image.image.url

                except ValueError:
                    image_url = ""

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

            # Reduce stock
            variant.stock -= cart_item.quantity

            variant.save(
                update_fields=["stock"]
            )

        # ------------------------------------------------
        # 7. Clear cart
        # ------------------------------------------------

        Cart.objects.filter(
            user=user
        ).delete()

        return order


def cancel_order(order_id, user):

    with transaction.atomic():

        # ------------------------------------------------
        # 1. Lock order and verify ownership
        # ------------------------------------------------

        try:

            order = (
                Order.objects
                .select_for_update()
                .get(
                    id=order_id,
                    user=user,
                )
            )

        except Order.DoesNotExist:

            return None, "Order not found."

        # ------------------------------------------------
        # 2. Check cancellation eligibility
        # ------------------------------------------------

        cancellable_statuses = [
            "pending",
            "confirmed",
            "processing",
        ]

        if order.status not in cancellable_statuses:

            return (
                None,
                "This order can no longer be cancelled."
            )

        if order.payment_status == "paid":

            return (
                None,
                "Paid orders require a refund process before cancellation."
            )

        # ------------------------------------------------
        # 3. Retrieve and lock order items
        # ------------------------------------------------

        order_items = list(
            order.items.all()
        )

        variant_ids = [
            item.variant_id
            for item in order_items
        ]

        variants = list(
            ProductVariant.objects
            .select_for_update()
            .filter(id__in=variant_ids)
            .order_by("id")
        )

        variant_map = {
            variant.id: variant
            for variant in variants
        }

        # ------------------------------------------------
        # 4. Restore stock
        # ------------------------------------------------

        for item in order_items:

            variant = variant_map.get(
                item.variant_id
            )

            if variant is None:
                continue

            variant.stock += item.quantity

            variant.save(
                update_fields=["stock"]
            )

        # ------------------------------------------------
        # 5. Cancel order
        # ------------------------------------------------

        order.status = "cancelled"

        order.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return order, None