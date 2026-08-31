from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class StaffStatus(models.TextChoices):
    AVAILABLE = "available", "Available"
    BUSY = "busy", "Busy"
    ON_LEAVE = "on_leave", "On Leave"
    INACTIVE = "inactive", "Inactive"


class StaffProfile(models.Model):
    """Additional profile information for staff users."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="staff_profile",
    )
    department = models.CharField(max_length=100, blank=True, default="")
    skills = models.TextField(blank=True, default="")
    experience_years = models.PositiveIntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=StaffStatus.choices,
        default=StaffStatus.AVAILABLE,
    )
    joining_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_assignable(self):
        return self.status == StaffStatus.AVAILABLE

    def __str__(self):
        return self.user.full_name


class RequestStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"


class RequestUrgency(models.TextChoices):
    STANDARD = "standard", "Standard"
    URGENT = "urgent", "Urgent"


class ItemRequest(models.Model):
    """Stock or supplies a staff member has asked the admin team to order."""

    staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="item_requests",
        limit_choices_to={"role": "staff"},
    )
    item = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    reason = models.TextField(blank=True, default="")
    urgency = models.CharField(
        max_length=20, choices=RequestUrgency.choices, default=RequestUrgency.STANDARD
    )
    status = models.CharField(
        max_length=20, choices=RequestStatus.choices, default=RequestStatus.PENDING
    )
    admin_notes = models.TextField(blank=True, default="")
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_item_requests",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.item} x{self.quantity} ({self.get_status_display()})"
