from django.urls import path

from . import views


app_name = "orders"


urlpatterns = [

    # Orders page
    path(
        "",
        views.order_list,
        name="order_list",
    ),

    # Order details
    path(
        "<uuid:order_id>/",
        views.order_detail,
        name="order_detail",
    ),

    # Tracking
    path(
        "<uuid:order_id>/tracking/",
        views.order_tracking,
        name="order_tracking",
    ),

    # Cancel
    path(
        "<uuid:order_id>/cancel/",
        views.cancel_order,
        name="cancel_order",
    ),

    # Delete from order history
    path(
        "<uuid:order_id>/delete/",
        views.delete_order,
        name="delete_order",
    ),
]