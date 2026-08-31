from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Review(models.Model):
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
        limit_choices_to={"role": "customer"},
    )
    product = models.ForeignKey(
        "products.Product", on_delete=models.CASCADE, null=True, blank=True, related_name="reviews"
    )
    service = models.ForeignKey(
        "services.Service", on_delete=models.CASCADE, null=True, blank=True, related_name="reviews"
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("customer", "product"),
                name="unique_customer_product_review",
            ),
            models.UniqueConstraint(
                fields=("customer", "service"),
                name="unique_customer_service_review",
            ),
        ]

    def clean(self):
        from django.core.exceptions import ValidationError

        if not self.product and not self.service:
            raise ValidationError("A review must reference a product or a service.")
        if self.product and self.service:
            raise ValidationError("A review cannot reference both a product and a service.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        target = self.product or self.service
        return f"{self.customer.full_name} -> {target}"
