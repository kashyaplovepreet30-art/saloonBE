from django.contrib.auth.models import AbstractUser
from django.db import models


class RoleChoices(models.TextChoices):
    ADMIN = "admin", "Admin"
    CUSTOMER = "customer", "Customer"
    STAFF = "staff", "Staff"


class User(AbstractUser):
    """Custom user model with role-based access control."""

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    role = models.CharField(
        max_length=20, choices=RoleChoices.choices, default=RoleChoices.CUSTOMER
    )
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, default="")
    profile_image = models.ImageField(
        upload_to="profiles/", blank=True, null=True
    )
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def full_name(self):
        return self.get_full_name() or self.email

    def __str__(self):
        return self.email or self.username
