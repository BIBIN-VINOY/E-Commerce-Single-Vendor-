
import uuid
from django.db import models
from django.conf import settings
from products.models import ProductVariant


class Wishlist(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wishlist_items"
    )

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="wishlisted_by"
    )

    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "variant")
        ordering = ["-added_at"]

    def __str__(self):
        return f"{self.user.username} - {self.variant}"