from .models import Notification


def create_notification(
    *,
    user,
    notification_type,
    title,
    message,
    order=None,
):
    return Notification.objects.create(
        user=user,
        order=order,
        notification_type=notification_type,
        title=title,
        message=message,
    )