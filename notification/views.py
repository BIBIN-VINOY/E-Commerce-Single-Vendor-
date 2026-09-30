from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import Notification


@login_required
def notification_list(request):

    notifications = Notification.objects.filter(
        user=request.user
    )

    return render(
        request,
        "notifications/notification_list.html",
        {
            "notifications": notifications,
        },
    )


@login_required
def mark_as_read(request, notification_id):

    notification = get_object_or_404(
        Notification,
        id=notification_id,
        user=request.user,
    )

    notification.is_read = True

    notification.save(
        update_fields=["is_read"]
    )

    if notification.order:
        return redirect(
            "orders:order_detail",
            order_id=notification.order.id,
        )

    return redirect(
        "notifications:list"
    )


@login_required
def mark_all_as_read(request):

    if request.method == "POST":

        Notification.objects.filter(
            user=request.user,
            is_read=False,
        ).update(
            is_read=True
        )

    return redirect(
        "notifications:list"
    )
