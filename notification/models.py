
import uuid

from django.conf import settings
from django.db import models

from orders.models import Order


class Notification(models.Model):

    NOTIFICATION_TYPES = [
        ("order_placed", "Order Placed"),
        ("order_cancelled", "Order Cancelled"),
        ("order_deleted", "Order Deleted"),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications",
    )

    notification_type = models.CharField(
        max_length=30,
        choices=NOTIFICATION_TYPES,
    )

    title = models.CharField(
        max_length=200
    )

    message = models.TextField()

    is_read = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} - {self.title}"