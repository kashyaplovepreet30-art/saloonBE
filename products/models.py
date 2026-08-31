from django.core.validators import MinValueValidator
from django.db import models

from categories.models import Category


class ProductStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    OUT_OF_STOCK = "out_of_stock", "Out of Stock"
    DRAFT = "draft", "Draft"
    INACTIVE = "inactive", "Inactive"


class Product(models.Model):
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name="products"
    )
    brand = models.CharField(max_length=100, blank=True, default="")
    description = models.TextField(blank=True, default="")

    # Storefront presentation fields. Editable from the admin dashboard so the
    # shop copy and styling are not hard-coded in the frontend.
    tagline = models.CharField(max_length=200, blank=True, default="")
    concern = models.CharField(
        max_length=100, blank=True, default="", help_text="e.g. Repair, Hydration, Brightening"
    )
    size = models.CharField(
        max_length=50, blank=True, default="", help_text="Display pack size, e.g. 50ml"
    )
    gradient = models.CharField(
        max_length=200,
        blank=True,
        default="",
        help_text="CSS background value used on product cards, e.g. var(--gradient-blush)",
    )
    bestseller = models.BooleanField(default=False)
    ingredients = models.TextField(blank=True, default="")
    details = models.JSONField(
        default=list, blank=True, help_text="List of short bullet strings shown on the product page"
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    discount = models.DecimalField(
        max_digits=5, decimal_places=2, default=0, validators=[MinValueValidator(0)]
    )
    gst_tax = models.DecimalField(
        max_digits=5, decimal_places=2, default=0, validators=[MinValueValidator(0)]
    )
    stock_quantity = models.PositiveIntegerField(default=0)
    weight = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    status = models.CharField(
        max_length=20, choices=ProductStatus.choices, default=ProductStatus.ACTIVE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    @property
    def final_price(self):
        """Price after discount, before tax."""
        return self.price - (self.price * self.discount / 100)

    @property
    def in_stock(self):
        return self.stock_quantity > 0

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="products/gallery/")
    alt_text = models.CharField(max_length=200, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - image {self.id}"
