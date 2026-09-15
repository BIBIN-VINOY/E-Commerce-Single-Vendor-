from django.shortcuts import render
from products.models import ProductVariant,Product,Color,ProductImage
from cart.models import Cart
from . models import Wishlist
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

# Create your views here.

@login_required(login_url='login')
def wishlist(request):

    wishlist_items = Wishlist.objects.filter(
        user=request.user
    ).select_related(
        "variant",
        "variant__product",
        "variant__color",
    )

    cart_variant_ids = set(
        Cart.objects.filter(user=request.user)
        .values_list("variant_id", flat=True)
    )

    

    context = {
        "wishlist_items": wishlist_items,
        "cart_variant_ids": cart_variant_ids,
    }

    return render(request, 'wishlist/wishlist.html', context)

    

@login_required(login_url='login')
def add_to_wishlist(request,pk):

    variant = get_object_or_404(
        ProductVariant,
        id=pk,
        is_active=True
    )

    wishlist_item,created=Wishlist.objects.get_or_create(
        user=request.user,
        variant=variant
    )

    return JsonResponse({
        "success": True,
        "created": created
    })

def product_search(request):
    return render(request,'wishlist/wishlist.html')

@login_required
def wishlist_remove(request, variant_id):
    variant = get_object_or_404(ProductVariant, id=variant_id)

    Wishlist.objects.filter(
        user=request.user,
        variant=variant
    ).delete()

    return redirect("wishlist:wishlist")

