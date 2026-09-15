
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from .models import Product,ProductVariant
from wishlist.models import Wishlist
from cart.models import Cart

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    variants = product.variants.filter(is_active=True)

    variant_id = request.GET.get("variant")

    if variant_id:
        default_variant = get_object_or_404(
            ProductVariant,
            id=variant_id,
            product=product,
            is_active=True,
        )
    else:
        default_variant = (
            variants.filter(is_default=True).first()
            or variants.first()
        )

    variants_data = {
        str(v.id): {
            "stock": v.stock,
            "price": str(v.price),
            "primary_image": v.primary_image_url,
            "gallery_images": v.gallery_urls,
            "cart_url": reverse("cart:add_to_cart", args=[v.id]),
            "wishlist_url": reverse("wishlist:add_to_wishlist", args=[v.id]),
            "is_in_cart": (
                Cart.objects.filter(user=request.user, variant=v).exists()
                if request.user.is_authenticated else False
            ),
            "is_wishlisted": (
                Wishlist.objects.filter(user=request.user, variant=v).exists()
                if request.user.is_authenticated else False
            ),
        }
        for v in variants
    }

    return render(request, "products/product_detail.html", {
        "product": product,
        "variants": variants,
        "default_variant": default_variant,
        "variants_data": variants_data,
    })
def product_search(request):
    return render(request,"dashboard.html")
