from django.urls import path

from . import views


app_name = "checkout"


urlpatterns = [
    path(
        "",
        views.checkout,
        name="checkout",
    ),

    path(
        "card-payment/",
        views.card_payment,
        name="card_payment",
    ),

    path(
        "complete-card-payment/",
        views.complete_card_payment,
        name="complete_card_payment",
    ),
]