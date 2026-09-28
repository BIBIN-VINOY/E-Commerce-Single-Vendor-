from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

# Adjust these imports to match your project layout
from products.models import ProductVariant
from .models import Cart


def _cart_totals(user):
    """Return (item_count, total) for the user's cart."""
    items = Cart.objects.filter(user=user)
    total = sum(item.subtotal for item in items)
    return items.count(), float(total)


@login_required
def cart(request):

    cart_items = (
        Cart.objects
        .filter(user=request.user)
        .select_related(
            "variant",
            "variant__product",
            "variant__color",
        )
    )

    total = sum(item.subtotal for item in cart_items)

    context = {
        "cart_items": cart_items,
        "total": total,
    }

    return render(request, "cart/cart.html", context)


@login_required
def add_to_cart(request, variant_id):

    variant = get_object_or_404(
        ProductVariant,
        id=variant_id,
        is_active=True,
    )

    # Only allow POST requests
    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "message": "Invalid request method.",
        }, status=405)

    # Get quantity sent from frontend
    try:
        quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 1

    # Validate quantity
    if quantity < 1:
        return JsonResponse({
            "success": False,
            "message": "Quantity must be at least 1.",
        }, status=400)

    # Check stock
    if quantity > variant.stock:
        return JsonResponse({
            "success": False,
            "message": f"Only {variant.stock} item(s) are available.",
        }, status=400)

    # Create or update cart item
    cart_item, created = Cart.objects.update_or_create(
        user=request.user,
        variant=variant,
        defaults={
            "quantity": quantity,
        },
    )

    cart_count, total = _cart_totals(request.user)

    return JsonResponse({
        "success": True,
        "quantity": cart_item.quantity,
        "cart_count": cart_count,
        "total": total,
    })


@login_required
@require_POST
def remove_from_cart(request, variant_id):

    Cart.objects.filter(
        user=request.user,
        variant_id=variant_id,
    ).delete()

    cart_count, total = _cart_totals(request.user)

    return JsonResponse({
        "success": True,
        "cart_count": cart_count,
        "total": total,
    })


@login_required
@require_POST
def increase_quantity(request, variant_id):

    cart_item = get_object_or_404(
        Cart.objects.select_related("variant"),
        user=request.user,
        variant_id=variant_id,
    )

    if cart_item.quantity >= cart_item.variant.stock:
        return JsonResponse({
            "success": False,
            "error": f"Only {cart_item.variant.stock} item(s) available.",
        }, status=400)

    cart_item.quantity += 1
    cart_item.save()

    cart_count, total = _cart_totals(request.user)

    return JsonResponse({
        "success": True,
        "deleted": False,
        "quantity": cart_item.quantity,
        "item_subtotal": float(cart_item.subtotal),
        "cart_count": cart_count,
        "total": total,
    })


@login_required
@require_POST
def decrease_quantity(request, variant_id):

    cart_item = get_object_or_404(
        Cart,
        user=request.user,
        variant_id=variant_id,
    )

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()

        deleted = False
        quantity = cart_item.quantity
        item_subtotal = float(cart_item.subtotal)

    else:
        # Quantity would drop below 1, so remove the item
        cart_item.delete()

        deleted = True
        quantity = 0
        item_subtotal = 0

    cart_count, total = _cart_totals(request.user)

    return JsonResponse({
        "success": True,
        "deleted": deleted,
        "quantity": quantity,
        "item_subtotal": item_subtotal,
        "cart_count": cart_count,
        "total": total,
    })