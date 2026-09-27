from django.contrib import admin

from .models import Order, OrderItem


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "status",
        "payment_method",
        "payment_status",
        "total_amount",
        "created_at",
    )

    list_filter = (
        "status",
        "payment_method",
        "payment_status",
    )

    search_fields = (
        "id",
        "user__username",
        "user__email",
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "product_name",
        "color_name",
        "quantity",
        "price",
        "subtotal",
    )

    search_fields = (
        "product_name",
        "color_name",
    )