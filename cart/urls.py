from django.urls import path
from . import views

app_name = "cart"

urlpatterns = [

    path("", views.cart, name="cart"),

    path(
        "add/<uuid:variant_id>/",
        views.add_to_cart,
        name="add_to_cart",
    ),

    path(
        "remove/<uuid:variant_id>/",
        views.remove_from_cart,
        name="remove_from_cart",
    ),

    path(
        "increase/<uuid:variant_id>/",
        views.increase_quantity,
        name="increase_quantity",
    ),

    path(
        "decrease/<uuid:variant_id>/",
        views.decrease_quantity,
        name="decrease_quantity",
    ),
]