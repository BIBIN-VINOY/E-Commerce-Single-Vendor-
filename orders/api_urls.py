from django.urls import path

from . import api_views


urlpatterns = [

    # Create order
    path(
        "",
        api_views.OrderCreateAPIView.as_view(),
        name="api_order_create",
    ),

    # Order history
    path(
        "history/",
        api_views.OrderListAPIView.as_view(),
        name="api_order_list",
    ),

    # Order details
    path(
        "<uuid:order_id>/",
        api_views.OrderDetailAPIView.as_view(),
        name="api_order_detail",
    ),

    # Cancel order
    path(
        "<uuid:order_id>/cancel/",
        api_views.OrderCancelAPIView.as_view(),
        name="api_order_cancel",
    ),

]