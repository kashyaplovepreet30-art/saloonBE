from django.core.validators import MinValueValidator
from django.db import models


class ServiceCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, default="")
    image = models.ImageField(upload_to="service_categories/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "service categories"
        ordering = ("name",)

    def __str__(self):
        return self.name


class ServiceStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"


class Service(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(
        ServiceCategory, on_delete=models.SET_NULL, null=True, related_name="services"
    )
    description = models.TextField(blank=True, default="")

    # Storefront presentation fields. Editable from the admin dashboard so the
    # services copy and styling are not hard-coded in the frontend.
    tagline = models.CharField(max_length=200, blank=True, default="")
    gradient = models.CharField(
        max_length=200,
        blank=True,
        default="",
        help_text="CSS background value used on service cards, e.g. var(--gradient-blush)",
    )
    includes = models.JSONField(
        default=list, blank=True, help_text="List of short bullet strings describing what is included"
    )

    duration_minutes = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    discount = models.DecimalField(
        max_digits=5, decimal_places=2, default=0, validators=[MinValueValidator(0)]
    )
    image = models.ImageField(upload_to="services/", blank=True, null=True)
    status = models.CharField(
        max_length=20, choices=ServiceStatus.choices, default=ServiceStatus.ACTIVE
    )
    required_staff = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    @property
    def final_price(self):
        return self.price - (self.price * self.discount / 100)

    def __str__(self):
        return self.name
