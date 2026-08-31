import uuid

from django.conf import settings
from django.db import models


class PaymentStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PAID = "paid", "Paid"
    FAILED = "failed", "Failed"
    REFUNDED = "refunded", "Refunded"


class PaymentMethod(models.TextChoices):
    UPI = "upi", "UPI"
    CREDIT_CARD = "credit_card", "Credit Card"
    DEBIT_CARD = "debit_card", "Debit Card"
    NET_BANKING = "net_banking", "Net Banking"
    WALLET = "wallet", "Wallet"
    CASH = "cash", "Cash"


class Payment(models.Model):
    transaction_id = models.CharField(max_length=100, unique=True, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payments"
    )
    order = models.ForeignKey(
        "orders.Order", on_delete=models.SET_NULL, null=True, blank=True, related_name="payments"
    )
    appointment = models.ForeignKey(
        "appointments.Appointment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(
        max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.CASH
    )
    status = models.CharField(
        max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING
    )
    gateway_reference = models.CharField(max_length=200, blank=True, default="")
    # Razorpay identifiers. gateway_order_id is created before the browser is
    # handed off; the other two arrive on the success callback and are what the
    # signature check is run against.
    gateway_order_id = models.CharField(max_length=100, blank=True, default="")
    gateway_payment_id = models.CharField(max_length=100, blank=True, default="")
    gateway_signature = models.CharField(max_length=200, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = "PAY-" + uuid.uuid4().hex[:10].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.transaction_id
