from django.conf import settings
from django.db import models
from products.models import ProductVariant


class Cart(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart_items",
    )

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="cart_items",
    )

    quantity = models.PositiveIntegerField(default=1)

    added_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "variant")
        ordering = ["-updated_at"]

    @property
    def subtotal(self):
        return self.variant.price * self.quantity

    def __str__(self):
        return f"{self.user.username} - {self.variant.product.name} ({self.quantity})"