from django.conf import settings
from django.db import models


class NotificationType(models.TextChoices):
    APPOINTMENT = "appointment", "Appointment"
    ORDER = "order", "Order"
    PAYMENT = "payment", "Payment"
    SYSTEM = "system", "System"


class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    notification_type = models.CharField(
        max_length=20, choices=NotificationType.choices, default=NotificationType.SYSTEM
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.user.full_name}: {self.title}"


def notify(user, notification_type, title, message):
    """Create an in-application notification for a user."""
    return Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message,
    )
