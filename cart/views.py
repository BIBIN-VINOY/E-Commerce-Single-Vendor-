from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from products.models import ProductVariant
from .models import Cart

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

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        variant=variant,
    )

    if not created:

        if cart_item.quantity < variant.stock:
            cart_item.quantity += 1
            cart_item.save()

    total = sum(
        item.subtotal
        for item in Cart.objects.filter(user=request.user)
    )

    return JsonResponse({
        "success": True,
        "quantity": cart_item.quantity,
        "cart_count": Cart.objects.filter(user=request.user).count(),
        "total": float(total),
    })


@login_required
def remove_from_cart(request, variant_id):

    Cart.objects.filter(
        user=request.user,
        variant_id=variant_id,
    ).delete()

    total = sum(
        item.subtotal
        for item in Cart.objects.filter(user=request.user)
    )

    return JsonResponse({
        "success": True,
        "cart_count": Cart.objects.filter(user=request.user).count(),
        "total": float(total),
    })


@login_required
def increase_quantity(request, variant_id):

    cart_item = get_object_or_404(
        Cart,
        user=request.user,
        variant_id=variant_id,
    )

    if cart_item.quantity < cart_item.variant.stock:
        cart_item.quantity += 1
        cart_item.save()

    total = sum(item.subtotal for item in Cart.objects.filter(user=request.user))

    return JsonResponse({
        "quantity": cart_item.quantity,
        "subtotal": float(cart_item.subtotal),
        "total": float(total),
    })

@login_required
def decrease_quantity(request, variant_id):

    cart_item = get_object_or_404(
        Cart,
        user=request.user,
        variant_id=variant_id,
    )

    deleted = False

    if cart_item.quantity > 1:

        cart_item.quantity -= 1
        cart_item.save()

        quantity = cart_item.quantity
        subtotal = float(cart_item.subtotal)

    else:

        cart_item.delete()

        deleted = True
        quantity = 0
        subtotal = 0

    total = sum(
        item.subtotal
        for item in Cart.objects.filter(user=request.user)
    )

    return JsonResponse({
        "success": True,
        "deleted": deleted,
        "quantity": quantity,
        "subtotal": subtotal,
        "total": float(total),
        "cart_count": Cart.objects.filter(user=request.user).count(),
    })
